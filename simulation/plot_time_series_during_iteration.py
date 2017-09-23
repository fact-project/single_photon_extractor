from sandbox import *

seed = 5

np.random.seed(seed)
sig_vs_t , mc_truth = fact_sig_vs_t(cfg)

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
mi = np.min(intermediate_sig_vs_t[0])
ma = np.max(intermediate_sig_vs_t[0])

for n in range(N):
    if n > 0: 
        axn = plt.subplot(N,1,n+1, sharex=axn) 
    else: 
        axn = plt.subplot(N,1,n+1)
    times = 1e9*time_slices(cfg['f_sample'], intermediate_sig_vs_t[n].shape[0])
    axn.step(times, intermediate_sig_vs_t[n])

    for true_arrival in true_arrivals:
        axn.plot([true_arrival/2, true_arrival/2],[mi, ma],'g', alpha=0.3)

    if n < N-1: 
        axn.plot([arrival_slices[n]/2, arrival_slices[n]/2],[mi, ma],'r')

    axn.set_ylim([mi,ma])
    axn.set_xlabel('t/ns')
    if n == 0: axn.set_ylabel('A/1')
plt.subplots_adjust(hspace=.0)

plt.show()