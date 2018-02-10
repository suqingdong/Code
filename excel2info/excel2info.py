#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""excel2info

Usage:
    excel2info --info=<info> [--pn=<pn>] [--outfile=<outfile>] [--fenqi=<fenqi>] [--disease=<disease>]
    excel2info (-h | --help)
    excel2info (-V | --version)

Options:
    -h --help                   Show this help.
    -V --version                Show the version.
    --pn=<pn>                   The project number.
    --fenqi=<fenqi>             The fenqi number[default: B1].
    --info=<info>               The information file(excel format).
    --outfile=<outfile>         The output file name.
    --disease=<disease>         The disease name if exists(better wrap by quotes).

Contact:
    suqingdong <suqingdong@novogene.com>
"""

import re
import sys

from collections import Counter

import xlrd
import docopt

try:
    import colorama
except ImportError:
    sys.path.append('/ifs/TJPROJ3/DISEASE/share/Software/python/site-packages')
    import colorama

from getDoID import getDoID, addFore


reload(sys)
sys.setdefaultencoding('utf-8')


def get_index(alist, name):

    for idx, n in enumerate(alist):
        if n.startswith(name):
            return idx


def get_value(values, idx, default='U'):

    if idx:
        return str(values[idx]).strip() or default

    return default


def check_name_dup(name_list, nameType=''):

    counter = Counter(name_list)
    duplist = [sample for (sample, count) in counter.items() if count > 1]
    if duplist:
        print 'Error! There are duplicate %s names: "%s"' % (nameType, ', '.join(duplist))
        exit(1)


def check_name_error(namelist, nameType=''):

    msg = '''==命名规则==：
    只能由字母、数字和下划线“_”组成，并且不能以数字和下划线开头，名称的长度不能超过15个字符
    为避免操作系统命名冲突，请不要选择由系统保留的设备名字、月份英文单词作为样品或组名'''

    error_names = [name for name in namelist if not re.match(r'^[a-zA-Z]\w*$', name)]

    if error_names:
        print 'Error! There are error %s names: "%s"' % (nameType, ', '.join(error_names))
        print msg
        exit(1)


def main(infile, outfile, pn, fenqi, disease):

    book = xlrd.open_workbook(infile)
    sheet = [sheet for sheet in book.sheets() if sheet.nrows][0]

    info_list = sheet.col_values(1)
    pn_idx = get_index(info_list, '子项目编号')
    disease_idx = get_index(info_list, '疾病名称')
    projectname_idx = get_index(info_list, '项目名称')

    # disease name
    disease = disease or sheet.cell_value(disease_idx, 4)
    if not re.match(r'^[ \w\-]*$', disease):
        print 'Ignored the disease name: "%s". Only accept one English name.' % disease
        disease = None

    # generate pn.txt
    pn = pn or [sheet.cell_value(pn_idx, 4) if pn_idx else ''][0].strip()
    projectname = [sheet.cell_value(projectname_idx, 4) if projectname_idx else None][0].strip()

    if not pn:
        exit('Error: pn was not supplied.')
    if not projectname:
        exit('Error: Project name was not found in excel file.')

    with open('pn.txt', 'w') as out:
        out.write('{}\t{}\n'.format(pn, projectname))

    # generate sample_info
    with open(outfile, 'w') as out:
        out.write('#%s\n' % fenqi)
        header = '#Familyid Sampleid Novoid Sex Normal/Patient PN'.split()
        if disease:
            doid = getDoID(disease)
            header.append('Disease')
            out.write("#disease:'%s'\n" % disease)
        out.write('\t'.join(header) + '\n')

        title_row_index = 13
        if '疾病发生组织类型' in sheet.row_values(title_row_index)[1]:
            title_row_index = 14
        title = sheet.row_values(title_row_index)
        # for each in title: print each

        title = [t.strip() for t in title]
        family_idx = get_index(title, '家系编号')
        sample_idx = get_index(title, '结题报告中样品名称')
        novo_idx = get_index(title, '诺禾编号')
        sex_idx = get_index(title, '性别')
        patient_idx = get_index(title, '是否患病')
        index_idx = get_index(title, 'index序列')

        if family_idx:
            family_list = [str(familyid).strip() for familyid in sheet.col_values(family_idx, title_row_index + 1) if familyid]
            check_name_error(family_list, 'FamilyID')

        sample_list = []
        novo_list = []
        for sample, novoid in zip(sheet.col_values(sample_idx, title_row_index + 1), sheet.col_values(novo_idx, title_row_index + 1)):
            sample, novoid = sample.strip(), novoid.strip()
            if sample:
                sample_list.append(sample)
                novoid = novoid or novo_list[-1]
                novo_list.append(novoid)

        if not len(sample_list):
            exit('Error! There is no sampleid.')
        check_name_error(sample_list, 'SampleID')
        check_name_dup(sample_list, 'SampleID')

        for rowx in xrange(title_row_index + 1, sheet.nrows):
            values = sheet.row_values(rowx)
            familyid = get_value(values, family_idx, '.')
            sampleid = get_value(values, sample_idx, None)
            novoid = get_value(values, novo_idx, novoid)
            sex = get_value(values, sex_idx)
            patient = get_value(values, patient_idx)

            if sex not in ('M', 'F', 'U'):
                exit('Error! Invalid sex: "%s"  Choose from ("M", "F", "U")' % sex)

            patient = ['U' if patient == '.' else patient][0]
            if patient not in ('P', 'N', 'U'):
                exit('Error! Invalid patient: "%s" Choose from ("P", "N", "U")' % patient)

            if sampleid and novo_list.count(novoid) > 1:
                index_seq = get_value(values, index_idx, None)
                if not index_seq:
                    exit('Error! Duplicates NovoID "%s" needs an index sequence, but not found.' % novoid)
                print 'Warning! There are duplicated NovoID: "%s". This might be a selflib project, NovoID_IndexSeq was used as a new NovoID.' % novoid
                # novoid = '_'.join([novoid, index_seq])
                linelist = [familyid, sampleid, '_'.join([novoid, index_seq]), sex, patient, pn]
            else:
                linelist = [familyid, sampleid, novoid, sex, patient, pn]

            if disease:
                linelist.append(doid)

            if sampleid:
                out.write('\t'.join(linelist) + '\n')

    print 'Generated files: {} and {}'.format(addFore(outfile, colorama.Fore.BLUE), addFore('pn.txt', colorama.Fore.BLUE))


if __name__ == "__main__":

    arguments = docopt.docopt(__doc__, version='v1.0')

    pn = arguments.get('--pn')
    fenqi = arguments.get('--fenqi')
    infile = arguments.get('--info')
    outfile = arguments.get('--outfile') or 'sample_info_' + fenqi
    disease = arguments.get('--disease')

    main(infile, outfile, pn, fenqi, disease)
