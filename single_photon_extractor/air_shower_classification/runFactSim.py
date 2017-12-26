"""
Usage: runFactSim -o=PATH [-n=NUMBER_RUNS] [-m=NUMBER]

Options:
    -h --help                             Prints this help message.
    -o --out_dir=PATH                     Path to write the output directroy.
    -n --num_runs=NUMBER    [default: 96] Number of runs.
    -m --num_shower=NUMBER  [default: 10] Number of runs.
    -p --prmpar=NUMBER      [default: 1]  CORSIKA primary particle ID.
"""
import docopt
import scoop
import os
import corsika_wrapper as cw
from collections import OrderedDict


def make_run(job):
    cw.corsika(
        steering_card=job['steering_card'],
        output_path=job['out_path'],
        save_stdout=True)
    return 0

if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        out_dir = arguments['--out_dir']
        num_shower = int(arguments['--num_shower'])
        num_runs = int(arguments['--num_runs'])
        prmpar = int(arguments['--prmpar'])

        os.makedirs(out_dir, exist_ok=True)
        jobs = []
        print('start')
        for r in range(num_runs):
            jobs.append({
                'run': r,
                'out_path': os.path.join(out_dir, str(r)+'.eventio')})
        print('make cards')
        for job in jobs:
            r = job['run']
            card = OrderedDict()
            card['RUNNR'] = [str(r)]
            card['EVTNR'] = [str(1)]
            card['NSHOW'] = [str(num_shower)]
            card['PRMPAR'] = [str(prmpar)]
            card['ESLOPE'] = ['-2.7']
            card['ERANGE'] = ['150 1500']
            card['THETAP'] = ['0. 2.5']
            card['PHIP'] = ['0. 360.']
            card['SEED'] = []
            card['SEED'].append(str(r)+' 0 0')
            # 1 for the hadron shower
            card['SEED'].append(str(r+1)+' 0 0')
            # 2 for the EGS4 part
            card['SEED'].append(str(r+2)+' 0 0')
            # 3 for the simulation of Cherenkov photons
            #   (only for CERENKOV option)
            card['SEED'].append(str(r+3)+' 0 0')
            # 4 for the random offset of Cherenkov telescope systems
            #   with respect of their nominal positions
            #   (only for IACT option)
            # 5 for the HERWIG routines in the NUPRIM option
            # 6 for the PARALLEL option
            # 7 for the CONEX option
            card['OBSLEV'] = ['2200.0e2']  # Roque de los Muchachos, La Palma
            card['FIXCHI'] = ['0.']
            card['MAGNET'] = ['1e-99 1e-99']
            card['ELMFLG'] = ['T T']
            card['MAXPRT'] = ['1']
            card['PAROUT'] = ['F F']
            card['TELESCOPE'] = ['0. 0. 0. 2.2e2']  # instrument radius
            card['ATMOSPHERE'] = ['8 T']  # MAGIC, Winter
            card['CWAVLG'] = ['250 700']
            card['CSCAT'] = ['1 75e2 0.0']
            card['CERQEF'] = ['F T F']  # pde, atmo, mirror
            card['CERSIZ'] = ['1']
            card['CERFIL'] = ['F']
            card['TSTART'] = ['T']
            card['EXIT'] = []
            job['steering_card'] = card
        print('ready for parallel')
        return_codes = list(scoop.futures.map(make_run, jobs))

    except docopt.DocoptExit as e:
        print(e)
