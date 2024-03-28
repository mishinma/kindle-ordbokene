from bs4 import BeautifulSoup, Comment

# Your HTML content
with open('selenuim_page.html', 'r', encoding='utf-8') as file:
    html_content = file.read()

soup = BeautifulSoup(html_content, 'html.parser')

# Function to remove comments
def remove_comments(tag):
    for comment in tag.findAll(string=lambda text: isinstance(text, Comment)):
        comment.extract()

# Function to simplify nested spans and remove empty or redundant tags
def clean_tags(tag):
    for t in tag.find_all(True, recursive=False):
        # Recursively clean child tags first
        clean_tags(t)

        # Simplify nested tags of the same type or spans with no attributes
        if t.name == t.parent.name or (t.name == 'span' and not t.attrs):
            t.unwrap()
        elif not t.contents or all(isinstance(c, str) and c.isspace() for c in t.contents):
            # If the tag is empty or contains only whitespace
            t.decompose()
        else:
            # Remove attributes to keep the tag clean
            t.attrs = {}

def simplify_list(list_tag):
    soup = BeautifulSoup('', 'html.parser')
    # Create a new list element of the same type (ul or ol)
    new_list = soup.new_tag(list_tag.name)

    for li in list_tag.find_all('li', recursive=False):
        # Extract text with formatting for emphasis
        text_parts = [content for content in li.stripped_strings]
        formatted_text = ' '.join(text_parts)

        # Create a new li tag with the formatted text
        new_li = soup.new_tag('li')
        new_li.string = formatted_text
        new_list.append(new_li)

    return new_list

# # Function to simplify nested spans, remove empty or redundant tags, but keep "class" attributes
# def clean_tags(tag):
#     for t in tag.find_all(True, recursive=False):
#         # Recursively clean child tags first
#         clean_tags(t)

#         # Simplify nested tags of the same type or spans with no additional information
#         if t.name == t.parent.name or (t.name == 'span' and not t.attrs.get('class')):
#             t.unwrap()
#         elif not t.contents or all(isinstance(c, str) and c.isspace() for c in t.contents):
#             # If the tag is empty or contains only whitespace
#             t.decompose()
#         else:
#             # Keep the class attribute but remove others
#             class_attr = t.get('class')
#             t.attrs = {}
#             if class_attr:
#                 t['class'] = class_attr

# Define basic elements to keep and clean
basic_elements = {
    'table', 'tr', 'td', 'th', 'thead', 'tbody', 'caption',
    'li', 'ul', 'div'}

# Remove comments from the soup
remove_comments(soup)

# Find and clean all defined basic elements
for basic_element in basic_elements:
    for element in soup.find_all(basic_element):
        clean_tags(element)

# Find all ul and ol elements and simplify them
for list_tag in soup.find_all(['ul']):
    new_list = simplify_list(list_tag)
    list_tag.replace_with(new_list)

# Prettify the cleaned HTML
cleaned_html = soup.prettify()

# Save the cleaned HTML to a file
with open('cleaned_page.html', 'w', encoding='utf-8') as file:
    file.write(cleaned_html)