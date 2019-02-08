'''
Sample sequences from a CoNLL format file to obtain a sampled  dataset to train a model.
Tries to keep the original distribution of the NER tags.
Still, you can choose the desired number of tags for each tag

Usage:
    CoNLL_dataset_creator.py FILE OUTPUT [-p PROPORTION]  [-n PCT] [-g TAGS] [-s]

Arguments:
    -g TAGS --tags=TAGS                 String representing the tags in the input dataset [default: PER,LOC,DATE,O]
    -s --stratified                     Try to keep the same prportion of tags as the source
    -p PROPORTION --proportion= PROPORTION   Override number of sequences for each tag. [default: LOC:3000,PER:1200,DATE:100,O:300000]
'''

from docopt import docopt
from collections import defaultdict
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def report_progress(desired, actual):
    for t, f in actual.items():
        logger.info("{}: We have {} of {} desired".format(t, f, desired[t]))
    logger.info("\n")


if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    conll_path = arguments["FILE"]
    new_dataset_file = arguments["OUTPUT"]
    tags_used = arguments["--tags"].split(",")

    desired_freqs = arguments["--proportion"].split(",")



    tags_freqs_src = {}
    sample_proportions = {}
    tags_occurrences = defaultdict(int)

    for tag in tags_used:
        logger.info("Getting the number of {} sequences on source file".format(tag))
        if tag == "O":
            cmd = "grep  -PRn  '\s{}' {} | wc -l".format(tag, conll_path)
        else:
            cmd = "grep  -PRn  'B-{}' {} | wc -l".format(tag, conll_path)

        output = int(os.popen(cmd).read().strip())
        tags_freqs_src[tag] = output

    desired_freqs = {k: min(int(v), tags_freqs_src[k]) for k, v in dict([f.split(":") for f in desired_freqs]).items()}


    # if "--stratified" in arguments:
    #     stratified = True
    #     n_all_sequences = sum(tags_freqs.values())
    #     for tag in tags_used:
    #         sample_proportions[tag] = (desired_n_sequences * tags_freqs[tag])/n_all_sequences

    output_file = open(new_dataset_file, "w")
    line_i = 0
    with open(conll_path, "r") as input_file:
        for line in input_file:
            if not line.strip():
                output_file.write("\n")
                continue

            if not line_i % 50000:
                report_progress(desired_freqs, tags_occurrences)

            keep_seq = False
            splitted = line.split()
            tag = splitted[-1]
            orig_tag = tag
            if "-" in tag:
                tag = tag.split("-")[1]
            token = splitted[0]
            if tags_occurrences[tag] >= desired_freqs[tag]:
                continue

            keep_seq = True
            if "B" in orig_tag or orig_tag[0] == "O":
                tags_occurrences[tag] += 1
            if keep_seq:
                output_file.write("{0} {1}\n".format(token, orig_tag))

            line_i += 1


            done = True
            for k, v in tags_occurrences.items():
                if v < desired_freqs[k]:
                    done = False
                    break

            if done:
                report_progress(desired_freqs, tags_occurrences)
                logger.info("Done !!")
                break
