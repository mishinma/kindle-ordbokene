
import os
from pathlib import Path
from mkdict.parse_html import parse_dictionary_entry
from mkdict.dict_entry import dictionary_entry_to_xhtml

PAGES_DIR = Path('pages')
SRC_DIR = Path('kindle_src')
DEST_DIR = Path('kindle_compiled')
CONTENT_TEMPLATE_FILE = 'content.template.xhtml'
CONTENT_DEST_FILE = DEST_DIR / 'content000.xhtml'

if __name__ == "__main__":

    # Recreate the destination directory
    if DEST_DIR.exists():
        os.system(f'rm -r {DEST_DIR}')
    os.mkdir(DEST_DIR)

    # Copy everything from the source directory to the destination directory
    os.system(f'cp -r {SRC_DIR}/* {DEST_DIR}')

    parsed_dict_entries = []

    # Get the list of downloaded pages
    for page_file in PAGES_DIR.iterdir():

        # Parse the dictionary entry from the HTML
        try:
            entry = parse_dictionary_entry(page_file)
        except Exception as e:
            print(f"Error parsing entry from {page_file}: {e}")
            continue

        parsed_dict_entries.append(entry)

    xhtml_entries = [dictionary_entry_to_xhtml(entry) for entry in parsed_dict_entries]

    # Load the content template
    with open(DEST_DIR/CONTENT_TEMPLATE_FILE, 'r') as f:
        content = f.read()

    # Generate the content file
    # Replace the placeholder with the actual content and add <hr/> between entries
    content = content.replace('{{ENTRIES}}', '<hr/>'.join(xhtml_entries))

    # Save the content file
    with open(CONTENT_DEST_FILE, 'w') as f:
        f.write(content)

    # Delete the content template file from the destination directory
    os.remove(DEST_DIR/CONTENT_TEMPLATE_FILE)

    # Create the final ZIP file
    os.system(f'cd {DEST_DIR} && zip -r ../kindle_dictionary.zip .')






