from single_photon_extractor.extractor import *
import matplotlib.patches as patches

plt.figure(figsize=(8, 3.43))
axn = plt.subplot(1, 1, 1)
times = 1e9*time_slices(cfg['f_sample'], subs_pulse_template.shape[0])
axn.step(times, - subs_pulse_template, 'C0')
axn.plot([-10, 0], [0, 0], 'C0')
axn.set_xlabel('t/ns')
axn.set_ylabel('A/1')
axn.set_ylim([-.22, 1.1])
axn.set_xlim([-10, 150])

axn.add_patch(
    patches.Rectangle(
        (0.0, 0.0),   # (x,y)
        10,          # width
        1,          # height
        edgecolor="none",
        facecolor="grey",
        alpha=0.45,
    )
)

plt.savefig(
    'template_pulses.png',
    dpi=256,
    bbox_inches='tight',
    pad_inches=0
)

plt.figure(figsize=(8, 3.43))
axn = plt.subplot(1, 1, 1)
pulse = - subs_pulse_template
A = white_noise(20 + pulse.shape[0], cfg['std_dev_el_noise'])
A[20:] += pulse
times = 1e9*time_slices(cfg['f_sample'], pulse.shape[0] + 20) - 10
axn.step(times, A, 'grey')

times = 1e9*time_slices(cfg['f_sample'], subs_pulse_template.shape[0])
axn.step(times, - subs_pulse_template, 'C0')
axn.plot([-10, 0], [0, 0], 'C0')

axn.set_xlabel('t/ns')
axn.set_ylabel('A/1')
axn.set_ylim([-.22, 1.1])
axn.set_xlim([-10, 150])
plt.savefig(
    'template_pulses_with_noise.png',
    dpi=256,
    bbox_inches='tight',
    pad_inches=0
)
