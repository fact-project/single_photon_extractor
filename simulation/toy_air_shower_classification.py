from sandbox import *
import photon_stream as ps
from photon_stream import plot as ps_plot
from sklearn.neighbors import NearestNeighbors
from matplotlib.patches import Circle


NUM_PIXEL = ps.GEOMETRY.x_angle.shape[0]

def add_ring_2_ax(x, y, r, ax, color='k', line_width=1.0):
    p = Circle((x, y), r, edgecolor=color, facecolor='none', lw=line_width)
    ax.add_patch(p)


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
        all_pixel_time_series[chid, :] = white_noise(N=roi, sigma=electronic_white_noise)
        for arrival_slice in phs[chid]:
            add_first_to_second_at(
                f1=sipm_vs_t(
                    f_sample=f_sample,
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


run = ps.EventListReader('20131103_167.phs.jsonl.gz')
electronic_white_noise = 0.1

ROI = 300
f_sample = 2e9
PHOTON_EQUIVALENT_INTEGRAL = 24.2


def classify_air_shower_using_main_pulses(
    nsb_time_series,
    air_shower_time_series,
):
    sum_time_series = nsb_time_series + air_shower_time_series

    half_max_positions = np.zeros(sum_time_series.shape[0], dtype=np.int64)
    for chid in range(NUM_PIXEL):
        half_max_positions[chid] = find_main_pulse(
            sum_time_series[chid, :])['half_max_position']

    photon_equivalent = np.zeros(sum_time_series.shape[0])
    for chid in range(NUM_PIXEL):
        photon_equivalent[chid] = extract_photon_equivalent(
            time_series=air_shower_time_series[chid, :],
            half_max_position=half_max_positions[chid])
    photon_equivalent /= PHOTON_EQUIVALENT_INTEGRAL

    # Cleaning Settings
    twoLevelTimeNeighbor_coreThreshold=5.5
    twoLevelTimeNeighbor_neighborThreshold=3.0
    #twoLevelTimeNeighbor_timeLimit=10
    twoLevelTimeNeighbor_minNumberOfPixel=2
    """
     *TwoLevelTimeMedian. Identifies showerPixel in the image array.
     *   Cleaning in three Steps:
     *  1) Identify all Core Pixel (Photoncharge higher than corePixelThreshold)
     *  2) Remove all Single Core Pixel
     *  3) Add all Neighbor Pixel, whose Photoncharge is higher than neighborPixelThreshold
    """
    chids = np.arange(1440)

    core = photon_equivalent > twoLevelTimeNeighbor_coreThreshold

    print('core: ', core.sum())
    for core_chid in chids[core]:
        is_alone = True
        for neighbor_chid in neighbor_chids[core_chid]:
            if core[neighbor_chid]:
                is_alone = False
        if is_alone:
            core[core_chid] = False

    print('core cluster: ', core.sum())

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

    return {
        'air_showr_mask': shower,
        'photon_equivalent': photon_equivalent
    }


def classify_air_shower_using_density_clustering(
    nsb_time_series,
    air_shower_time_series,
):
    sum_time_series = nsb_time_series + air_shower_time_series

    phs_lol = []
    for chid in range(NUM_PIXEL):
        extracted_arrival_slices = extraction(
            sig_vs_t=sum_time_series[chid, 20:245],
            puls_template=puls_template,
            subs_pulse_template=subs_pulse_template)
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
            mask=reco_cluster.labels>=0, raw_phs=phs.raw)
    )
    reco_nsb_hist = ps.representations.raw_phs_to_image_sequence(
        ps.representations.masked_raw_phs(
            mask=reco_cluster.labels==-1, raw_phs=phs.raw)
    )

    return reco_air_shower_hist, reco_nsb_hist

nice_events = [7, 12, 19, 20, 24, 34, 44, 47, 58, 61, 68, 69, 72, 78, 82, 84, 85, 125, 130]

for event in run:
    clusters = ps.PhotonStreamCluster(event.photon_stream)
    """
    if (clusters.labels>=0).sum() > 50:
        ps_plot.event(event, mask=clusters.labels>=0)
    else:
        print('no cluster')
    """

    raw_nsb = ps.representations.masked_raw_phs(
        mask=(clusters.labels == -1),
        raw_phs=event.photon_stream.raw)

    raw_air_showr = ps.representations.masked_raw_phs(
        mask=(clusters.labels >= 0),
        raw_phs=event.photon_stream.raw)

    nsb = ps.representations.raw_phs_to_list_of_lists(raw_phs=raw_nsb)
    air_showr = ps.representations.raw_phs_to_list_of_lists(raw_phs=raw_air_showr)

    nsb_time_series = photon_stream_to_time_sereis(
        phs=nsb,
        electronic_white_noise=electronic_white_noise,
        roi=ROI)

    air_shower_time_series = photon_stream_to_time_sereis(
        phs=air_showr,
        electronic_white_noise=electronic_white_noise,
        roi=ROI)


    mp = classify_air_shower_using_main_pulses(
        nsb_time_series=nsb_time_series,
        air_shower_time_series=air_shower_time_series)

    reco_as_hist, reco_nsb_hist = classify_air_shower_using_density_clustering(
        nsb_time_series=nsb_time_series,
        air_shower_time_series=air_shower_time_series)

    mp_as = np.zeros(NUM_PIXEL)
    mp_as[mp['air_showr_mask']] = mp['photon_equivalent'][mp['air_showr_mask']]


    dc_as = np.zeros(NUM_PIXEL)
    dc_as = np.sum(reco_as_hist, axis=0)

    true_as = np.sum(
        ps.representations.raw_phs_to_image_sequence(raw_air_showr),
        axis=0)

    if dc_as.sum() > 25:
        print(event.observation_info.event ,'dc_as', dc_as.sum(), 'mp_as', mp_as.sum())
        R = 195
        edgecolor = '#D0D0D0'
        from fact import plotting as fa_plot
        # Three subplots, unpack the axes array immediately
        fig_w=9
        fig_h=3
        im_w = fig_w/3
        dpi=180
        fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)

        ax0 = fig.add_axes((0*im_w/fig_w,
                            0/fig_h,
                            im_w/fig_w,
                            fig_h/fig_h))

        ax1 = fig.add_axes((1*im_w/fig_w,
                            0/fig_h,
                            im_w/fig_w,
                            fig_h/fig_h))

        ax2 = fig.add_axes((2*im_w/fig_w,
                            0/fig_h,
                            im_w/fig_w,
                            fig_h/fig_h))

        add_ring_2_ax(x=0, y=0, r=R, ax=ax0)
        add_ring_2_ax(x=0, y=0, r=R, ax=ax1)
        add_ring_2_ax(x=0, y=0, r=R, ax=ax2)
        fa_plot.camera(dc_as, cmap='Blues', edgecolor=edgecolor, ax=ax0)
        fa_plot.camera(true_as, cmap='Blues', edgecolor=edgecolor, ax=ax1)
        fa_plot.camera(mp_as, cmap='Blues', edgecolor=edgecolor, ax=ax2)

        ax0.set_xlabel('DBSCAN')
        ax1.set_xlabel('true')
        ax2.set_xlabel('two stage')

        for side in ['bottom','right','top','left']:
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
        plt.show()