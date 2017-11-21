# coursera2gift
A little script to convert Coursera's YAML quiz format to GIFT format (used by moodle). 

The usage is:

~~~~bash
python coursera2gift courseraInputFile.yaml outputFile.gift
~~~~

It currently only supports multiple choice and choose all that apply questions. 

If a question has multiple variations, it currenlty just exports the first one. 
