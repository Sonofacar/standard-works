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

    if length <= 0:
        length = 1

    while remaining != '':

        if len(remaining) <= length:
            output.append(remaining)
            remaining = ''
            break

        spaces = [x for x in re.finditer(' ', remaining)]
        cuts = [x for x in spaces if x.start() < length]

        if not cuts:
            output.append(remaining[:length])
            remaining = remaining[length:]
            continue

        output.append(remaining[0:cuts[-1].start()])
        remaining = remaining[cuts[-1].end():]

    return output

def _highlight(line: str, term: str) -> str:
    """
    Wrap case-insensitive matches of term in a line with ANSI yellow.
    """
    if not term:
        return line
    output = ''
    lower = line.lower()
    term_lower = term.lower()
    tlen = len(term)
    i = 0
    while True:
        j = lower.find(term_lower, i)
        if j == -1:
            output += line[i:]
            break
        output += line[i:j] + '\x1b[33m' + line[j:j + tlen] + '\x1b[0m'
        i = j + tlen
    return output

def _format_verse(verse: tuple, line_length: int, highlight: str, prefix: str) -> list:
    """
    Wrap, indent, number, and optionally highlight a single verse's text.
    """
    lines = split_lines(verse[-1], line_length)
    lines = ['\t' + x for x in lines]
    lines[0] = prefix + '.' + lines[0]
    if highlight:
        lines = [_highlight(line, highlight) for line in lines]
    return lines

def print_verses(original_phrase: str, verses: list, line_length: int, page: bool = False, highlight: str = None) -> None:
    """
    Handle the printing of verses, including the selection of verses, and
    allowing for a specified maximum line length. `highlight` wraps matching
    substrings in the verse text with ANSI color.
    """
    output = original_phrase + '\n'

    for verse in verses:
        for line in _format_verse(verse, line_length, highlight, str(verse[2])):
            output = output + line + '\n'

    if page:
        pydoc.pager(output)
    else:
        print(output)

def print_search_list(verses: list) -> None:
    """
    Print only the reference (Book Chapter:Verse) of each matching verse,
    one per line.
    """
    for verse in verses:
        print(str(verse[0]) + ' ' + str(verse[1]) + ':' + str(verse[2]))

def print_search(verses: list, line_length: int, page: bool = False, highlight: str = None) -> None:
    """
    Print search results, each with its reference (Book Chapter:Verse) on its
    own line, followed by the verse rendered as normal. `highlight` wraps
    matching substrings in the verse text with ANSI color.
    """
    output = ''

    for verse in verses:
        reference = str(verse[0]) + ' ' + str(verse[1]) + ':' + str(verse[2])
        output = output + reference + '\n'
        for line in _format_verse(verse, line_length, highlight, str(verse[2])):
            output = output + line + '\n'
        output = output + '\n'

    if page:
        pydoc.pager(output)
    else:
        print(output)

