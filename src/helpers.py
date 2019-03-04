import itertools
import logging
import re
import os
from sentence_splitter import split_text_into_sentences
from joblib import Parallel, delayed
from sacremoses.tokenize import MosesTokenizer, MosesDetokenizer
from tqdm import tqdm


N_CORES = int(len(os.sched_getaffinity(0)) * 0.75)
MOSES_TOKENIZER = MosesTokenizer(lang="fr")


logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def pre_treat_text(raw_text):
    # TODO: We should really use the same tokenizer used to generate the train.iob file (moses) as doctrine did
    # pre_treat_text = re.sub(r"(\w{2,})-(\w+)", r"\1@-@\2", raw_text, flags=re.IGNORECASE)  # Add @ to dashes
    pre_treated_text = re.sub(r"\n{2,}", r"\n", raw_text)  # Replace two or more lines by a single line
    pre_treated_text = re.sub(r"\xa0", r" ", pre_treated_text)  # Replace this new line symbol by a space
    pre_treated_text = re.sub(r"_+", r"", pre_treated_text)  # Underscore kills Tagger training :/
    pre_treated_text = re.sub(r"’", r"'", pre_treated_text)
    pre_treated_text = re.sub(r"^\s+$", r"", pre_treated_text,
                            flags=re.MULTILINE)  # Remove empty lines only containing spaces

    pre_treated_lines = pre_treated_text.split("\n")

    return pre_treated_lines, pre_treated_text


def post_treat_text(text):
    post_treated_text = re.sub(r"(\.\.\.\s?){2,}", r"...", text)
    post_treated_text = re.sub(r"(…\s?)+", r"… ", post_treated_text)
    post_treated_text = re.sub(r"(\s\w')\s(.)", r"\1\2", post_treated_text)  # Remove space after apostrophe
    post_treated_text = re.sub(r"(\()\s+(\w)", r"\1\2", post_treated_text)  # Space after left parenthesis
    post_treated_text = re.sub(r"(.)\s@\s?-\s?@\s(.)", r"\1-\2", post_treated_text)  # Remove Moses tokenizer dash @ symbol
    # post_treat_text = re.sub(r"\w(\.)(\.{2,})", r"\1 \2", post_treat_text)  # Fix Moses pasting three dots together with precedent token
    return post_treated_text


def tokenize_text_parallel(text_lines, n_jobs=None):
    if n_jobs:
        n_jobs = n_jobs
    else:
        n_jobs = N_CORES
    sentences_tokens = Parallel(n_jobs=n_jobs, prefer="processes")(delayed(tokenize_line)(line) for line in tqdm(text_lines))
    sentences_tokens = list(itertools.chain(*sentences_tokens))
    return sentences_tokens

def tokenize_line(line):
    line_sentences = []
    sentences = split_text_into_sentences(line, language="fr")
    for sentence in sentences:
        tokens = MOSES_TOKENIZER.tokenize(sentence, aggressive_dash_splits=True, escape=False)
        line_sentences.append(tokens)
    return line_sentences


def tokenize_text(text_lines):
    sentences_tokens = []

    if not isinstance(text_lines, list):
        text_lines = [text_lines]

    total_lines = len(text_lines)
    for idx,line in enumerate(text_lines):
        sentences = split_text_into_sentences(line, language="fr")
        for sentence in sentences:
            tokens = MOSES_TOKENIZER.tokenize(sentence, aggressive_dash_splits=True, escape=False)
            sentences_tokens.append(tokens)

        if idx%1500 == 0:
            logger.info("Segmenting and tokenizing line {0}/{1}".format(idx, total_lines))


    return sentences_tokens
