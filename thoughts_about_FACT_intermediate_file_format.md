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

-----

## Results of test run over 4month: (01-04.2014)

438 out of 5065 runs wrote this into their stderr file:
```
java.lang.StringIndexOutOfBoundsException: String index out of range: -1
        at java.lang.String.substring(String.java:1911)
        at fact.auxservice.AuxFileService$1.accept(AuxFileService.java:135)
        at java.io.File.list(File.java:1087)
        at fact.auxservice.AuxFileService.findAuxFileUrls(AuxFileService.java:128)
        at fact.auxservice.AuxFileService.getAuxiliaryData(AuxFileService.java:62)
        at fact.features.source.SourcePosition.process(SourcePosition.java:211)
        at stream.runtime.AbstractProcess.process(AbstractProcess.java:126)
        at stream.runtime.AbstractProcess.execute(AbstractProcess.java:184)
        at stream.runtime.ProcessThread.run(ProcessThread.java:123)
```

This is independent of the use of the `SinglePulseExtractor` processor.
Not all of the json files, which belong to a `StringIndexOutOfBoundsException`-stderr file are `[]` empty lists.
All json files I've seen, also those with the exception, are valid json files.

The entire test for 4 month took a day, that's pretty fast, I think.

So even those, which show problems ... can be further analyzed.
