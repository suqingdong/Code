#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""getDoID

Usage:
    getDoID <diseaseName> [--data=<data>]
    getDoID (-h | --help)
    getDoID (-V | --version)

Options:
    <diseaseName>       The disease name of input.     
    --data=<data>       The DoID library file[default: /PUBLIC/software/HUMAN/project/DisGeNet.json].
    -h --help           Show help messages.
    -V --version        Show the version.

Contact:
    suqingdong <suqingdong@novogene.com>
"""

import sys
import json
import docopt

try:
    import fuzzywuzzy.process
    import colorama
except ImportError:
    sys.path.append('/ifs/TJPROJ3/DISEASE/share/Software/python/site-packages')
    import fuzzywuzzy.process
    import colorama


# colorama needs init before used
colorama.init()


def addFore(text, color=colorama.Fore.CYAN):
    return '%s%s%s' % (color, text, colorama.Fore.RESET)


def getDoID(diseaseName, data='/PUBLIC/software/HUMAN/project/DisGeNet.json'):
    
    print 'Use disease data: %s' % addFore(data, colorama.Fore.BLUE)

    with open(data) as f:
        diseaseDict = json.load(f)

    result = fuzzywuzzy.process.extractBests(diseaseName, diseaseDict.keys())
    disease, score = result[0]
    DoID = diseaseDict.get(disease)
    print 'Your input disease name: %s' % addFore(diseaseName)
    print 'Matched disease: %s[DoID:%s] (sorce:%s)' % (addFore(disease, colorama.Fore.YELLOW), addFore(DoID, colorama.Fore.RED), score)
    if int(score) < 90:
        print 'But the score is too low, maybe you should try again with another name'
    # elif int(score) < 100:
    if int(score) < 95:
	print 'Other matched results: \n\t%s\n\t%s\n\t%s\n\t%s ' % tuple(
	    map(
		lambda x: '{disease}[DoID:{doid}] (score:{score})'.format(
		    disease = addFore(x[0], colorama.Fore.YELLOW),
		    doid = addFore(diseaseDict.get(x[0]), colorama.Fore.RED),
		    score = x[1]
		), 
		result[1:6]
	    )
	) 

    return DoID


if __name__ == "__main__":

    arguments = docopt.docopt(__doc__, help=True, version='v1.0')

    diseaseName = arguments.get('<diseaseName>')
    data = arguments.get('--data')

    getDoID(diseaseName, data)

