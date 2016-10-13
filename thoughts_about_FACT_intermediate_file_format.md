For a FACT intermediate file format we want to use this single_pulse_extractors output. But not only this
We want to of course include also some more information, we get basically for free.

So for testing, we are currently doing the std analysis together with the `SinglePulseExtraction` processor on some data. The processing and so on can be found here:
    isdc:/home/guest/neise/facttools_massive_production/single_photon_extractor

An `ls` shows what we've got there:
    
    analysis.xml
    fact-tools-v0.16.0.jar
    out_dir -> /scratch/fact/single_photon_extractor
    submit.py
    workernode.sh

There are a few more files, but they are not important. 
So everybody can see the `analysis.xml` and as you see, we use fact-tools v0.16.0, no development version.
`workernode.sh` is just doing the `java -jar <jarfile> <xmlfile>` call, nothing more.
`submit.py` is walking through an input folder, finding all the data run, finding the right drs-file for them, and doing the `qsub`. 

----
## Testrun

We did a testrun `time java -jar fact-tools-v0.16.0.jar analysis.xml`
Result was:
```
real    10m50.059s
user    10m15.534s
sys     0m8.046s
```
output file size: 86MB
gzip took 13 seconds --> zipped file size: 30MB

Note: when not doing `PerformanceMeasuringProcess` the thing takes the same time. 
Note: now we use `gzip="true"` for the JSONWriter in the xml directly.
