#!/usr/bin/env zsh

conda activate pseudo-de-pseudonymizer

python xml2txt.py /data/capp_legifrance/extracto/*.xml /data/capp_legifrance/dataset

# Replace pseudonyms by LOC, PER, DATE tags in train, dev, test

python tagger_capp.py /data/capp_legifrance/dataset/train.txt /data/capp_legifrance/dataset/train_tagged.txt

python tagger_capp.py /data/capp_legifrance/dataset/dev.txt /data/capp_legifrance/dataset/dev_tagged.txt

python tagger_capp.py /data/capp_legifrance/dataset/test.txt /data/capp_legifrance/dataset/test_tagged.txt


# Transform tagged files into CoNLL format files

python txt2conll.py /data/capp_legifrance/dataset/train_tagged.txt
python txt2conll.py /data/capp_legifrance/dataset/dev_tagged.txt
python txt2conll.py /data/capp_legifrance/dataset/test_tagged.txt