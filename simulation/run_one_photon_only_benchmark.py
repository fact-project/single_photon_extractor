from sandbox import *

SEED = 0
ROI = 300
F_SAMPLE = 2e9
SLICE_DURATION = 1/F_SAMPLE
INJECTION_SLICE = 100

bins = np.linspace(-3, 2, 153)

plt.figure(figsize=(8,2*3.43))

for noise_amplitude in np.array([0.0, 0.1, 0.2]):

    n_thrown = int(1e5)
    n_detected = 0
    residual_times = []

    for sub_offset in np.random.uniform(low=0.0, high=SLICE_DURATION, size=n_thrown):
        true_arrival_time = INJECTION_SLICE/F_SAMPLE + sub_offset


        one_gapd_pulse = sipm_vs_t(
            F_SAMPLE,
            N=ROI*5,
            t_offset=sub_offset
        )

        time_series = np.zeros(ROI)
        electronics_noise = white_noise(ROI, noise_amplitude)
        add_first_to_second_at(one_gapd_pulse, time_series, [INJECTION_SLICE])
        add_first_to_second_at(electronics_noise, time_series, [0])


        extracted_arrival_slice = extraction(
            sig_vs_t=time_series,
            puls_template=puls_template,
            subs_pulse_template=subs_pulse_template,
            return_intermediate_sig_vs_t=False
        )

        if len(extracted_arrival_slice) > 0:
            n_detected += 1
            arrival_slice = extracted_arrival_slice[0]
            extracted_arrival_time = arrival_slice/F_SAMPLE
            residual_times.append(
                true_arrival_time - extracted_arrival_time
            )

    residual_times = np.array(residual_times)
    residual_times *= 1e9 # in ns

    with open('one_benchmark.txt', 'at') as fout:
        fout.write('noise_amplitude')
        fout.write(str(noise_amplitude))
        fout.write(', ')

        fout.write('mean')
        fout.write(str(np.mean(residual_times)))
        fout.write(', ')

        fout.write('std')
        fout.write(str(np.std(residual_times)))
        fout.write('\n')

    counts, bin_edges = np.histogram(
        residual_times,
        bins=bins
    )

    counts = counts*(n_detected/n_thrown)/counts.sum()

    plt.step(
        bin_edges[:-1],
        counts,
        #color='C0',
        label=str(noise_amplitude),
    )

plt.ylabel('rate/1')
plt.xlabel('true minus extracted arrival time/ns')
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