'''Tags a text file into PER, LOC, DATE classes and outputs a CoNLL formatted file

Usage:
    regex_tagger.py <i> [options]

Arguments:
    <i>                   An input file or directory (if dir it will convert all txt files inside).
    -t TYPE            Type of the input file, CoNLL or normal [default: CoNLL]
'''

import logging
import re
from itertools import groupby

from argopt import argopt
from sacremoses import MosesDetokenizer
from sacremoses import MosesTokenizer
import numpy as np

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# NAMES
PER1 = re.compile(r"([\n\r\s])(?:[A-Z])\1{0,}.*?")

PERS = [PER1]


# ADDRESSES
LOC1 = re.compile(r"(\s?).*?[\s\n]*[à\-]?\s*[0-9]{5}(?:\s*[À-ÖA-Z\'\-]{2,}\s?)+(.)",
                  flags=re.DOTALL)  # ... à ANDREZIEUX-BOUTHEON


LOC2 = re.compile(r"(demeurant\s*)a?u?\s*.*?", flags=re.IGNORECASE)
LOC3 = re.compile(r"(lieu\s*dit\s*).*?", flags=re.IGNORECASE)
LOC4 = re.compile(r"(\ssis\s*à?\s*).*?", flags=re.IGNORECASE)
LOC5 = re.compile(r"(située? [àa]u?\s*).*?\s", flags=re.IGNORECASE)
LOC6 = re.compile(r"(située?\s*).*?\s", flags=re.IGNORECASE)
LOC7 = re.compile(r"(domicilié [àa]u?\s*).*?\s", flags=re.IGNORECASE)
LOC10 = re.compile(r"(\ssiège\s*a?u?\s*).*?", flags=re.IGNORECASE)
LOC11 = re.compile(r"(demeurée?\s*).*?", flags=re.IGNORECASE)
LOC12 = re.compile(r"(à\s*).*?\s", flags=re.IGNORECASE)
LOC13 = re.compile(r"(domiciliée?\s*).*?", flags=re.IGNORECASE)



LOC8 = re.compile(r"([^A-Z]).*?\s*(\([0-9]{5}\)\s*[A-Z][^\.])", flags=re.DOTALL)  # ... 75007 Paris
LOC9 = re.compile(r"([^A-Z]).*?\s*[à\-]\s*[0-9A-Z]", flags=re.DOTALL)  # ... - PARIS



LOCS = [LOC1, LOC2, LOC3, LOC4, LOC5, LOC6, LOC7, LOC8, LOC9, LOC10, LOC11, LOC12, LOC13]

# DATES
DATE1 = re.compile(r"(née? le\s*).*?")
DATES = [DATE1]





def read_file(input_path):
    with open(input_path, "r") as filo:
        text = [l.strip() for l in filo.readlines()]
    return text


def treat_CoNLL(text_lines):
    """
    Check if this CoNLL file has classes or other features (tokens after the words)
    
    :param text_lines: 
    :return: 
    """

    test = text_lines[0]
    test_split = test.split()
    if len(test_split) > 1:
        # We have classes so we remove them
        text_lines = [l.split()[0] if l else l for l in text_lines]

    return text_lines


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    input_path = parser.i
    file_type = parser.t
    assert (file_type in ["normal", "CoNLL"])

    text_lines = read_file(input_path)
    if file_type == "CoNLL":
        text_lines = treat_CoNLL(text_lines)
        mos = MosesDetokenizer(lang="fr")
        key = lambda sep: sep == ''
        sequences = [list(group) for is_key, group in groupby(text_lines, key) if not is_key]

        text_lines_detok = [mos.detokenize(l, unescape=False) for l in sequences]
        pass
