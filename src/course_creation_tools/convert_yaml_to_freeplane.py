import yaml
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
import uuid
import argparse
import os

def generate_node_id():
    """Generate a unique ID for a node."""
    return f"ID_{str(uuid.uuid4()).replace('-', '_')}"

def create_note_element(note_text):
    """Create a richcontent note element with the given text."""
    richcontent = Element('richcontent', {
        'TYPE': 'NOTE',
        'CONTENT-TYPE': 'xml/'
    })
    html = SubElement(richcontent, 'html')
    head = SubElement(html, 'head')
    body = SubElement(html, 'body')
    p = SubElement(body, 'p')
    p.text = note_text
    return richcontent

def add_node_recursive(parent_element, node_data, position=None):
    """Recursively add nodes to the mind map."""
    # Create node element with basic attributes
    node_attrs = {
        'TEXT': node_data['title'],
        'ID': generate_node_id()
    }
    if position:
        node_attrs['POSITION'] = position

    node = SubElement(parent_element, 'node', node_attrs)

    # Add note if present
    if 'note' in node_data:
        node.append(create_note_element(node_data['note']))

    # Process children if present
    if 'children' in node_data:
        # Alternate positions for children
        positions = ['right', 'left']
        position_index = 0
        
        for child_key, child_data in node_data['children'].items():
            # Alternate between right and left for top-level children
            child_position = positions[position_index % 2] if parent_element.tag == 'map' else None
            position_index += 1
            add_node_recursive(node, child_data, child_position)

def converter(yaml_content):
    """Convert YAML content to Freeplane mind map format."""
    # Parse YAML content
    data = yaml.safe_load(yaml_content)

    # Create the base map element
    map_elem = Element('map', {'version': '1.9.13'})

    # Add the root node and its children
    add_node_recursive(map_elem, data['root'])

    # Convert to string and pretty print
    rough_string = tostring(map_elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="    ")

    # Add XML declaration
    if not pretty_xml.startswith('<?xml'):
        pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + pretty_xml

    return pretty_xml

def convert_yaml_file(yaml_file_path, output_file_path):
    """Convert a YAML file to a Freeplane mind map file."""
    with open(yaml_file_path, 'r', encoding='utf-8') as yaml_file:
        yaml_content = yaml_file.read()
    
    mind_map_xml = converter(yaml_content)
    
    with open(output_file_path, 'w', encoding='utf-8') as mm_file:
        mm_file.write(mind_map_xml)

# Example usage:
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert YAML file to Freeplane mind map')
    parser.add_argument('input_file', help='Input YAML file path')
    parser.add_argument('output_dir', help='Output directory for the mind map file')
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Generate output filename based on input filename
    input_basename = os.path.splitext(os.path.basename(args.input_file))[0]
    output_file = os.path.join(args.output_dir, f"{input_basename}.mm")
    
    convert_yaml_file(args.input_file, output_file)