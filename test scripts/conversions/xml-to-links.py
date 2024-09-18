import xml.etree.ElementTree as ET

def parse_xml(input_file, output_file, search_tag):
    try:
        # Parse the XML file
        tree = ET.parse(input_file)
        root = tree.getroot()

        # Open the output file
        with open(output_file, 'w') as f:
            # Iterate over elements and search for the specific tag
            for elem in root.iter(search_tag):
                # Write the element to the output file
                f.write(ET.tostring(elem, encoding='unicode'))
                f.write('\n')

        print(f"Results written to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
input_file = 'literature_review.xml'
output_file = 'new_lit_review.xml'
search_tag = 'link'  # Change this to the tag you are searching for

parse_xml(input_file, output_file, search_tag)
