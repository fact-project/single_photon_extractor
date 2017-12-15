from sandbox import *
import json

np.random.seed = 0
ROI = 300
F_SAMPLE = 2e9
SLICE_DURATION = 1/F_SAMPLE
INJECTION_SLICE = 100

n_thrown = int(1e5)

noises = [
    {'noise_amplitude': 0.0, 'color': 'lightgrey', 'linestyle': '-'},
    {'noise_amplitude': 0.05, 'color': 'lightgrey', 'linestyle': ':'},
    {'noise_amplitude': 0.2, 'color': 'lightgrey', 'linestyle': '--'},
    {'noise_amplitude': 0.1, 'color': 'k', 'linestyle': '-'},
]

for n in noises:

    n_detected = 0
    residual_times = []

    for sub_offset in np.random.uniform(
        low=0.0,
        high=SLICE_DURATION,
        size=n_thrown
    ):
        true_arrival_time = INJECTION_SLICE/F_SAMPLE + sub_offset

        one_gapd_pulse = sipm_vs_t(
            F_SAMPLE,
            N=ROI*5,
            t_offset=sub_offset
        )

        time_series = np.zeros(ROI)
        electronics_noise = white_noise(ROI, n['noise_amplitude'])

        add_first_to_second_at(one_gapd_pulse, time_series, [INJECTION_SLICE])
        add_first_to_second_at(electronics_noise, time_series, [0])

        extracted_arrival_slice = extraction(
            sig_vs_t=time_series,
            puls_template=puls_template,
            subs_pulse_template=subs_pulse_template,
            return_intermediate_sig_vs_t=False
        )

        n_detected += len(extracted_arrival_slice)
        if len(extracted_arrival_slice) > 0:
            arrival_slice = extracted_arrival_slice[0]
            extracted_arrival_time = arrival_slice/F_SAMPLE
            residual_times.append(
                true_arrival_time - extracted_arrival_time
            )

    n['n_thrown'] = n_thrown
    n['n_detected'] = n_detected
    n['residual_times'] = residual_times
    n['mean'] = np.mean(np.array(residual_times))
    n['std'] = np.std(np.array(residual_times))

with open('one_benchmark.jsonl', 'wt') as fout:
    for n in noises:
        fout.write(json.dumps(n))
        fout.write('\n')


bin_edges = np.linspace(-3, 2, 200)
plt.figure(figsize=(8, 2*3.43))

for n in noises:

    residual_times_ns = np.array(n['residual_times'])*1e9
    counts, bin_edges = np.histogram(
        residual_times_ns,
        bins=bin_edges
    )

    normalized_counts = counts*(n['n_detected']/n['n_thrown'])/counts.sum()

    plt.step(
        bin_edges[:-1],
        normalized_counts,
        color=n['color'],
        label=str(n['noise_amplitude']),
        linestyle=n['linestyle']
    )

plt.ylabel('rate/1')
plt.xlabel('true arrival time - extracted arrival time/ns')
plt.legend(
    bbox_to_anchor=(0., 1.02, 1., .102),
    loc=3,
    ncol=2,
    mode="expand", borderaxespad=0.
)
plt.savefig(
    'one_benchmark.png',
    dpi=256,
    bbox_inches='tight',
    pad_inches=0
)
