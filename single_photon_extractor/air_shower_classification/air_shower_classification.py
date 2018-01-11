"""
Copyright Sebastrian A. Mueller, 2017

Compare air-shower and night-sky-background photon classification of first
density based clustering in the photon-stream, and second
two-level-time-neighbor cleaning in the main-pulses.
"""
from .. import extractor
import numpy as np
import photon_stream as ps
from photon_stream import plot as ps_plot
from sklearn.neighbors import NearestNeighbors
from matplotlib.patches import Circle
import os
from fact import plotting as fa_plot
import matplotlib.pyplot as plt
plt.rc('text', usetex=True)

# np.random.seed(0)
NUM_PIXEL = ps.GEOMETRY.x_angle.shape[0]
EXPOSURE_TIME = 50e-9
ROI = 300
F_SAMPLE = 2e9
PHOTON_EQUIVALENT_INTEGRAL = 24.2
IMAGE_SENSOR_RADIUS = 195


def eucledian_angle_between(image1, image2):
    return np.arccos(
            np.dot(image1, image2) /
            (
                np.linalg.norm(image1) *
                np.linalg.norm(image2)
            )
        )


def eucledian_distance_between(image1, image2):
    return np.linalg.norm(image1 - image2)


def estimate_neighbor_pixels():
    xy = np.array([ps.GEOMETRY.x_angle, ps.GEOMETRY.y_angle]).T
    neighbors = NearestNeighbors(
        n_neighbors=7,
        radius=np.deg2rad(0.15)).fit(xy)
    neighbors_distances, neighbors_chids = neighbors.kneighbors(xy)
    neighbors_chids = neighbors_chids[:, 1:]
    neighbors_distances = neighbors_distances[:, 1:]
    n_chids = []
    for chid in range(NUM_PIXEL):
        ns = []
        for nchid, d in enumerate(neighbors_distances[chid]):
            if d < np.deg2rad(0.125):
                ns.append(neighbors_chids[chid, nchid])
        n_chids.append(ns)
    return n_chids

neighbor_chids = estimate_neighbor_pixels()


def photon_stream_to_time_sereis(phs, electronic_white_noise=0.1, roi=300):
    number_pixel = len(phs)
    all_pixel_time_series = np.zeros(shape=(number_pixel, roi))
    for chid in range(len(phs)):
        all_pixel_time_series[chid, :] = extractor.white_noise(
            N=roi,
            sigma=electronic_white_noise)
        for arrival_slice in phs[chid]:
            extractor.add_first_to_second_at(
                f1=extractor.sipm_vs_t(
                    f_sample=F_SAMPLE,
                    N=ROI,
                    t_offset=0.0),
                f2=all_pixel_time_series[chid, :],
                injection_slices=[arrival_slice])
    return all_pixel_time_series


def find_main_pulse(time_series):
    # According to std fact-tools 'BasicExtraction.java'
    startSearchWindow = 35
    rangeSearchWindow = 90
    rangeHalfHeightWindow = 25

    max_position = np.argmax(
        time_series[
            startSearchWindow:
            startSearchWindow+rangeSearchWindow]) + startSearchWindow

    max_amplitude = time_series[max_position]
    half_max_amplitude = max_amplitude/2

    for half_max_position in np.flip(
        np.arange(max_position - rangeHalfHeightWindow, max_position), axis=0
    ):
        if time_series[half_max_position] < half_max_amplitude:
            break

    return {
        'max_position': max_position,
        'half_max_position': half_max_position,
        'max_amplitude': max_amplitude,
    }


def extract_photon_equivalent(time_series, half_max_position):
    # According to std fact-tools 'BasicExtraction.java'
    integrationWindow = 30
    return np.sum(
        time_series[half_max_position:half_max_position+integrationWindow])


def classify_air_shower_using_main_pulses(all_pixel_time_series):
    half_max_positions = np.zeros(
        all_pixel_time_series.shape[0],
        dtype=np.int64)
    for chid in range(NUM_PIXEL):
        half_max_positions[chid] = find_main_pulse(
            all_pixel_time_series[chid, :])['half_max_position']

    photon_equivalent = np.zeros(all_pixel_time_series.shape[0])
    for chid in range(NUM_PIXEL):
        photon_equivalent[chid] = extract_photon_equivalent(
            time_series=all_pixel_time_series[chid, :],
            half_max_position=half_max_positions[chid])
    photon_equivalent /= PHOTON_EQUIVALENT_INTEGRAL

    # Cleaning Settings
    twoLevelTimeNeighbor_coreThreshold = 5.5
    twoLevelTimeNeighbor_neighborThreshold = 3.0
    twoLevelTimeNeighbor_timeLimit = 10
    twoLevelTimeNeighbor_minNumberOfPixel = 2
    """
    TwoLevelTimeMedian. Identifies showerPixel in the image array.
    Cleaning in three Steps:
    1) Identify all Core Pixel (Photoncharge higher than corePixelThreshold)
    2) Remove all Single Core Pixel
    3) Add all Neighbor Pixel, whose Photoncharge is higher than
       neighborPixelThreshold
    """
    chids = np.arange(1440)

    core = photon_equivalent > twoLevelTimeNeighbor_coreThreshold
    for core_chid in chids[core]:
        is_alone = True
        for neighbor_chid in neighbor_chids[core_chid]:
            if core[neighbor_chid]:
                is_alone = False
        if is_alone:
            core[core_chid] = False

    shower = core.copy()

    def spread(chid, shower_mask, photon_equivalent):
        for neighbor_chid in neighbor_chids[chid]:
            if not shower_mask[neighbor_chid]:
                if (
                    photon_equivalent[neighbor_chid] >
                    twoLevelTimeNeighbor_neighborThreshold
                ):
                    shower[neighbor_chid] = True
                    spread(neighbor_chid, shower_mask, photon_equivalent)

    for core_chid in chids[shower]:
        spread(core_chid, shower, photon_equivalent)

    arrival_times = half_max_positions.copy()
    median_arrival_time = np.median(arrival_times[shower])

    arrival_time_is_close_to_median = (
        (arrival_times - median_arrival_time) < twoLevelTimeNeighbor_timeLimit
    )

    shower_time = shower & arrival_time_is_close_to_median

    return {
        'mask': shower_time,
        'photon_equivalent': photon_equivalent
    }


def classify_air_shower_using_density_clustering(all_pixel_time_series):
    phs_lol = []
    for chid in range(NUM_PIXEL):
        extracted_arrival_slices = extractor.extraction(
            sig_vs_t=all_pixel_time_series[chid, 20:245],
            puls_template=extractor.puls_template,
            subs_pulse_template=extractor.subs_pulse_template)
        extracted_arrival_slices += 20
        in_output_window = []
        for arr in extracted_arrival_slices:
            if arr >= 30 and arr < 130:
                in_output_window.append(arr)
        phs_lol.append(in_output_window)

    phs = ps.PhotonStream()
    phs.raw = ps.representations.list_of_lists_to_raw_phs(lol=phs_lol)
    phs.saturated_pixels = np.array([], dtype=np.uint16)

    reco_cluster = ps.PhotonStreamCluster(phs)
    """
    e = ps.Event()
    e.photon_stream = phs
    e.az = 0.
    e.zd = 0.0
    e.simulation_truth = ps.simulation_truth.SimulationTruth()
    e.simulation_truth.run = 0
    e.simulation_truth.event = 0
    e.simulation_truth.reuse = 0
    if (reco_cluster.labels>=0).sum() > 50:
        ps_plot.event(e, mask=reco_cluster.labels>=0)
    else:
        print('no reco cluster')
    """
    reco_air_shower_hist = ps.representations.raw_phs_to_image_sequence(
        ps.representations.masked_raw_phs(
            mask=reco_cluster.labels >= 0, raw_phs=phs.raw)
    )

    return reco_air_shower_hist


def add_ring_2_ax(x, y, r, ax, color='k', line_width=1.0):
    p = Circle((x, y), r, edgecolor=color, facecolor='none', lw=line_width)
    ax.add_patch(p)


# run = ps.EventListReader('20131103_167.phs.jsonl.gz')
# electronic_white_noise = 0.1
# nice_events = [
#     7, 12, 19, 20, 24, 34, 44, 47, 58, 61,
#     68, 69, 72, 78, 82, 84, 85, 125, 130]
# out_dir = 'air_shower_classification_demo'
# os.makedirs(out_dir, exist_ok=True)


def benchmark_on_single_event(
    event,
    electronic_white_noise=0.1,
    ROI=ROI,
):
    nsb_lol = ps.representations.raw_phs_to_list_of_lists(event['nsb'])
    nsb_time_series = photon_stream_to_time_sereis(
        phs=nsb_lol,
        electronic_white_noise=electronic_white_noise,
        roi=ROI)

    air_shower_lol = ps.representations.raw_phs_to_list_of_lists(
        event['air_shower'])
    air_shower_time_series = photon_stream_to_time_sereis(
        phs=air_shower_lol,
        electronic_white_noise=electronic_white_noise,
        roi=ROI)

    sum_time_series = nsb_time_series + air_shower_time_series

    mp = classify_air_shower_using_main_pulses(
        all_pixel_time_series=sum_time_series)
    mp_air_shower = np.zeros(NUM_PIXEL)
    mp_air_shower[mp['mask']] = mp['photon_equivalent'][mp['mask']]

    dc_air_shower_histogram = classify_air_shower_using_density_clustering(
        all_pixel_time_series=sum_time_series)
    dc_air_shower = np.sum(dc_air_shower_histogram, axis=0)

    true_air_shower = np.sum(
        ps.representations.raw_phs_to_image_sequence(event['air_shower']),
        axis=0
    )

    event['image_true'] = true_air_shower

    event['image_dc'] = dc_air_shower
    event['delta_dc'] = eucledian_angle_between(dc_air_shower, true_air_shower)
    event['dist_dc'] = eucledian_distance_between(
        dc_air_shower, true_air_shower)

    event['image_mp'] = mp_air_shower
    event['delta_mp'] = eucledian_angle_between(mp_air_shower, true_air_shower)
    event['dist_mp'] = eucledian_distance_between(
        mp_air_shower, true_air_shower)

    num_nsb_photons = event['nsb'].shape[0] - NUM_PIXEL
    num_nsb_per_pixel = num_nsb_photons/NUM_PIXEL
    event['mean_nsb_rate'] = num_nsb_per_pixel/EXPOSURE_TIME

    return event


def plot_event(
    event,
    path,
    pixel_edgecolor='#D0D0D0',
    cmap='Blues',
    dpi=256
):
    e = event
    print(
        'true_as', e['image_true'].sum(),
        'dc_as', e['image_dc'].sum(),
        'mp_as', e['image_mp'].sum(),
        'nsb rate MBq',  e['mean_nsb_rate']/1e6)

    fig_w = 9
    fig_h = 3
    im_w = fig_w/3
    dpi = 180
    fig = plt.figure(figsize=(fig_w, fig_h+0.6), dpi=dpi)
    ho = 0.25
    ax0 = fig.add_axes((0*im_w/fig_w,
                        (ho + 0)/fig_h,
                        im_w/fig_w,
                        fig_h/fig_h))

    ax1 = fig.add_axes((1*im_w/fig_w,
                        (ho + 0)/fig_h,
                        im_w/fig_w,
                        fig_h/fig_h))

    ax2 = fig.add_axes((2*im_w/fig_w,
                        (ho + 0)/fig_h,
                        im_w/fig_w,
                        fig_h/fig_h))

    add_ring_2_ax(x=0, y=0, r=IMAGE_SENSOR_RADIUS, ax=ax0)
    add_ring_2_ax(x=0, y=0, r=IMAGE_SENSOR_RADIUS, ax=ax1)
    add_ring_2_ax(x=0, y=0, r=IMAGE_SENSOR_RADIUS, ax=ax2)
    fa_plot.camera(
        e['image_dc'],
        cmap=cmap,
        edgecolor=pixel_edgecolor,
        ax=ax0)
    fa_plot.camera(
        e['image_true'],
        cmap=cmap,
        edgecolor=pixel_edgecolor,
        ax=ax1)
    fa_plot.camera(e['image_mp'],
        cmap=cmap,
        edgecolor=pixel_edgecolor,
        ax=ax2)

    #fig.suptitle(
    #    'NSB ' +
    #    '{:.1f}M photons/(pixel s)'.format(e['mean_nsb_rate']/1e6))

    #ax0.set_title('density-clustering\nin photon-stream', fontsize=16)
    ax0.set_xlabel(
        '{:d} photons\n'.format(e['image_dc'].sum()) +
        r'$\delta=${:.1f}$^\circ$, '.format(np.rad2deg(e['delta_dc'])) +
        r'$D=${:.1f} photons'.format(e['dist_dc']),
        fontsize=16
    )

    #ax1.set_title('Truth', fontsize=16)
    ax1.set_xlabel(
        '{:d} photons'.format(e['image_true'].sum()),
        fontsize=16)

    #ax2.set_title('two-level-time-neighbor\non main-pulses', fontsize=16)
    ax2.set_xlabel(
        '{:.1f} photon-equivalents\n'.format(e['image_mp'].sum()) +
        r'$\delta=${:.1f}$^\circ$, '.format(np.rad2deg(e['delta_mp'])) +
        r'$D=${:.1f} p.e.'.format(e['dist_mp']),
        fontsize=16
    )

    for side in ['bottom', 'right', 'top', 'left']:
        ax0.spines[side].set_visible(False)
        ax1.spines[side].set_visible(False)
        ax2.spines[side].set_visible(False)

    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)

    plt.setp(ax0.get_yticklabels(), visible=False)
    plt.setp(ax1.get_yticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)

    ax0.get_xaxis().set_ticks([])
    ax1.get_xaxis().set_ticks([])
    ax2.get_xaxis().set_ticks([])

    ax0.get_yaxis().set_ticks([])
    ax1.get_yaxis().set_ticks([])
    ax2.get_yaxis().set_ticks([])
    plt.savefig(path, dpi=dpi)
    plt.close('all')


def generate_nsb(nsb_rate_per_pixel):
    phs = []
    for chid in range(NUM_PIXEL):
        arrival_times = extractor.poisson_arrival_times(EXPOSURE_TIME, nsb_rate_per_pixel)
        arrival_slices = (
            np.floor(arrival_times*F_SAMPLE) +
            ps.io.magic_constants.NUMBER_OF_TIME_SLICES_OFFSET_AFTER_BEGIN_OF_ROI
        ).astype(np.uint64)
        phs.append(arrival_slices)
    return phs


import glob
import os
import json

FACT_TRIGGER_THRESHOLD = 21

def run_benchmark(
    air_shower_dir,
    nsb_rate=40e6,
    electronic_white_noise=0.1
):
    paths = glob.glob(os.path.join(air_shower_dir, '*.phs'))
    events = []

    fout = open(os.path.join(air_shower_dir, 'benchmark.jsonl'), 'wt')

    for path in paths:
        run = ps.EventListReader(path)
        for evt in run:
            # if len(events) > 100:
            #   break
            if evt.photon_stream.number_photons >= FACT_TRIGGER_THRESHOLD:
                event = {
                    'run': evt.simulation_truth.run,
                    'event': evt.simulation_truth.event,
                    'reuse': evt.simulation_truth.reuse,
                    'air_shower': evt.photon_stream.raw,
                    'nsb': ps.representations.list_of_lists_to_raw_phs(
                        generate_nsb(nsb_rate)
                    )
                }
                print(event['run'], event['event'], event['reuse'])
                event = benchmark_on_single_event(
                    event=event,
                    electronic_white_noise=electronic_white_noise)

                fout.write(json.dumps(
                    {
                        'run': int(event['run']),
                        'event': int(event['event']),
                        'reuse': int(event['reuse']),
                        'delta_dc': float(event['delta_dc']),
                        'dist_dc': float(event['dist_dc']),
                        'delta_mp': float(event['delta_mp']),
                        'dist_mp': float(event['dist_mp']),
                        'mean_nsb_rate': float(event['mean_nsb_rate']),
                        'num_photons_true': int(event['image_true'].sum()),
                        'num_photons_dc': int(event['image_dc'].sum()),
                        'num_photons_mp': int(event['image_mp'].sum()),
                    }
                )+"\n")
                events.append(event)


    fout.close()
    return events


def read_in_jsonl(path):
    l = []
    with open(path, 'rt') as fin:
        while fin:
            line = fin.readline()
            if len(line) > 1:
                l.append(json.loads(line))
            else:
                break
    return l