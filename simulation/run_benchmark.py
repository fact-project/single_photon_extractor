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
            if distance < windowRadius:
                arrivalsExtractedRemaining = np.delete(arrivalsExtractedRemaining, match) 
                bench.truePositive += 1
            else:
                bench.falseNegative += 1

    bench.falsePositive += arrivalsExtractedRemaining.shape[0]

    return bench

#-------------------------------------------------------------------------------
maxWindowRadius = 10
windowRadii = np.linspace(0,maxWindowRadius,maxWindowRadius, endpoint=False)
trueFindings = np.zeros(maxWindowRadius)
falseFindings = np.zeros(maxWindowRadius)

for s, windowRadius in enumerate(windowRadii):
    
    bench = Bench()
    for i in tqdm(range(5000)):
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

    trueFindings[s] = bench.truePositiveRate()
    falseFindings[s] = bench.falseNegativeRate()

plt.step(windowRadii/2, falseFindings, color='g', linewidth=5.0, label='false negative rate (Miss Rate)')
plt.step(windowRadii/2, trueFindings, color='b', linewidth=5.0, label='true positive rate (Sensitivity)')
plt.ylabel('rate/1')
plt.xlabel('matching window radius/ns')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)