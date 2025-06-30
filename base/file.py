# Retrieve remote or local files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import codecs
import logging
from datetime import datetime
from glob import glob
from httpx import BasicAuth, Client, HTTPError
from lxml import etree
from lxml.etree import ParserError as XmlParserError
from os import linesep, makedirs, remove
from os.path import isdir, isfile
from rdflib import Graph, Namespace
from rdflib.exceptions import ParserError as RdfParserError
from shutil import rmtree
from time import sleep
from validators import url
from zipfile import BadZipFile, ZipFile

# Define namespaces
SCHEMA = Namespace('http://schema.org/')

# Set up logging
logger = logging.getLogger(__name__)


class File:


    def __init__(self, location:str, content_type:str|None = None, ba_username:str|None = None, ba_password:str|None = None, user_agent:str = 'Hydra Scraper/0.9.5'):
        '''
        Retrieve remote or local files

            Parameters:
                location (str): URL or local path to retrieve the file
                content_type (str): Content type to request or parse
                ba_username (str): Basic Auth username for requests
                ba_password (str): Basic Auth password for requests
                user_agent (str): User agent to use in remote file requests
        '''

        # Vars
        self.success:bool = False
        self.unpack:str = 'unpack'

        # Content vars
        self.location:str = location
        self.ba_username:str|None = ba_username
        self.ba_password:str|None = ba_password
        self.text:str|None = None
        self.directory:list|None = None
        self.directory_path:str|None = None
        self.rdf:Graph|None = None
        self.xml:etree|None = None
        self.content_type:str|None = content_type
        self.file_type:str|None = None
        self.file_extension:str|None = None
        self.user_agent:str = user_agent
        self.request_time:datetime|None = None

        # Remote, local, or folder routine
        if url(self.location):
            self.remote_file()
        elif isfile(self.location):
            self.local_file()
        elif isdir(self.location):
            self.local_folder()
        else:
            logger.error('Location ' + self.location + ' is neither a URL nor a local path nor a folder')


    def remote_file(self):
        '''
        Retrieve remote file and store content
        '''

        # Set request time to allow for delays
        self.request_time = datetime.now()

        # Compose request headers
        headers = {
            'User-Agent': self.user_agent,
        }
        if self.content_type:
            headers['Accept'] = self.content_type

        # Compose Basic Auth data
        auth = None
        if self.ba_username and self.ba_password:
            auth = BasicAuth(username = self.ba_username, password = self.ba_password)

        # Set up three request attempts in case of server issues
        try:
            lap = 0
            while lap < 3:
                lap += 1

                # Wait for servers to recover from server-side issues in consecutive attempts
                if lap > 1:
                    timer = 30
                    sleep(timer)
                    logger.info('Waiting for ' + str(timer) + ' seconds for the server to recover')

                # Request response from URL
                with Client(headers = headers, auth = auth, timeout = 1800.0, follow_redirects = True) as client:
                    r = client.get(self.location)

                    # Check if response is valid
                    if r.status_code == 200:
                        self.success = True
                        logger.info('Fetched remote file ' + self.location)

                        # Check response for 301 to save subsequent URI in redirect chain or successful URI
                        check_next = False
                        for prev_r in r.history:
                            if check_next:
                                self.location = str(prev_r.url)
                                check_next = False
                            if prev_r.status_code == 301:
                                check_next = True
                        if check_next:
                            self.location = str(r.url)

                        # Store and clean content type
                        self.content_type = r.headers['Content-Type']
                        self.content_type.replace('; charset=UTF-8', '')
                        self.content_type.replace('; charset=utf-8', '')
                        self.content_type.replace(';charset=UTF-8', '')
                        self.content_type.replace(';charset=utf-8', '')

                        # Determine file type and extension based on content type
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
                        elif 'application/xml' in self.content_type:
                            self.file_type = 'xml'
                            self.file_extension = 'xml'
                        elif 'application/zip' in self.content_type:
                            self.file_type = 'folder'
                            self.file_extension = 'zip'
                        elif 'text/plain' in self.content_type:
                            self.file_type = 'txt'
                            self.file_extension = 'txt'
                        else:
                            self.file_type = 'txt'
                            self.file_extension = 'txt'
                            logger.warning('Could not recognise file type of ' + self.location)

                        # Store content
                        if not self.file_extension == 'zip':
                            self.text = r.text
                            self.parse_content()

                        # Handle ZIP file
                        else:
                            zip = self.unpack + '/payload.zip'
                            with open(zip, 'wb') as f:
                                f.write(r.content)
                            unpack_zip(zip, self.unpack)
                            remove(zip)
                            self.local_folder(self.unpack)

                        # Prevent further attempts in case of successful retrieval
                        break
                    
                    # Try again for server-side issues that may heal themselves
                    elif r.status_code in [500, 502, 503, 504]:
                        if lap >= 3:
                            logger.warning('Server-side issue, could not fetch remote file ' + self.location)
                        pass

                    # Prevent further attempts in case of URI issues retrieval
                    else:
                        logger.warning('Could not fetch remote file ' + self.location + ' due to a URI issue')
                        break

        # Log info
        except HTTPError:
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

                # Determine content and file type based on file extension
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
                elif self.file_extension == 'xml':
                    self.content_type = 'application/xml' # Could also be 'application/rdf+xml'
                    self.file_type = 'xml'
                elif self.file_extension == 'zip':
                    self.content_type = 'application/zip'
                    self.file_type = 'folder'
                elif self.file_extension == 'txt':
                    self.content_type = 'text/plain'
                    self.file_type = 'txt'
                else:
                    self.content_type = 'text/plain'
                    self.file_type = 'txt'
                    logger.warning('Could not recognise file type of ' + self.location)
                
                # Remember directory
                directory_path_index = self.location.rfind('/')
                if directory_path_index > 0:
                    self.directory_path = self.location[:directory_path_index]

                # Store content
                if not self.file_extension == 'zip':
                    self.text = f.read()
                    self.parse_content()

                # Handle ZIP file
                else:
                    unpack_zip(self.location, self.unpack)
                    self.local_folder(self.unpack)

        # Log info
        except OSError:
            logger.error('Could not fetch local file ' + self.location)


    def local_folder(self, location:str|None = None):
        '''
        Retrieve content of a local folder
        '''

        if not location:
            location = self.location

        # Retrieve folder content
        files = files_in_folder(location)
        if len(files) > 0:
            self.success = True
            logger.info('Indexed local folder ' + location)

            # Set content and file type as well as file extension
            self.content_type = 'application/zip'
            self.file_type = 'folder'
            self.file_extension = 'zip'

            # Store file list
            self.directory = files

        # Log info
        else:
            logger.error('Empty local folder ' + location)


    def parse_content(self):
        '''
        Parse content as RDF or XML
        '''

        # Check HTML and XHTML responses for embedded JSON-LD
        if self.file_type == 'rdfa':
            self.find_embedded_jsonld()

        # Remove UTF-8 BOM if present
        if self.text[0:1].encode() == codecs.BOM_UTF8:
            self.text = self.text[1:]

        # Parse as RDF
        if self.file_type in ['rdfa', 'xml', 'n3', 'turtle', 'trig', 'trix', 'nquads', 'json-ld', 'hext', 'nt']:
            try:
                self.rdf = Graph()
                self.rdf.bind('schema', SCHEMA, replace = True) # "Replace" overrides the RDFLib schema namespace (SDO), which uses "https"
                self.rdf.parse(data = self.text.encode(), format = self.file_type)

            # Parse as XML instead (nested because RDF may be XML)
            except RdfParserError:
                if self.file_type == 'xml':
                    try:
                        self.xml = etree.fromstring(self.text.encode())
                    except XmlParserError:
                        logger.error('Could not parse XML file ' + self.location)
                else:
                    logger.error('Could not parse RDF file ' + self.location)


    def find_embedded_jsonld(self):
        '''
        Finds embedded JSON-LD as it is not automatically recognized by RDFLib (yet)
        '''

        # Find JSON-LD block
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
                self.text = strip_lines(self.text)


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


def strip_lines(input:str) -> str:
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


def strip_string(input:str) -> str:
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


def unpack_zip(file_path:str, folder_path:str):
    '''
    Unpack a ZIP archive to a local folder

        Parameters:
            file_path (str): Path to the ZIP archive to unpack
            folder_path (str): Path to the folder to unpack the archive in
    '''

    try:
        with ZipFile(file_path, 'r') as zip:
            zip.extractall(folder_path)
        logger.info('Unpacked ZIP archive ' + file_path)

    # Log info
    except BadZipFile:
        logger.error('Failed to unpack ZIP archive ' + file_path)


def files_in_folder(folder_path:str) -> list:
    '''
    Read a local folder and return a list of resources

        Parameters:
            folder_path (str): Path to the folder to read
    '''

    # Prepare list and path
    entries = []
    folder_path += '/**/*'

    # Add each file path to list
    for entry in glob(folder_path, recursive = True):
        entries.append(entry)

    # Return entries
    return entries


def create_folder(folder_name:str):
    '''
    Create a folder with a given name

        Parameters:
            folder_name (str): Name of the folder to create
    '''

    # Create folders, may be error-prone
    try:
        makedirs(folder_name, exist_ok = True)
    except OSError:
        pass


def remove_folder(folder:str, contents_only:bool = False):
    '''
    Removes a temporary folder and its contents

        Parameters:
            folder (str): Path of the folder to remove
    '''

    # Remove entire folder
    if not contents_only:
        rmtree(folder)

    # Only remove files in folder
    else:
        files = files_in_folder(folder)
        for file in files:
            remove(file)
