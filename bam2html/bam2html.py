#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""
\x1b[1;32m\n\t\tGenerate position highlighted HTML file by `samtools tview`\x1b[0m

\x1b[31mUsage:
    bam2html <bam> <positions>...
        [--ref=<ref>] [--suffix=<suffix>] [--columns=<columns>]         
        [--color=<color>] [--background=<bg>]
        [--font-size=<fs>] [--bold=<T,F>]
        [--outdir=<outdir>]

\x1b[36mOptions:
    <bam>                    The bam file
    <positions>              The position(s) to highlight(format: chr:pos [chr-pos chr_pos ...])
    --ref=<ref>              The reference genome[default: /PUBLIC/database/HUMAN/genome/Human/human_g1k_v37_decoy.fasta]
    --suffix=<suffix>        The suffix of out file name(outfile eg: suffix_chr_pos.highlight.html)
    --columns=<columns>      The columns of window[default: 80]
    --color=<color>          The highlight color[default: red]
    --background=<bg>        The highlight background color[default: yellow]
    --font-size=<fs>         The font size[default: 13]
    --bold=<T,F>             Whether the highlighted base is shown as bold[default: F]
    --outdir=<outdir>        The output directory[default: .]

\x1b[1;34mExamples:
    bam2html test.final.bam 1:1000000 3:123456 
    bam2html test.final.bam 1:1000000 3:123456 --columns 200 --color green --background grey

\x1b[1;37mContact:
    suqingdong <suqingdong@novogene.com>

"""
import os
import re
import sys
import docopt

try:
    import colorama
except ImportError:
    sys.path.append('/ifs/TJPROJ3/DISEASE/share/Software/python/site-packages')
    import colorama


# colorama needs init before used
colorama.init()


def add_class(seq, index):

    highlight_base = "<i class='highlight'>{}</i>".format(seq[index])
    new_seq = seq[:index] + highlight_base + seq[index + 1:]

    return new_seq


def highlight_span(span, highlight_index):

    linelist = re.split(r'(<.*?>)', span)
    # print linelist

    total_len = 0
    for idx, each in enumerate(linelist):
        if not re.match(r'^<.*?>$', each):
            total_len += len(each)
            if total_len > highlight_index:
                true_index = highlight_index - (total_len - len(each))
                linelist[idx] = add_class(linelist[idx], true_index)
                # print linelist
                break

    return ''.join(linelist)


def main():

    bamfile = arguments.get('<bam>')
    positions = arguments.get('<positions>')
    reference = arguments.get('--ref')
    suffix = arguments.get('--suffix')
    columns = int(arguments.get('--columns'))
    color = arguments.get('--color')
    background = arguments.get('--background')
    bold = arguments.get('--bold')
    fontsize = arguments.get('--font-size')
    outdir = arguments.get('--outdir')

    fontweight = ['bold' if bold == 'T' else 'none'][0]
    highlight_css = '.highlight {color:%s;background:%s;font-weight:%s;font-style:normal;}\n' % (color, background, fontweight)
    highlight_css += '.tviewpre {font-size:%s}\n' % fontsize

    bamindex = bamfile + '.bai'
    if not os.path.exists(bamindex):
        print 'Index file not exits for: %s\nCreating index...' % bamfile
        cmd = "samtools index '%s'" % bamfile
        assert not os.system(cmd)
        print 'Index created successfully!'

    suffix = suffix or os.path.basename(bamfile).split('.')[0]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for position in positions:
        # chrom, pos = position.split(':')
        chrom, pos = re.split(r':|_|-', position)
        cmd = 'export COLUMNS={columns} && samtools tview -d H -p {chrom}:{start_pos} {bam} {ref} > {suffix}_{chrom}_{pos}.html'.format(
            columns=columns,
            chrom=chrom,
            start_pos=int(pos) - columns / 2,
            pos=pos,
            bam=bamfile,
            ref=reference,
            suffix=suffix
        )
        # print cmd
        assert not os.system(cmd)

        infile = '{}_{}_{}.html'.format(suffix, chrom, pos)
        outfile = '{}_{}_{}.highlight.html'.format(suffix, chrom, pos)
        outfile = os.path.join(outdir, outfile)

        with open(infile) as f, open(outfile, 'w') as out:
            for line in f:
                if not line.startswith('</style>'):
                    out.write(line)
                    continue
                out.write(highlight_css)

                prefix_html = re.findall(r'(</style>.*?)<span', line)[0]
                suffix_html = '</pre></div></body></html>'

                spans = re.findall(r'(<span.*?)<br/>', line)

                position_line = spans[0] + '<br/>'

                first_position = re.findall(r"<div class='tviewtitle'>.*?:(\d+?)</div>", prefix_html)[0]         # according to the .tviewtitle

                last_span = re.findall(r'<br/>(<span[^(br)]*?</span>)</pre>', line)[-1]  # the last span has no <br/>

                # new_line == prefix_html + position_line + spans_line + suffix_html
                new_line = prefix_html + position_line

                for span in spans[1:] + [last_span]:

                    highlight_index = int(pos) - int(first_position)
                    if highlight_index not in range(0, columns):                 # validate the position
                        msg = 'Error Position: {}\nShould be in range {} ~ {}'.format(pos, first_position, int(first_position) + columns - 1)
                        exit(msg)
                    span = highlight_span(span, highlight_index)            # highlight one or more position for each span

                    new_line += span + '<br/>'

                new_line = new_line[:-5]                                        # remove the last span's <br/>
                new_line += suffix_html

                out.write(new_line)
        print 'Successfully generate the highlighted file: %s' % outfile


if __name__ == "__main__":

    arguments = docopt.docopt(__doc__)
    # print arguments; exit()

    main()
