from bs4 import BeautifulSoup

from dict_entry import VerbInflections

# Define a custom exception for parsing errors
class ParseError(Exception):
    pass


def extract_word_and_pos(soup):

    # Find the word in the deepest span with class 'lookup'
    word_span = soup.find('span', class_='lookup')
    if not word_span:
        raise ParseError('Word span not found in the HTML snippet')

    # Extract subheader spans to avoid including them in word extraction
    subheader = word_span.find('span', class_='subheader')
    if not subheader:
        raise ParseError('Part of speech span not found in the HTML snippet')

    extracted = subheader.extract()
    part_of_speech = extracted.get_text(strip=True)

    # Now get_text() will not include part of speech for the word
    word = word_span.get_text(separator=' ', strip=True)
    word = word.split(' ')[0]

    # Remove whitespace
    word = word.strip()
    part_of_speech = part_of_speech.strip()

    return word, part_of_speech


def parse_verb_basic_inflections(table):
    verb_forms = {}
    rows = table.find_all('tr')
    if len(rows) != 2:
        raise ParseError(f'Unexpected number of rows in the table ({len(rows)}). Expected 2.')

    # Assuming the first row is headers and the second row contains the verb forms
    cells = rows[1].find_all('td')
    if len(cells) != 5:
        raise ParseError(f'Unexpected number of cells in the table ({len(cells)}). Expected 5.')

    for i, cell in enumerate(cells):
        verb_form = cell.get_text(strip=True, separator=' ')
        verb_form = verb_form.split('+')[0].strip()  # Removing contextual info if present
        if i == 0:
            # Clean å from the infinitive form, before the verb
            if verb_form.startswith('å '):
                verb_form = verb_form[2:]
            verb_forms['infinitiv'] = verb_form.strip()
        elif i == 1:
            verb_forms['presens'] = verb_form
        elif i == 2:
            verb_forms['preteritum'] = verb_form
        elif i == 3:
            verb_forms['presens_perfektum'] = verb_form
        elif i == 4:
            if verb_form.endswith('!'):
                verb_form = verb_form[:-1]
            verb_forms['imperativ'] = verb_form.strip()
    return verb_forms


def parse_verb_participle_inflections(table):
    participle_forms = {}
    rows = table.find_all('tr')
    # For participle forms, there should be 3 rows, 2 headers and 1 with verb forms
    if len(rows) != 3:
        raise ParseError(f'Unexpected number of rows in the table ({len(rows)}). Expected 3.')

    # Assuming the first two rows are headers and the third row contains the verb forms
    cells = rows[2].find_all('td')
    if len(cells) != 5:
        raise ParseError(f'Unexpected number of cells in the table ({len(cells)}). Expected 5.')

    for i, cell in enumerate(cells):
        participle_form = cell.get_text(strip=True, separator=' ')
        participle_form = participle_form.split('+')[0].strip()
        if i == 0:
            participle_forms['perfektum_partisipp_hankjonn'] = participle_form
        elif i == 1:
            participle_forms['perfektum_partisipp_intetkjonn'] = participle_form
        elif i == 2:
            # if starts with den/det remove it
            if participle_form.startswith('den/det '):
                participle_form = participle_form[8:]
            participle_forms['perfektum_partisipp_bestemt_form'] = participle_form.strip()
        elif i == 3:
            participle_forms['perfektum_partisipp_flertall'] = participle_form
        elif i == 4:
            participle_forms['presens_partisipp'] = participle_form
    return participle_forms


def extract_verb_inflections(soup):

    tables = soup.find_all('table')[:2]  # Extract the first two tables

    if len(tables) != 2:
        raise ParseError(f'Unexpected number of tables in the HTML snippet ({len(tables)}). Expected 2.')

    basic_inflections_table = tables[0]
    participle_inflections_table = tables[1]

    # Parse the first table for basic verb forms
    basic_verb_forms = parse_verb_basic_inflections(basic_inflections_table)
    # Parse the second table for participle forms
    participle_forms = parse_verb_participle_inflections(participle_inflections_table)

    # Create a VerbInflections instance with the combined data

    all_verb_forms = basic_verb_forms | participle_forms
    verb_inflections = VerbInflections(**all_verb_forms)

    return verb_inflections


if __name__ == '__main__':
    import os
    # find path to ../html_pages/ and iterate through the .html files
    html_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'html_pages')
    # for html_file in os.listdir(html_dir):
    #     if html_file.endswith('.html'):
    #         with open(os.path.join(html_dir, html_file), 'r', encoding='utf-8') as file:
    #             html_snippet = file.read()

    #         word, part_of_speech = extract_word_and_pos(html_snippet)
    #         print(f'{word} - {part_of_speech}')

    # find verb-sjonne-cleaned.html
    html_file = 'verb-sjonne-cleaned.html'
    with open(os.path.join(html_dir, html_file), 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    word, part_of_speech = extract_word_and_pos(soup)
    print(f'{word} - {part_of_speech}')

    # Example usage with HTML content
    verb_inflections_instance = extract_verb_inflections(soup)
    print(verb_inflections_instance)