from dataclasses import dataclass, field
from typing import List, Optional, Any, Tuple, Dict

VALID_PARTS_OF_SPEECH = [
    "verb", "substantiv", "adjektiv", "determinativ",
    "pronomen", "adverb", "preposisjon", "konjunksjon", "interjeksjon"]


@dataclass
class Definition:
    definition: List[str]
    examples: List[str] = field(default_factory=list)

@dataclass
class Expression:
    expression: str
    definitions: List[Definition]


@dataclass
class Inflections:
    # General inflection fields, can be extended or used directly if suitable
    # This class can be subclassed for specific needs of nouns, verbs, adjectives, etc.
    # generic_inflections: dict = field(default_factory=dict)

    def to_lowercase(self, value: Any) -> Any:
        """Recursively convert strings in a nested structure to lowercase."""
        if isinstance(value, str):
            return value.lower()
        elif isinstance(value, dict):
            return {self.to_lowercase(key): self.to_lowercase(val) for key, val in value.items()}
        elif isinstance(value, list):
            return [self.to_lowercase(item) for item in value]
        return value

    def __post_init__(self):
        # Apply lowercase conversion to generic_inflections or any other attributes
        for attr_name, attr_value in self.__dict__.items():
            setattr(self, attr_name, self.to_lowercase(attr_value))


@dataclass
class NounInflections(Inflections):
    entall_bestemt_form: str
    entall_ubestemt_form: str
    flertall_bestemt_form: str
    flertall_ubestemt_form: str


@dataclass
class VerbInflections(Inflections):
    infinitiv: str
    presens: str
    preteritum: str
    presens_perfektum: str
    imperativ: Optional[str] = None
    perfektum_partisipp_hankjonn: Optional[str] = None
    perfektum_partisipp_intetkjonn: Optional[str] = None
    perfektum_partisipp_bestemt_form: Optional[str] = None
    perfektum_partisipp_flertall: Optional[str] = None
    presens_partisipp: Optional[str] = None


@dataclass
class DeterminativeInflections(Inflections):
    entall_hankjonn: str
    entall_hunkjonn: str
    entall_intetkjonn: str
    flertall: str


@dataclass
class AdjectiveInflections(Inflections):
    entall_hankjonn: str
    entall_intetkjonn: str
    bestempt_form: str
    flertall: str
    komparativ: str
    superlativ_ubestemt_form: str
    superlativ_bestemt_form: str


@dataclass
class DictionaryEntry:
    id: int
    word: str
    part_of_speech: str
    definitions: List[Definition]
    gender: Optional[str] = None
    inflections: Optional[Inflections] = None
    expressions: List[Expression] = field(default_factory=list)

    def __post_init__(self):
        self.word = self.word.lower()
        self.part_of_speech = self.part_of_speech.lower()
        if self.part_of_speech not in VALID_PARTS_OF_SPEECH:
            raise ValueError(f"Invalid part of speech '{self.part_of_speech}'."
                             f"Must be one of {', '.join(VALID_PARTS_OF_SPEECH)}.")

        # For nouns, gender must be specified
        if self.part_of_speech == "substantiv" and not self.gender:
            raise ValueError("Gender must be specified for a noun entry.")

    def pretty_print(self):
        print(f"WORD: {self.word}")
        print(f"PART OF SPEECH: {self.part_of_speech}")
        if self.gender:
            print(f"GENDER: {self.gender}")
        print()
        if self.inflections:
            print("INFLECTIONS:")
            # Depending on the specific class of inflections, you might want to adjust this
            for attr, value in self.inflections.__dict__.items():
                print(f"  {attr}: {value}")
        print()
        print("DEFINITIONS:")
        for definition in self.definitions:
            print(f"  - Definition: {'; '.join(definition.definition)}")
            if definition.examples:
                print("    Examples:")
                for example in definition.examples:
                    print(f"      - {example}")
            print()

        if self.expressions:
            print("EXPRESSIONS:")
            for expression in self.expressions:
                print(f"  - Expression: {expression.expression}")
                print("    Definitions:")
                for defn in expression.definitions:
                    print(f"      - {'; '.join(defn.definition)}")
                    if defn.examples:
                        print("        Examples:")
                        for example in defn.examples:
                            print(f"          - {example}")
                print()


def dictionary_entry_to_html(entry: DictionaryEntry, css_file_path='dictionary_style.css') -> str:
    """
    Converts a DictionaryEntry instance to an HTML string with external CSS.

    :param entry: DictionaryEntry instance
    :param css_file_path: Path to the CSS file
    :return: A string containing HTML representation of the entry
    """
    html = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="{css_file_path}">
        <title>{entry.word}</title>
    </head>
    <body>
        <h1 class="word-title">{entry.word} <span class="part-of-speech">({entry.part_of_speech})</span></h1>
    '''

    # Adding gender if available
    if entry.gender:
        html += f'<div class="gender"><strong>Gender:</strong> {entry.gender}</div>'

    # Adding inflections if available
    if entry.inflections:
        html += '<div class="inflections"><strong>Inflections</strong><ul>'
        for attr, value in vars(entry.inflections).items():
            if not attr.startswith("_"):  # Skip private attributes or methods
                html += f'<li class="inflection-item">{attr.replace("_", " ").capitalize()}: {value}</li>'
        html += '</ul></div>'

    # Adding definitions and examples
    html += '<div class="definitions"><strong>Definitions</strong><ul>'
    for definition in entry.definitions:
        html += f'<li class="definition-item">{", ".join(definition.definition)}</li>'
        if definition.examples:
            html += '<ul class="example-list">'
            for example in definition.examples:
                html += f'<li class="example-item">{example}</li>'
            html += '</ul>'
    html += '</ul></div>'

    # Adding expressions
    if entry.expressions:
        html += '<div class="expressions"><strong>Expressions</strong><ul>'
        for expression in entry.expressions:
            html += f'<li class="expression-item"><strong>{expression.expression}</strong><ul>'
            for definition in expression.definitions:
                html += f'<li class="expression-definition-item">{", ".join(definition.definition)}</li>'
                if definition.examples:
                    html += '<ul class="example-list">'
                    for example in definition.examples:
                        html += f'<li class="example-item">{example}</li>'
                    html += '</ul>'
            html += '</ul></li>'
        html += '</ul></div>'

    html += '''
    </body>
    </html>
    '''

    return html


def dictionary_entry_to_xhtml(entry: DictionaryEntry) -> str:
    """
    Generates XHTML content for a Kindle dictionary entry, to be included inside a <mbp:frameset> tag.

    :param entry: DictionaryEntry instance
    :return: A string containing XHTML representation of the entry
    """
    # Initialize the XHTML for the dictionary entry
    xhtml = f'''
        <idx:entry name="default" scriptable="yes" spell="yes">
            <idx:short><a id="{entry.id}"></a>
                <idx:orth value="{entry.word}">
                    <b>{entry.word}</b>
                    {generate_inflections(entry)}
                </idx:orth>
        '''

    # Adding gender if available
    if entry.gender:
        xhtml += f'<div class="gender"><strong>Gender:</strong> {entry.gender}</div>'

    # Adding inflections if available
    if entry.inflections:
        xhtml += '<div class="inflections"><strong>Inflections</strong><ul>'
        for attr, value in vars(entry.inflections).items():
            if not attr.startswith("_"):  # Skip private attributes or methods
                xhtml += f'<li class="inflection-item">{attr.replace("_", " ").capitalize()}: {value}</li>'
        xhtml += '</ul></div>'

    # Adding definitions and examples
    xhtml += '<div class="definitions"><strong>Definitions</strong><ul>'
    for definition in entry.definitions:
        xhtml += f'<li class="definition-item">{", ".join(definition.definition)}</li>'
        if definition.examples:
            xhtml += '<ul class="example-list">'
            for example in definition.examples:
                xhtml += f'<li class="example-item">{example}</li>'
            xhtml += '</ul>'
    xhtml += '</ul></div>'

    # Adding expressions
    if entry.expressions:
        xhtml += '<div class="expressions"><strong>Expressions</strong><ul>'
        for expression in entry.expressions:
            xhtml += f'<li class="expression-item"><strong>{expression.expression}</strong><ul>'
            for definition in expression.definitions:
                xhtml += f'<li class="expression-definition-item">{", ".join(definition.definition)}</li>'
                if definition.examples:
                    xhtml += '<ul class="example-list">'
                    for example in definition.examples:
                        xhtml += f'<li class="example-item">{example}</li>'
                    xhtml += '</ul>'
            xhtml += '</ul></li>'
        xhtml += '</ul></div>'

    xhtml += '''
                </idx:short>
        </idx:entry>
    '''

    return xhtml


def generate_inflections(entry):
    """
    Generates inflection XHTML for the given entry.

    :param entry: DictionaryEntry instance
    :return: A string containing inflection XHTML
    """
    if not entry.inflections:
        return ''

    inflections_xhtml = '<idx:infl>'
    # for inflection in entry.inflections.values():
        # inflections_xhtml += f'<idx:iform value="{inflection}"></idx:iform>'
    # include name of the inflection as well
    for attr, value in vars(entry.inflections).items():
        if not attr.startswith("_") and value:
            inflections_xhtml += f'<idx:iform name="{attr.replace("_", " ")}" value="{value}"></idx:iform>'
    inflections_xhtml += '</idx:infl>'

    return inflections_xhtml


# def generate_definitions(entry):
#     """
#     Generates definitions XHTML for the given entry.

#     :param entry: DictionaryEntry instance
#     :return: A string containing definitions XHTML
#     """
#     definitions_xhtml = ''
#     for definition in entry.definitions:
#         definitions_xhtml += f'<p>{", ".join(definition.definition)}</p>'
#         if definition.examples:
#             for example in definition.examples:
#                 definitions_xhtml += f'<p>{example}</p>'

#     return definitions_xhtml
