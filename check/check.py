#!/usr/bin/env python
# -*- coding=utf-8 -*-
import os
import glob
import commands
import argparse

from collections import OrderedDict


__version__ = '2.0'
__author__ = 'suqingdong'


class Check(object):

    """Check Result directory for disease pipeline"""

    def __init__(self):

        self.result_path = args.get('dir')
        self.check_all = args.get('all')
        self.show_bytes = args.get('bytes')

        self.errors = OrderedDict()

    def start(self):

        self.errors['file_not_exists_error'] = []
        self.errors['file_empty_error'] = []
        self.errors['md5_error'] = []
        self.errors['fq_error'] = []

        os.chdir(self.result_path)
        print '\033[32m|=== Release Directory: %s\033[0m' % os.getcwd()

        if 'ReleaseResult' in os.listdir('.'):
            self.check_46()
        else:
            self.check_45()

        print '|' + '-' * 100
        print '|\033[1;36;40m{:-^100s}\033[0m'.format(' Check Summary ')
        if any(self.errors.values()):
            for error_type, error_list in self.errors.iteritems():
                if error_list:
                    print '|-- {}\n|  {}'.format(
                        error_type.upper(),
                        '\n|  '.join(error_list)
                    )
        else:
            print '|{:^100s}'.format('There seems to be no obvious error')
        print '|' + '-' * 100

    @staticmethod
    def human_readable_size(size):

        if size > 1024 * 1024 * 1024:
            size = str(round(size / 1024. / 1024. / 1024., 1)) + 'G'
        elif size > 1024 * 1024:
            size = str(round(size / 1024. / 1024., 1)) + 'M'
        elif size > 1024:
            size = str(round(size / 1024., 1)) + 'K'
        elif 0 < size < 1024:
            size = str(size)
        else:
            print 'size must greater then zero'

        return size

    def get_size(self, infile):

        if not os.path.exists(infile):
            size = '\033[31;5mError\033[0m'
            self.errors['file_not_exists_error'].append('{}\t{}'.format(size, infile))
        elif os.path.getsize(infile) == 0:
            size = '\033[31;5m0\033[0m'
            self.errors['file_empty_error'].append('{}\t{}'.format(size, infile))
        else:
            size = os.path.getsize(infile) if self.show_bytes else self.human_readable_size(os.path.getsize(infile))

        return size

    def print_glob_size(self, path):

        path_list = [path] if type(path) != list else path

        for path in path_list:
            for f in glob.glob(path):
                f = f.lstrip('./')
                size = self.get_size(f)
                print '| {:6s}\t{}'.format(str(size), f)

    def check_raw_clean(self, name, data_path='.'):

        print '\033[33m|{:=^100s} \033[0m'.format(' Checking %s ' % name)
        sample_nums = commands.getoutput('ls {}/{} | wc -l'.format(data_path, name))
        print '\033[323m|-- {}样本数: {}\033[0m'.format(name, sample_nums)

        # fq_nums = commands.getoutput('ls %s/%s/*/*.fq.gz | wc -l' % (data_path, name))
        fq_nums = len(glob.glob('%s/%s/*/*.fq.gz' % (data_path, name)))

        cmd = 'wc -l %s/%s/*/MD5.txt | grep -vE "(total)|(总用量)" | awk \'{print $1}\'' % (data_path, name)
        # print cmd
        md5_nums = sum(int(n) for n in commands.getoutput(cmd).split('\n'))

        print '|-- fq.gz文件数:', fq_nums
        print '|-- MD5总行数:', md5_nums

        if fq_nums != md5_nums:
            print '\033[31m|-- fq.gz文件数和MD5总行数不相等，请检查!!!\033[0m'
            self.errors['md5_error'].append('{} fq.gz文件数({})和MD5总行数({})不相等'.format(name, fq_nums, md5_nums))
        elif fq_nums == 0:
            print '\033[31m|-- fq.gz文件不存在，请检查!!!\033[0m'
            self.errors['fq_error'].append('{} fq.gz文件不存在'.format(name))

        self.print_glob_size('{}/{}/*/*.fq.gz'.format(data_path, name))

        for md5 in glob.glob('{}/{}/*/MD5.txt'.format(data_path, name)):
            md5 = md5.lstrip('./')
            md5_num = commands.getoutput('wc -l %s | awk \'{print $1}\'' % md5)
            md5_num = '\033[31;5m{}\033[0m'.format(md5_num) if md5_num == '0' else md5_num
            print '| {:6s}\t{}'.format(md5_num, md5)

    def check_bam(self, name='Mapping', data_path='Mapping'):

        print '\033[33m|{:=^100s} \033[0m'.format(' Checking %s ' % name)
        sample_nums = commands.getoutput('ls -l {} | grep "^d" | wc -l'.format(data_path))
        print '\033[323m|-- Mapping样本数: {}\033[0m'.format(sample_nums)

        self.print_glob_size('{}/*/*.bam*'.format(data_path))

    def check_variation(self, name='Variation', data_path='Variation'):

        print '\033[33m|{:=^100s} \033[0m'.format(' Checking %s ' % name)
        sample_nums = commands.getoutput('ls -l {} | grep "^d" | wc -l'.format(data_path))
        print '\033[323m|-- Variation样本数: {}\033[0m'.format(sample_nums)

        for each in ('SNP', 'InDel', 'SV', 'CNV'):
            if glob.glob('{}/*/{}'.format(data_path, each)):
                print '|-- checking %s ...' % each
                self.print_glob_size([
                    '{}/*/{}/*.*'.format(data_path, each),
                    '{}/*/{}/Circos/*'.format(data_path, each),
                ])

    def check_advance(self, name='Advance', data_path='Advance'):

        print '\033[33m|{:=^100s} \033[0m'.format(' Checking %s ' % name)

        analysis_items = sorted(str(d) for d in os.listdir(data_path) if 'Total' not in d)

        print '|-- analysis items:\n|  ' + '\n|  '.join(analysis_items)

        if glob.glob('{}/Total.candidate_gene.xls'.format(data_path)):
            print '\033[33m|-- checking 0.Total.candidate_gene.xls ...\033[0m'
            self.print_glob_size('{}/Total.candidate_gene.xls'.format(data_path))

        # Other analysis check needs to add here
        analysis_map = OrderedDict()
        analysis_map['FilterDB'] = [
            data_path + '/*FilterDB*/VCF/*',
            data_path + '/*FilterDB*/Filter/*/*'
        ]
        for each in ('ACMG', 'FilterCNV_SV', 'ModelF'):
            analysis_map[each] = data_path + '/*{}*/*/*'.format(each)
        analysis_map['Denovo'] = [
            data_path + '/*Denovo*/SNP_INDEL/Denovo*/*/*/*',
            data_path + '/*Denovo*/SNP_INDEL/IntersectResult/*xls',
            data_path + '/*Denovo*/SNP_INDEL/IntersectResult/*/*',
            data_path + '/*Denovo*/CNV_SV/*/*/*'
        ]
        for each in ('Noncoding', 'Network', 'PPI', 'Share'):
            analysis_map[each] = data_path + '/*{}*/*'.format(each)
        analysis_map['Pathway'] = [
            data_path + '/*Pathway*/*.*',
            data_path + '/*Pathway*/KEGG_maps/*.*',
            data_path + '/*Pathway*/KEGG_maps/png/*'
        ]
        analysis_map['Custom'] = data_path + '/*Custom*/*.*'

        for analysis_detail in analysis_items:
            for analysis in analysis_map:
                if analysis in analysis_detail:
                    print '\033[33m|-- checking %s ...\033[0m' % analysis_detail
                    self.print_glob_size(analysis_map[analysis])

    def check_46(self):

        print '\033[36m|=== Check result for disease pipeline 4.6 ...\033[0m'


        # Data
        if 'Data' in os.listdir('ReleaseResult'):

            # RawData and CleanData
            for each in ('RawData', 'CleanData'):
                if each in os.listdir('ReleaseResult/Data'):
                    self.check_raw_clean(each, 'ReleaseResult/Data')

            # BamData
            if 'BamData' in os.listdir('ReleaseResult/Data'):
                self.check_bam('BamData', 'ReleaseResult/Data/BamData')

        # PrimaryAnalysis
        if 'PrimaryAnalysis' in os.listdir('ReleaseResult'):

            # SampleVariation
            if 'SampleVariation' in os.listdir('ReleaseResult/PrimaryAnalysis'):
                self.check_variation('SampleVariation', 'ReleaseResult/PrimaryAnalysis/SampleVariation')

            # FilterAnalysis
            if 'FilterAnalysis' in os.listdir('ReleaseResult/PrimaryAnalysis'):
                print '\033[33m|{:=^100s} \033[0m'.format(' Checking FilterAnalysis ')
                self.print_glob_size('ReleaseResult/PrimaryAnalysis/FilterAnalysis/*/*/*')

        # FinalResult
        if 'FinalResult' in os.listdir('ReleaseResult'):

            self.check_advance('FinalResult', 'ReleaseResult/FinalResult')

        # 4.6的Advance目录只用于信息自查，不释放
        if self.check_all:
            print '|' + '-' * 100
            print '|\033[33m{:-^100s}\033[0m'.format(' The below directories will not be released, just used for self checking! ')
            if 'Advance' in os.listdir('.'):
                self.check_advance()

    def check_45(self):

        print '\033[36m|=== Check result for disease pipeline 4.5 ...\033[0m'

        directories = os.listdir('.')

        # RawData and QC
        for each in ('RawData', 'QC'):
            if each in directories:
                self.check_raw_clean(each)

        # Mapping
        if 'Mapping' in directories:
            self.check_bam()

        # Variation
        if 'Variation' in directories:
            self.check_variation()

        # Advance
        if 'Advance' in directories:
            self.check_advance()

        # Advance_brief
        if 'Advance_brief' in directories:
            self.check_advance('Advance_brief', 'Advance_brief')


def main():

    Check().start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='Check',
        description='Check Result directory for disease pipeline',
        epilog='Contact: {0} <{0}@novogene.com>'.format(__author__),
        formatter_class=argparse.RawTextHelpFormatter,
        version=__version__
    )

    parser.add_argument('-d', '--dir', help='The data release path to check [default="%(default)s"]', default='.')
    parser.add_argument('-a', '--all', help='Whether check Advance directory or not for 4.6 pipeline', action='store_true')
    parser.add_argument('-b', '--bytes', help='Show file sizes in bytes, default will show in human-readable format(K, M, G)', action='store_true')

    args = vars(parser.parse_args())

    main()
