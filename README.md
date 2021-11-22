# datasetsxml

This is a set of tools for working with ERDDAP's datasets.xml file.

While ERDDAP requires all datasets to be contained in a single xml file, maintenance can be easier dataset are defined one per file. These files are re-assembled before sharing with ERDDAP.

## Requirements

 * python3
 * [python3-lxml](https://lxml.de/)

## Acknowledgments

<span style="background-color:#fff;"><img src="https://raw.githubusercontent.com/IrishMarineInstitute/zapidox/master/img/dafm.png" alt="DAFM Logo" style="height: 50px;"/> <img src="https://raw.githubusercontent.com/IrishMarineInstitute/zapidox/master/img/forasnamara.jpg" alt="Marine Institute Logo" style="height: 50px;"/> <img src="https://raw.githubusercontent.com/IrishMarineInstitute/zapidox/master/img/eu-emff.png" alt="EU EMFF Logo" style="height: 50px;"/> <img src="https://raw.githubusercontent.com/IrishMarineInstitute/zapidox/master/img/eu_sifp.jpg" alt="EU Structural Infrastructure Fund and Programme Logo" style="height: 50px;"/></span>

This work is supported by the Irish Government and the European Maritime & Fisheries Fund as part of the EMFF Operational Programme for 2014–2020.

## Splitting datasets.xml

Use the bin/split_datasetsxml.py tool to split the dataset into parts, which will be put into a new parts folder.

## Joining datasets.xml

Use the bin/join_datsetsxml.py tool to join the dataset parts into a single datasets.xml document

## Diffing two datasets.xml

Use the bin/diff_datsetsxml.py tool to determine which datasets have changes between two datasets.xml files. This can be useful for setting the flags file.

```bash
for dataset in $(bin/diff_datasetsxml.py /opt/tomcat/content/erddap/datasets.xml /opt/tomcat/content/erddap/datasets.xml.old)
  do touch /opt/erddap/flag/$dataset
done
```
