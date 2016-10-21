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
All json files I've seen, also those with the exception, are valid json files. So even those, which show problems ... can be further analyzed.

The entire test for 4 month took a day, that's pretty fast, I think. The entire size of the 4month json output folder is 136GB. So if these 4 months are representative 5 years of data would end up as 2TB not 10TB.

I start now the rest of 2014. Now is 17.10.2016 ~10:10h. (submission of 8 month of jobs, takes roughly 10minutes)
The number of total jobs submitted is a little less than 17k.

At the moment we get 117 workernodes at ISDC, which at an estimated job runtime of 15minutes gives us 11k jobs per day. So 2014 should be done by tomorrow evening.


----

New fact-tools version 0.16.1 came out hopefully solving some problems. So I tested it again on the first four month of 2014.

One file (20140210_085) was not processed at all, meaning: There was not even an empty json file. 
total output size was 141GB. So a little more files were processed than before.

Here is an overview off the errors I found
```{python}
            {'java.lang.ArrayIndexOutOfBoundsException:': ['out_test/err/2014/01/03/20140103_259.txt'],
             'java.lang.RuntimeException': ["all files from 20140405"],
             'stream.util.parser.ParseException:': ['out_test/err/2014/02/10/20140210_085.txt'],
             'java.nio.BufferUnderflowException': ['out_test/err/2014/01/01/20140101_086.txt',
                                                   'out_test/err/2014/01/05/20140105_262.txt',
                                                   'out_test/err/2014/01/05/20140105_263.txt',
                                                   'out_test/err/2014/01/05/20140105_267.txt',
                                                   'out_test/err/2014/01/06/20140106_254.txt',
                                                   'out_test/err/2014/01/21/20140121_214.txt',
                                                   'out_test/err/2014/01/21/20140121_215.txt',
                                                   'out_test/err/2014/02/07/20140207_087.txt',
                                                   'out_test/err/2014/02/11/20140211_197.txt',
                                                   'out_test/err/2014/03/17/20140317_043.txt',
                                                   'out_test/err/2014/03/18/20140318_045.txt',
                                                   'out_test/err/2014/03/19/20140319_030.txt',
                                                   'out_test/err/2014/03/19/20140319_031.txt',
                                                   'out_test/err/2014/03/19/20140319_033.txt',
                                                   'out_test/err/2014/03/19/20140319_036.txt',
                                                   'out_test/err/2014/03/19/20140319_051.txt',
                                                   'out_test/err/2014/03/19/20140319_052.txt',
                                                   'out_test/err/2014/03/20/20140320_049.txt',
                                                   'out_test/err/2014/03/20/20140320_128.txt',
                                                   'out_test/err/2014/03/20/20140320_129.txt',
                                                   'out_test/err/2014/03/20/20140320_130.txt',
                                                   'out_test/err/2014/03/21/20140321_057.txt',
                                                   'out_test/err/2014/03/21/20140321_077.txt',
                                                   'out_test/err/2014/03/21/20140321_079.txt',
                                                   'out_test/err/2014/03/21/20140321_080.txt',
                                                   'out_test/err/2014/03/21/20140321_178.txt',
                                                   'out_test/err/2014/03/21/20140321_179.txt',
                                                   'out_test/err/2014/03/21/20140321_180.txt',
                                                   'out_test/err/2014/03/22/20140322_028.txt',
                                                   'out_test/err/2014/03/22/20140322_076.txt',
                                                   'out_test/err/2014/03/22/20140322_078.txt',
                                                   'out_test/err/2014/03/22/20140322_081.txt',
                                                   'out_test/err/2014/03/22/20140322_087.txt',
                                                   'out_test/err/2014/03/23/20140323_028.txt',
                                                   'out_test/err/2014/03/23/20140323_031.txt',
                                                   'out_test/err/2014/03/23/20140323_033.txt',
                                                   'out_test/err/2014/03/23/20140323_074.txt',
                                                   'out_test/err/2014/03/23/20140323_078.txt',
                                                   'out_test/err/2014/03/23/20140323_164.txt',
                                                   'out_test/err/2014/03/23/20140323_167.txt',
                                                   'out_test/err/2014/03/23/20140323_172.txt',
                                                   'out_test/err/2014/03/24/20140324_165.txt',
                                                   'out_test/err/2014/03/24/20140324_168.txt',
                                                   'out_test/err/2014/03/24/20140324_169.txt',
                                                   'out_test/err/2014/03/24/20140324_172.txt',
                                                   'out_test/err/2014/03/26/20140326_062.txt',
                                                   'out_test/err/2014/03/26/20140326_170.txt',
                                                   'out_test/err/2014/03/26/20140326_172.txt',
                                                   'out_test/err/2014/03/27/20140327_042.txt',
                                                   'out_test/err/2014/03/27/20140327_053.txt',
                                                   'out_test/err/2014/03/27/20140327_054.txt',
                                                   'out_test/err/2014/03/27/20140327_056.txt',
                                                   'out_test/err/2014/03/27/20140327_066.txt',
                                                   'out_test/err/2014/03/27/20140327_068.txt',
                                                   'out_test/err/2014/04/04/20140404_032.txt',
                                                   'out_test/err/2014/04/06/20140406_149.txt',
                                                   'out_test/err/2014/04/06/20140406_150.txt',
                                                   'out_test/err/2014/04/06/20140406_151.txt',
                                                   'out_test/err/2014/04/06/20140406_152.txt',
                                                   'out_test/err/2014/04/07/20140407_145.txt',
                                                   'out_test/err/2014/04/07/20140407_148.txt',
                                                   'out_test/err/2014/04/07/20140407_152.txt',
                                                   'out_test/err/2014/04/08/20140408_145.txt',
                                                   'out_test/err/2014/04/08/20140408_146.txt',
                                                   'out_test/err/2014/04/08/20140408_149.txt',
                                                   'out_test/err/2014/04/09/20140409_102.txt',
                                                   'out_test/err/2014/04/09/20140409_104.txt',
                                                   'out_test/err/2014/04/09/20140409_110.txt',
                                                   'out_test/err/2014/04/17/20140417_057.txt',
                                                   'out_test/err/2014/04/17/20140417_082.txt',
                                                   'out_test/err/2014/04/17/20140417_088.txt'],
             'java.util.NoSuchElementException:': ['out_test/err/2014/01/01/20140101_152.txt',
                                                   'out_test/err/2014/01/06/20140106_253.txt',
                                                   'out_test/err/2014/01/13/20140113_258.txt',
                                                   'out_test/err/2014/01/21/20140121_102.txt',
                                                   'out_test/err/2014/02/03/20140203_059.txt',
                                                   'out_test/err/2014/02/11/20140211_195.txt',
                                                   'out_test/err/2014/02/11/20140211_198.txt',
                                                   'out_test/err/2014/02/11/20140211_199.txt',
                                                   'out_test/err/2014/03/18/20140318_046.txt',
                                                   'out_test/err/2014/03/18/20140318_047.txt',
                                                   'out_test/err/2014/03/19/20140319_032.txt',
                                                   'out_test/err/2014/03/19/20140319_037.txt',
                                                   'out_test/err/2014/03/19/20140319_038.txt',
                                                   'out_test/err/2014/03/19/20140319_050.txt',
                                                   'out_test/err/2014/03/19/20140319_053.txt',
                                                   'out_test/err/2014/03/20/20140320_032.txt',
                                                   'out_test/err/2014/03/20/20140320_033.txt',
                                                   'out_test/err/2014/03/20/20140320_043.txt',
                                                   'out_test/err/2014/03/20/20140320_044.txt',
                                                   'out_test/err/2014/03/20/20140320_045.txt',
                                                   'out_test/err/2014/03/20/20140320_046.txt',
                                                   'out_test/err/2014/03/20/20140320_050.txt',
                                                   'out_test/err/2014/03/20/20140320_051.txt',
                                                   'out_test/err/2014/03/20/20140320_052.txt',
                                                   'out_test/err/2014/03/20/20140320_053.txt',
                                                   'out_test/err/2014/03/20/20140320_125.txt',
                                                   'out_test/err/2014/03/21/20140321_066.txt',
                                                   'out_test/err/2014/03/21/20140321_078.txt',
                                                   'out_test/err/2014/03/21/20140321_081.txt',
                                                   'out_test/err/2014/03/22/20140322_033.txt',
                                                   'out_test/err/2014/03/22/20140322_034.txt',
                                                   'out_test/err/2014/03/22/20140322_046.txt',
                                                   'out_test/err/2014/03/22/20140322_072.txt',
                                                   'out_test/err/2014/03/22/20140322_075.txt',
                                                   'out_test/err/2014/03/22/20140322_077.txt',
                                                   'out_test/err/2014/03/22/20140322_083.txt',
                                                   'out_test/err/2014/03/22/20140322_084.txt',
                                                   'out_test/err/2014/03/22/20140322_086.txt',
                                                   'out_test/err/2014/03/23/20140323_023.txt',
                                                   'out_test/err/2014/03/23/20140323_024.txt',
                                                   'out_test/err/2014/03/23/20140323_025.txt',
                                                   'out_test/err/2014/03/23/20140323_032.txt',
                                                   'out_test/err/2014/03/23/20140323_075.txt',
                                                   'out_test/err/2014/03/23/20140323_152.txt',
                                                   'out_test/err/2014/03/23/20140323_163.txt',
                                                   'out_test/err/2014/03/23/20140323_168.txt',
                                                   'out_test/err/2014/03/23/20140323_170.txt',
                                                   'out_test/err/2014/03/23/20140323_171.txt',
                                                   'out_test/err/2014/03/24/20140324_064.txt',
                                                   'out_test/err/2014/03/24/20140324_065.txt',
                                                   'out_test/err/2014/03/24/20140324_173.txt',
                                                   'out_test/err/2014/03/24/20140324_174.txt',
                                                   'out_test/err/2014/03/26/20140326_150.txt',
                                                   'out_test/err/2014/03/26/20140326_171.txt',
                                                   'out_test/err/2014/03/27/20140327_040.txt',
                                                   'out_test/err/2014/03/27/20140327_043.txt',
                                                   'out_test/err/2014/03/27/20140327_046.txt',
                                                   'out_test/err/2014/03/27/20140327_048.txt',
                                                   'out_test/err/2014/03/27/20140327_049.txt',
                                                   'out_test/err/2014/03/27/20140327_050.txt',
                                                   'out_test/err/2014/03/27/20140327_055.txt',
                                                   'out_test/err/2014/03/27/20140327_067.txt',
                                                   'out_test/err/2014/04/04/20140404_031.txt',
                                                   'out_test/err/2014/04/04/20140404_033.txt',
                                                   'out_test/err/2014/04/06/20140406_155.txt',
                                                   'out_test/err/2014/04/07/20140407_132.txt',
                                                   'out_test/err/2014/04/07/20140407_133.txt',
                                                   'out_test/err/2014/04/07/20140407_134.txt',
                                                   'out_test/err/2014/04/07/20140407_146.txt',
                                                   'out_test/err/2014/04/07/20140407_147.txt',
                                                   'out_test/err/2014/04/07/20140407_151.txt',
                                                   'out_test/err/2014/04/07/20140407_153.txt',
                                                   'out_test/err/2014/04/07/20140407_154.txt',
                                                   'out_test/err/2014/04/07/20140407_159.txt',
                                                   'out_test/err/2014/04/08/20140408_131.txt',
                                                   'out_test/err/2014/04/08/20140408_132.txt',
                                                   'out_test/err/2014/04/08/20140408_143.txt',
                                                   'out_test/err/2014/04/08/20140408_144.txt',
                                                   'out_test/err/2014/04/08/20140408_150.txt',
                                                   'out_test/err/2014/04/09/20140409_097.txt',
                                                   'out_test/err/2014/04/09/20140409_098.txt',
                                                   'out_test/err/2014/04/09/20140409_099.txt',
                                                   'out_test/err/2014/04/09/20140409_103.txt',
                                                   'out_test/err/2014/04/09/20140409_105.txt',
                                                   'out_test/err/2014/04/09/20140409_108.txt',
                                                   'out_test/err/2014/04/09/20140409_109.txt',
                                                   'out_test/err/2014/04/09/20140409_112.txt',
                                                   'out_test/err/2014/04/09/20140409_113.txt',
                                                   'out_test/err/2014/04/09/20140409_114.txt',
                                                   'out_test/err/2014/04/17/20140417_065.txt',
                                                   'out_test/err/2014/04/17/20140417_078.txt'],
             })
