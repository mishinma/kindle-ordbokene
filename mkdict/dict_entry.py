from dataclasses import dataclass, field
from typing import List, Union, Optional, Any

VALID_PARTS_OF_SPEECH = [
    "verb", "substantiv", "adjektiv", "determinativ",
    "pronomen", "adverb", "preposisjon", "konjunksjon", "interjeksjon"]


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
    imperativ: str
    perfektum_partisipp_hankjonn: str
    perfektum_partisipp_intetkjonn: str
    perfektum_partisipp_bestemt_form: str
    perfektum_partisipp_flertall: str
    presens_partisipp: str


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
    word: str
    part_of_speech: str
    gender: Optional[str] = None
    definitions: List[Union[str, List[str]]] = field(default_factory=list)
    inflections: Inflections = field(default_factory=Inflections)

    def __post_init__(self):
        self.word = self.word.lower()
        self.part_of_speech = self.part_of_speech.lower()
        if self.part_of_speech not in self.VALID_PARTS_OF_SPEECH:
            raise ValueError(f"Invalid part of speech '{self.part_of_speech}'."
                             f"Must be one of {', '.join(self.VALID_PARTS_OF_SPEECH)}.")

        # For nouns, gender must be specified
        if self.part_of_speech == "substantiv" and not self.gender:
            raise ValueError("Gender must be specified for a noun entry.")


# Example of usage
if __name__ == "__main__":
    verb_inflections = VerbInflections(
        infinitiv="skrive",
        presens="skriver",
        preteritum="skrev",
        presens_perfektum="har skrevet",
        imperativ="skriv",
        perfektum_partisipp_hankjonn="skrevet",
        perfektum_partisipp_hunkjonn="skrevet",
        perfektum_partisipp_intetkjonn="skrevet",
        perfektum_partisipp_bestemt_form="skrevne",
        perfektum_partisipp_flertall="skrevne",
        presens_partisipp="skrivende",
    )

    verb_entry = DictionaryEntry(
        word="å skrive",
        part_of_speech="verb",
        definitions=[
            ("To compose text in a readable form", ["Jeg skriver et brev.", "Hun skrev en bok."])
        ],
        inflections=verb_inflections
    )

    print(verb_entry)
