import json
import numpy

arrival_time_resolutions = []

with open('./one_benchmark.jsonl', 'rt') as fin:
    for line in fin:
        arrival_time_resolutions.append(json.loads(line))


noise_amplitude_in_fact = 0.1
arrival_time_resolution = arrival_time_resolutions[3]
assert arrival_time_resolution['noise_amplitude'] == noise_amplitude_in_fact

residual_arrival_times = np.array(arrival_time_resolution['residual_times'])

start_time = -3e-9
end_time = 2e-9
num_bins = 200

bin_edges = np.linspace(start_time, end_time, num_bins)
counts, bin_edges = np.histogram(
    residual_arrival_times,
    bins=bin_edges
)


bin_width = (end_time - start_time)/num_bins
mean_time = np.mean(residual_arrival_times)
mean_bin = int(np.round((mean_time - start_time)/bin_width))


time_coincidence_radii = np.linspace(0, end_time-start_time, num_bins)
rate = np.zeros(num_bins)

for bin_radius, time_coincidence_radius in enumerate(time_coincidence_radii):
    start_bin = mean_bin - bin_radius
    end_bin = mean_bin + bin_radius + 1
    if start_bin < 0:
        start_bin = 0
    if end_bin > num_bins-1:
        end_bin = num_bins-1

    rate[bin_radius] = np.sum(counts[start_bin: end_bin])

rate /= np.sum(counts)


with open('./one_benchmark_true_positive_rate.json', 'wt') as fout:
    fout.write(json.dumps({
        'noise_amplitude': float(noise_amplitude_in_fact),
        'time_coincidence_radius':time_coincidence_radii.tolist(),
        'rate':rate.tolist()}))