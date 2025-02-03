# Imports
import pandas
import sqlite3
import requests
from bs4 import BeautifulSoup
import re
import time

# Variables
creation_phrase = '''CREATE TABLE IF NOT EXISTS references (
work TEXT,
book TEXT,
chapter INTEGER,
verse INTEGER,
word INTEGER,
type TEXT,
to_work TEXT,
location TEXT)
;'''
base_url = 'https://www.churchofjesuschrist.org'
href_endpoints = [('/study/scriptures/bofm/1-ne/1', '/study/scriptures/bofm/moro/10'),
                  ('/study/scriptures/ot/gen/1', '/study/scriptures/ot/mal/4'),
                  ('/study/scriptures/nt/matt/1', '/study/scriptures/nt/rev/22'),
                  ('/study/scriptures/dc-testament/dc/1', '/study/scriptures/dc-testament/dc/138'),
                  ('/study/scriptures/pgp/moses/1', '/study/scriptures/pgp/a-of-f/1')]
next_page = '.nextLink-otfJl .icon-RXkDY'
note_attrs = {'class': 'marker', 'data-type': 'verse'}

# Functions
def find_note_locations(soup, verse_num):
    verse = soup.find('p', {'id': 'p' + str(verse_num)})
    char_index = 0
    pieces = verse.contents.copy()
    pieces = [x for x in pieces if x.name != 'span']
    output = []

    for x in pieces:
        if isinstance(x, str):
            char_index += len(x)
        else:
            try:
                note_index = x.find('sup').attrs['data-value']
            except:
                note_index = ''
            note_text = x.text.strip()
            char_start = char_index
            char_index += len(note_text)
            char_end = char_index
            output.append({'verse': verse_num,
                           'letter': note_index,
                           'text': note_text,
                           'start_char_index': char_start,
                           'end_char_index': char_end})
    return output

def extract_notes(verse_soup):
    verse = int(verse_soup.attrs['data-marker'])
    notes = verse_soup.find_all('li')
    ref_list = []

    for note in notes:
        index = note.attrs['data-marker']
        spans = note.find_all('span')

        for span in spans:
            note_type = span.attrs['data-note-category']
            refs = span.find_all('a')

            for ref in refs:
                raw_string = re.sub('â\x80\x93', '-', re.sub(r'Â\xa0', ' ', ref.text.strip()))
                context_string = ''
                ref_string = ''

                if note_type == 'cross-ref':
                    parts = raw_string.split(':')

                    if len(parts) > 1:
                        emphasis = parts[1].split('(')[0]
                        start = parts[0]
                        end = parts[1]
                    else:
                        emphasis = parts[0].split('(')[0]
                        end = parts[0]

                    ref_string = start + ':' + emphasis

                    if '(' in end:
                        context = end.split('(')[1].replace(')', '')
                        context_string = start + ':' + context
                    else:
                        context_string = ''
                else:
                    ref_string = raw_string

                info = {'verse': verse,
                        'letter': index,
                        'href': ref.attrs['href'],
                        'type': note_type,
                        'ref': ref_string,
                        'context': context_string}
                ref_list.append(info)

    return ref_list

def refs_on_page(soup):
    verse_count = len(soup.find_all('p', {'class': 'verse'}))
    ref_info = []

    for verse in range(1, verse_count + 1):
        ref_info += find_note_locations(soup, verse)

    footer = soup.find_all('ul', note_attrs)[0]
    verses = footer.find_all('li', recursive = False)
    refs = []

    for verse in verses:
        refs += extract_notes(verse)

    ref_table = pandas.DataFrame(refs)
    info_table = pandas.DataFrame(ref_info)
    merge = ref_table.merge(info_table, on = ['verse', 'letter'])
    return merge

# Script
con = sqlite3.Connection('references.sql')
con.execute(creation_phrase)
output = []

for start, end in href_endpoints:
    href = start
    keep_going = True

    while keep_going:
        time.sleep(1)
        url = base_url + href

        page = requests.get(url)
        soup = BeautifulSoup(page.text)

        try:
            tmp_df = refs_on_page(soup)
        except:
            print('error: ' + href)
        else:
            output.append(tmp_df)

        href = soup.select(next_page)[0].attrs['href']

        if href == end:
            keep_going = False
