from single_photon_extractor.extractor import *

for seed in [2, 4, 5, 8, 13, 30, 33, 35, 46]:

    np.random.seed(seed)
    sig_vs_t, mc_truth = fact_sig_vs_t(cfg)

    arrival_slices, intermediate_sig_vs_t = extraction(
        sig_vs_t=sig_vs_t,
        puls_template=puls_template,
        subs_pulse_template=subs_pulse_template,
        return_intermediate_sig_vs_t=True
    )

    N = len(intermediate_sig_vs_t)
    true_arrivals = mc_truth['pulse_injection_slices']
    true_arrivals = true_arrivals[true_arrivals > 0]

    assert N > 0
    assert N == len(arrival_slices) + 1

    mi = np.min([np.min(A) for A in intermediate_sig_vs_t])
    ma = np.max([np.max(A) for A in intermediate_sig_vs_t])

    # Combined figure
    # ---------------
    plt.figure(figsize=(8, N*3.43/3))

    for n in range(N):
        if n > 0:
            axn = plt.subplot(N, 1, n+1, sharex=axn)
        else:
            axn = plt.subplot(N, 1, n+1)
        times = 1e9*time_slices(
            cfg['f_sample'],
            intermediate_sig_vs_t[n].shape[0])
        axn.step(times, intermediate_sig_vs_t[n])

        for true_arrival in true_arrivals:
            axn.plot([
                true_arrival/2, true_arrival/2],
                [mi, ma],
                'g',
                alpha=0.3)

        if n < N-1:
            axn.plot(
                [arrival_slices[n]/2, arrival_slices[n]/2],
                [mi, ma],
                'r')

        axn.set_ylim([mi, ma])
        axn.set_xlabel('t/ns')
        if n == 0:
            axn.set_ylabel('A/1')
    plt.subplots_adjust(hspace=.0)
    plt.savefig(
        'example_extraction_seed_'+str(seed)+'.png',
        dpi=256,
        bbox_inches='tight',
        pad_inches=0
    )

    # Separate figures
    # ----------------

    for n in range(N):
        plt.figure(figsize=(8, 3.43/3))
        ax = plt.gca()
        times = 1e9*time_slices(
            cfg['f_sample'],
            intermediate_sig_vs_t[n].shape[0])
        ax.step(times, intermediate_sig_vs_t[n])

        for true_arrival in true_arrivals:
            ax.plot(
                [true_arrival/2, true_arrival/2],
                [mi, ma],
                'g',
                alpha=0.3)

        if n < N-1:
            ax.plot(
                [arrival_slices[n]/2, arrival_slices[n]/2],
                [mi, ma],
                'r')

        ax.set_ylim([mi, ma])
        ax.set_xlabel('t/ns')
        ax.set_ylabel('A/1')

        plt.savefig(
            'example_extraction_seed_'+str(seed)+'_'+str(n)+'.png',
            dpi=256,
            bbox_inches='tight',
            pad_inches=0
        )
