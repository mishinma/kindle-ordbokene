from bs4 import BeautifulSoup
from dict_entry import VerbInflections, Definition, Expression, DictionaryEntry

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


def parse_definitions(soup):

    section = soup.select_one('section.definitions')
    if not section:
        raise ParseError('Definitions section not found in the HTML snippet.')
    # Assert there is only one li element with definition level1
    defenitions_lvl1 = section.select('li.definition.level1')
    if len(defenitions_lvl1) != 1:
        raise ParseError(f'Unexpected number of definition lvl1 elements ({len(defenitions_lvl1)}).'
                         'Expected 1.')

    # Find all li elements with class definition level2
    definitions = defenitions_lvl1[0].select('li.definition.level2')

    parsed_definitions = []

    for definition in definitions:
        # The explanations text is the li class="explanation" element and
        # examples are the li class="example" element
        explanations = definition.select('li.explanation')
        examples = definition.select('li.example')

        # Extract the text from the explanations and examples
        explanation_texts = [explanation.get_text(strip=True, separator=' ') for explanation in explanations]
        example_texts = [example.get_text(strip=True, separator=' ') for example in examples]

        # Append the extracted data to the list
        parsed_definitions.append(Definition(explanation_texts, example_texts))

    return parsed_definitions


# Function to check if a ul element has a class of 'explanations' or 'examples'
def is_ul_explanations_or_examples(tag):
    return (tag.name == 'ul' and tag.get('class') and
            ('explanations' in tag['class'] or 'examples' in tag['class']))


def parse_expressions(soup):
    """ Parse expressions with explanations from the HTML content."""
    expressions_with_explanations = []

    section = soup.select_one('section.expressions')
    if not section:
        return expressions_with_explanations

    # Possible scenarios:
    # I.
    # li class sub_article - contains everything
    #   span class sub_article_header - expression
    #   ul class explanations
    #       li class explanation
    #
    # II.
    # li class sub_article - contains everything
    #   span class sub_article_header - expression
    #   ul class explanations
    #       li class explanation
    #   ul class explanations
    #       li class explanation
    #   ul class examples -- related to the last explanation
    #       li class example
    #
    # III.
    # li class sub_article - contains everything
    #   span class sub_article_header - expression
    #   ul class explanations -- empty
    #   ul class sub_definitions
    #       ul class explanations
    #           li class explanation - several explanations
    #       ul class examples
    #           li class example - several examples
    #       repeated for each sub-definition
    #
    # IV.
    # li class sub_article - contains everything
    #   span class sub_article_header - expression
    #   ul class sub_definitions
    #     ul class explanations
    #       li class explanation

    sub_articles = section.select('li.sub_article')
    for sub_article in sub_articles:

        expression = sub_article.select_one('span.sub_article_header').get_text(strip=True, separator=' ')
        # Find all ul elements with the class 'explanations' or 'examples'
        desired_ul_elements = sub_article.find_all(is_ul_explanations_or_examples)

        explanations_and_examples = []
        # Extract the text from the explanations and examples
        for ul in desired_ul_elements:
            if 'explanations' in ul['class']:
                explanations = ul.select('li.explanation')
                explanation_texts = [explanation.get_text(strip=True, separator=' ') for explanation in explanations]
                if not explanation_texts:
                    continue
                explanations_and_examples.append(('explanation', explanation_texts))

            elif 'examples' in ul['class']:
                examples = ul.select('li.example')
                example_texts = [example.get_text(strip=True, separator=' ') for example in examples]
                if not example_texts:
                    continue
                explanations_and_examples.append(('example', example_texts))

        # Iterate through the list in reverse to pair explanations with examples
        # Example will always be after the explanation, but some explanations may not have examples
        paired_explanations_and_examples = []
        i = len(explanations_and_examples) - 1
        while i >= 0:
            entry = explanations_and_examples[i]

            if entry[0] == 'example':
                # If the entry is an example, pair it with the last explanation
                paired_explanations_and_examples.append(Definition(explanations_and_examples[i-1][1], entry[1]))
                # Remove the paired explanation and example from the list
                explanations_and_examples.pop(i)
                explanations_and_examples.pop(i-1)
                i -= 2
            else: # If the entry is an explanation, add it to the list
                paired_explanations_and_examples.append(Definition(entry[1], []))
                explanations_and_examples.pop(i)
                i -= 1

        # reverse the list to maintain the order of explanations and examples
        paired_explanations_and_examples.reverse()
        expressions_with_explanations.append(Expression(expression, paired_explanations_and_examples))

    return expressions_with_explanations


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
    html_file = 'verb-sjonne.html'
    with open(os.path.join(html_dir, html_file), 'r', encoding='utf-8') as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, 'html.parser')

    word, part_of_speech = extract_word_and_pos(soup)

    # Example usage with HTML content
    verb_inflections_instance = extract_verb_inflections(soup)

    # Extract definitions and examples
    definitions = parse_definitions(soup)
    expressions = parse_expressions(soup)

    dict_entry = DictionaryEntry(
        word,
        part_of_speech,
        definitions,
        inflections=verb_inflections_instance,
        expressions=expressions
        )

    dict_entry.pretty_print()

