'''Transforms raw text into files format CoNLL (one token per line)

Usage:
    txt2conll.py <i> [options]

Arguments:
    <i>                   An input file or directory (if dir it will convert all txt files inside).
'''
import glob
import logging
import os
import random
import re

import numpy as np
import pandas as pd
from argopt import argopt
from helpers import pre_treat_text, tokenize_text_parallel
from nltk.tokenize.regexp import RegexpTokenizer
from sacremoses.tokenize import MosesTokenizer
from tqdm import tqdm

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

pattern = r"\@-\@|\w+['´`]|\w+|\S+"
regex_tokenizer = RegexpTokenizer(pattern, flags=re.UNICODE | re.IGNORECASE)

moses_tokenizer = MosesTokenizer(lang="fr")

MONTHS = ["janvier", "février", "mars", "avril", "mai", "june", "juillet",
          "août", "septembre", "octobre", "novembre", "décembre"]

NAMES_TOKENIZER = re.compile(r"(?:\@-\@)|\s")


def _load_names(filter_n=10):
    df_names = pd.read_csv("resources/names/prenom.csv")
    df_last_names = pd.read_csv("resources/names/patronymes.csv")

    # Filter top filter_n names
    df_names = df_names[df_names["sum"] >= filter_n]
    df_last_names = df_last_names[df_last_names["count"] >= filter_n]

    return df_names.prenom.dropna().values, df_last_names.patronyme.dropna().values


NAMES_ARRAY = _load_names()


def _load_communes_addresses():
    df_communes = pd.read_csv("resources/addresses/all_communes_uniq.txt", header=None)
    df_addresses = pd.read_csv("resources/addresses/all_addresses_uniq.txt", header=None)
    df_cp = pd.read_csv("resources/addresses/all_cp_uniq.txt", header=None)
    return df_communes[0].dropna().values, df_addresses[0].dropna().values, df_cp[0].dropna().values


COMUMNES_ARRAY, ADDRESSES_ARRAY, CP_ARRAY = _load_communes_addresses()


def tokens2conll(tokens, iob_tag, begin=True, capitalize=False):
    splitted = moses_tokenizer.tokenize(tokens, aggressive_dash_splits=True, escape=False)
    if capitalize:
        splitted = [s.capitalize() for s in splitted]

    if begin:
        pos = "B"
    else:
        pos = "I"
    splitted[0] = "{0} {1}-{2}".format(splitted[0], pos, iob_tag)
    splitted[1:] = ["{0} I-{1}".format(f, iob_tag) for f in splitted[1:]]
    final_token = "\n".join(splitted)
    return final_token


def per_repl(iob_tag="PER", num_names=(0, 1)):
    """
    Get a random name to represent the tag PER
    :param iob_tag: Tag to identify this entity. Default: PER
    :param num_names: Tuple with (number_names, number_last_names)
    :return:
    """

    def capitalize(name, cap_prob=0.7):
        if random.random() <= cap_prob:
            return name.capitalize()
        else:
            return name

    sampled_fname = []
    for fn in range(num_names[0]):
        sampled_fname.append(np.random.choice(NAMES_ARRAY[0]).strip().capitalize())
    sampled_lname = []
    for fn in range(num_names[1]):
        last_name = capitalize(np.random.choice(NAMES_ARRAY[1]).strip(), 0.2)
        sampled_lname.append(last_name)

    sampled_name = " ".join(sampled_fname + sampled_lname)
    sampled_name = moses_tokenizer.tokenize(sampled_name, aggressive_dash_splits=True, escape=False)
    sampled_name[0] = "{0} B-{1}".format(sampled_name[0], iob_tag)
    sampled_name[1:] = ["{0} I-{1}".format(f, iob_tag) for f in sampled_name[1:]]
    sampled_name = "\n".join(sampled_name)
    return sampled_name


def loc_repl(iob_tag="LOC"):
    number = "{} B-{}".format(np.random.randint(1, 200), iob_tag)
    commune = tokens2conll(np.random.choice(COMUMNES_ARRAY), iob_tag, False)
    rue = tokens2conll(np.random.choice(ADDRESSES_ARRAY), iob_tag, False, capitalize=True)
    cp = "{} B-{}".format(np.random.choice(CP_ARRAY), iob_tag)
    return "\n".join([number, rue, "\n", cp, commune.upper(), "\n"])


def date_repl(iob_tag="DATE"):
    day = np.random.randint(1, 31)
    month = random.choice(MONTHS)
    year = np.random.randint(1920, 2000)
    fake_date = "{0} B-{3}\n{1} I-{3}\n{2} I-{3}".format(day, month, year, iob_tag)
    return fake_date


def txt2conll(file_path, output_path):
    assert (os.path.exists(file_path))
    with open(file_path, "r") as docu:
        logger.info("Reading text file ...")
        raw_text = docu.read()
        logger.info("Pretreating text file ...")
        pre_treated_lines, _ = pre_treat_text(raw_text)
        # segment sentences and tokens
        logger.info("Segmenting and tokenizing text file ...")

        sentences_tokens = tokenize_text_parallel(pre_treated_lines)

        logger.info("Writing output text file ...")

        dict_tags = {"PERPERPER": per_repl, "LOCLOCLOC": loc_repl, "DATEDATEDATE": date_repl}
        with open(output_path, "w") as docu:
            for sentence in tqdm(sentences_tokens):
                for token in sentence:
                    token_ = token.strip()
                    if not token_:
                        continue
                    if token_ in dict_tags:
                        token_ = dict_tags[token_]()

                    else:
                        token_ = "{} O".format(token_)
                    docu.write(token_ + "\n")
                docu.write("\n")


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    input_path = parser.i
    output_path = os.path.dirname(input_path)

    paths_input = []
    if os.path.isdir(input_path):
        for file_input in glob.glob(os.path.join(input_path, "*.txt"))[:100]:
            paths_input.append(file_input)
    else:
        paths_input.append(input_path)

    for file_input in paths_input:
        logger.info("Converting to CoNLL format {}...".format(file_input))
        output_file = file_input[:-4] + "_CoNLL.txt"
        txt2conll(file_input, output_file)
