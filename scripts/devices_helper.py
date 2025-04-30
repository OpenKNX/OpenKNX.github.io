# Handling/Mapping of Devíce Names Used by Firmware in Releases
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import logging


class DeviceHelper:
    def __init__(self):
        self.device_name_map = {
            "1TE-RP2040-SmartMF": "SmartMF-1TE-RP2040",
            "AB-SmartHouse-BinaryClock": "AB-SmartHouse-BinaryClock",
            "ABSmartHouse-BinaryInput": "AB-SmartHouse-BinaryInput",
            "AB-SmartHouse-PresenceMR16": "AB-SmartHouse-PresenceMR16",
            "AB-SmartHouse-PresenceMultiSensor": "AB-SmartHouse-PresenceMultiSensor",
            "AB-SmartHouse-PresenceWall": "AB-SmartHouse-PresenceWall",
            "AB-SmartHouse-SwitchActuator-REG6-8CH": "AB-SmartHouse-SwitchActuator-REG6-8CH",
            "AccessControl": "AB-AccessControl",
            "DeveloperBoard-JustForTesters": "?-DeveloperBoard-JustForTesters",
            "EnoceanGateway_RP2040": "Smart-MF Enocean Gateway RP2040",
            "firmware_UP1-GW-RS485": "OpenKNX UP1 RS485 Gateway",
            "firmware_SOM_UP": "Smart-MF Soundmodul",
            "GardenControl": "SmartMF-GardenControl",
            "GW-UP1-IR": "OpenKNX UP1 8xSensor",  # TODO: deprecated
            "IP-Router-REG1-Eth": "OpenKNX REG1 Basismodul IP",
            "IP-Router-REG1-LAN-TP-Base": "OpenKNX REG1 Basismodul LAN+TP",
            "OpenKNX-PiPico-BCU-Connector": "OpenKNX PiPico BCU Connector",
            "OpenKNX-REG1-Base-V0": "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-BASE-V0": "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-Base": "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Base-V1": "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-BASE-V1": "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Basismodul": "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Basismodul-V0": "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-MultiSensor": "OpenKNX REG1 Multisensor",
            "OpenKNX-UP1-8xSensor": "OpenKNX UP1 8xSensor",
            "PiPico_BCU_Connector": "OpenKNX PiPico BCU Connector",
            "PiPico-BCU-Connector": "OpenKNX PiPico BCU Connector",
            "RealPresence": "?-RealPresence",
            "RealPresence_v2.0": "?-RealPresence_v2.0",
            "REG1_BASE_V0": "OpenKNX REG1 Basismodul V0",
            "REG1_BASE_V1": "OpenKNX REG1 Basismodul",

            # DALI-Devices
            "REG1-v0": "OpenKNX REG1 Dali Gateway V0",
            "REG1-v1": "OpenKNX REG1 Dali Gateway",
            "REG1-rp2040-v1": "OpenKNX REG1 Dali Gateway",
            "REG1-esp32": "OpenKNX REG1 Basismodul LAN+TP Devboard V00.02 (ESP32)",

            "REG2_PIPICO_V1": "OpenKNX REG2 PiPico2 V1",
            "Sensormodul-v3.0-SAMD": "SmartMF-Sensormodul-v3.0-SAMD",
            "Sensormodul-v3.1-SAMD": "SmartMF-Sensormodul-v3.1-SAMD",
            "Sensormodul-v4.x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
            "Sensormodul-v4x-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
            "SEN-UP1-8XTH": "OpenKNX UP1 8xSensor",
            "SmartMF-1TE-RP2040": "SmartMF-1TE-RP2040",
            "Smart-MF-eHZ-Schnittstelle": "Smart-MF-eHZ-Schnittstelle",
            "Smart-MF-S0-Zaehlermodul": "Smart-MF-S0-Zaehlermodul",
            "SmartMF-Sensormodul-RP2040": "SmartMF-Sensormodul-v4.x-RP2040",
            "UP1-GW-IR": "OpenKNX UP1 8xSensor",  # TODO: check
            "UP1-PM-HF": "OpenKNX UP1 Präsenzmelder+",
            "XIAO_MINI_V1": "OpenKNXiao V1",
        }

    def is_open_device(self, device_name):
        return "OpenKNX" in device_name

    def hw_name_mapping(self, oam, hw_text):
        if oam == "SEN-UP1-8xTH" and hw_text == "firmware":
            logging.warning(f"((>>WORKAROUND<<)) OAM-specific mapping of device-name for '{hw_text}' in '{oam}'")
            return "OpenKNX UP1 8xSensor"
        if oam == "OAM-EnoceanGateway" and hw_text == "firmware":
            logging.warning(f"((>>WORKAROUND<<)) OAM-specific mapping of device-name for '{hw_text}' in '{oam}'")
            return "Smart-MF Enocean Gateway (SAMD)"
        if hw_text in self.device_name_map:
            return self.device_name_map[hw_text]
        else:
            logging.warning(f"Unknown Device Name in '{oam}': {hw_text}")
            return f"(???)-{hw_text}"
