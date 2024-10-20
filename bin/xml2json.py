# Initialize imports
import json

from xml.etree import ElementTree as et
from datetime import datetime
from os import path
from pathfinder import PathFinder as pf


class xml2json:

    def __init__(self, file_path):
        # Set filepath variable
        self.file_path = file_path
        # Set timestamp for file naming/tracking
        self.timestamp = datetime.now().replace(microsecond=0)
        self.formatted_timestamp = self.timestamp.strftime("%Y-%m-%d_%H-%M-%S")

        # Read the xml as a string
        self.xml_string = et.fromstring(self._read_file_as_bytes())
        # Create xml tree
        self.tree = et.parse(f'{self.file_path}')
        self.root = self.tree.getroot()

        self.template_dict = {"templates": []}
        self.mxcell_connections = {"cell_connections": []} 
        self.mxfile = {
                'diagram': {
                    'mxGraphModel': {
                        'root': {

                        }
                    }
                }
            }

        self.path_finder = pf() 
        
    def _read_file_as_bytes(self):
        # Read the file as bytes to ensure data remains unchanged during extraction
        with open(self.file_path, 'rb') as xml_file:
            data = xml_file.read()

        return data

    def _preserve_escape_chars(self, text):
        # Ensure the text is returned as is to preserve the escape characters draw.io requires in its xml format
        return text

    def create_dict(self):
        # Iterate through the xml root and extract the needed values. Values are then stored inside a dictionary
        num_cells = 0
        num_points = 0
        num_array = 0
        for item in self.xml_string.iter():
            if item.tag == "mxfile":
                pass
            elif item.tag == "diagram":
                self.mxfile["diagram"].update(
                    dict(self._preserve_escape_chars(item.attrib)))
            elif item.tag == "mxGraphModel":
                self.mxfile["diagram"]["mxGraphModel"].update(
                    dict(self._preserve_escape_chars(item.attrib)))
            elif item.tag == "mxCell":
                num_cells += 1
                self.mxfile["diagram"]["mxGraphModel"]["root"].update(
                    dict({f"mxCell-{num_cells}": self._preserve_escape_chars(item.attrib)}))
            elif item.tag == "mxGeometry":
                self.mxfile["diagram"]["mxGraphModel"]["root"][f"mxCell-{num_cells}"].update(
                    dict({"mxGeometry": self._preserve_escape_chars(item.attrib)}))
            elif item.tag == "Array":
                num_array = num_cells
                self.mxfile["diagram"]["mxGraphModel"]["root"][f"mxCell-{num_cells}"]["mxGeometry"].update(
                    dict({"Array": self._preserve_escape_chars(item.attrib)}))
            elif item.tag == "mxPoint" and num_array == num_cells:
                num_points += 1
                self.mxfile["diagram"]["mxGraphModel"]["root"][f"mxCell-{num_cells}"]["mxGeometry"]["Array"].update(
                    dict({f"mxPoint-{num_points}": self._preserve_escape_chars(item.attrib)}))
            elif item.tag == "mxPoint":
                num_points += 1
                self.mxfile["diagram"]["mxGraphModel"]["root"][f"mxCell-{num_cells}"]["mxGeometry"].update(
                    dict({f"mxPoint-{num_points}": self._preserve_escape_chars(item.attrib)}))

        return self.mxfile

    def write_json(self, temp_name: str):
        # Write the json file to disk to store as a future template
        with open(f'{self.path_finder.JSON_DIR}{temp_name}_{self.timestamp}.json', 'w') as cell:
            json.dump(obj=self.create_dict(), fp=cell, indent=4, ensure_ascii=False)
    
    def from_string(self):
        # Returns the xml string as is to ensure proper encoding
        return self.xml_string

