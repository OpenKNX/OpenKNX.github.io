<?php
/*
 * catalog.openknx.de: holt den Gerätekatalog aus OpenKNX/OpenKNX.github.io (Branch siehe SOURCE, docs/catalog/).
 *
 * Liegt im Verzeichnis von catalog.openknx.de, zusammen mit der .htaccess aus diesem Ordner.
 * Aufruf:
 *   - per Cronjob, z. B. alle 15 Minuten:  php /pfad/zu/catalog.openknx/update.php
 *   - per HTTP von der Action update_device_catalog.yml nach jeder Änderung: https://catalog.openknx.de/update.php
 *     (höchstens einmal pro Minute; die Quelle ist fest eingetragen und öffentlich, ein Aufruf durch Dritte
 *     kann nur einen Abgleich auslösen)
 *
 * Ablauf: devices.json laden (bei unverändertem ETag fertig), geänderte Bilder anhand ?v=<SHA-256-Präfix> in der
 * Bild-URL holen und prüfen, nicht mehr verwendete Bilder löschen, zuletzt devices.json ersetzen. Jede Datei wird
 * erst vollständig geschrieben und dann umbenannt. Bei einem Fehler bleibt der bisherige Stand stehen.
 * Es werden keine Zugangsdaten benötigt.
 */
declare(strict_types=1);

const SOURCE = 'https://raw.githubusercontent.com/OpenKNX/OpenKNX.github.io/v1-registry/docs/catalog/';
const MIN_INTERVAL = 60;          // Sekunden zwischen zwei HTTP-Aufrufen
const MAX_JSON = 5 * 1024 * 1024;
const MAX_IMAGE = 15 * 1024 * 1024;

$cli = PHP_SAPI === 'cli';
if (!$cli) {
    header('Content-Type: text/plain; charset=utf-8');
    header('Cache-Control: no-store');
}

function out(string $msg): void { echo $msg, "\n"; }

function fail(string $msg, int $code = 500): void
{
    if (PHP_SAPI !== 'cli') { http_response_code($code); }
    out("Fehler: $msg");
    exit(1);
}

/** GET mit optionalem ETag; liefert [status, body, etag]. */
function fetch(string $url, int $max, ?string $etag = null): array
{
    $ch = curl_init($url);
    $headers = ['User-Agent: OpenKNX-catalog-update'];
    if ($etag !== null && $etag !== '') { $headers[] = "If-None-Match: $etag"; }
    $newEtag = null;
    curl_setopt_array($ch, [
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_FOLLOWLOCATION => false,
        CURLOPT_CONNECTTIMEOUT => 15,
        CURLOPT_TIMEOUT => 60,
        CURLOPT_HTTPHEADER => $headers,
        CURLOPT_PROTOCOLS => CURLPROTO_HTTPS,
        CURLOPT_HEADERFUNCTION => function ($ch, string $line) use (&$newEtag) {
            if (stripos($line, 'ETag:') === 0) { $newEtag = trim(substr($line, 5)); }
            return strlen($line);
        },
    ]);
    $body = curl_exec($ch);
    if ($body === false) { fail("$url: " . curl_error($ch)); }
    $status = (int)curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    if (strlen($body) > $max) { fail("$url: Antwort zu groß"); }
    return [$status, $body, $newEtag];
}

function write_atomic(string $path, string $content): void
{
    $tmp = $path . '.tmp';
    if (file_put_contents($tmp, $content) !== strlen($content) || !rename($tmp, $path)) {
        @unlink($tmp);
        fail("$path: Schreiben fehlgeschlagen");
    }
}

$dir = __DIR__;
$imgDir = "$dir/devices/img";
$stateFile = "$dir/.update-state.json";

// Nur ein Lauf gleichzeitig
$lock = fopen("$dir/.update.lock", 'c');
if ($lock === false || !flock($lock, LOCK_EX | LOCK_NB)) { out('Läuft bereits'); exit(0); }

$state = is_file($stateFile) ? (json_decode((string)file_get_contents($stateFile), true) ?: []) : [];
if (!$cli && time() - (int)($state['lastHttp'] ?? 0) < MIN_INTERVAL) {
    http_response_code(429);
    out('Zu häufig, später erneut');
    exit(0);
}
if (!$cli) {
    $state['lastHttp'] = time();
    write_atomic($stateFile, json_encode($state));
}

// devices.json; ?t= umgeht den Cache von raw.githubusercontent.com, der ETag spart die Übertragung
$haveJson = is_file("$dir/devices.json");
[$status, $json, $etag] = fetch(SOURCE . 'devices.json?t=' . time(), MAX_JSON, $haveJson ? ($state['etag'] ?? null) : null);
if ($status === 304) { out('devices.json unverändert'); exit(0); }
if ($status !== 200) { fail("devices.json: HTTP $status"); }

$catalog = json_decode($json, true);
if (!is_array($catalog) || ($catalog['OpenKnxContentType'] ?? '') !== 'OpenKNX/Devices' || !is_array($catalog['data'] ?? null)) {
    fail('devices.json: kein gültiger Gerätekatalog');
}

if (!is_dir($imgDir) && !mkdir($imgDir, 0755, true)) { fail("$imgDir: Anlegen fehlgeschlagen"); }

// Bilder holen, die fehlen oder sich geändert haben
$wanted = [];
$loaded = 0;
foreach ($catalog['data'] as $id => $dev) {
    if (!preg_match('/^[A-Za-z0-9_-]+$/', (string)$id)) { fail("ungültige Geräte-ID: $id"); }
    if (!isset($dev['image'])) { continue; }
    if (!preg_match('/[?&]v=([0-9a-f]{8})$/', (string)$dev['image'], $m)) { fail("$id: Bild-URL ohne ?v="); }
    $hash = $m[1];
    $file = "$imgDir/$id.jpg";
    $wanted["$id.jpg"] = true;
    if (is_file($file) && substr(hash_file('sha256', $file), 0, 8) === $hash) { continue; }
    [$st, $img] = fetch(SOURCE . "devices/img/$id.jpg?v=$hash", MAX_IMAGE);
    if ($st !== 200) { fail("$id.jpg: HTTP $st"); }
    if (substr(hash('sha256', $img), 0, 8) !== $hash) { fail("$id.jpg: Prüfsumme passt nicht (Quelle noch nicht aktuell?)"); }
    write_atomic($file, $img);
    $loaded++;
}

// Nicht mehr verwendete Bilder entfernen
$removed = 0;
foreach (glob("$imgDir/*.jpg") ?: [] as $file) {
    if (!isset($wanted[basename($file)])) { unlink($file); $removed++; }
}

write_atomic("$dir/devices.json", $json);
$state['etag'] = $etag;
$state['updated'] = gmdate('Y-m-d\TH:i:s\Z');
write_atomic($stateFile, json_encode($state));
out(sprintf('Aktualisiert: %d Geräte, %d Bilder geladen, %d entfernt', count($catalog['data']), $loaded, $removed));
