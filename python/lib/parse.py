import re

def is_range(phrase):
    return '-' in phrase

def has_book(phrase):
    return re.match(r'[0-9]?[ ]?[A-z& ]* [0-9]{1,3}:[0-9]{1,3}', phrase)

def has_chapter(phrase):
    return ':' in phrase

def is_broken(phrase):
    return ',' in phrase

def parse_range(phrase):
    first = phrase.split('-')[0]
    second = phrase.split('-')[1]

    first_results = parse(first)
    if not has_book(second):
        if not has_chapter(second):
            second_results = parse(second, chapter = first_results['chapters'], book = first_results['books'])
        else:
            second_results = parse(second, book = first_results['books'])
    else:
        second_results = parse(second)

    return {'type': 'range',
            'books': first_results['books'],
            'chapters': first_results['chapters'],
            'verses': first_results['verses'],
            'ranges': (first_results, second_results)}

def parse_normal(phrase):
    output = []
    if is_broken(phrase):
        parts = phrase.split(',')
        start = parse(parts[0])
        output.append(start)
        book = start['books']
        chapter = start['chapters']
        for i in range(1,len(parts)):
            if not has_book(parts[i]):
                if not has_chapter(parts[i]):
                    piece = parse(parts[i], chapter = chapter, book = book)
                    output.append(piece)
                else:
                    piece = parse(parts[i], book = book)
                    chapter = piece['chapters']
                    output.append(piece)
            else:
                piece = parse(parts[i])
                book = piece['books']
                chapter = piece['chapters']
                output.append(piece)

    else:
        output.append(parse(phrase))

    books = [x['books'] for x in output if x['type'] == 'normal']
    chapters = [x['chapters'] for x in output if x['type'] == 'normal']
    verses = [x['verses'] for x in output if x['type'] == 'normal']
    ranges = [x['ranges'] for x in output if x['type'] == 'range']

    return {'type': 'multiple',
            'books': books,
            'chapters': chapters,
            'verses': verses,
            'ranges': ranges}

def parse(phrase, book = '', chapter = ''):
    if book != '':
        if chapter != '':
            phrase = book + ' ' + chapter + ':' + phrase
        else:
            phrase = book + ' ' + phrase

    first = phrase.split(',')[0]

    if is_broken(phrase):
        output = parse_normal(phrase)

    elif is_range(phrase):
        output = parse_range(phrase)

    else:
        book_match = re.search('[0-9]?[ ]?[A-z ]*', first)
        book = first[book_match.start():book_match.end()]
        ending = first.split(' ')[-1]
        chapter = ending.split(':')[0]
        verse = ending.split(':')[1]
        ranges = (None, None)

        output = {'type': 'normal',
                  'books': book.strip(),
                  'chapters': chapter.strip(),
                  'verses': verse.strip(),
                  'ranges': ranges}

    return output
