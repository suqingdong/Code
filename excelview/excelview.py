#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""View contents of excel file

Usage:
    excelview <infile>
    excelview <infile> | other_commands
    excelview <infile> <<< sheet_index
    excelview <infile> <<< sheet_index | other_commands

Contact:
    suqingdong<suqingdong@novogene.com>
"""
import os
import sys
import signal

import codecs

import docopt
import xlrd

try:
    import chardet
except ImportError as e:
    sys.path.append('/ifs/TJPROJ3/DISEASE/share/Software/python/site-packages')
    import chardet


# Solve the encoding problem
reload(sys)
sys.setdefaultencoding('utf-8')

# Solve the IOError: [Errno 32] Broken pipe
signal.signal(signal.SIGPIPE, signal.SIG_DFL)


def get_true_path(infile):

    while True:
        if os.path.islink(infile):
            infile = os.readlink(infile)
        else:
            break

    return infile


def get_encoding(infile):
    
    with open(infile, 'rb') as f:
        result = chardet.detect(f.read())

        return result.get('encoding')
    

def read_excel(infile):

    with xlrd.open_workbook(infile) as book:

        # default view the first non-empty sheet
        sheet = [sheet for sheet in book.sheets() if sheet.nrows][0]

        sheet_names = book.sheet_names()
        sheet_list = ['{}:{}'.format(index, sheet_name) for index, sheet_name in enumerate(sheet_names)]
        if len(sheet_names) > 1:
            print 'There are more than one sheet'
            while True:
                sheet_index = input('Please choose a sheet index to view\n%s:' % '\t'.join(sheet_list))
                if sheet_index in range(len(sheet_names)):
                    break
                print 'Invalid input, try again with one of %s' % range(len(sheet_names))
            sheet = book.sheet_by_index(sheet_index)

        for rowx in xrange(sheet.nrows):
            values = [str(each) for each in sheet.row_values(rowx)]
            print('\t'.join(values))


def main(infile):

    infile = get_true_path(infile)

    if 'binary' in os.popen('file --mime-encoding %s' % infile).read():
        read_excel(infile)
    else:
        charset = get_encoding(infile)
        print '\nThis is plain text file...\n'
        with codecs.open(infile, encoding=charset) as f:
            for line in f:
                sys.stdout.write(line)


if __name__ == "__main__":

    arguments = docopt.docopt(__doc__)
    infile = arguments.get('<infile>')

    main(infile)
