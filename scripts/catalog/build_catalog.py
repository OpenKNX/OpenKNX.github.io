"""Aggregator der Device-Registry: erzeugt devices.json und die Bilder für catalog.openknx.de.

Liest die Gerätedateien aus OGM-HardwareConfig (devices/*.json, dort geprüft) und die Bilder aus
data/devices/img/ (mit check_images.py geprüft) und schreibt
  <out>/devices.json
  <out>/devices/img/<DEVICE_ID>.jpg      (unverändert kopiert; nicht mehr vorhandene werden entfernt)

Ergänzt gegenüber den Gerätedateien:
  - Dateikopf OpenKnxContentType, OpenKnxFormatVersion, generated, source
  - id als Schlüssel unter data
  - kind: openknx, wenn vendor = OpenKNX, sonst third-party
  - ip: true, wenn network lan, wlan oder spe enthält
  - links.wiki: https://device.openknx.de/<id>, wenn die Gerätedatei keinen wiki-Link hat und diese URL erreichbar
    ist (dort ist eine Weiterleitung eingetragen); explizite wiki-Links werden ebenfalls geprüft, aber nur gemeldet
  - image: URL des Bildes, wenn data/devices/img/<id>.jpg existiert, mit ?v=<8 Zeichen SHA-256 des Bildes>; so ändert
    ein neues Bild devices.json, und catalog.openknx.de (update.php) sowie Clients erkennen es

devices.json wird nur neu geschrieben, wenn sich der Inhalt (data) geändert hat; sonst bleiben generated und
source stehen, damit der zeitgesteuerte Lauf keine leeren Commits erzeugt.

Aufruf: python scripts/catalog/build_catalog.py --registry <OGM-HardwareConfig> [--images data/devices/img]
        [--out docs/catalog] [--base-url https://catalog.openknx.de] [--no-link-check]
"""
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import urllib.error
import urllib.request

IP_NETWORKS = {"lan", "wlan", "spe"}
ORDER = ["name", "vendor", "kind", "category", "platform", "formFactor", "mcu", "network", "ip", "power",
         "status", "availability", "description", "translations", "links", "image"]


def link_ok(url):
    """True = erreichbar (Weiterleitungen gefolgt), False = HTTP-Fehler (z. B. 404), None = Netzwerkfehler."""
    req = urllib.request.Request(url, headers={"User-Agent": "OpenKNX-catalog"})
    try:
        with urllib.request.urlopen(req, timeout=30):
            return True
    except urllib.error.HTTPError:
        return False
    except (urllib.error.URLError, OSError):
        return None


def registry_sha(path):
    try:
        return subprocess.run(["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "v1"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, help="Checkout von OGM-HardwareConfig")
    ap.add_argument("--images", default=os.path.join("data", "devices", "img"))
    ap.add_argument("--out", default=os.path.join("docs", "catalog"))
    ap.add_argument("--base-url", default="https://catalog.openknx.de")
    ap.add_argument("--no-link-check", action="store_true", help="wiki-Links nicht prüfen (offline)")
    args = ap.parse_args()

    devdir = os.path.join(args.registry, "devices")
    outimg = os.path.join(args.out, "devices", "img")
    os.makedirs(outimg, exist_ok=True)

    data = {}
    for f in sorted(os.listdir(devdir), key=str.lower):
        if not f.endswith(".json") or f == "schema.json":
            continue
        with open(os.path.join(devdir, f), encoding="utf-8-sig") as fh:
            dev = json.load(fh)
        dev_id = dev.pop("id")
        dev["kind"] = "openknx" if dev["vendor"] == "OpenKNX" else "third-party"
        dev["ip"] = bool(IP_NETWORKS & set(dev["network"]))
        links = dev.setdefault("links", {})
        if "wiki" in links:
            if not args.no_link_check and link_ok(links["wiki"]) is False:
                print(f"Hinweis: {dev_id}: wiki-Link {links['wiki']} nicht erreichbar")
        else:
            wiki = f"https://device.openknx.de/{dev_id}"
            ok = True if args.no_link_check else link_ok(wiki)
            if ok is None:
                print(f"Warnung: {dev_id}: {wiki} nicht prüfbar (Netzwerk), Link bleibt")
            if ok is False:
                print(f"Hinweis: {dev_id}: {wiki} nicht erreichbar, kein wiki-Link")
            else:
                links["wiki"] = wiki
        if not links:
            del dev["links"]
        img = os.path.join(args.images, dev_id + ".jpg")
        if os.path.isfile(img):
            target = os.path.join(outimg, dev_id + ".jpg")
            with open(img, "rb") as fh:
                content = fh.read()
            if not os.path.isfile(target) or content != open(target, "rb").read():
                shutil.copyfile(img, target)
            dev["image"] = f"{args.base_url}/devices/img/{dev_id}.jpg?v={hashlib.sha256(content).hexdigest()[:8]}"
        data[dev_id] = {k: dev[k] for k in ORDER if k in dev}

    for f in os.listdir(outimg):
        if os.path.splitext(f)[0] not in data or "image" not in data[os.path.splitext(f)[0]]:
            os.remove(os.path.join(outimg, f))

    out_json = os.path.join(args.out, "devices.json")
    try:
        with open(out_json, encoding="utf-8") as fh:
            unchanged = json.load(fh).get("data") == data
    except (OSError, ValueError):
        unchanged = False
    if unchanged:
        print(f"{len(data)} Geräte, devices.json unverändert")
        return

    catalog = {
        "OpenKnxContentType": "OpenKNX/Devices",
        "OpenKnxFormatVersion": "v1.0.0",
        "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": f"https://github.com/OpenKNX/OGM-HardwareConfig/tree/{registry_sha(args.registry)}/devices",
        "data": data,
    }
    with open(out_json, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(catalog, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print(f"{len(data)} Geräte, {sum(1 for d in data.values() if 'image' in d)} mit Bild, Ausgabe in {args.out}")


if __name__ == "__main__":
    main()
