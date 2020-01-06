#!/usr/bin/env python3
import os
import re
import sys
from tidyxml import parse_tree, tidy
from io import BytesIO
from xml.parsers.expat import ParserCreate, ExpatError, errors
from xml.sax import saxutils
import shutil

class DatasetFile(object):

    def __init__(self):
        self.master_file = BytesIO()
        self.dataset_file = None

    def open_dataset(self,datasetID):
        filename = 'parts/{0}.xml'.format(datasetID)
        self.dataset_file = open(filename, 'wb')

    def write(self, data):
        if self.dataset_file:
          self.dataset_file.write(data)
        else:
          self.master_file.write(data)

    def close_dataset(self):
        self.dataset_file.close()
        self.dataset_file = None

class DatasetExtractor(saxutils.XMLGenerator):
    
    def __init__(self, encoding='ISO-8859-1', *args, **kwargs):
        self.out_file = DatasetFile()
        saxutils.XMLGenerator.__init__(self, self.out_file, encoding=encoding, *args, **kwargs)
        self.secrets_file = None
        self.mock_secrets_file = None
        self.context = []
        self._in_entity = 0
        self._in_cdata = 0
        self._in_secret = 0
        self.encoding = encoding
        self.master_header = BytesIO()
        self.secret_prefix = ''
        self.secret_entity = ''

    def entityName(self, datasetID):
        # TODO: no duplicates
        return re.sub('[^0-9a-zA-Z_]','_',datasetID)

    def parse(self, filename):
        self.secrets_file = open('parts/_actual_secrets.txt', 'wb')
        self.mock_secrets_file = open('parts/_example_secrets.txt', 'wb')
        parser = ParserCreate()
        parser.CommentHandler = self.commentHandler
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characters

        parser.StartCdataSectionHandler = self.startCDATA
        parser.EndCdataSectionHandler = self.endCDATA

        saxutils.XMLGenerator(out=self.master_header).startDocument()
        self.master_header.write(b'<!DOCTYPE erddapDatasets [\n');
        self.master_header.write(b'<!ENTITY % secrets SYSTEM "_secrets.txt">\n');
        self.master_header.write(b'%secrets;\n');
        parser.ParseFile(open(filename,"rb"))
        self.master_header.write(b']>\n');
        self.master_header.write(self.out_file.master_file.getvalue())
        with open("parts/_datasets.xml","wb") as f:
            f.write(self.master_header.getvalue())
        self.secrets_file.close()
        self.mock_secrets_file.close()

    def commentHandler(self,comment):
        self.out_file.write(b'<!--')
        self.out_file.write(bytes(comment,self.encoding))
        self.out_file.write(b'-->')

    def startElement(self, name, attrs):
        if name == 'dataset' or len(self.context):
          if name == 'connectionProperty':
              self._in_secret = self._in_secret + 1
              self.secret_entity = "{0}_cp_{1}".format(self.secret_prefix,attrs["name"])
          if name == 'dataset':
              datasetID = attrs["datasetID"]
              self.out_file.open_dataset(datasetID)
              self.secret_prefix = self.entityName(datasetID);
          self.context.append((name, attrs))
        saxutils.XMLGenerator.startElement(self, name, attrs)

    def endElement(self, name):
        saxutils.XMLGenerator.endElement(self, name)
        if len(self.context):
          el = self.context.pop()
          if name == 'connectionProperty':
              self._in_secret = self._in_secret - 1
          if name == 'dataset':
              self.out_file.close_dataset()
              self.context = []
              datasetID = el[1]["datasetID"]
              if datasetID in ["etopo180","etopo360"]:
                  e = '<dataset type="EDDGridFromEtopo" datasetID="{0}" />'.format(datasetID)
                  self.out_file.master_file.write(bytes(e,self.encoding))
              else:
                entity = self.entityName(datasetID)
                entdecl = '<!ENTITY {0} SYSTEM "{1}.xml">\n'.format(entity, datasetID)
                self.master_header.write(bytes(entdecl,self.encoding))
                entref = '&{0};'.format(entity)
                self.out_file.write(bytes(entref,self.encoding))

    def characters(self, content):
        if self._in_entity:
            return
        elif self._in_cdata:
            self.out_file.write(bytes(content,self.encoding))
        elif self._in_secret:
            templ = '<!ENTITY {} "{}" >\n'
            decl = templ.format(self.secret_entity, content)
            self.secrets_file.write(bytes(decl,self.encoding))
            self.out_file.write(bytes('&{0};'.format(self.secret_entity),self.encoding))
            decl = templ.format(self.secret_entity, "(secret)")
            self.mock_secrets_file.write(bytes(decl,self.encoding))
        else:
            saxutils.XMLGenerator.characters(self, content)

    # -- LexicalHandler interface

    def startDTD(self, name, public_id, system_id):
        self.out_file.write('<!DOCTYPE %s' % name)
        if public_id:
            self.out_file.write(' PUBLIC %s %s' % (
                saxutils.quoteattr(public_id),
                saxutils.quoteattr(system_id)))
        elif system_id:
            self.out_file.write(' SYSTEM %s' % saxutils.quoteattr(system_id))

    def endDTD(self):
        self.out_file.write('>\n')

    def startEntity(self, name):
        self.out_file.write('&%s;' % name)
        self._in_entity = 1

    def endEntity(self, name):
        self._in_entity = 0

    def startCDATA(self):
        self.out_file.write(b'<![CDATA[')
        self._in_cdata = 1

    def endCDATA(self):
        self.out_file.write(b']]>')
        self._in_cdata = 0

def write_parts_READMEmd(filename):
    with open("parts/README.md",'a') as out:
        out.write('''# datasets.xml split

This folder contains a split version of {0}

## Important Files

 * _datasets.xml is the master xml document
 * _actual_secrets.txt contains your secrets (connectionProperties) as XML entities. Probably you *don't* want to put this file to version control.
 * _mock_secrets contains the XML entites but no secrets, and is OK to put to version control
 * _secrets contains the XML entities which are one or other of _actual_secrets.txt or _mock_secrets.txt. Probaby you *don't* want to put this file to version control.
 * There is one xml file per dataset.

## Before committing your files to version control...

 1. Check _datasets.xml does not contain any secrets (for example in commented out datasets)
 2. Make a safe copy of _actual_secrets.txt

# Regenerating datasets.xml

 1. First make sure you are using the actual secrets:
    ```cp parts/_actual_secrets.txt parts/secrets.txt```
    
 2. Use the join datasets script

```bin/join_datasets.xml > new_datasets.xml``

'''.format(filename))

def success_message():
    return '''The file was successfully split to parts/_datasets.xml

WARNING: secrets are contained in file parts/_actual_secrets.txt

See parts/README.md to find out more.'''

if __name__ == "__main__":
    if len(sys.argv) != 2:
        usage = '''USAGE: {0} path/to/datasets.xml
        '''.format(sys.argv[0])
        print(usage , file=sys.stderr)
        exit(2)

    if os.path.exists('parts'):
        print("Folder exits: parts. Remove the parts folder to start again.")
        exit(1)

    os.mkdir('parts')
    filename = sys.argv[1]
    tree = parse_tree(filename)
    parser = DatasetExtractor(tree.docinfo.encoding)
    parser.parse(filename)
    success = False
    try:
        shutil.copyfile('parts/_actual_secrets.txt', 'parts/_secrets.txt')
        before = BytesIO()
        tidy(filename, before)
        after = BytesIO()
        tidy("parts/_datasets.xml", after)
        if before.getvalue() == after.getvalue():
            success = True
    finally:
        shutil.copyfile('parts/_example_secrets.txt', 'parts/_secrets.txt')
    if not success:
        print("WARNING: The original file and generated file do not match exactly", file=sys.stderr)
    write_parts_READMEmd(filename)
    print(success_message(), file=sys.stderr)
    exit(0)
