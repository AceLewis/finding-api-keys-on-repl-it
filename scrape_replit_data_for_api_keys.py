from tqdm import tqdm

import csv
import re
import sys

# Some of the csv fields are very big the to max size needs to be increased
maxInt = sys.maxsize

while True:
    # decrease the maxInt value by factor 10
    # as long as the OverflowError occurs.

    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)


def append_list_as_row(file_name, list_of_elem):
    """Append a list to a csv file"""
    # Open file in append mode
    with open(file_name, 'a+', encoding='utf8') as write_obj:
        # Create a writer object from csv module
        csv_writer = csv.writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)


def search_whole_file_for_matches(filename, save_filename, regex_dict):
    """Search the 1.6 GB file for all regex matches and save to a file for later"""
    with open(filename, 'r', encoding='utf8') as csvfile:
        datareader = csv.reader(csvfile)
        for i, row in tqdm(enumerate(datareader, 1)):
            # Limited file length because if the file is too long it is probably just loads of
            # random data e.g someone put a binary that is base64 encoded.
            if len(row[-1]) < 12000:
                if any(regex.search(row[-1]) for regex in regex_dict.values()):
                    append_list_as_row(save_filename, row)


def group_found_api_keys(filename, regex_dict):
    """
    Group all API keys, they were saved to a file so the main search only needs to be done once.
    """
    random_dict = {}

    for key in tqdm(regex_dict.keys()):
        interesting_rows = []
        with open(filename, 'r', encoding='utf8') as csvfile:
            datareader = csv.reader(csvfile)
            for i, row in tqdm(enumerate(datareader, 1)):
                if row and len(row[-1]) < 12000:
                    if regex_dict[key].search(row[-1]):
                        interesting_rows.append(row)
        random_dict.update({key: interesting_rows})
    return random_dict


regex_dict = {
    'Artifactory API Token': re.compile(r'''(?:\s|=|:|"|^)AKC[a-zA-Z0-9]{10,}'''),
    'AWS Client ID': re.compile(r'''(A3T[A-Z0-9]|AKIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA|ASIA)[A-Z0-9]{16}'''),
    'AWS MWS Key': re.compile(r'''amzn\.mws\.[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'''),
    'AWS Secret Key': re.compile(r'''(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]'''),
    'Cloudinary Basic Auth': re.compile(r'''cloudinary:\/\/[0-9]{15}:[0-9A-Za-z]+@[a-z]+'''),
    'Facebook Access Token': re.compile(r'''EAACEdEose0cBA[0-9A-Za-z]+'''),
    'Facebook Client ID': re.compile(r'''(?i)(facebook|fb)(.{0,20})?['\"][0-9]{13,17}'''),
    'Facebook Oauth': re.compile(r'''[f|F][a|A][c|C][e|E][b|B][o|O][o|O][k|K].*['|\"][0-9a-f]{32}['|\"]'''),
    'Facebook Secret Key': re.compile(r'''(?i)(facebook|fb)(.{0,20})?['\"][0-9a-f]{32}'''),
    'Github': re.compile(r'''(?i)github(.{0,20})?['\"][0-9a-zA-Z]{35,40}'''),
    'Google API Key': re.compile(r'''AIza[0-9A-Za-z\\-_]{35}'''),
    'Google Cloud Platform API Key': re.compile(r'''(?i)(google|gcp|youtube|drive|yt)(.{0,20})?['\"][AIza[0-9a-z\\-_]{35}]['\"]'''),
    'Google Oauth': re.compile(r'''[0-9]+-[0-9A-Za-z_]{32}\.apps\.googleusercontent\.com'''),
    'Google Oauth Access Token': re.compile(r'''ya29\\.[0-9A-Za-z\\-_]+'''),
    'Heroku API Key': re.compile(r'''[h|H][e|E][r|R][o|O][k|K][u|U].{0,30}[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}'''),
    'LinkedIn Client ID': re.compile(r'''(?i)linkedin(.{0,20})?['\"][0-9a-z]{12}['\"]'''),
    'LinkedIn Secret Key': re.compile(r'''(?i)linkedin(.{0,20})?['\"][0-9a-z]{16}['\"]'''),
    'Mailchamp API Key': re.compile(r'''[0-9a-f]{32}-us[0-9]{1,2}'''),
    'Mailgun API Key': re.compile(r'''key-[0-9a-zA-Z]{32}'''),
    'Mailto:': re.compile(r'''(?<=mailto:)[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+'''),
    'Picatic API Key': re.compile(r'''sk_live_[0-9a-z]{32}'''),
    'Slack Token': re.compile(r'''xox[baprs]-([0-9a-zA-Z]{10,48})?'''),
    'Slack Webhook': re.compile(r'''https://hooks.slack.com/services/T[a-zA-Z0-9_]{8}/B[a-zA-Z0-9_]{8}/[a-zA-Z0-9_]{24}'''),
    'Stripe API Key': re.compile(r'''(?:r|s)k_live_[0-9a-zA-Z]{24}'''),
    'Square Access Token': re.compile(r'''sqOatp-[0-9A-Za-z\\-_]{22}'''),
    'Square Oauth Secret': re.compile(r'''sq0csp-[ 0-9A-Za-z\\-_]{43}'''),
    'Twilio API Key': re.compile(r'''SK[0-9a-fA-F]{32}'''),
    'Twitter Client ID': re.compile(r'''(?i)twitter(.{0,20})?['\"][0-9a-z]{18,25}'''),
    'Twitter Oauth': re.compile(r'''[t|T][w|W][i|I][t|T][t|T][e|E][r|R].{0,30}['\"\\s][0-9a-zA-Z]{35,44}['\"\\s]'''),
    'Twitter Secret Key': re.compile(r'''(?i)twitter(.{0,20})?['\"][0-9a-z]{35,44}'''),
    'Twitter': re.compile(r'''[1-9][ 0-9]+-[0-9a-zA-Z]{40}'''),
    'Square OAuth Secret': re.compile(r'''q0csp-[ 0-9A-Za-z-_]{43}'''),
    'Paypal Access Token': re.compile(r'''access_token,production$[0-9a-z]{161}[0-9a,]{32}'''),
    'praw': re.compile(r'''Reddit\([\S\n ]*client_secret[\S\n ]*\)'''),
    }

filename = 'repl-it_data.csv'
save_filename = 'all_matched_data.csv'
search_whole_file_for_matches(filename, save_filename, regex_dict)
api_keys = group_found_api_keys(save_filename, regex_dict)
