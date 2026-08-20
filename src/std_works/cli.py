import std_works as lib
import argparse
import builtins
import os
import sys
import termios
import tty
import unicodedata

prompt = '📚 > '
history = []
verbs = {'print': 'print',
         'show': 'print',
         'page': 'page',
         'explore': 'page',
         'search': 'search',
         'find': 'search',
         'grep': 'search',
         'list-search': 'list-search',
         'exit': 'exit',
         'quit': 'exit',
         'q': 'exit',
         'leave': 'exit',
         'help': 'help',
         '?': 'help'}

def _color_enabled():
    if os.environ.get('NO_COLOR'):
        return False
    if os.environ.get('TERM') in ('dumb', 'emacs'):
        return False
    return True

def run_search(term, work, page, length, list_mode=False):
    try:
        verses = lib.search_phrase(term, work)
    except ValueError as e:
        print('Error: ' + str(e))
        return 1

    if not verses:
        print('No matches for "' + term + '".')
        return 0

    if list_mode:
        lib.print_search_list(verses)
        return 0

    highlight = term if _color_enabled() else None
    if not page and not sys.stdout.isatty():
        highlight = None

    lib.print_search(verses, length, page, highlight)
    return 0

def print_help():
    message = """Usage:
    \t<print, show> <verse(s)>
    Simply print the desired verses.

    \t<page, explore> <verse(s)>
    Print the verses inside a pager.

    \t<search, find, grep> <term> [book]
    Print matching verses, each with its reference.

    \t<list-search> <term> [book]
    Print only the references of matching verses, one per line.

    \t<help, ?>
    Print this help message.
    """

    print(message)

def _width(s):
    return sum(2 if unicodedata.east_asian_width(c) in ('W', 'F') else 1 for c in s)

def _redraw(prompt, buf, cur=0):
    sys.stdout.write('\r\x1b[2K' + prompt + buf)
    tail = buf[cur:]
    if tail:
        sys.stdout.write('\x1b[%dD' % _width(tail))
    sys.stdout.flush()

def read_input(prompt):
    if not sys.stdin.isatty():
        return builtins.input(prompt)
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    buf = ''
    cur = 0
    pos = len(history)
    try:
        tty.setcbreak(fd)
        _redraw(prompt, buf)
        while True:
            ch = os.read(fd, 1)
            if ch in (b'\r', b'\n'):
                sys.stdout.write('\r\n')
                sys.stdout.flush()
                return buf
            if ch == b'\x03':
                raise KeyboardInterrupt
            if ch == b'\x04':
                raise EOFError
            if ch in (b'\x7f', b'\x08'):
                if cur > 0:
                    buf = buf[:cur - 1] + buf[cur:]
                    cur -= 1
                    _redraw(prompt, buf, cur)
                continue
            if ch == b'\x1b':
                seq = os.read(fd, 1) + os.read(fd, 1)
                if seq == b'[A':
                    if pos > 0:
                        pos -= 1
                        buf = history[pos]
                        cur = len(buf)
                        _redraw(prompt, buf, cur)
                elif seq == b'[B':
                    if pos < len(history):
                        pos += 1
                        buf = history[pos] if pos < len(history) else ''
                        cur = len(buf)
                        _redraw(prompt, buf, cur)
                elif seq == b'[C':
                    if cur < len(buf):
                        cur += 1
                        _redraw(prompt, buf, cur)
                elif seq == b'[D':
                    if cur > 0:
                        cur -= 1
                        _redraw(prompt, buf, cur)
                continue
            try:
                c = ch.decode()
            except UnicodeDecodeError:
                continue
            buf = buf[:cur] + c + buf[cur:]
            cur += 1
            _redraw(prompt, buf, cur)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def get_verse(query):
    dictionary = lib.parse(query)
    phrase = lib.make_phrase(dictionary)
    verses = lib.get_verses(phrase)
    return verses

def parse_action(info):
    output = {}
    info = info.strip()

    for verb in verbs:
        if info.startswith(verb + ' ') or info == verb:
            output['action'] = verbs[verb]
            output['target'] = info[len(verb):].strip()
            return output

    output['action'] = 'print'
    output['target'] = info
    return output

def do_command(action_dict, length = 70):
    match action_dict['action']:
        
        case 'print':
            phrase = action_dict['target']
            verses = get_verse(phrase)
            lib.print_verses(phrase, verses, length)
            return True

        case 'page':
            phrase = action_dict['target']
            verses = get_verse(phrase)
            lib.print_verses(phrase, verses, length, True)
            return True

        case 'search':
            target = action_dict['target']
            scope = ''
            words = target.split()
            if len(words) > 1 and lib.canonical_book(words[-1]) in lib.book_names:
                scope = words[-1]
                target = ' '.join(words[:-1])
            run_search(target, scope, False, length)
            return True

        case 'list-search':
            target = action_dict['target']
            scope = ''
            words = target.split()
            if len(words) > 1 and lib.canonical_book(words[-1]) in lib.book_names:
                scope = words[-1]
                target = ' '.join(words[:-1])
            run_search(target, scope, False, length, True)
            return True

        case 'exit':
            return False

        case 'help':
            print_help()
            return True

        case _:
            print('Command not understood.')
            return True

def main():
    parser = argparse.ArgumentParser(
            prog = "Standard Works",
            description = """
            Read the full Standard Works of the Church of Jesus Christ of
            Latter-day Saints from your terminal."""
            )
    parser.add_argument(
            "selection",
            nargs = "?",
            type = str,
            help = """
            The selection of verses desired. If not given, it will go to
            the command line interface."""
            )
    parser.add_argument(
            "-p",
            "--page",
            action = "store_true",
            help = "Print verse inside a pager (e.g. less)."
            )
    parser.add_argument(
            "-c",
            "--chars",
            action = "store",
            type = int,
            default = 70,
            help = "Set maximum number of characters in a line."
            )
    parser.add_argument(
            "-s",
            "--search",
            action = "store",
            type = str,
            default = None,
            help = "Search the scriptures for a term."
            )
    parser.add_argument(
            "-S",
            "--list-search",
            action = "store",
            type = str,
            default = None,
            help = "Search the scriptures and print only the references of matching verses."
            )
    parser.add_argument(
            "--work",
            action = "store",
            type = str,
            default = "",
            help = "Restrict --search to a specific book or work."
            )
    args = vars(parser.parse_args(sys.argv[1:]))

    if args['search'] is not None or args['list_search'] is not None:
        if args['search'] is not None and args['list_search'] is not None:
            print('Error: --search and --list-search cannot be used together.')
            return 1
        term = args['search'] if args['search'] is not None else args['list_search']
        list_mode = args['list_search'] is not None
        if list_mode and args['page']:
            print('Warning: --page is ignored with --list-search.', file = sys.stderr)
        work = args['work']
        if not work and args['selection']:
            work = args['selection']
        return run_search(term, work, args['page'], args['chars'], list_mode)

    if args['selection'] == None:
        Commandline = True
        Page = False
    else:
        Commandline = False
        Page = args['page']

        action = {}
        if Page:
            action['action'] = 'page'
        else:
            action['action'] = 'print'
        action['target'] = args['selection'].strip()

        try:
            do_command(action, args['chars'])
        except Exception as e:
            print('Error: ' + str(e))
            return 1

        return 0

    while Commandline:
        try:
            command = read_input(prompt).strip()
            if command:
                history.append(command)
        except (EOFError, KeyboardInterrupt):
            print()
            break

        action = parse_action(command)

        try:
            Commandline = do_command(action, args['chars'])
        except Exception:
            print('Command not understood; try again.')

    return 0

if __name__ == '__main__':
    sys.exit(main())