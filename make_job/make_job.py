#!/usr/bin/env python
# -*- coding=utf-8 -*-
"""make a job

Usage:
    make_job <configFile> [--outfile=<outfile>] [--logdir=<logdir>] [--queue=<queue>]

Options:
    <configFile>             The configure file
    --logdir=<logdir>        The log directory[default: ./log]
    --queue=<queue>          The queue was used[default: all.q,novo.q]
    --outfile=<outfile>      The output filename [default: out.job]

ConfigFile Example:
    #script memory  depend_scripts
    test1.sh 2G
    test2.sh 3G
    test3.sh 1G test1.sh,test2.sh
    test4.py 1M test3.sh

Contact:
    suqingdong <suqingdong@novogene.com>
"""
import os
import string
import docopt


jobTemplate = string.Template('''\
job_begin
  name ${jobname}
  memory ${memory}
  status ${status}
  sched_options ${scheds}
  cmd_begin
    ${cmd}
  cmd_end
job_end
\n''')


def write_job(jobname, memory, cmd, status='waiting', scheds='-V -cwd -q all.q -q novo.q'):

    return jobTemplate.safe_substitute(
        jobname=jobname,
        memory=memory,
        cmd=cmd,
        status=status,
        scheds=scheds
    )


def write_order(job1, job2):

    return 'order {} after {}\n'.format(job1, job2)


def main():

    arguments = docopt.docopt(__doc__)
    # print arguments

    configFile = arguments.get('<configFile>')
    logdir = arguments.get('--logdir')
    queue = arguments.get('--queue')
    outfile = arguments.get('--outfile')

    queue_list = [' -q ' + q for q in queue.split(',')]
    scheds = '-V -cwd' + ''.join(queue_list)
    # print scheds

    pwd = os.getcwd()

    if not os.path.exists(configFile):
        exit('File not exists: %s' % configFile)

    order_list = []
    with open(configFile) as f, open(outfile, 'w') as out:

        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            linelist = line.strip().split()
            script = linelist[0]
            memory = linelist[1]
            if script.endswith('.sh'):
                cmd = 'sh ' + os.path.join(pwd, script)
            elif script.endswith('.py'):
                cmd = 'python ' + os.path.join(pwd, script)
            # write each script job
            out.write(write_job(script, memory, cmd, scheds=scheds))

            if len(linelist) == 3:
                depend_scripts = linelist[2]
                for depend_script in depend_scripts.split(','):
                    order_list.append((script, depend_script))

        # write order list
        for order in order_list:
            out.write(write_order(*order))

        # write logdir
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        out.write('\nlog_dir %s\n' % logdir)

if __name__ == "__main__":

    main()
