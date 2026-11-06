"""Prüft die Gerätebilder data/devices/img/ gegen die Device-Registry (OGM-HardwareConfig, devices/*.json).

Fehler (Exit-Code 1):
  - Dateiname ist nicht <DEVICE_ID>.jpg oder die Datei ist kein JPEG.
  - Bild ist nicht quadratisch oder kleiner als 500 x 500 Pixel.
  - Zu einem Bild gibt es keine Gerätedatei devices/<DEVICE_ID>.json in der Registry.
Hinweis (kein Fehler): Gerät der Registry ohne Bild.

Aufruf: python scripts/catalog/check_images.py --registry <OGM-HardwareConfig> [--images data/devices/img]
"""
import argparse
import os
import sys

from PIL import Image

IMAGE_MIN = 500
errors = []


def report(kind, path, msg):
    if kind == "error":
        errors.append((path, msg))
    if os.environ.get("GITHUB_ACTIONS"):
        print(f"::{kind} file={path}::{msg}")
    else:
        print(f"{'FEHLER' if kind == 'error' else 'HINWEIS'} {path}: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--registry", required=True, help="Checkout von OGM-HardwareConfig")
    ap.add_argument("--images", default=os.path.join("data", "devices", "img"))
    args = ap.parse_args()

    devdir = os.path.join(args.registry, "devices")
    devices = {f[:-5] for f in os.listdir(devdir) if f.endswith(".json") and f != "schema.json"}
    images = sorted(os.listdir(args.images)) if os.path.isdir(args.images) else []

    for f in images:
        path = f"data/devices/img/{f}"
        stem, ext = os.path.splitext(f)
        if ext != ".jpg":
            report("error", path, "Bilder müssen <DEVICE_ID>.jpg heißen")
            continue
        if stem not in devices:
            report("error", path, f"keine Gerätedatei devices/{stem}.json in OGM-HardwareConfig")
        try:
            with Image.open(os.path.join(args.images, f)) as im:
                fmt, (w, h) = im.format, im.size
        except OSError as e:
            report("error", path, f"Bild nicht lesbar: {e}")
            continue
        if fmt != "JPEG":
            report("error", path, f"kein JPEG, sondern {fmt}")
        if w != h or w < IMAGE_MIN:
            report("error", path, f"{w} x {h} Pixel; erwartet quadratisch, mindestens {IMAGE_MIN} x {IMAGE_MIN}")

    for dev in sorted(devices - {os.path.splitext(f)[0] for f in images}):
        report("notice", f"data/devices/img/{dev}.jpg", "Gerät ohne Bild")

    print(f"{len(images)} Bilder geprüft, {len(errors)} Fehler")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
