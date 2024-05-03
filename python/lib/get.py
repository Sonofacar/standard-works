import sqlite3

default_location = 'scriptures.sql'

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

columns_to_get = 'name,chapter,verse,text'

def is_short_name(book_name):
    return book_name in short_names

def is_list(obj):
    return isinstance(obj, list)

def map_to_work(book):
    if book in bible:
        return 'bible'
    if book in bom:
        return 'bom'
    if book in dc:
        return 'dc'
    if book in pogp:
        return 'pogp'
    return 'error'

def use_phrase(phrase):
    con = sqlite3.Connection(default_location)
    cur = con.cursor()
    cur.execute(phrase)
    output = cur.fetchall()
    con.close()
    return output

def make_normal_phrase(verse_dict, index = False):
    book = verse_dict['books']
    work = map_to_work(book)
    chapter = verse_dict['chapters']
    verse = verse_dict['verses']
    get = columns_to_get
    if index:
        get = 'indx'
    if is_short_name(book):
        return 'SELECT ' + get + ' FROM ' + work + ' WHERE short_name LIKE \"' + book + '\" AND chapter = ' + chapter + ' AND verse = ' + verse + ';'
    return 'SELECT ' + get + ' FROM ' + work + ' WHERE name LIKE \"' + book + '\" AND chapter = ' + chapter + ' AND verse = ' + verse + ';'

def make_range_phrase(start, end):
    work = map_to_work(start['books'])
    start_phrase = make_normal_phrase(start, index = True)
    end_phrase = make_normal_phrase(end, index = True)
    Start = use_phrase(start_phrase)[0][0]
    try:
        End = use_phrase(end_phrase)[0][0]
    except:
        raise RuntimeError('Range not acceptable; it\'s too long.')
    return 'SELECT ' + columns_to_get + ' FROM ' + work + ' WHERE indx BETWEEN ' + str(Start) + ' AND ' + str(End) + ';'

def make_phrase(verse_dict):
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

    for i in range(len(verse_dict['books'])):
        dictionary = {'type': 'normal',
                      'books': verse_dict['books'][i],
                      'chapters': verse_dict['chapters'][i],
                      'verses': verse_dict['verses'][i],
                      'ranges': (None, None)}
        output.append(make_normal_phrase(dictionary))

    return output

def get_verses(phrases):
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
