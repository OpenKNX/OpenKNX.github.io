# Central Handling of Filesystem-Paths for OAM-/OFM-/Devices-Info
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import os
import re


class PathManager:
    def __init__(self, base_dir="docs"):
        """
        Initialisiert den PathManager mit einem Basisverzeichnis.

        :param base_dir: Das Basisverzeichnis, in dem alle Dateien und Ordner erstellt werden.
        """
        self.base_dir = base_dir

    def get_base_path(self):
        """
        Gibt den Basisverzeichnispfad zurück.
        """
        return self.base_dir

    def create_path(self, *subdirs, filename=""):
        """
        Erstellt einen Pfad basierend auf dem Basisverzeichnis, den angegebenen Unterverzeichnissen
        und einem optionalen zusätzlichen Verzeichnis.

        :param subdirs: Beliebige Anzahl von Unterverzeichnissen. None wird entfernt
        :param filename: Ein optionaler Dateiname.
        :return: Der vollständige Pfad.
        """
        subdirs = tuple(filter(None, subdirs))
        os.makedirs(os.path.join(self.base_dir, *subdirs), exist_ok=True)
        if filename:
            return os.path.join(self.base_dir, *subdirs, filename)
        return os.path.join(self.base_dir, *subdirs)

    def get_oam_path(self, oam_name, filename=""):
        """
        Gibt den Pfad für ein spezifisches OAM zurück.

        :param oam_name: Der Name des OAM | `None` für Übersicht.
        :return: Der Pfad für das OAM.
        """
        return self.create_path("oam", oam_name, filename=filename)

    def get_ofm_path(self, ofm_name, filename=""):
        """
        Gibt den Pfad für ein spezifisches OFM zurück.

        :param ofm_name: Der Name des OFM | `None` für Übersicht.
        :return: Der Pfad für das OFM.
        """
        return self.create_path("ofm", ofm_name, filename=filename)

    def get_device_path(self, device_name, filename=""):
        """
        Gibt den Pfad für ein spezifisches Gerät zurück.

        :param device_name: Der Name des Geräts | `None` für Übersicht.
        :return: Der Pfad für das Gerät.
        """
        device_filename = self.to_device_pathname(device_name) if device_name else None
        return self.create_path("devices", device_filename, filename=filename)

    def ensure_directory(self, *subdirs):
        """
        Stellt sicher, dass ein Verzeichnis existiert, und erstellt es bei Bedarf.

        :param subdirs: Beliebige Anzahl von Unterverzeichnissen.
        :return: Der vollständige Pfad des erstellten Verzeichnisses.
        """
        path = self.create_path(*subdirs)
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def to_device_pathname(device_name):
        umlauts = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue'}
        for umlaut, replacement in umlauts.items():
            device_name = device_name.replace(umlaut, replacement)

        # allow alphanumeric, _ and - characters only
        return re.sub(r'[^A-Za-z0-9_-]', '_', device_name)
