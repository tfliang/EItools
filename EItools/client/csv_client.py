import codecs
import csv


class CSVClient(object):
    def __init__(self, csv_name):
        self.csv_name = csv_name

    def getWriter(self, mode):
        with codecs.open(self.csv_name, mode, encoding='utf-8') as f:
            f_csv = csv.writer(f)

    def getReader(self, mode):
        with codecs.open(self.csv_name, mode, encoding='utf-8') as f:
            f_csv = csv.reader(f)
            return f_csv
