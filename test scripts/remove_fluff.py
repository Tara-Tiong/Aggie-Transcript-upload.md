from bs4 import BeautifulSoup, NavigableString
import re

"""cleans up html code from a html file"""
def delete_string(soup, search_string):
    for tag in soup.find_all(string=True):  # Find all text nodes
            if search_string in tag:
                # Replace the search_string with an empty string
                new_string = tag.replace(search_string, '')
                tag.replace_with(new_string)

    return soup

def delete_tag_with_string(soup, search_string):
    # Iterate over all tags
    for tag in soup.find_all(True):  # True finds all tags
        if search_string in tag.get_text():  # Check if the string is in the tag's text
            tag.decompose()  # Remove the tag and its contents

    return soup

def delete_parent_tag_with_string(soup, old_tag_name, search_string):
    """
    Deletes all occurrences of a specified HTML tag that contains a certain string.

    Parameters:
    - soup: The BeautifulSoup object containing the parsed HTML content.
    - old_tag_name: The tag name to search for (e.g., 'strong').
    - search_string: The string to search for within the tag content (e.g., 'By').

    Returns:
    - Modified BeautifulSoup object with matching tags (and their parents) removed.
    """
    for tag in soup.find_all(old_tag_name):
        if tag.string and search_string in tag.string:
            parent = tag.find_parent()  # Get the parent of the tag
            if parent and parent.name == 'div':  # Check if the parent is a div
                parent.decompose()  # Remove the parent div and all its contents
            else:
                tag.decompose()  # Remove only the tag if no div parent is found

    return soup


def replace_tag(soup, old_tag_name, search_string, new_tag_name):
    """Changes the specified tag with a new tag"""
    # locate the tag and string
    for tag in soup.find_all(old_tag_name):
            if tag.string and search_string in tag.string:
                # Create a new tag (new_tag_name)
                new_tag = soup.new_tag(new_tag_name)
                new_tag.string = tag.string.strip()  # Copy the content from the old tag
                # Replace the old tag with the new one
                tag.replace_with(new_tag)
    return soup


def replace_parent_with_tag(soup, tag_to_find, new_tag_name):
    # deletes the tag found and changes into text
    """
    Replaces the parent <div> of the specified tag with a new tag in the given soup.

    :param soup: The BeautifulSoup object containing parsed HTML.
    :param tag_to_find: The tag to search for, e.g., <strong>title</strong>.
    :param new_tag_name: The name of the new tag to replace the parent div with.
    :return: Modified BeautifulSoup object.
    """
    # Find all occurrences of the specified tag
    target_tags = soup.find_all(tag_to_find[0], string=tag_to_find[1])

    for target_tag in target_tags:
        # Get the parent <div>
        parent_div = target_tag.find_parent('div')

        if parent_div:
            # Extract the target tag (remove it)
            target_tag.extract()

            # Get the remaining text from the parent div
            remaining_text = parent_div.get_text(strip=True)

            # Create a new tag to replace the <div>
            new_tag = soup.new_tag(new_tag_name)
            new_tag.string = remaining_text

            # Replace the parent div with the new tag
            parent_div.replace_with(new_tag)

    return soup

def rename_parent_with_tag(soup, tag_to_find, new_tag_name):
    """
    Replaces the parent <div> of the specified tag with a new tag in the given soup,
    while preserving all the children (nested tags and content) of the parent <div>.

    :param soup: The BeautifulSoup object containing parsed HTML.
    :param tag_to_find: A tuple (tag name, text) to search for, e.g., ('strong', 'title').
    :param new_tag_name: The name of the new tag to replace the parent div with.
    :return: Modified BeautifulSoup object.
    """
    # Find all occurrences of the specified tag
    target_tags = soup.find_all(tag_to_find[0], string=tag_to_find[1])

    for target_tag in target_tags:
        # Get the parent <div> of the found tag
        parent_div = target_tag.find_parent('div')

        if parent_div:
            # Create the new tag that will replace the <div>
            new_tag = soup.new_tag(new_tag_name)

            # Move all contents of the parent <div> to the new tag (including nested tags)
            for child in parent_div.contents:
                new_tag.append(child)

            # Replace the parent <div> with the new tag
            parent_div.replace_with(new_tag)

    return soup

def rename_parent_div(soup, search_string, new_tag_name):
    """
    Renames the parent <div> tag that contains a specific string with a new tag name.

    Parameters:
    - soup: The BeautifulSoup object containing the parsed HTML content.
    - search_string: The string to search for within the <div> tag.
    - new_tag_name: The new tag name to replace the old <div> with.

    Returns:
    - Modified BeautifulSoup object with the specified <div> replaced.
    """
    for div in soup.find_all('div'):

        if div.string and search_string in div.string:
            new_tag = soup.new_tag(new_tag_name)
            new_tag.append(div.contents)  # Move contents from old <div> to new tag
            div.replace_with(new_tag)  # Replace the old <div> with the new tag

    return soup

def wrap_with_tag_around_content(soup, start_string, end_string, new_tag_name):
    """
    Wraps a new tag around content between specific start and end strings in the HTML soup.

    :param soup: The BeautifulSoup object containing parsed HTML.
    :param start_string: The string to start wrapping around.
    :param end_string: The string to end wrapping around.
    :param new_tag_name: The name of the new tag to wrap around the content.
    :return: Modified BeautifulSoup object.
    """
    # Find all occurrences of the start_string
    start_elem = soup.find(string=start_string)

    if not start_elem:
        return soup

    # Find all occurrences of the end_string
    end_elem = soup.find(string=end_string)

    if not end_elem:
        return soup

    # Create a new tag
    new_tag = soup.new_tag(new_tag_name)

    # Define the content to be wrapped
    current = start_elem
    while current and current != end_elem:
        next_sibling = current.find_next_sibling()
        new_tag.append(current.extract())
        current = next_sibling

    # Append the end string to the new tag
    if end_elem:
        new_tag.append(end_elem.extract())

    # Find the parent of the start element to insert the new tag
    parent = start_elem.find_parent()

    if parent:
        # Insert the new tag before the first sibling after the end element
        next_sibling = end_elem.find_next_sibling()
        if next_sibling:
            next_sibling.insert_before(new_tag)
        else:
            # If there are no siblings after the end element, append the new tag to the parent
            parent.append(new_tag)

    return soup

def modify_html(file_path, output_path):
    """
    Reads an HTML file, modifies it by replacing specific tags, and writes the modified HTML to a new file.

    :param file_path: Path to the input HTML file.
    :param output_path: Path to the output HTML file.
    """
    # Read the input HTML file
    with open(file_path, 'r', encoding='utf-8') as file:
        input_html = file.read()

    # Parse the HTML
    soup = BeautifulSoup(input_html, 'html.parser')

    """Apply the transformations"""
    # article sections
    # soup = replace_parent_with_tag(soup, ('strong', 'item'), 'article')
    # soup = replace_parent_with_tag(soup, ('strong','item'),'article')
    # delete only tag
    # soup = delete_tag_with_string(soup,'<strong>{http://purl.org/rss/1.0/modules/content/}encoded</strong>')
    # soup = replace_tag(soup, 'strong','{http://purl.org/rss/1.0/modules/content/}encoded','')
    # modified_soup = wrap_content_with_body(soup, "Author's Note", ['b', 'strong'])

    # delete tag and it's parent
    # soup = delete_parent_tag_with_string(soup, 'strong', 'category')
    # soup = delete_parent_tag_with_string(soup,'strong','creator')
    # soup = delete_parent_tag_with_string(soup,'strong','guid')
    # soup = delete_parent_tag_with_string(soup, 'strong', 'description')
    # # Replace <div> with <title> for <strong>title</strong>
    # soup = replace_parent_with_tag(soup, ('strong', 'title'), 'title')
    # # Replace <div> with <strong> for <date>MM/DD/YYYY</date>
    # soup = replace_parent_with_tag(soup, ('strong', 'pubDate'), 'date')
    # soup = replace_parent_with_tag(soup, ('strong', 'link'), 'link')
    # # replace "<strong>By" with the <author> tag
    # soup = replace_tag (soup,'strong','By', 'author')
    soup = wrap_with_tag_around_content(soup, "Author's Note:", "</ol><br>", 'body')

    # restructuring the body paragraphs
    # soup = rename_parent_with_tag(soup, ('strong', 'item'), 'article')

    # soup = replace_tag(soup,'style="font-weight: 400"')

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(soup.prettify())


# Example usage:
input_file = 'random.html'
#  input_file = 'outline_literature_review.html'  # Replace with your input HTML file path
output_file = 'draft_literature_review.html'  # Replace with your desired output HTML file path

modify_html(input_file, output_file)
