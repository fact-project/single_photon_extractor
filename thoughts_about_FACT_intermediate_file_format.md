For a FACT intermediate file format we want to use this single_pulse_extractors output. But not only this
We want to of course include also some more information, we get basically for free:

In order not to forget anything, we work on a list of fact_tools key names:

output is here: `isdc-nx00:/home/guest/neise/facttools_massive_production/test`


xml looks like this:
```{xml}
<container>

        <properties url="classpath:/default/settings.properties" />

    <property name="infile" value="file:/fact/raw/2016/10/08/20161008_068.fits.fz" />
    <property name="drsfile" value="file:/fact/raw/2016/10/08/20161008_064.drs.fits.gz" />

    <property name="integralGainFile" value="classpath:/default/gain_sorted_20131127.csv" />
    <property name="pixelDelayFile" value="classpath:/default/delays_lightpulser_20150217.csv" />

    <property name="outfile" value="file:./foobar.json" />

    <property name="auxFolder" value="file:/fact/aux/2016/10/08/" />
    <service id="auxService" class="fact.auxservice.AuxFileService" auxFolder="${auxFolder}" />

    <service id="calibService" class="fact.calibrationservice.ConstantCalibService" />

    <stream id="fact" class="fact.io.zfits.ZFitsStream"  url="${infile}"/>

    <process class="fact.PerformanceMeasuringProcess" url="file:./measured_runtime.json" id="1" input="fact" warmupIterations="1">
        <!-- prevEventAndSkip: -->
        <!-- PreviousEventInfo, Skip(no Data Trigger) -->
        <include url="classpath:/default/data/prevEventAndSkip.xml" />
        <!-- Output: Data -->

        <!-- Calibration: -->
        <!-- DrsCalibration, PatchJumpRemoval, RemoveSpikes,
        DrsTimeCalibration, ArrayTimeCorrection, InterpolateBadPixel -->
        <include url="classpath:/default/data/calibration.xml" />
        <!-- Output: DataCalibrated -->

        <fact.extraction.SinglePulseExtraction 
            dataKey="DataCalibrated"
            outputKey="PhotonArrivals"
            maxIterations="1000"
        />
        <!-- Extraction -->
        <!-- BasicExtraction, RisingEdgeForPositions, RisingEdgePolynomFit, TimeOverThreshold,
        PhotonChargeTimeOverThreshold, HandleSaturation, CorrectPixelDelays-->
        <include url="classpath:/default/data/extraction.xml" />
        <!-- Output: photoncharge, arrivalTime -->

        <!-- Cleaning -->
        <!-- SourcePosition(Cetatauri), CoreNeighborCleanTimeNeighbor-->
        <include url="classpath:/default/data/cleaning.xml" />
        <!-- Output: shower -->

        <!-- Parameter calculation (only source independent) -->
        <!-- ArrayMean(photoncharge,arrivalTime), ArrayStatistics(photoncharge,arrivalTime,maxSlopes,
        arrivalTimePos,maxSlopesPos,maxAmplitudePosition,photonchargeSaturated,arrivalTimeTOT),
        Size, DistributionFromShower, M3Long, Length, Width, NumberOfIslands, TimeGraident,
        Concentration, ConcentrationCore, ConcentrationAtCenterOfGravity, Leakage, TimeSpread,
        ShowerSlope, Disp -->
        <include url="classpath:/default/data/parameterCalc.xml" />
        <!-- Output: source independent parameters -->

        <!-- Parameter calculation (only source dependent) -->
        <!-- SourcePosition(${sourcename}), AntiSourcePosition(5), Alpha(for 6 Sources),
        Distance(for 6 Sources), CosDeltaAlpha(for 6 Sources), Theta(for 6 Sources) -->
        <include url="classpath:/default/data/sourceParameter.xml" />
        <!-- Output: source dependent parameters -->


        <fact.io.JSONWriter url="${outfile}" keys="${keysForOutput},PhotonArrivals" />
    </process>
</container>
```
