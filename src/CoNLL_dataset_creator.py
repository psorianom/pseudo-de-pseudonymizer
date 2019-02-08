'''
Sample sequences from a CoNLL format file to obtain a dataset to train a model.
You can choose the proportion for train, dev, test. And also maybe det

Usage:
    CoNLL_dataset_creator.py FILE OUTPUT  [-n PCT] [-g TAGS] [-s]

Arguments:
    -n PCT --num_seq=PCT    Number of sequences to keep in new dataset [default: 10000]
    -g TAGS --tags=TAGS     String representing the tags in the input dataset [default: PER,LOC,DATE,O]
    -s --stratified         Try to keep the same
'''


from docopt import docopt
from collections import defaultdict
import os
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    arguments = docopt(__doc__, version='1.0')

    conll_path = arguments["FILE"]
    new_dataset_file = arguments["OUTPUT"]
    desired_n_sequences = int(arguments["--num_seq"])
    tags_used = arguments["--tags"].split(",")
    tags_freqs = {}
    sample_proportions = {}
    tags_occurrences = defaultdict(int)
    for tag in tags_used:

        logger.info("Getting the number of {} sequences on source file".format(tag))
        if tag == "O":
            cmd = "grep  -PRn  '\sO' {} | wc -l".format(conll_path)
        else:
            cmd = "grep  -PRn  'B-{}' {} | wc -l".format(tag, conll_path)
        output = int(os.popen(cmd).read().strip())
        tags_freqs[tag] = output

    if "--stratified" in arguments:
        stratified = True
        n_all_sequences = sum(tags_freqs.values())
        for tag in tags_used:
            sample_proportions[tag] = (desired_n_sequences * tags_freqs[tag])/n_all_sequences

    actual_n_sequences = 0
    output_file = open(new_dataset_file, "w")
    with open(conll_path, "r") as input_file:
        for line in input_file:

            if actual_n_sequences != "ALL" and actual_n_sequences > desired_n_sequences:
                break
            sequence = ""
            while line:
                splitted = line.split()
                tag = splitted[-1]
                token = splitted[0]

                tags_occurrences[tag] += 1
                actual_n_sequences = input_file.tell()
            output_file.write("{0} {1}\n".format(token, tag))




