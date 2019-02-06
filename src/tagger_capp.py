import re
from collections import defaultdict
import sys
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# NAMES
NAME1 = re.compile(r"([\w\W])[A-Z]\.\.\.")

NAMES = [NAME1]


# ADDRESSES
LOC1 = re.compile(r"(\s?)\[?\.\.\.\]?\s*\n*\s*[à\-]?\s*[0-9]{5}(?:\s*[À-ÖA-Z\'\-]{2,}\s*)+",
                  flags=re.DOTALL | re.MULTILINE)  # ... à ANDREZIEUX-BOUTHEON


LOC2 = re.compile(r"(demeurant\s*)\[?\.\.\.\]?")
LOC3 = re.compile(r"(lieu\s*dit\s*)\[?\.\.\.\]?")
LOC4 = re.compile(r"(\ssis\s*à?\s*)\[?\.\.\.\]?")
LOC5 = re.compile(r"(située? [àa]u?\s*)\[?\.\.\.\]?\s")
LOC6 = re.compile(r"(située?\s*)\[?\.\.\.\]?\s")
LOC7 = re.compile(r"(domicilié [àa]u?\s*)\[?\.\.\.\]?\s")
LOC10 = re.compile(r"(\ssiège\s*a?u?\s*)\[?\.\.\.\]?")
LOC11 = re.compile(r"(demeurée?\s*)\[?\.\.\.\]?")
LOC12 = re.compile(r"(à\s*)\[?\.\.\.\]?\s")
LOC13 = re.compile(r"(domiciliée?\s*)\[?\.\.\.\]?")



LOC8 = re.compile(r"([^A-Z])\.\.\.\.*\s*([0-9]{5}\s*[A-Z][^\.])", flags=re.DOTALL)  # ... 75007 Paris
LOC9 = re.compile(r"([^A-Z])\[?\.\.\.\]?\s*[à\-]\s*[0-9A-Z]", flags=re.DOTALL)  # ... - PARIS



LOCS = [LOC1, LOC2, LOC3, LOC4, LOC5, LOC6, LOC7, LOC8, LOC9, LOC10, LOC11, LOC12, LOC13]

# DATES
DATE1 = re.compile(r"(née? le\s*)\[?\.\.\.\]?")
DATES = [DATE1]

CLEANER1 = re.compile(r"(.)([A-Z]\.\.\.)(.)", flags=re.DOTALL)
CLEANER2 = re.compile(r"(.)([xX]{3,})(.)", flags=re.DOTALL)



def text2clean(text):
    """
    Cleans text, tries to remove les coquilles,
    """
    logger.info("Cleaning text ...")
    text = CLEANER1.sub(r"\1 \2 \3", text)
    text = CLEANER2.sub(r"\1 ... \3", text)

    return text


def dots2tags(file_name, output_file=None):
    if not output_file:
        output_file = file_name[-4:] + "tagged.txt"

    regexes = {"PER": NAMES, "DATE": DATES, "LOC": LOCS}
    modifs_sums = defaultdict(int)
    with open(file_name, "r") as filo:
        all_text = filo.read()[:]
        all_text = text2clean(all_text)
        logger.info("Starting the replacements ...")

        for k, v in regexes.items():
            logger.info("Replacing {}".format(k))
            for rgx in v:
                if rgx.groups == 1:
                    # print("Soy uno", rgx.pattern)
                    result = rgx.subn(r"\1 {0}{0}{0} ".format(k), all_text)
                elif rgx.groups >= 2:
                    # print("Soy dos", rgx.pattern)
                    result = rgx.subn(r"\1 {0}{0}{0} \2".format(k), all_text)
                if result[1]:
                    all_text = result[0]
                    modifs_sums[k] += result[1]
                else:
                    logger.info("Regex: {} did not match any content".format(rgx.pattern))

    for k, v in modifs_sums.items():
        logger.info("Number of tagged {0}: {1}".format(k, v))

    with open(output_file, "w") as filo:
        filo.write(all_text)
    return all_text


if __name__ == '__main__':
    if len(sys.argv) < 3:
        logger.error("Please specify the input file and the output file paths")
        exit()

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    tagged_text = dots2tags(input_file, output_file)
