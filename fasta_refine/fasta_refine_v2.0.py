#!/usr/bin/env python
# -*- encoding: utf-8 -*-

__author__ = 'suqingdong'
__contact__ = 'suqingdong@novogene.com'
__version__ = 'v2.0'


def safe_open(infile, mode='r'):

    try:
        if infile.endswith('.gz'):
            import gzip
            mode += 'b'
            return gzip.open(infile, mode)
        return open(infile, mode)
    except IOError:
        print 'File not exists: %s!' % infile


def main():

    infile = args.get('infile')
    outfile = args.get('outfile') or infile.rsplit('.', 1)[0]+'.refined.fa'
    N = args.get('N')
    M = args.get('M')
    convert = args.get('convert')

    with safe_open(infile) as f, safe_open(outfile, 'w') as out:
        for line in f:
            if line.startswith('>'):
                out.write(line)
                continue

            seq = line.strip()
            if convert in ('L', 'lower'):
                seq = seq.lower()
            elif convert in ('U', 'upper'):
                seq = seq.upper()

            for i, base in enumerate(seq):
                pos = i + 1
                out.write(base)                     # write every base
                if pos % N == 0:                    # write a space every N bases
                    out.write(' ')
                if pos % M == 0:                    # write a line break every M bases
                    out.write('{}\n'.format(pos))
                if pos == len(seq):                 # handle the last line
                    last_len = pos % M
                    num_of_space = M - last_len + (M/N - last_len/N)
                    out.write('{}{}\n'.format(' '*num_of_space, pos))


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        prog='fasta_refine',
        version='%(prog)s {}'.format(__version__),
        description='\033\t\t[36mRefine a fasta file [{}]\033[0m'.format(__version__),
        epilog=(
            'examples:\n  %(prog)s -i test.fa -o out.refined.fa\n'
            '  %(prog)s -i test.fa.gz -N 20 -M 100 -c U\n\n'
            'contact: {} <{}>'
        ).format(__author__, __contact__),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument('-i', '--infile', help='The input fasta file (.gz also accepted)', required=True)
    parser.add_argument('-o', '--outfile', help='The output refined fasta file (.gz also accepted)')
    parser.add_argument('-N', help='The length of each short sequence [default=%(default)s]', default=10, type=int)
    parser.add_argument('-M', help='The max length of each row [default=%(default)s]', default=60, type=int)
    parser.add_argument(
        '-c', '--convert',
        metavar='Convert',
        help='Convert the base to lowercase or uppercase, choose from [%(choices)s] [default=%(default)s]',
        choices=['lower', 'L', 'upper', 'U', 'unchange', 'N'],
        default='lower'
    )

    args = vars(parser.parse_args())

    main()
