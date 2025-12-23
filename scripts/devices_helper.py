# Handling/Mapping of Devíce Names Used by Firmware in Releases
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import json
import logging
import os


class DeviceHelper:
    def __init__(self):
        with open(os.path.join("data", 'devices_mapping.json'), 'r', encoding='utf-8') as f:
            self.device_name_map = json.load(f)

    def is_open_device(self, device_name):
        return "OpenKNX" in device_name

    def hw_name_mapping(self, oam, hw_text):
        hw_text_oam = f"{hw_text}@{oam}"
        if hw_text_oam in self.device_name_map:
            logging.warning(f"((>>WORKAROUND<<)) OAM-specific mapping of device-name for '{hw_text}' in '{oam}'")
            return self.device_name_map[hw_text_oam]
        if hw_text in self.device_name_map:
            return self.device_name_map[hw_text]
        else:
            logging.warning(f"Unknown Device Name in '{oam}': {hw_text}")
            return f"(???)-{hw_text}"
