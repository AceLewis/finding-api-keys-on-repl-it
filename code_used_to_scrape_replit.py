import requests
from bs4 import BeautifulSoup
from baseconv import BaseConverter

import re
import json
import html
import string
import os
import csv


class NewSession:
    """Create a session for connecting to repl.it. The session is good because
    then one connection to repl.it is needed for all scrapes and not a new
    connection per scrape."""

    def __init__(self, proxies={}):
        # Create new session
        self.request_session = requests.Session()
        self.proxies = proxies
        # Use header that makes it seem less like a bot
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                        "Accept-Language": "en-US,en;q=0.8",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"}
        # repl base is A-Z0-9a-z
        repl_it_string = string.ascii_uppercase + string.digits + string.ascii_lowercase
        self.repl_it_base = BaseConverter(repl_it_string)

    def decode(self, number):
        "Decode repl.it code id to a base 10 number"
        return int(self.repl_it_base.decode(number))

    def encode(self, number):
        "Encode base 10 number to repl.it code id"
        return self.repl_it_base.encode(number)

    def get_repl_save(self, code_id):
        "Save repl.it by code id"
        repl_html = self.get_repl_it_html(code_id)
        return self.get_data_from_html(repl_html, code_id)

    def get_repl_it_html(self, code_id):
        "Get html for code id"
        url = 'https://repl.it/{}'.format(code_id)
        return self.request_session.get(url, proxies=self.proxies, headers=self.headers).text

    def get_data_from_html(self, repl_html, code_id):
        "Get all data from the html"
        # All the data we need is in the HTML
        soup = BeautifulSoup(repl_html, 'html.parser')
        try:
            editor_data = [x.text for x in soup.findAll('script') if 'REPLIT_DATA' in x.text][0]
        except IndexError:
            data = {}
            data['session_id'] = code_id
            for x in ['language', 'time_created',
                      'time_updated', 'owner', 'title', 'editor_text']:
                data[x] = '404'
            return data
        editor_data_json = re.findall('{.*}', editor_data)[0]
        data = json.loads(editor_data_json)
        del data['console_dump']  # Not needed
        # String is HTML escaped so we need to unescape it
        data['editor_text'] = html.unescape(data['editor_text'])

        return data


def add_under_base(session, repl_number, what_to_add):
    "Get the repl code ID in "
    return session.encode(session.decode(repl_number) + what_to_add)


def save_repl_data(repl_data_dir, code_data):
    "Function to save the repl.it code data to a json info file and a text document with code in"
    code_data_save_dir = ''.join([['l', 'u'][x.isupper()] + x for x in code_data['session_id']])
    save_dir = repl_data_dir + '\\' + code_data_save_dir
    code = code_data['editor_text']
    code_data.pop('editor_text', None)

    os.makedirs(save_dir, exist_ok=True)
    with open(save_dir + r'\data.json', 'w') as outfile:
        json.dump(code_data, outfile)

    with open(save_dir + '\\' + code_data['session_id'] + '.txt', 'w', encoding='utf-8') as outfile:
        outfile.write(code)


def append_to_csv(repl_data_dir, code_data):
    "Append the data to a CSV file"
    fieldnames = ['session_id', 'language', 'time_created', 'time_updated', 'owner', 'title', 'editor_text']
    for unused in ['is_project', 'revision_id', 'files', 'id']:
        code_data.pop(unused, None)

    with open(repl_data_dir + r'\repl-it_data.csv', 'a+', newline='', encoding='utf-8') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writerow(code_data)


repl_data_dir = r'F:\repl_it'
session = NewSession()
repl_number = 'l4K'
number = 0

while repl_number[0] != '-':
    number += 1
    code_data = session.get_repl_save(repl_number)
    print("{:<8}Scraped:{:>5}, language: {:<15}".format(number, code_data['session_id'], code_data['language']), end='')
    append_to_csv(repl_data_dir, code_data)
    print("saved")
    repl_number = add_under_base(session, repl_number, -1)
