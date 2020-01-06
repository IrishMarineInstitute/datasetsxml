import os
import re
import sys
from io import BytesIO
from xml.parsers.expat import ParserCreate, ExpatError, errors
from xml.sax import saxutils

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
    
    def __init__(self, encoding='ISO-8859-1', out=None, *args, **kwargs):
        saxutils.XMLGenerator.__init__(self, out, encoding=encoding, *args, **kwargs)
        self.out_file = out
        self.context = []
        self._in_entity = 0
        self._in_cdata = 0
        self._in_secret = 0
        self.encoding = encoding
        self.master_header = BytesIO()

    def entityName(self, datasetID):
        # TODO: no duplicates
        return re.sub('[^0-9a-zA-Z_]','_',datasetID)

    def parse(self, filename):
        parser = ParserCreate()
        parser.CommentHandler = self.commentHandler
        parser.StartElementHandler = self.startElement
        parser.EndElementHandler = self.endElement
        parser.CharacterDataHandler = self.characters

        parser.StartCdataSectionHandler = self.startCDATA
        parser.EndCdataSectionHandler = self.endCDATA

        saxutils.XMLGenerator(out=self.master_header).startDocument()
        self.master_header.write(b'<!DOCTYPE erddapDatasets [\n');
        parser.ParseFile(open(filename,"rb"))
        self.master_header.write(b']>\n');
        self.master_header.write(self.out_file.master_file.getvalue())
        with open("parts/_datasets.xml","wb") as f:
            f.write(self.master_header.getvalue())

    def commentHandler(self,comment):
        self.out_file.write(b'<!--')
        self.out_file.write(bytes(comment,self.encoding))
        self.out_file.write(b'-->')

    def startElement(self, name, attrs):
        if name == 'dataset' or len(self.context):
          if name == 'connectionProperty':
              self._in_secret = self._in_secret + 1
          if name == 'dataset':
              datasetID = attrs["datasetID"]
              self.out_file.open_dataset(datasetID)
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
            self.out_file.write(b'(secret)')
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


if __name__ == "__main__":
    filename, encoding = sys.argv[1:]

    #saxhandler = DatasetExtractor(encoding, out=DatasetFile())
    parser = DatasetExtractor(encoding, out=DatasetFile())
    #parser.setContentHandler(saxhandler)
    #parser.setProperty(handler.property_lexical_handler, saxhandler)
    parser.parse(filename)
