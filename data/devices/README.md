# Gerätebilder der Device-Registry

Die Gerätedaten stehen in [OpenKNX/OGM-HardwareConfig](https://github.com/OpenKNX/OGM-HardwareConfig) unter
`devices/<DEVICE_ID>.json`. Hier liegen nur die Bilder dazu; `.github/workflows/update_device_catalog.yml` erzeugt
aus beidem `docs/catalog/devices.json` und `docs/catalog/devices/img/`.

## Regeln

- `img/<DEVICE_ID>.jpg`, JPEG, quadratisch, mindestens 500 × 500 Pixel.
- Zu jedem Bild gibt es `devices/<DEVICE_ID>.json` in OGM-HardwareConfig `v1`. Bei einem neuen Gerät deshalb
  zuerst die Gerätedatei dort, danach das Bild hier per PR einreichen.
- Geräte ohne Bild sind erlaubt.

Prüfung: `python scripts/catalog/check_images.py --registry <Checkout von OGM-HardwareConfig>` (braucht Pillow).

## Veröffentlichung auf catalog.openknx.de

catalog.openknx.de holt `docs/catalog/` selbst von GitHub, es werden keine Zugangsdaten hinterlegt. Im Verzeichnis
der Subdomain liegen `scripts/catalog/webspace/update.php` und `.htaccess`; ein Cronjob ruft `update.php` alle
15 Minuten auf, zusätzlich stößt die Action den Abgleich nach jeder Änderung an.
