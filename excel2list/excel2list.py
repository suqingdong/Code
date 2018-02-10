#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""excel2list

Usage:
    excel2list --list=<list> --info=<info> [--pn=<pn>] [--outfile=<outfile>] [--fenqi=<fenqi>]
    excel2list (-h | --help)
    excel2list (-V | --version)

Options:
    -h --help                   Show this help.
    -V --version                Show the version.
    --pn=<pn>                   The project number.
    --fenqi=<fenqi>             The fenqi number[default: B1].
    --list=<list>               The path file(excel format).
    --info=<info>               The information file(excel format).
    --outfile=<outfile>         The output file name.

Contact:
    suqingdong <suqingdong@novogene.com>
"""
import os
import re
import sys

import xlrd
import docopt

try:
    import colorama
except ImportError:
    sys.path.append('/ifs/TJPROJ3/DISEASE/share/Software/python/site-packages')
    import colorama


reload(sys)
sys.setdefaultencoding('utf-8')

# colorama needs init before used
colorama.init()


def addFore(text, color=colorama.Fore.CYAN):
    return '%s%s%s' % (color, text, colorama.Fore.RESET)


def get_index(alist, name):

    for idx, n in enumerate(alist):
        if name in n:
            return idx


def get_value(values, idx):
    if idx != None:
        return str(values[idx]).strip()


def get_novo_sample_dict(infofile):

    book = xlrd.open_workbook(infofile)
    sheet = [sheet for sheet in book.sheets() if sheet.nrows][0]

    title = sheet.row_values(13)
    title = [t.strip() for t in title]

    sample_idx = get_index(title, '结题报告中样品名称')
    novo_idx = get_index(title, '诺禾编号')
    index_idx = get_index(title, 'index序列')

    novo_list = [novoid.strip() for novoid in sheet.col_values(novo_idx, 14) if novoid]

    novo_sample_dict = {}
    for rowx in xrange(14, sheet.nrows):
        values = sheet.row_values(rowx)
        sampleid = get_value(values, sample_idx)
        novoid = get_value(values, novo_idx)
        index_seq = get_value(values, index_idx)

        if novo_list.count(novoid) > 1:
            index_seq = get_value(values, index_idx)
            if not index_seq:
                exit('Error! Duplicates NovoID "%s" needs an index sequence, but not found.' % novoid)
            novoid = '_'.join([novoid, index_seq])

        novo_sample_dict[novoid] = sampleid

    return novo_sample_dict


def safe_open(infile):
    try:
        if infile.endswith('.gz'):
            import gzip
            return gzip.open(infile)
        else:
            return open(infile)
    except Exception as e:
        print e


def isNova(adapter_path):
    with safe_open(adapter_path) as f:
        f.next()
        if f.next().startswith('A'):
            return True
    return False


def main(listfile, infofile, outfile, fenqi, pn_input):

    novo_sample_dict = get_novo_sample_dict(infofile)
    # print novo_sample_dict

    book = xlrd.open_workbook(listfile)
    sheet = [sheet for sheet in book.sheets() if sheet.nrows][0]

    title = sheet.row_values(0)
    title = [t.strip() for t in title]

    lane_idx = get_index(title, 'LaneID')
    novo_idx = get_index(title, '诺禾编号')
    lib_idx = get_index(title, '文库名')
    index_idx = get_index(title, 'INDEX')
    index_seq_idx = get_index(title, 'INDEX序列')
    path_idx = get_index(title, 'PATH')

    pn_idx = get_index(title, '项目编号')
    owner_idx = get_index(title, '信息负责人')

    # generate sample_list
    with open(outfile, 'w') as out:
        header = '#Ori_lane PatientID SampleID LibID NovoID Index Path'.split()
        out.write('\t'.join(header) + '\n')

        for rowx in xrange(1, sheet.nrows):
            values = sheet.row_values(rowx)

            pn = get_value(values, pn_idx)
            if pn_input and (pn_input != pn):
                continue

            lane = get_value(values, lane_idx)
            novoid = get_value(values, novo_idx)
            libid = get_value(values, lib_idx)
            index = get_value(values, index_idx)
            index_seq = get_value(values, index_seq_idx)
            path = get_value(values, path_idx)

            if novoid not in novo_sample_dict:
                novoid = '{}_{}'.format(novoid, index_seq)
            if novoid not in novo_sample_dict:
                continue

            sampleid = patientid = novo_sample_dict.get(novoid)

            linelist = [lane, patientid, sampleid, libid, novoid, index, path]
            out.write('\t'.join(linelist) + '\n')

            adapter_path = os.path.join(path, libid, '{}_L{}_1.adapter.list.gz'.format(libid, lane))
            if isNova(adapter_path):
                print '%s is a nova data' % os.path.dirname(adapter_path)
                lane = ['2' if lane == '1' else '1'][0]
                linelist = [lane, patientid, sampleid, libid, novoid, index, path]
                out.write('\t'.join(linelist) + '\n')

    print 'Generated files: {}'.format(addFore(outfile, colorama.Fore.BLUE))


if __name__ == "__main__":

    arguments = docopt.docopt(__doc__, version='v1.0')

    pn_input = arguments.get('--pn')
    fenqi = arguments.get('--fenqi')
    infofile = arguments.get('--info')
    listfile = arguments.get('--list')
    outfile = arguments.get('--outfile') or 'sample_list_' + fenqi

    main(listfile, infofile, outfile, fenqi, pn_input)
