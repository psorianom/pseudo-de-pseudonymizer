'''
Replaces the specified pseduonym string by the same string BUT numbered according to its apparition in the input text

Usage:
    txt2conll.py <s> <i> <o>

Arguments:
    <-s>                   The string to replace by its numbered version
    <-i>                   An input file or directory (if dir it will convert all txt files inside).
    <-o>                   An output directory.
'''
import re
from argopt import argopt

COUNTER = 0


def dots_repl(matchobject):
    global COUNTER
    numbered_dots = "{0} PSEUDOPSEUDOPSEUDO{2} {3}".format(matchobject.groups()[0], matchobject.groups()[1], COUNTER,
                                             matchobject.groups()[2])
    COUNTER += 1

    return numbered_dots


def dots2numberedDots(all_text, replace_string="..."):
    replace_string = re.escape(replace_string)
    dots_regex = re.compile(r"(\s?)\[?({})\]?(\s*)".format(replace_string))
    all_text = dots_regex.sub(dots_repl, all_text)
    return all_text


if __name__ == '__main__':
    parser = argopt(__doc__).parse_args()
    input_path = parser.i
    output_path = parser.o
    string_to_replace = parser.s

    with open(input_path, "r") as filo:
        all_text = filo.read()
        numbered_dots_text = dots2numberedDots(all_text, replace_string=string_to_replace)

    with open(output_path, "w") as filo:
        filo.write(numbered_dots_text)
