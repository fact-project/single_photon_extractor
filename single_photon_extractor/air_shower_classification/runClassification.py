"""
Usage: runClassification -i=PATH -o=PATH [-t=NUM_PHOTONS] [-n=RATE] [-p]

Options:
    -h --help               Prints this help message.
    -i --in_dir=PATH        Input directory of FACT responses.
    -o --out_path=PATH      Output pandas DataFrame msg-pack path.
    -n --nsb_rate=RATE                      [default: 40e6] Rate of
                                            night-sky-background photons
                                            per pixel and second.
    -t --trigger_threshold=NUM_PHOTONS      [default: 21] Minimal number of
                                            air-shower photons.
    -p --plot               Make plots of all events.
"""
import docopt
import glob
import scoop
import single_photon_extractor.air_shower_classification.air_shower_classification as asc
import photon_stream as ps
import pandas as pd
import os

def num_photons_in_stream(raw_phs):
    return len(raw_phs) - ps.representations.NUMBER_OF_PIXELS

def classify_airshowers_in_run(job):
    result = {
        'run': int(job['run']),
        'event': int(job['event']),
        'reuse': int(job['reuse']),
        'trigger': 0,
    }

    if num_photons_in_stream(job['air_shower']) >= job['trigger_threshold']:
        job['nsb'] = ps.representations.list_of_lists_to_raw_phs(
            asc.generate_nsb(job['nsb_rate'])
        )
        job = asc.benchmark_on_single_event(event=job)

        result['trigger'] = 1
        result['delta_dc'] = float(job['delta_dc'])
        result['dist_dc'] = float(job['dist_dc'])
        result['delta_mp'] = float(job['delta_mp'])
        result['dist_mp'] = float(job['dist_mp'])
        result['mean_nsb_rate'] = float(job['mean_nsb_rate'])
        result['num_photons_true'] = int(job['image_true'].sum())
        result['num_photons_dc'] = int(job['image_dc'].sum())
        result['num_photons_mp'] = int(job['image_mp'].sum())

        if job['plot_path']:
            asc.plot_event(
                event=job,
                path=job['plot_path']
            )

    return result

if __name__ == '__main__':
    try:
        arguments = docopt.docopt(__doc__)
        in_dir = arguments['--in_dir']
        out_path = arguments['--out_path']
        nsb_rate = float(arguments['--nsb_rate'])
        trigger_threshold = float(arguments['--trigger_threshold'])
        make_plots = float(arguments['--plot'])
        input_run_paths = glob.glob(os.path.join(in_dir, '*.phs'))
        jobs = []
        for input_run_path in input_run_paths:
            run = ps.EventListReader(input_run_path)
            for evt in run:
                job = {
                    'run': evt.simulation_truth.run,
                    'event': evt.simulation_truth.event,
                    'reuse': evt.simulation_truth.reuse,
                    'air_shower': evt.photon_stream.raw,
                    'nsb_rate': nsb_rate,
                    'trigger_threshold': trigger_threshold,
                }
                if make_plots:
                    job['plot_path'] = '{:03d}_{:04d}_{:02d}'.format(
                        evt.simulation_truth.run,
                        evt.simulation_truth.event,
                        evt.simulation_truth.reuse,
                    )
                else:
                    job['plot_path'] = None

                jobs.append(job)

        results = list(scoop.futures.map(classify_airshowers_in_run, jobs))
        df_results = pd.DataFrame(results)
        df_results.to_msgpack(out_path)
    except docopt.DocoptExit as e:
        print(e)
