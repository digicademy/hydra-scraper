# Retrieve remote or local files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from datetime import datetime
from httpx import Client
from lxml import etree
from os import linesep
from os.path import isfile
from rdflib import Graph, Namespace
from validators import url

# Import script modules
from base.organise import harvest_identifier

# Define namespaces
SCHEMA = Namespace('http://schema.org/')

# Set up logging
logger = logging.getLogger(__name__)


class File:


    def __init__(self, location:str, content_type:str|None = None):
        '''
        Retrieve remote or local files

            Parameters:
                location (str): URL or local path to retrieve the file
                content_type (str): Content type to request or parse
        '''

        # Vars
        self.success:bool = False

        # Content vars
        self.location:str|None = None
        self.text:str|None = None
        self.content:any = None
        self.content_type:str|None = None
        self.file_type:str|None = None
        self.file_extension:str|None = None
        self.rdf:Graph|None = None
        self.xml:any = None
        self.request_time:datetime|None = None

        # Assign arguments to object
        self.location = location
        self.content_type = content_type

        # Decide whether to use remote or local routine
        if url(self.location):
            self.remote_file()
        elif isfile(self.location):
            self.local_file()
        else:
            logger.error('Location ' + self.location + ' is neither a URL nor a local path')

        # Determine file type and extension
        if self.success:
            self.determine_type()
            self.find_embedded_jsonld()
            self.parse_content()


    def remote_file(self):
        '''
        Retrieve remote file and store content
        '''

        # Set request time to allow for delays
        self.request_time = datetime.now()

        # Compose request headers
        headers = {
            'User-Agent': harvest_identifier,
        }
        if self.content_type:
            headers['Accept'] = self.content_type

        # Request response from URL
        try:
            with Client(headers = headers, timeout = 30.0, follow_redirects = True) as client:
                r = client.get(self.location)

                # Check if response is valid
                if r.status_code == 200:
                    self.success = True
                    logger.info('Fetched remote file ' + self.location)

                    # Store content type
                    self.content_type = r.headers['Content-Type']
                    self.content_type.replace('; charset=UTF-8', '')
                    self.content_type.replace('; charset=utf-8', '')
                    self.content_type.replace(';charset=UTF-8', '')
                    self.content_type.replace(';charset=utf-8', '')

                    # Store content
                    self.text = r.text
                    self.content = r.content

        # Log info
        except:
            logger.error('Could not fetch remote file ' + self.location)


    def local_file(self):
        '''
        Retrieve local file and store content
        '''

        # Retrieve file content
        try:
            with open(self.location) as f:
                self.success = True
                logger.info('Fetched local file ' + self.location)

                # Get file extension
                i = self.location.rfind('.')
                if i:
                    i += 1
                    self.file_extension = self.location[i:]

                # Store content
                self.content = f.read()
                self.text = self.content

        # Log info
        except:
            logger.error('Could not fetch local file ' + self.location)


    def determine_type(self):
        '''
        Determine file type and extension based on a content type
        '''

        # Routine for remote files
        if self.content_type:

            # RDF file types and extensions, list mostly based on
            # https://github.com/RDFLib/rdflib/blob/main/rdflib/parser.py#L561
            if 'text/html' in self.content_type:
                self.file_type = 'rdfa'
                self.file_extension = 'html'
            elif 'application/xhtml+xml' in self.content_type:
                self.file_type = 'rdfa'
                self.file_extension = 'xhtml'
            elif 'application/rdf+xml' in self.content_type:
                self.file_type = 'xml'
                self.file_extension = 'xml'
            elif 'text/n3' in self.content_type:
                self.file_type = 'n3'
                self.file_extension = 'n3'
            elif 'text/turtle' in self.content_type or 'application/x-turtle' in self.content_type:
                self.file_type = 'turtle'
                self.file_extension = 'ttl'
            elif 'application/trig' in self.content_type:
                self.file_type = 'trig'
                self.file_extension = 'trig'
            elif 'application/trix' in self.content_type:
                self.file_type = 'trix'
                self.file_extension = 'trix'
            elif 'application/n-quads' in self.content_type:
                self.file_type = 'nquads'
                self.file_extension = 'nq'
            elif 'application/ld+json' in self.content_type:
                self.file_type = 'json-ld'
                self.file_extension = 'jsonld'
            elif 'application/json' in self.content_type:
                self.file_type = 'json-ld'
                self.file_extension = 'json'
            elif 'application/hex+x-ndjson' in self.content_type:
                self.file_type = 'hext'
                self.file_extension = 'hext'
            elif 'application/n-triples' in self.content_type:
                self.file_type = 'nt'
                self.file_extension = 'nt'

            # Non-RDF file types and extensions
            elif 'application/xml' in self.content_type:
                self.file_type = 'xml'
                self.file_extension = 'xml'
            elif 'text/plain' in self.content_type:
                self.file_type = 'txt'
                self.file_extension = 'txt'
            else:
                self.file_type = 'txt'
                self.file_extension = 'txt'
                logger.warning('Could not recognise file type of ' + self.location)

        # Routine for local files
        elif self.file_extension:

            # RDF content and file types
            if self.file_extension.startswith('htm'):
                self.content_type = 'text/html'
                self.file_type = 'rdfa'
            elif self.file_extension.startswith('xhtm'):
                self.content_type = 'application/xhtml+xml'
                self.file_type = 'rdfa'
            elif self.file_extension == 'n3':
                self.content_type = 'text/n3'
                self.file_type = 'n3'
            elif self.file_extension == 'ttl':
                self.content_type = 'text/turtle'
                self.file_type = 'turtle'
            elif self.file_extension == 'trig':
                self.content_type = 'application/trig'
                self.file_type = 'trig'
            elif self.file_extension == 'trix':
                self.content_type = 'application/trix'
                self.file_type = 'trix'
            elif self.file_extension == 'nq':
                self.content_type = 'application/n-quads'
                self.file_type = 'nquads'
            elif self.file_extension.startswith('json'):
                self.content_type = 'application/ld+json'
                self.file_type = 'json-ld'
            elif self.file_extension == 'hext':
                self.content_type = 'application/hex+x-ndjson'
                self.file_type = 'hext'
            elif self.file_extension == 'nt':
                self.content_type = 'application/n-triples'
                self.file_type = 'nt'

            # Non-RDF file types and extensions
            elif self.file_extension == 'xml':
                self.content_type = 'application/xml' # Could also be 'application/rdf+xml'
                self.file_type = 'xml'
            elif self.file_extension == 'txt':
                self.content_type = 'text/plain'
                self.file_type = 'txt'
            else:
                self.content_type = 'text/plain'
                self.file_type = 'txt'
                self.file_extension = 'txt'
                logger.warning('Could not recognise file type of ' + self.location)

        # Edge case
        else:
            self.content_type = 'text/plain'
            self.file_type = 'txt'
            self.file_extension = 'txt'
            logger.warning('Could not recognise file type of ' + self.location)


    def find_embedded_jsonld(self):
        '''
        Finds embedded JSON-LD as it is not supported by RDFLib yet
        '''

        # Go ahead in HTML and XHTML responses
        if self.file_type == 'rdfa':
            embed = self.text.find('application/ld+json')
            if embed != -1:

                # Get start and end of JSON-LD block without requiring Beatiful Soup
                embed_start = self.text.find('>', embed) + 1
                embed_end = self.text.find('</script>', embed)
                if embed_start > 0 and embed_end > embed_start:

                    # Correct original assumptions
                    self.file_type = 'json-ld'
                    self.file_extension = 'jsonld'
                    self.text = self.text[embed_start:embed_end]

                    # Remove empty lines
                    self.text = self.strip_lines(self.text)
                    self.content = self.text.encode()


    def parse_content(self):
        '''
        Parse content as RDF or XML
        '''

        # Parse as RDF
        if self.file_type in ['rdfa', 'xml', 'n3', 'turtle', 'trig', 'trix', 'nquads', 'json-ld', 'hext', 'nt']:
            try:
                self.rdf = Graph()
                self.rdf.bind('schema', SCHEMA, replace = True) # "Replace" overrides the RDFLib schema namespace (SDO), which uses "https"
                self.rdf.parse(self.content, format = self.file_type)

            # Parse as XML instead (nested because RDF may be XML)
            except:
                if self.file_type == 'xml':
                    try:
                        self.xml = etree.fromstring(self.content)
                    except:
                        logger.error('Could not parse XML file ' + self.location)
                else:
                    logger.error('Could not parse RDF file ' + self.location)


    def strip_lines(self, input:str) -> str:
        '''
        Take a multi-line string, remove empty lines and comments, and return string

            Parameters:
                input (str): Input string to remove lines from

            Returns:
                str: Cleaned output string
        '''

        # Split up by lines and remove empty ones or comments
        lines = [
            line for line in input.splitlines()
            if line.strip() and line[0] != '#'
        ]

        # Return re-assembled string
        return linesep.join(lines)


    def strip_string(self, input:str) -> str:
        '''
        Take a string, remove quotation marks and newlines, and return the string

            Parameters:
                string (str): Input string to clean

            Returns:
                str: Cleaned output string
        '''

        # Remove offending characters
        input = input.replace('"', '\'')
        input = input.replace('\n', '')
        input = input.replace('\r', '')

        # Return clean string
        return input


    def save(self, file_path:str, format:str|None = None):
        '''
        Save content or RDF to file

            Parameters:
                file_path (str): Path of the file to create
                format (str|None): Optional RDFLib file format to use
        '''

        # Write content to file
        if self.success:
            if not format:
                file_path = file_path + '.' + self.file_extension
                f = open(file_path, 'w')
                f.write(self.text)
                f.flush
                logger.info('Saved content to file ' + file_path)

            # Serialise RDF content
            elif self.rdf:
                if format == 'turtle':
                    file_extension = 'ttl'
                elif format == 'json-ld':
                    file_extension = 'jsonld'
                elif format == 'nquads':
                    file_extension = 'nq'
                elif format == 'pretty-xml':
                    file_extension = 'xml'
                else:
                    file_extension = format
                file_path = file_path + '.' + file_extension
                self.rdf.serialize(destination = file_path, format = format)
                logger.info('Saved RDF to file ' + file_path)

            else:
                logger.error('No RDF content to save in file ' + self.location)
        else:
            logger.error('Could not save file as it was not retrieved successfully from ' + self.location)


    def turtle(self, file_path:str):
        '''
        Serialise triples as a Turtle file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Shorthand method
        self.save(file_path, 'turtle')


    def ntriples(self, file_path:str):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Shorthand method
        self.save(file_path, 'nt')


    def rdfxml(self, file_path:str):
        '''
        Serialise triples as an RDF/XML file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Shorthand method
        self.save(file_path, 'xml')


    def jsonld(self, file_path:str):
        '''
        Serialise triples as a JSON-LD file

            Parameters:
                file_path (str): Path of the file to create
        '''

        # Shorthand method
        self.save(file_path, 'json-ld')
