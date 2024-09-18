import json

def json_to_html(json_file, output_html_file):
    # Load data from JSON
    with open(json_file, 'r') as file:
        data = json.load(file)

    # Extract the body HTML
    body_html = data.get('body', '<p>No content found.</p>')

    # Write the HTML content to a new file
    with open(output_html_file, 'w') as file:
        file.write(body_html)

    print(f"HTML content saved to {output_html_file}")

# Convert JSON to HTML and save it
json_to_html('article.json', 'test_article.html')
