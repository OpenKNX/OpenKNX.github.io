# OAM Filter and Sort Configuration
# (C) 2025-2026 Cornelius Köpp; For Usage in OpenKNX-Project only

from dataclasses import dataclass

from model.oam_data import OamData


@dataclass(frozen=True)
class OamConfig:
    appPrefix: str
    appSpecialNames: list[str]
    appExclusion: list[str]
    appOrder: list[str]

    def include_repo(self, repo: dict[str, str]) -> bool:
        rn = repo["name"]
        return (rn.startswith(self.appPrefix) or rn in self.appSpecialNames) and rn not in self.appExclusion

    def sort(self, oam_data: dict[str, OamData]) -> dict[str, OamData]:
        # Sort based on given order, all others at end
        oam_data_sorted = {oam: oam_data[oam] for oam in self.appOrder if oam in oam_data}
        oam_data_unsorted = {oam: oam_data[oam] for oam in oam_data if oam not in self.appOrder}
        return {**oam_data_sorted, **oam_data_unsorted}

# names for identification of app repos:
appConfig = OamConfig(
    appPrefix = "OAM-",
    appSpecialNames = {
        "SOM-UP",
        "GW-REG1-Dali",
        "SEN-UP1-8xTH",
        "BEM-GardenControl",
    },
    appExclusion = {
        "OAM-TestApp",
    },
    appOrder = [

        # virtual only
        "OAM-LogicModule",
        "OAM-StateEngine",
        "OAM-ShutterController",
        "OAM-ClimateControl",

        # virtual with optional hardware
        "OAM-RaumController",
        "OAM-PresenceModule",
        "OAM-VirtualButton",
        "OAM-Meter",

        # universal sensor hardware
        "OAM-SensorModule",
        "SEN-UP1-8xTH",
        "OAM-UP1-8xSensor",

        # gateways to other systems
        "GW-REG1-Dali",
        "OAM-InfraredGateway",
        "OAM-OneWireModule",
        "OAM-EnoceanGateway",
        "OAM-EnoceanGateway_V2",
        "OAM-ModbusGateway",
        "OAM-Aircondition",
        "OAM-Nuki",

        # gateway with ip + direct hardware control
        "OAM-SonosNFCPlayer",
        # gateways with ip
        "OAM-Sonos",
        "OAM-Homematic",
        "OAM-SmartHomeBridge",

        # network
        "OAM-InternetServices",
        "OAM-IP-Router",

        # dummy-app only
        "OAM-Dummy",

        # special hardware
        "OAM-WeatherWN90LP",
        "OAM-NeoPixel",
        "SOM-UP",
        "OAM-AccessControl",
        "BEM-GardenControl",
        "OAM-TouchRound",

        # "boring" hardware
        "OAM-UP1-Taster",
        "OAM-REG1-Schaltaktor-4x",
        "OAM-SwitchActuator",
        "OAM-BinaryInput",
        "OAM-HeatingActuator",
        "OAM-LedDimmer-AB",

        # very, very special
        "OAM-ElectricDoorDrive",
        "OAM-BinaryClock",
    ]
)
