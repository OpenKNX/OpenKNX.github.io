# Collect AppIDs used by OAMs
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from collections import defaultdict, OrderedDict


def extract_attributes_from_xml_tree(root_dir):
    """
    Durchsucht alle XML-Dateien in einem Verzeichnisbaum und extrahiert
    die Attribute `OpenKnxId` und `ApplicationNumber` aus dem Element `op:ETS`.

    Args:
        root_dir: Wurzelverzeichnis für die Suche

    Returns:
        dict: Verschachtelte Struktur {direktes_unterverzeichnis: {relativer_pfad: {"OpenKnxId": ..., "ApplicationNumber": ...}}}
    """
    result = defaultdict(dict)
    root_path = Path(root_dir)

    # Durchsuche alle XML-Dateien im Verzeichnisbaum
    for xml_file in root_path.rglob('*.xml'):
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()

            # Suche nach Element `op:ETS` (Namespace-aware)
            # Für `op:ETS` als namespaced Element
            element = root.find('.//{*}ETS') or root.find('. //op:ETS', {'op': ''})

            # Alternative: Wenn `op:ETS` ein einfacher Tag-Name ist
            if element is None:
                for elem in root.iter():
                    if elem.tag.endswith('ETS') or elem.tag == 'op:ETS':
                        element = elem
                        break

            if element is not None:
                attributes = {
                    'OpenKnxId': int(element.get('OpenKnxId'), 0),
                    'ApplicationNumber': int(element.get('ApplicationNumber'), 0)
                }

                # Nur hinzufügen, wenn mindestens ein Attribut vorhanden ist
                if attributes['OpenKnxId'] is not None or attributes['ApplicationNumber'] is not None:
                    # Berechne relativen Pfad zur Root
                    relative_path = xml_file.relative_to(root_path)

                    # Erstes Verzeichnis (direktes Unterverzeichnis von root)
                    if len(relative_path.parts) > 1:
                        # Datei liegt in einem Unterverzeichnis
                        first_level_dir = relative_path.parts[0]
                        # Pfad innerhalb des Unterverzeichnisses
                        second_level_path = str(Path(*relative_path.parts[1:]))
                    else:
                        # Datei liegt direkt in root
                        first_level_dir = "."
                        second_level_path = str(relative_path)

                    result[first_level_dir][second_level_path.replace("\\", "/")] = attributes

        except ET.ParseError as e:
            print(f"Fehler beim Parsen von {xml_file}: {e}")
        except Exception as e:
            print(f"Fehler bei {xml_file}: {e}")

    return dict(result)


if __name__ == "__main__":
    # need all repos
    root_directory = "repos"

    results = extract_attributes_from_xml_tree(root_directory)

    id_app_to_repo = {}
    for app, info in results.items():
        for file, info2 in info.items():
            appref = app + " / " + file.split("/")[-1]
            id_app_to_repo.setdefault(info2['OpenKnxId'], {}).setdefault(info2['ApplicationNumber'], []).append(re.sub("\.xml$", "", appref))

    appid_to_repo = OrderedDict()
    for app_id, info in id_app_to_repo.items():
        for app_number, info2 in info.items():
            appid_to_repo["0x%04X" % ((app_id << 8) | app_number)] = info2[0] if len(info2) == 1 else info2


    # Ausgabe
    import json

    print(json.dumps(results, indent=2, ensure_ascii=False))
    print(json.dumps(id_app_to_repo, indent=2, ensure_ascii=False))
    appid2repo = {
        "OpenKnxContentType": "OpenKNX/OAMs/Id2Repo",
        "OpenKnxFormatVersion": "v0.1.0",
        "data": appid_to_repo
    }
    print(json.dumps(appid2repo, indent=2, ensure_ascii=False, sort_keys=True))