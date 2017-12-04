from sandbox import *

#-------------------------------------------------------------------------------
class Bench(object):
    def __init__(self):
        self.truePositive = 0
        self.falsePositive = 0
        self.trueNegative = 0
        self.falseNegative = 0

    def truePositiveRate(self):
        return self.truePositive/(self.truePositive + self.falseNegative)

    def falseNegativeRate(self):
        return self.falsePositive/(self.truePositive + self.falseNegative)

    def delta_truePositiveRate(self):
        tp = self.truePositive
        fn = self.falseNegative

        D_tp = np.sqrt(tp)
        D_fn = np.sqrt(fn)

        dS_dtp = fn/(tp + fn)**2
        dS_dfn =-tp/(tp + fn)**2
        return np.sqrt(
            (dS_dtp**2)*(D_tp**2) + 
            (dS_dfn**2)*(D_fn**2)
        )

    def delta_falseNegativeRate(self):
        fp = self.falsePositive
        tp = self.truePositive
        fn = self.falseNegative

        D_fp = np.sqrt(fp)
        D_tp = np.sqrt(tp)
        D_fn = np.sqrt(fn)

        dM_dfp = 1/(tp + fn)
        dM_dtp = -fp/(tp+fn)**2
        dM_dfn = -fp/(tp+fn)**2
        return np.sqrt(
            (dM_dfp**2)*(D_fp**2) + 
            (dM_dtp**2)*(D_tp**2) + 
            (dM_dfn**2)*(D_fn**2)
        )

    def __str__(self):
        out=''
        out+='correct positive rate '+str(self.truePositiveRate())
        out+='false negative rate '+str(self.falseNegativeRate())
        return out

#-------------------------------------------------------------------------------
def benchmark(arrivalsExtracted, arrivalsTruth, windowRadius=10):

    arrivalsExtracted = np.sort(arrivalsExtracted)
    arrivalsTruth = np.sort(arrivalsTruth)

    def find_nearest(array, value):
        return (np.abs(array-value)).argmin()

    bench = Bench()

    arrivalsExtractedRemaining = arrivalsExtracted.copy()

    for arrivalTruth in arrivalsTruth:

        if arrivalsExtractedRemaining.shape[0] == 0:
            bench.falseNegative += 1
        else:
            match = find_nearest(arrivalsExtractedRemaining, arrivalTruth)
            distance = np.abs(arrivalsExtractedRemaining[match] - arrivalTruth)
            if distance <= windowRadius:
                arrivalsExtractedRemaining = np.delete(arrivalsExtractedRemaining, match) 
                bench.truePositive += 1
            else:
                bench.falseNegative += 1

    bench.falsePositive += arrivalsExtractedRemaining.shape[0]

    return bench

#-------------------------------------------------------------------------------
maxWindowRadius = 10
windowRadii = np.linspace(0,maxWindowRadius,maxWindowRadius, endpoint=False)
truePositiveRate = np.zeros(maxWindowRadius)
falseNegativeRate = np.zeros(maxWindowRadius)
delta_truePositiveRate = np.zeros(maxWindowRadius)
delta_falseNegativeRate = np.zeros(maxWindowRadius)

for s, windowRadius in enumerate(windowRadii):
    
    bench = Bench()
    for i in tqdm(range(1440)):
        sig_vs_t , mc_truth = fact_sig_vs_t(cfg)

        arrivalSlicesTruth = mc_truth['pulse_injection_slices'][mc_truth['pulse_injection_slices']>=0]
        arrivalSlices = extraction(sig_vs_t, puls_template, subs_pulse_template)

        arrivalSlices = np.sort(arrivalSlices)
        arrivalSlicesTruth = np.sort(arrivalSlicesTruth)

        arrivalSlices += 2

        arrivalSlices=arrivalSlices[arrivalSlices>25]
        arrivalSlices=arrivalSlices[arrivalSlices<275]

        arrivalSlicesTruth=arrivalSlicesTruth[arrivalSlicesTruth>25]
        arrivalSlicesTruth=arrivalSlicesTruth[arrivalSlicesTruth<275]

        b = benchmark(
            arrivalSlices,
            arrivalSlicesTruth, 
            windowRadius=windowRadius)

        bench.truePositive += b.truePositive
        bench.falsePositive += b.falsePositive
        bench.falseNegative += b.falseNegative

    truePositiveRate[s] = bench.truePositiveRate()
    delta_truePositiveRate[s] = bench.delta_truePositiveRate()

    falseNegativeRate[s] = bench.falseNegativeRate()
    delta_falseNegativeRate[s] = bench.delta_falseNegativeRate()



plt.figure(figsize=(8,2*3.43))
plt.errorbar(
    windowRadii/2, 
    truePositiveRate, 
    xerr=0.25, 
    yerr=delta_truePositiveRate, 
    fmt=',', 
    color='C0',
    label='True positive rate'
)
plt.errorbar(
    windowRadii/2, 
    falseNegativeRate, 
    xerr=0.25, 
    yerr=delta_falseNegativeRate, 
    fmt=',', 
    color='C1',
    label='False negative rate'
)
plt.ylabel('rate/1')
plt.xlabel('time coincidence radius/ns')
plt.legend(
    bbox_to_anchor=(0., 1.02, 1., .102), 
    loc=3,
    ncol=2, 
    mode="expand", borderaxespad=0.
)
plt.savefig(
    'benchmark.png', 
    dpi=256, 
    bbox_inches='tight', 
    pad_inches=0
)