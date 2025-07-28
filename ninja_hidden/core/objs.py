from dataclasses import dataclass
from enum import Enum
from .logic import _key_generator,generate_key,_hash256,generate_fktext,generate_chars,generate_char_by_indx,_libaccess


class KeyGenerators(Enum):
    key_from_string = _key_generator
    key = generate_key
    sha256 = _hash256
    matrix = generate_fktext
    text = generate_chars
    char_by_idx = generate_char_by_indx
    char_lists = _libaccess


