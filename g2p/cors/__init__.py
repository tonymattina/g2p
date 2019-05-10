import csv
import os
from openpyxl import load_workbook
from g2p import exceptions
from g2p.cors.langs import LANGS


class Correspondence():
    def __init__(self, language, reverse: bool = False):
        self.path = language
        self.reverse = reverse
        # Load workbook, either from correspondence spreadsheets, or user loaded
        this_dir = os.path.dirname(os.path.abspath(__file__))
        if not isinstance(language, type(None)):
            if isinstance(language, list):
                self.path = 'user supplied data'
                if all('from' in d for d in language) and all('to' in d for d in language):
                    if self.reverse:
                        language = self.reverse_cors(language)
                    if not all('before' in cor for cor in language):
                        for cor in language:
                            cor['before'] = ''
                    if not all('after' in cor for cor in language):
                        for cor in language:
                            cor['after'] = ''
                    self.cor_list = language
                else:
                    raise exceptions.MalformedCorrespondence()
            elif isinstance(language, object):
                if not "lang" in language or not "table" in language:
                    raise exceptions.MalformedLookup()
                else:
                    try:
                        self.cor_list = self.load_from_file(LANGS[language['lang']][language['table']])
                    except KeyError:
                        raise exceptions.CorrespondenceMissing(language)
            else:
                self.cor_list = self.load_from_file(language)
        else:
            raise exceptions.CorrespondenceMissing(language)

    def __len__(self):
        return len(self.cor_list)

    def __repr__(self):
        return f"g2p.cors.Correspondence object containing unordered, parsed correspondences from {self.path}"

    def __call__(self):
        return self.cor_list

    def __iter__(self):
        return iter(self.cor_list)

    def reverse_cors(self, cor_list):
        for cor in cor_list:
            cor['from'], cor['to'] = cor['to'], cor['from']
        return cor_list

    def load_from_file(self, path):
        if path.endswith('csv'):
            return self.load_from_csv(path)
        elif path.endswith('xlsx'):
            return self.load_from_workbook(path)

    def load_from_csv(self, language):
        ws = []
        with open(language, encoding='utf8') as f:
            reader = csv.reader(f)
            for line in reader:
                ws.append(line)
        # Create wordlist
        cor_list = []
        # Loop through rows in worksheet, create if statements for different columns and append Cors to cor_list.
        for entry in ws:
            newCor = {"from": "", "to": "", "before": "", "after": ""}
            newCor['from'] = entry[0]
            newCor['to'] = entry[1]
            try:
                newCor['before'] = entry[2]
            except IndexError:
                newCor['before'] = ''
            try:
                newCor['after'] = entry[3]
            except IndexError:
                newCor['after'] = ''
            for k in newCor:
                if isinstance(newCor[k], float) or isinstance(newCor[k], int):
                    newCor[k] = str(newCor[k])

            cor_list.append(newCor)

        if self.reverse:
            cor_list = self.reverse_cors(cor_list)

        return cor_list

    def load_from_workbook(self, language):
        wb = load_workbook(language)
        ws = wb.active
        # Create wordlist
        cor_list = []
        # Loop through rows in worksheet, create if statements for different columns and append Cors to cor_list.
        for entry in ws:
            newCor = {"from": "", "to": "", "before": "", "after": ""}
            for col in entry:
                if col.column == 'A':
                    value = col.value
                    if type(value) == float or int:
                        value = str(value)
                    newCor["from"] = value
                if col.column == 'B':
                    value = col.value
                    if type(value) == float or int:
                        value = str(value)
                    newCor["to"] = value
                if col.column == 'C':
                    if col.value is not None:
                        value = col.value
                        if type(value) == float or int:
                            value = str(value)
                        newCor["before"] = value
                if col.column == 'D':
                    if col.value is not None:
                        value = col.value
                        if type(value) == float or int:
                            value = str(value)
                        newCor["after"] = value
            cor_list.append(newCor)

        if self.reverse:
            cor_list = self.reverse_cors(cor_list)

        return cor_list
