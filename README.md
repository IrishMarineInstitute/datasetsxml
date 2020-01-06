# datasetsxml

This is a set of tools for working with ERDDAP's datasets.xml file.

While ERDDAP requires all datasets to be contained in a single xml file, maintenance can be easier dataset are defined one per file. These files are re-assembled before sharing with ERDDAP.

## Requirements

 * python3
 * [python3-lxml](https://lxml.de/)

## Splitting datasets.xml

Use the bin/split_datasetsxml.py tool to split the dataset into parts, which will be put into a new parts folder.

## Joining datasets.xml

Use the bin/join_datsetsxml.py tool to join the dataset parts into a single datasets.xml document

