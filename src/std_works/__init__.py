from std_works.get import *
from std_works.parse import *
import re
import pydoc

def split_lines(text: str, length: int) -> list:
    """
    Split text into lines. Lines keep whole words together while approaching
    a maximum length.
    """
    output = []
    remaining = text

    while remaining != '':

        if len(remaining) <= length:
            output.append(remaining)
            remaining = ''
            break

        spaces = [x for x in re.finditer(' ', remaining)]
        cuts = [x for x in spaces if x.start() < length]
        output.append(remaining[0:cuts[-1].start()])
        remaining = remaining[cuts[-1].end():]

    return output

def print_verses(original_phrase: str, verses: list, line_length: int, page: bool = False) -> None:
    """
    Handle the printing of verses, including the selection of verses, and
    allowing for a specified maximum line length.
    """
    output = original_phrase + '\n'

    for verse in verses:
        lines = split_lines(verse[-1], line_length)
        lines = ['\t' + x for x in lines]
        lines[0] = str(verse[2]) + '.' + lines[0]

        for line in lines:
            output = output + line + '\n'

    if page:
        pydoc.pager(output)
    else:
        print(output)

