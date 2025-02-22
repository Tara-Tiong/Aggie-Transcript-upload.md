# Aggie Transcript Site Porting
I transported the Aggie Transcript's Wordpress Site to SiteFarm. I used python to create an automated article port. My script took the articles from Wordpress in an .xml file. 
It then autofills SiteFarm's layout for adding content, since there is no place to add backend code. My script automated the tedious "copy and paste" task for a human. 

## Instructions for the scripts
### Autofill SiteFarm Articles
This program autofills sitefarm articles for the AggieTranscript

### What does each script do?
- *xml-to-links.py* : converts the xml file containing the Wordpress articles and turns it into an HTML file with lists of links.
- *scrape_multArticles.py* : this goes through each link in the linked_XML file and saves it as a JSON dictionary. --> articles.JSON
- *autofill_one.py* : tests functions and uploads only one article on aggietranscript site
- *upload_articles.py* : the final product, which uses the JSON dictionary created to fill in the body paragraphs.


