#!/usr/bin/env python
# -*- coding=utf-8 -*-

import sys
import xlrd

reload(sys)
sys.setdefaultencoding('utf-8')


book = xlrd.open_workbook('test/自建库.xlsx')

sheet = [sheet for sheet in book.sheets() if sheet.nrows][0]

header = sheet.row_values(13, 10)

print '\t'.join(header)

diseaseName = sheet.cell_value(10, 4)
print diseaseName
