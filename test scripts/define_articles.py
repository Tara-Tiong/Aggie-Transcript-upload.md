from bs4 import BeautifulSoup

# Function to clean and restructure HTML with <strong> tags and identify titles and authors
def clean_and_restructure_html(file_path, output_path):
    # Open and parse the HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Remove all <div> tags that contain the string "{http://wordpress.org/export/1.2/}"
    divs_to_remove = soup.find_all('div','strong', string=lambda text: text and "{http://wordpress.org/export/1.2/}" in text)
    for div in divs_to_remove:
        div.decompose()

    # Create a list to store articles as dictionaries
    articles = []

    # Find all <strong> tags, assuming these represent either titles or authors
    strong_tags = soup.find_all('strong')

    current_article = {}

    # Loop through each <strong> tag to identify and extract article content
    for strong_tag in strong_tags:
        strong_text = strong_tag.text.strip()

        # Identify title (assuming it's the first strong tag or based on your pattern)
        if 'By' not in strong_text and 'by' not in strong_text:  # Exclude authors
            # Assume the first <strong> is the title
            current_article['title'] = strong_text

        # Identify author (assuming it starts with "By")
        elif 'By' in strong_text or 'by' in strong_text:
            author_name = strong_text.replace('By', '').replace('by', '').strip()
            current_article['author'] = author_name

        # Now gather the content after author (if any text follows)
        content = []
        for sibling in strong_tag.find_next_siblings():
            # Stop when another <strong> tag is found (which could be the start of the next article)
            if sibling.name == 'strong':
                break
            content.append(str(sibling))  # Append content between tags

        current_article['content'] = ' '.join(content).strip()

        # Add the current article to the articles list and reset for the next one
        articles.append(current_article)
        current_article = {}

    # Restructure and save the articles with new tags
    with open(output_path, 'w', encoding='utf-8') as output_file:
        for article in articles:
            output_file.write(f"<article>\n")
            output_file.write(f"  <title>{article.get('title', 'No Title')}</title>\n")
            if 'author' in article:
                output_file.write(f"  <author>{article['author']}</author>\n")
            output_file.write(f"  <content>{article['content']}</content>\n")
            output_file.write(f"</article>\n\n")

    print(f"Processed HTML saved to {output_path}")

# Run the function on a sample HTML file
clean_and_restructure_html('outline_literature_review.html', 'draft_literature_review.html')
