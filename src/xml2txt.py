'''Transforms XML files into format CoNLL (one token per line)

Usage:
    txt2conll.py <i> <o> [options]

Arguments:
    <i>                   An input file or directory (if dir it will convert all txt files inside).
    <o>                   An output directory.
    --num=<n> NUM                  Number of decisions [default: 200]
    -r RATIO                   Ratio train/dev/test [default: 60/20/20]
'''
import os
import xml.etree.ElementTree
import glob
import logging
from argopt import argopt
import numpy as np
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_datasets(array_documents, ratio):
    splitted = np.array([int(d) for d in ratio.split("/")]) / 100
    if len(splitted) != 3:
        logger.error("We need three integers as ratio!!")
        exit(-1)

    r_train, r_dev, r_test = splitted
    n_docs = len(array_documents)
    all_indices = np.arange(len(array_documents))
    train_indices = np.random.choice(all_indices, int(r_train * n_docs), replace=False)
    rest_indices = np.setdiff1d(all_indices, train_indices)
    dev_indices = np.random.choice(rest_indices, int(r_dev * n_docs), replace=False)
    test_indices = np.setdiff1d(rest_indices, dev_indices)

    assert (len(np.intersect1d(train_indices, dev_indices)) == 0)
    assert (len(np.intersect1d(train_indices, test_indices)) == 0)
    assert (len(np.intersect1d(test_indices, dev_indices)) == 0)

    return array_documents[train_indices], array_documents[dev_indices], array_documents[test_indices]


def xml2txt(files_to_treat, label, output_path):
    # files_to_treat = np.array(list(glob.glob('../data/dev/*.xml')))
    n_files = len(files_to_treat)

    output_file = os.path.join(output_path, label + ".txt")
    with open(output_file, "w") as filo:
        for i,f in enumerate(files_to_treat):
            print("Treating file {0} => {1}/{2}\n".format(f, i+1 , n_files))
            e = xml.etree.ElementTree.parse(f).getroot()

            try:
                text = [t for t in e.find("TEXTE").find("BLOC_TEXTUEL").find("CONTENU").itertext()]
                space_text = "\n".join(text)
                filo.write("".join(space_text) + "\n")

            except Exception as e:
                print("Could not parse file {}\n because {}".format(f, e))


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    input_path = parser.i
    output_path = parser.o
    number_decisions = int(parser.num)
    if parser.r:
        ratio = parser.r

    # all_files = np.array(list(glob.glob('../data/dev/*.xml')))
    all_files = np.array(list(glob.glob(input_path)))

    # take sample
    all_files = np.random.choice(all_files, number_decisions, replace=False)

    train, dev, test = generate_datasets(all_files, ratio)

    for t, l in zip([train, dev, test], ["train", "dev", "test"]):
        xml2txt(t, l, output_path)

