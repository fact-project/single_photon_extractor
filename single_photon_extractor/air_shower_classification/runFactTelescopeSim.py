#! /usr/bin/env python
"""
Usage: runFactTelescopeSim -i=PATH -m=PATH

Options:
    -h --help           Prints this help message.
    -i --in_dir=PATH    Path to write the output directroy.
    -m --mct_path=PATH  Path to mctracer executable for FACT simulation.

Generates photon-stream responses of FACT for all *.eventio files in directory.
"""
import docopt
import os
import glob
import subprocess

if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        in_dir = arguments['--in_dir']
        mct = arguments['--mct_path']

        input_run_paths = glob.glob(os.path.join(in_dir, '*.eventio'))

        for input_run_path in input_run_paths:

            output_basename = os.path.basename(input_run_path).split('.')[0]
            subprocess.call([
                mct,
                '-i', input_run_path,
                '-o', os.path.join(in_dir, output_basename+'.phs')])

    except docopt.DocoptExit as e:
        print(e)
