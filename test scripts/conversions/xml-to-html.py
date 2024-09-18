import xml.etree.ElementTree as ET

def xml_to_html(xml_file, html_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Open the HTML file for writing
    with open(html_file, 'w') as html:
        # Write the basic HTML structure
        html.write('<html>\n<head>\n<title>XML to HTML</title>\n</head>\n<body>\n')
        html.write('<h1>XML Data</h1>\n')

        # Recursively process the XML elements
        def process_element(element, depth=0):
            # Add indentations for better HTML readability
            indent = '  ' * depth
            html.write(f'{indent}<div>\n')

            # Add the tag name
            html.write(f'{indent}  <strong>{element.tag}</strong>: {element.text.strip() if element.text else ""}<br>\n')

            # Process attributes, if any
            if element.attrib:
                html.write(f'{indent}  <em>Attributes:</em> {element.attrib}<br>\n')

            # Process children elements recursively
            for child in element:
                process_element(child, depth + 1)

            html.write(f'{indent}</div>\n')

        # Start processing the root element
        process_element(root)

        # Close the HTML structure
        html.write('</body>\n</html>\n')

# Convert the XML to HTML
xml_to_html('news.xml', 'news.html')

print("Conversion complete! Check the 'output.html' file.")
