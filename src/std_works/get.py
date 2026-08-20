import sqlite3
import os
from contextlib import closing
default_location = os.path.join(os.path.dirname(__file__), 'scriptures.sql')

short_names = ['Ge', 'Exo', 'Lev', 'Num', 'Deu', 'Josh', 'Jdgs', 'Ruth', '1Sm',
               '2Sm', '1Ki', '2Ki', '1Chr', '2Chr', 'Ezra', 'Neh', 'Est', 'Job',
               'Psa', 'Prv', 'Eccl', 'SSol', 'Isa', 'Jer', 'Lam', 'Eze', 'Dan',
               'Hos', 'Joel', 'Amos', 'Obad', 'Jonah', 'Mic', 'Nahum', 'Hab', 'Zep', 'Hag',
               'Zec', 'Mal', 'Mat', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor',
               'Gal', 'Eph', 'Phi', 'Col', '1Th', '2Th', '1Tim', '2Tim', 'Titus', 'Phmn',
               'Heb', 'Jas', '1Pet', '2Pet', '1Jn', '2Jn', '3Jn', 'Jude', 'Rev', '1Ne',
               '2Ne', 'Jacob', 'Enos', 'Jarom', 'Omni', 'WofM', 'Mosiah', 'Alma', 'Hel', '3Ne',
               '4Ne', 'Morm', 'Ether', 'Moro', 'DandC', 'Moses', 'Abr', 'JS_M', 'JS_H', 'AofF']

bible = ['Ge', 'Exo', 'Lev', 'Num', 'Deu', 'Josh', 'Jdgs', 'Ruth', '1Sm',
         '2Sm', '1Ki', '2Ki', '1Chr', '2Chr', 'Ezra', 'Neh', 'Est', 'Job',
         'Psa', 'Prv', 'Eccl', 'SSol', 'Isa', 'Jer', 'Lam', 'Eze', 'Dan',
         'Hos', 'Joel', 'Amos', 'Obad', 'Jonah', 'Mic', 'Nahum', 'Hab', 'Zep', 'Hag',
         'Zec', 'Mal', 'Mat', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor',
         'Gal', 'Eph', 'Phi', 'Col', '1Th', '2Th', '1Tim', '2Tim', 'Titus', 'Phmn',
         'Heb', 'Jas', '1Pet', '2Pet', '1Jn', '2Jn', '3Jn', 'Jude', 'Rev', 
         'Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy', 'Joshua',
         'Judges', 'Ruth', '1 Samuel', '2 Samuel', '1 Kings', '2 Kings',
         '1 Chronicles', '2 Chronicles', 'Ezra', 'Nehemiah', 'Esther', 'Job',
         'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon', 'Isaiah',
         'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel', 'Hosea', 'Joel', 'Amos',
         'Obadiah', 'Jonah', 'Micah', 'Nahum', 'Habakkuk', 'Zephaniah', 'Haggai',
         'Zechariah', 'Malachi', 'Matthew', 'Mark', 'Luke', 'John', 'The Acts',
         'Romans', '1 Corinthians', '2 Corinthians', 'Galatians', 'Ephesians',
         'Philippians', 'Colossians', '1 Thessalonians', '2 Thessalonians',
         '1 Timothy', '2 Timothy', 'Titus', 'Philemon', 'Hebrews', 'James',
         '1 Peter', '2 Peter', '1 John', '2 John', '3 John', 'Jude', 'Revelation']

bom   = ['1Ne', '2Ne', 'Jacob', 'Enos', 'Jarom', 'Omni', 'WofM', 'Mosiah', 'Alma',
         'Hel', '3Ne', '4Ne', 'Morm', 'Ether', 'Moro', '1 Nephi', '2 Nephi',
         'Jacob', 'Enos', 'Jarom', 'Omni', 'Words of Mormon', 'Mosiah', 'Helaman',
         '3 Nephi', '4 Nephi', 'Mormon', 'Ether', 'Moroni']

dc    = ['DandC', 'Doctrine and Covenants']

pogp  = ['Moses', 'Abr', 'JS_M', 'JS_H', 'AofF', 'Moses', 'Abraham',
         'Joseph Smith Matthew', 'Joseph Smith History', 'Articles of Faith']

book_names = bible + bom + dc + pogp

columns_to_get = 'name,chapter,verse,text'

works = ['bible', 'bom', 'dc', 'pogp']

_aliases = {'d&c': 'DandC', 'dc': 'DandC'}

_canonical_map = {}
for _name in book_names:
    _canonical_map.setdefault(_name.lower().replace(' ', ''), _name)

def canonical_book(book: str) -> str:
    """
    Resolve a book name to its canonical form, tolerating case and aliases.
    """
    if book in book_names:
        return book
    norm = book.lower().replace(' ', '')
    if norm in _aliases:
        return _aliases[norm]
    return _canonical_map.get(norm, book)

def is_short_name(book_name: str) -> bool:
    """
    Check if a name is in short form
    """
    return book_name in short_names

def is_whole_chapter(verse_dict: dict) -> bool:
    """
    Check if query is for an entire chapter
    """
    return verse_dict['verses'] == None

def map_to_work(book: str) -> str:
    """
    Sort out which work a book belongs to
    """
    canon = canonical_book(book)
    if canon in bible:
        return 'bible'
    if canon in bom:
        return 'bom'
    if canon in dc:
        return 'dc'
    if canon in pogp:
        return 'pogp'
    return 'error'

def use_phrase(phrase: str) -> list:
    """
    Execute an SQL query to get a selection of verses
    """
    with closing(sqlite3.connect(default_location)) as con:
        cur = con.cursor()
        cur.execute(phrase)
        return cur.fetchall()

def search_phrase(term: str, work: str = '') -> list:
    """
    Search the text of the scriptures for a term and return matching verses.
    `work` may be a book name or a table name.
    """
    if not term.strip():
        raise ValueError('Empty search term.')
    escaped = term.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
    match = ' WHERE text LIKE \'%' + escaped + '%\' ESCAPE \'\\\''

    if work:
        book = canonical_book(work)
        if book in works:
            table = book
            name_clause = ''
        else:
            table = map_to_work(book)
            if table == 'error':
                raise ValueError('Unknown book: ' + work)
            if is_short_name(book):
                name_clause = ' AND short_name LIKE \'' + book + '\''
            else:
                name_clause = ' AND name LIKE \'' + book + '\''
        phrase = 'SELECT ' + columns_to_get + ' FROM ' + table + match + name_clause + ';'
        output = use_phrase(phrase)
    else:
        output = []
        for table in works:
            phrase = 'SELECT ' + columns_to_get + ' FROM ' + table + match + ';'
            output.extend(use_phrase(phrase))

    return output

def make_normal_phrase(verse_dict: dict, index: bool = False) -> str:
    """
    Create an SQL query that simply selects a single verse
    """
    book = canonical_book(verse_dict['books'])
    work = map_to_work(book)
    if work == 'error':
        raise ValueError('Unknown book: ' + book)
    get = columns_to_get

    if index:
        get = 'indx'

    if verse_dict.get('whole_book'):
        if is_short_name(book):
            return 'SELECT ' + get + ' FROM ' + work + ' WHERE short_name LIKE \"' + book + '\";'
        else:
            return 'SELECT ' + get + ' FROM ' + work + ' WHERE name LIKE \"' + book + '\";'

    chapter = verse_dict['chapters']
    verse = verse_dict['verses']

    if is_short_name(book):
        output = 'SELECT ' + get + ' FROM ' + work + ' WHERE short_name LIKE \"' + book + '\" AND chapter = ' + chapter
    else:
        output = 'SELECT ' + get + ' FROM ' + work + ' WHERE name LIKE \"' + book + '\" AND chapter = ' + chapter

    if is_whole_chapter(verse_dict):
        output += ';'
    else:
        output += ' AND verse = ' + verse + ';'

    return output

def make_range_phrase(start: dict, end: dict) -> str:
    """
    Create an SQL query that select a range of verses
    """
    work = map_to_work(start['books'])
    if work == 'error':
        raise ValueError('Unknown book: ' + start['books'])
    end_work = map_to_work(end['books'])
    if end_work == 'error':
        raise ValueError('Unknown book: ' + end['books'])
    if end_work != work:
        raise ValueError('Range spans multiple works.')
    start_phrase = make_normal_phrase(start, index = True)
    end_phrase = make_normal_phrase(end, index = True)
    Start_rows = use_phrase(start_phrase)
    if not Start_rows:
        raise RuntimeError('Range not acceptable; it\'s too long.')
    Start = Start_rows[0][0]
    End_rows = use_phrase(end_phrase)
    if not End_rows:
        raise RuntimeError('Range not acceptable; it\'s too long.')
    End = End_rows[-1][0]
    return 'SELECT ' + columns_to_get + ' FROM ' + work + ' WHERE indx BETWEEN ' + str(Start) + ' AND ' + str(End) + ';'

def make_phrase(verse_dict: dict) -> str | list:
    """
    Create an SQL phrase or phrases to query scriptures
    """
    if verse_dict['type'] == 'range':
        output = make_range_phrase(verse_dict['ranges'][0], verse_dict['ranges'][1])
        return output

    if verse_dict['type'] == 'normal':
        output = make_normal_phrase(verse_dict)
        return output

    output = []
    for pair in verse_dict['ranges']:
        if pair == (None, None):
            continue
        output.append(make_range_phrase(pair[0], pair[1]))

    whole_books = verse_dict.get('whole_book', [False] * len(verse_dict['books']))
    if isinstance(whole_books, bool):
        whole_books = [whole_books] * len(verse_dict['books'])

    for i in range(len(verse_dict['books'])):
        dictionary = {'type': 'normal',
                      'books': verse_dict['books'][i],
                      'chapters': verse_dict['chapters'][i],
                      'verses': verse_dict['verses'][i],
                      'ranges': (None, None),
                      'whole_book': whole_books[i]}
        output.append(make_normal_phrase(dictionary))

    return output

def get_verses(phrases: str | list) -> list:
    """
    Use a phrase or phrases and return selected verses
    """
    output = []

    if isinstance(phrases, list):
        for x in phrases:
            tmp = use_phrase(x)
            if isinstance(tmp, list):
                for y in tmp:
                    output.append(y)
            else:
                output.append(tmp)
        return output

    return use_phrase(phrases)

