# Collect Statistic Data from App-XML of OpenKNX-Releas
# (C) 2025 Cornelius Köpp; For Usage in OpenKNX-Project only

import xml.etree.ElementTree as ET
from io import BytesIO


class AppSizingStat:
    """Class to extract and store application sizing information from ETS app XML files."""

    def __init__(self, xml_file):
        """
        Initialize AppSizingStat with XML file data.
        
        Args:
            xml_file: File-like object containing the XML data
        """
        self.application_number = 0
        self.application_version = 0
        self.replaces_version = []
        self.application_name = ""
        self.application_id = ""

        # Initialize properties
        self.parameter_memory_size = 0
        self.file_size = 0
        self.line_count = 0
        # Add counters for the requested XML elements
        self.parameter_count = 0
        self.parameter_ref_count = 0
        self.parameter_calculation_count = 0
        self.com_object_count = 0
        self.com_object_ref_count = 0
        # Max size of AddressTable und AssociationTable
        self.address_table_max_entries = 0
        self.association_table_max_entries = 0
        # Script Size
        self.script_size = 0
        self.script_lines = 0
        # ModuleDefs
        self.module_def_count = 0
        # Dynamic elements
        self.dynamic_element_count = 0
        self.choose_element_count = 0
        self.assign_element_count = 0
        # ParameterBlock and ParamRefRef
        self.parameter_block_count = 0
        self.max_param_ref_ref_count = 0

        # Process the file
        self._process_file(xml_file)

    def _process_file(self, xml_file):
        """Process the XML file to extract statistics"""
        try:
            # Read content (works for both file paths and file-like objects)
            content = self._read_content(xml_file)
            if not content:
                return

            # Get content size
            self.file_size = len(content)

            # Count lines
            if isinstance(content, bytes):
                self.line_count = content.count(b'\n') + 1
            else:
                self.line_count = content.count('\n') + 1

            # Create BytesIO for parsing
            if isinstance(content, str):
                content = content.encode('utf-8')

            xml_data = BytesIO(content)
            tree = ET.parse(xml_data)
            root = tree.getroot()

            # Erfasse die Attribute des Elements ApplicationProgram
            application_program = root.find(".//{*}ApplicationProgram")
            if application_program is not None:
                self.application_number = application_program.get("ApplicationNumber", -1)
                self.application_version = application_program.get("ApplicationVersion", -1)
                self.replaces_version = application_program.get("ReplacesVersions", "").split(" ")
                self.application_name = application_program.get("Name", "")
                self.application_id = application_program.get("Id", "")

            # Extract parameter memory size
            for segment in root.findall(".//{*}Static/{*}Code/{*}RelativeSegment[@Size]"):
                self.parameter_memory_size += int(segment.get('Size'))

            # Count XML elements
            self.parameter_count = len(root.findall(".//{*}Parameter"))
            self.parameter_ref_count = len(root.findall(".//{*}ParameterRef"))
            self.parameter_calculation_count = len(root.findall(".//{*}ParameterCalculation"))
            self.com_object_count = len(root.findall(".//{*}ComObject"))
            """ TODO 
                Ermittle die Gesamtgröße der KOs, durch Nutzung des Attribus ObjectSize in den Elementen ComObject. Dieser kann folgende Arten von Werten enthalten:
                * "1 Bit"
                * "2 Bits"
                * "1 Byte"
                * "2 Bytes"            
            """
            self.com_object_ref_count = len(root.findall(".//{*}ComObjectRef"))
            # Max size of AddressTable und AssociationTable
            address_table = root.find(".//{*}AddressTable[@MaxEntries]")
            if address_table is not None:
                self.address_table_max_entries = int(address_table.get("MaxEntries"))
            association_table = root.find(".//{*}AssociationTable[@MaxEntries]")
            if association_table is not None:
                self.association_table_max_entries = int(association_table.get("MaxEntries"))

            # Calculate the length of the text content in <Script> elements
            for script in root.findall(".//{*}Script"):
                if script.text:
                    self.script_size += len(script.text)
                    self.script_lines += script.text.count('\n') + 1

            # Count <ModuleDef> elements within <ModuleDefs>
            self.module_def_count = len(root.findall(".//{*}ModuleDefs/{*}ModuleDef"))

            # Count elements inside <Dynamic>
            dynamic = root.find(".//{*}ApplicationProgram/{*}Dynamic")
            if dynamic is not None:
                self.dynamic_element_count = len(dynamic.findall(".//*"))
                self.choose_element_count = len(dynamic.findall(".//{*}choose"))
                self.assign_element_count = len(dynamic.findall(".//{*}Assign"))

                self.parameter_block_count = 0
                self.max_param_ref_ref_count = 0
                for block in dynamic.findall('.//{*}ParameterBlock'):
                    if block.get('Inline') != "true":
                        # Count Non-Inline ParameterBlocks
                        self.parameter_block_count += 1
                        # Determine the maximum number of ParamRefRef elements within such ParameterBlock
                        param_ref_refs = block.findall(".//{*}ParameterRefRef")
                        self.max_param_ref_ref_count = max(self.max_param_ref_ref_count, len(param_ref_refs))

        except Exception as e:
            print(f"Error processing XML: {e}")

    def _read_content(self, file_obj):
        """Read content from file object or path"""
        try:
            # If it's a string (file path)
            if isinstance(file_obj, str):
                with open(file_obj, 'rb') as f:
                    return f.read()

            # If it's a file-like object
            elif hasattr(file_obj, 'read'):
                return file_obj.read()

            return None
        except Exception as e:
            print(f"Error reading file: {e}")
            return None

    def __str__(self):
        """
        Return a string representation of the application sizing statistics.
        
        Returns:
            String with formatted information about parameter memory, file size, and line count
        """
        return f"<App Statistics>:[ApplicationNumber={self.application_number}, " \
               f"ApplicationVersion={self.application_version}, ReplacesVersion={self.replaces_version}, " \
               f"Name={self.application_name}, Id={self.application_id}, " \
               f"Parameter Memory={self.parameter_memory_size} bytes, " \
               f"File Size={self.file_size} bytes, Lines={self.line_count}, " \
               f"Parameters={self.parameter_count}, ParameterRefs={self.parameter_ref_count}, " \
               f"ParameterCalculations={self.parameter_calculation_count}, ComObjects={self.com_object_count}, " \
               f"ComObjectRefs={self.com_object_ref_count}, " \
               f"AddressTableMaxEntries={self.address_table_max_entries}, " \
               f"AssociationTableMaxEntries={self.association_table_max_entries}, " \
               f"ScriptSize={self.script_size} ({self.script_lines} lines), " \
               f"ModuleDefs={self.module_def_count}, " \
               f"DynamicElements={self.dynamic_element_count} (Choose={self.choose_element_count}, Assign={self.assign_element_count}), " \
               f"ParameterBlocks={self.parameter_block_count}, " \
               f"MaxParamRefRefsInBlock={self.max_param_ref_ref_count}]"
