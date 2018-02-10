#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import os
import sys


__author__ = 'suqingdong'
__contact__ = 'suqingdong@novogene.com'
__version__ = 'v1.0'


def safe_open(infile, mode='r'):

    try:
	if infile.endswith('.gz'):
	    import gzip
	    mode += 'b'
	    return gzip.open(infile, mode)
	return open(infile, mode)
    except IOError:
	print 'File not exists: %s!' % infile 


def main(infile, outfile=None, N=10, M=60):

    outfile = outfile or infile.rsplit('.', 1)[0]+'.refine.txt'
    N = int(N)
    M = int(M)

    with safe_open(infile) as f, safe_open(outfile,'w') as out:
        for line in f:
            if line.startswith('>'):
                out.write(line)
		continue
	    lower_seq = line.lower().strip()
	    for i,c in enumerate(lower_seq):
		out.write(c)
		if (i+1) % N == 0:
		    out.write(' ')
		if (i+1) % M == 0:
		    out.write('{}\n'.format((i+1)))
		if (i+1) == len(lower_seq):
		    last_len = (i+1) % M
		    space = M - last_len + (M/N - last_len/N)
		    out.write('{}{}\n'.format(' '*space, (i+1)))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print (
	    '\033[1;32mUsage: {} <infile> [outfile] [N] [M]\033[0m\n'
	    '\033[36;40mOptions:\n'
	    '\tinfile\tThe name of input fasta file (.gz also accepted) \n'
	    '\toutfile\tThe name of output refined fasta file (.gz also accepted) \n'
	    '\tN\tThe length of each short sequcence [default: 10]\n'
	    '\tM\tThe max length of eachline [default: 60]\033[0m\n'
	    'Contact: {} <{}>'
	).format(os.path.basename(__file__), __author__, __contact__)
        exit(1)

    main(*sys.argv[1:])

