# Handling/Mapping of Devíce Names Used by Firmware in Releases
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import logging


class DeviceHelper:
    def __init__(self):
        self.device_name_map = {
            "AB-SmartHouse-BinaryClock":                     "AB-SmartHouse-BinaryClock",
            "AB-SmartHouse_CC_REG_12CH":                     "AB-SmartHouse_CC_REG_12CH",
            "AB-SmartHouse_CC_UP_16CH":                      "AB-SmartHouse_CC_UP_16CH",
            "AB-SmartHouse_CC_UP_8CH":                       "AB-SmartHouse_CC_UP_8CH",
            "AB-SmartHouse_CV_REG_12CH":                     "AB-SmartHouse_CV_REG_12CH",
            "AB-SmartHouse_CV_REG_12CH_CS":                  "AB-SmartHouse_CV_REG_12CH_CS",
            "AB-SmartHouse_CV_UP_6CH":                       "AB-SmartHouse_CV_UP_6CH",
            "AB-SmartHouse_CV_UP_6CH_CS":                    "AB-SmartHouse_CV_UP_6CH_CS",
            "AB-SmartHouse-PresenceMR16":                    "AB-SmartHouse-PresenceMR16",
            "AB-SmartHouse-PresenceMultiSensor":             "AB-SmartHouse-PresenceMultiSensor",
            "AB-SmartHouse-PresenceWall":                    "AB-SmartHouse-PresenceWall",
            "AB-SmartHouse-SwitchActuator-REG6-8CH":         "AB-SmartHouse-SwitchActuator-REG6-8CH",
            "AB-TouchRound-RP2350":                          "AB-SmartHouse-TouchRound-RP2350",
            "ABSmartHouse-BinaryInput":                      "AB-SmartHouse-BinaryInput",
            "AccessControl":                                 "AB-AccessControl",
            "Aircondition-AZDelivery_DevKit_C_V4_IP":        "OpenKNX AZDelivery ESP32 Board Dev Kit C V4 (IP)",
            "Aircondition-AZDelivery_DevKit_C_V4_TP":        "OpenKNX AZDelivery ESP32 Board Dev Kit C V4 (TP)",
            "Aircondition-Adafruit_Feather_ESP32_V2_IP":     "OpenKNX Adafruit ESP32 Feather V2",
            "Aircondition-Adafruit_Feather_ESP32_V2_TP":     "OpenKNX Adafruit ESP32 Feather V2 (TP)",
            "DeveloperBoard-JustForTesters":                 "SmartMF Entwicklerboard",
            "EnoceanGateway_RP2040":                         "SmartMF Enocean Gateway RP2040",
            "GW-UP1-IR":                                     "OpenKNX UP1 8xSensor",  # TODO: deprecated
            "GardenControl":                                 "SmartMF-GardenControl",
            "IP-Router-REG1-Eth":                            "OpenKNX REG1 LAN Gateway",
            "IP-Router-REG1-LAN-TP-Base":                    "OpenKNX REG1 Basismodul LAN+TP",
            "InternetServices-Adafruit_Feather_ESP32_V2_IP": "OpenKNX Adafruit ESP32 Feather V2",
            "InternetServices-Adafruit_Feather_ESP32_V2_TP": "OpenKNX Adafruit ESP32 Feather V2 (TP)",
            "InternetServices-REG1-ETH":                     "OpenKNX REG1 LAN Gateway",
            "InternetServices-REG1-LAN-Base":                "OpenKNX REG1 Basismodul IP",
            "InternetServices-REG1-LAN-TP-Base":             "OpenKNX REG1 Basismodul LAN+TP",
            "OpenKNX-OpenKNXiao-V1-Mini-ESP32":              "OpenKNXiao V1 Mini ESP32",
            "OpenKNX-OpenKNXiao-V1-Mini-RP2040":             "OpenKNXiao V1 Mini RP2040",
            "OpenKNX-PiPico-BCU-Connector":                  "OpenKNX PiPico BCU Connector",
            "OpenKNX-REG1-BASE":                             "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-BASE-V0":                          "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-BASE-V1":                          "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Base":                             "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Base-V0":                          "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-Base-V1":                          "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Base___no-time-led":               "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Base___time-led3":                 "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Basismodul":                       "OpenKNX REG1 Basismodul",
            "OpenKNX-REG1-Basismodul-IP":                    "OpenKNX REG1 Basismodul IP",
            "OpenKNX-REG1-Basismodul-V0":                    "OpenKNX REG1 Basismodul V0",
            "OpenKNX-REG1-LAN-BASE":                         "OpenKNX REG1 Basismodul IP",
            "OpenKNX-REG1-LAN-TP-BASE":                      "OpenKNX REG1 Basismodul LAN+TP",
            "OpenKNX-REG1-MultiSensor":                      "OpenKNX REG1 Multisensor",
            "OpenKNX-REG2-PiPico-V1":                        "OpenKNX REG2 PiPico V1",
            "OpenKNX-REG2-PiPico-V1-DeviceDisplay-Meter":    "OpenKNX REG2 PiPico V1 DeviceDisplay Meter",
            "OpenKNX-UP1-8xSensor":                          "OpenKNX UP1 8xSensor",
            "OpenKNX-UP1-PM-HF":                             "OpenKNX UP1 Präsenzmelder+",
            "OpenKNX-UP1-SEN-8x":                            "OpenKNX UP1 8xSensor",
            "PiPico-BCU-Connector":                          "OpenKNX PiPico BCU Connector",
            "PiPico_BCU_Connector":                          "OpenKNX PiPico BCU Connector",
            "REG1-Dali":                                     "OpenKNX REG1 Dali Gateway",
            "REG1-LAN-TP-2xDali":                            "OpenKNX REG1 2x DALI LAN Gateway",
            "REG1-esp32":                                    "OpenKNX REG1 Basismodul LAN+TP Devboard V00.02 (ESP32)",
            "REG1-rp2040-v1":                                "OpenKNX REG1 Dali Gateway",
            "REG1-v0":                                       "OpenKNX REG1 Dali Gateway V0",
            "REG1-v1":                                       "OpenKNX REG1 Dali Gateway",
            "REG1_BASE_V0":                                  "OpenKNX REG1 Basismodul V0",
            "REG1_BASE_V1":                                  "OpenKNX REG1 Basismodul",
            "REG2_PIPICO_V1":                                "OpenKNX REG2 PiPico V1",  # old, # TODO check removal
            "RealPresence":                                  "SmartMF RealPresence",
            "RP2040@OAM-ModbusGateway":                      "SmartMF-Modbus--???--RP2040",
            "1TE-RP2040-SmartMF":                            "SmartMF-1TE-RP2040",
            "RealPresence_v2.0":                             "SmartMF RealPresence_v2.0",
            "SAMD@OAM-ModbusGateway":                        "SmartMF-Modubus--???--SAMD",
            "SEN-UP1-8XTH":                                  "OpenKNX UP1 8xSensor",
            "Sensormodul-v3.0-SAMD":                         "SmartMF-Sensormodul-v3.0-SAMD",
            "Sensormodul-v3.1-SAMD":                         "SmartMF-Sensormodul-v3.1-SAMD",
            "Sensormodul-v4.x-RP2040":                       "SmartMF-Sensormodul-v4.x-RP2040",
            "Sensormodul-v4x-RP2040":                        "SmartMF-Sensormodul-v4.x-RP2040",
            "Smart-MF-S0-Zaehlermodul":                      "SmartMF-S0-Zaehlermodul",
            "Smart-MF-eHZ-Schnittstelle":                    "SmartMF-eHZ-Schnittstelle",
            "SmartHomeBridge-Adafruit_Feather_ESP32_V2_IP":  "OpenKNX Adafruit ESP32 Feather V2",
            "SmartHomeBridge-Adafruit_Feather_ESP32_V2_TP":  "OpenKNX Adafruit ESP32 Feather V2 (TP)",
            "SmartHomeBridge-REG1-LAN-Base":                 "OpenKNX REG1 Basismodul IP",
            "SmartHomeBridge-REG1-LAN-TP-Base":              "OpenKNX REG1 Basismodul LAN+TP",
            "SmartMF-1TE-REG":                               "SmartMF-1TE-RP2040",
            "SmartMF-1TE-RP2040":                            "SmartMF-1TE-RP2040",
            "SmartMF-RealPresence-V2":                       "SmartMF RealPresence_v2.0",
            "SmartMF-Sensormodul-RP2040":                    "SmartMF-Sensormodul-v4.x-RP2040",
            "SmartMF-Soundmodul-REG":                        "Smart-MF Soundmodul REG",
            "SmartMF-Soundmodul-UP":                         "Smart-MF Soundmodul UP",
            "SmartMF-Soundmodul-UP-EXT-PWR":                 "Smart-MF Soundmodul UP (Ext-Power)",
            "Sonos-Adafruit_Feather_ESP32_V2_IP":            "OpenKNX Adafruit ESP32 Feather V2",
            "Sonos-Adafruit_Feather_ESP32_V2_TP":            "OpenKNX Adafruit ESP32 Feather V2 (TP)",
            "Sonos-REG1-LAN-Base":                           "OpenKNX REG1 Basismodul IP",
            "Sonos-REG1-LAN-TP-Base":                        "OpenKNX REG1 Basismodul LAN+TP",
            "TouchRound-RP2350":                             "AB-SmartHouse_TouchRound_RP2350",
            "UP1-GW-IR":                                     "OpenKNX UP1 8xSensor",  # TODO: check
            "UP1-PM-HF":                                     "OpenKNX UP1 Präsenzmelder+",
            "UP1-SEN-8x":                                    "OpenKNX UP1 8xSensor",
            "XIAO_MINI_V1":                                  "OpenKNXiao V1",  # old, # TODO check removal
            "firmware@OAM-EnoceanGateway":                   "SmartMF Enocean Gateway (SAMD)",
            "firmware@SEN-UP1-8xTH":                         "OpenKNX UP1 8xSensor",
            "firmware_REG1-GW-RS485":                        "OpenKNX REG1 RS485 Gateway",
            "firmware_REG1-SA-4xSELV":                       "OpenKNX REG1 4xSELV Schaltaktor",
            "firmware-RP2040-Breakout-just-for-testers":     "SmartMF-RP2040-Breakout-just-for-testers",
            "firmware_SMARTMF_1TE_REG":                      "SmartMF-1TE-RP2040",
            "firmware_SOM_UP":                               "Smart-MF Soundmodul UP",
            "firmware_UP1-GW-RS485":                         "OpenKNX UP1 RS485 Gateway",
        }

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
