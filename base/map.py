# Map extracted data to other formats/standards
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import logging
from rdflib import Graph

# Import script modules
from base.data import Uri, UriList, Label, LabelList, UriLabelList, Date, DateList, Incipit, Media

# Set up logging
logger = logging.getLogger(__name__)


class MapInterface:


    def __init__(self, data:any = None):
        '''
        Map extracted data to other formats/standards

            Parameters:
                data (any): Data object to provide data of a feed or a feed element
        '''

        # Vars
        self.success:bool = False
        self.rdf:Graph = Graph()
        self.content:str|None = None
        self.file_extension:str|None = None

        # Retrieve and pass on data if available
        if data:
            if data.success == True:
                self.data(data)
            else:
                logger.error('Could not map data because extraction was not successful')


    def data(self, data:any):
        '''
        Placeholder to clean and use data gathered by extraction routines
        '''

        # Do nothing
        pass


    def generate(self, prepare:list|None = None):
        '''
        Placeholder to generate triples and fill the store attribute

            Parameters:
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Do nothing
        pass


    def save(self, file_path:str, format:str|None = None, prepare:list|None = None):
        '''
        Serialise content or triples as a file

            Parameters:
                file_path (str): Path of the file to create
                format (str|None): Optional RDFLib file format to use
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Store content or triples
        if not self.success:
            self.generate(prepare)

        # Save text content
        if not format:
            if self.file_extension:
                file_extension = self.file_extension
            else:
                file_extension = 'txt'
            file_path = file_path + '.' + self.file_extension
            f = open(file_path, 'w')
            f.write(self.content)
            f.flush

            # Log info
            logger.info('Mapped data to file ' + file_path)

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

            # Log info
            logger.info('Mapped data to RDF file ' + file_path)

        # Log data issues
        else:
            logger.error('There was no data to save to file')


    def turtle(self, file_path:str, prepare:list|None = None):
        '''
        Serialise triples as a Turtle file

            Parameters:
                file_path (str): Path of the file to create
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Shorthand method
        self.save(file_path, 'turtle', prepare)


    def ntriples(self, file_path:str, prepare:list|None = None):
        '''
        Serialise triples as an NTriples file

            Parameters:
                file_path (str): Path of the file to create
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Shorthand method
        self.save(file_path, 'nt', prepare)


    def rdfxml(self, file_path:str, prepare:list|None = None):
        '''
        Serialise triples as an RDF/XML file

            Parameters:
                file_path (str): Path of the file to create
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Shorthand method
        self.save(file_path, 'xml', prepare)


    def jsonld(self, file_path:str, prepare:list|None = None):
        '''
        Serialise triples as a JSON-LD file

            Parameters:
                file_path (str): Path of the file to create
                prepare (list|None): Prepare cto output for this NFDI4Culture feed and catalog ID
        '''

        # Shorthand method
        self.save(file_path, 'json-ld', prepare)


class MapFeedInterface(MapInterface):


    def __init__(self, data:any = None):
        '''
        Map extracted feed data to other formats/standards

            Parameters:
                data (any): Data object to provide data of a feed or a feed element
        '''

        # Content vars
        self.feed_uri:Uri = Uri()
        self.feed_uri_same:UriList = UriList()
        self.catalog_uri:Uri = Uri()
        self.catalog_uri_same:UriList = UriList()
        self.catalog_uri_next:Uri = Uri()
        self.modified_date:Date = Date()
        self.element_uris:list = []
        self.feed_elements:list = []

        # Inherit from interface class
        super().__init__(data)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        return self.success


    def __str__(self) -> str:
        '''
        String representation of a feed element
        '''

        # Put together all properties
        properties = \
            'Feed map:\n' +\
            '- feed_uri: ' + str(self.feed_uri) + '\n' +\
            '- feed_uri_same: ' + str(self.feed_uri_same) + '\n' +\
            '- feed_uri_next: ' + str(self.feed_uri_next) + '\n' +\
            '- catalog_uri: ' + str(self.catalog_uri) + '\n' +\
            '- catalog_uri_same: ' + str(self.catalog_uri_same) + '\n' +\
            '- modified_date: ' + str(self.modified_date) + '\n' +\
            '- element_uris: ' + str(self.element_uris) + '\n' +\
            '- feed_elements: '

        # Add element properties
        elements = self.feed_elements
        if elements != None:
            for element in elements:
                properties += '\n\n' + str(element)
        else:
            properties += 'None'

        # Return string
        return properties


    def data(self, data:any):
        '''
        Use feed data gathered by extraction routines

            Parameters:
                data (any): Data object to set up the feed
        '''

        # Pass data to properties
        if data.feed_uri:
            self.feed_uri = data.feed_uri
        if data.feed_uri_same:
            self.feed_uri_same = data.feed_uri_same
        if data.feed_uri_next:
            self.feed_uri_next = data.feed_uri_next
        if data.catalog_uri:
            self.catalog_uri = data.catalog_uri
        if data.catalog_uri_same:
            self.catalog_uri_same = data.catalog_uri_same
        if data.modified_date:
            self.modified_date = data.modified_date
        if data.element_uris:
            self.element_uris = data.element_uris
        if data.feed_elements:
            self.feed_elements = data.feed_elements


class MapFeedElementInterface(MapInterface):


    def __init__(self, data:any = None):
        '''
        Map extracted feed data to other formats/standards

            Parameters:
                data (any): Data object to provide data of a feed or a feed element
        '''

        # Content vars
        self.feed_uri:Uri = Uri()
        self.element_uri:Uri = Uri()
        self.element_uri_same:UriList = UriList()
        self.element_type:Uri = Uri() # Deprecated, remove along with CTO2
        self.element_type_short:str = ''
        self.data_concept_short:str = ''
        self.label:LabelList = LabelList()
        self.label_alt:LabelList = LabelList()
        self.holding_org:Uri = Uri()
        self.shelf_mark:LabelList = LabelList()
        self.media:Media = Media()
        self.lyrics:LabelList = LabelList()
        self.teaser:LabelList = LabelList()
        self.incipit:Incipit = Incipit()
        self.source_file:Label = Label()
        self.publisher:UriList = UriList()
        self.license:UriLabelList = UriLabelList()
        self.byline:LabelList = LabelList()
        self.vocab_element_type:UriLabelList = UriLabelList() # Deprecated, remove along with CTO2
        self.vocab_subject_concept:UriLabelList = UriLabelList() # Deprecated, remove along with CTO2
        self.vocab_classifier:UriLabelList = UriLabelList()
        self.vocab_related_location:UriLabelList = UriLabelList()
        self.vocab_related_event:UriLabelList = UriLabelList()
        self.vocab_related_organization:UriLabelList = UriLabelList()
        self.vocab_related_person:UriLabelList = UriLabelList()
        self.vocab_further:UriLabelList = UriLabelList()
        self.related_item:UriList = UriList()
        self.birth_date:Date = Date()
        self.death_date:Date = Date()
        self.foundation_date:Date = Date()
        self.dissolution_date:Date = Date()
        self.start_date:Date = Date()
        self.end_date:Date = Date()
        self.creation_date:Date = Date()
        self.creation_period:DateList = DateList()
        self.destruction_date:Date = Date()
        self.approximate_period:DateList = DateList()
        self.existence_period:DateList = DateList()

        # Inherit from interface class
        super().__init__(data)


    def __bool__(self) -> bool:
        '''
        Indicate whether object holds content

            Returns:
                bool: Whether or not there is content
        '''

        # Return bool
        return self.success


    def __str__(self) -> str:
        '''
        String representation of a feed element
        '''

        # Put together all properties
        properties = \
            'Feed element map:\n' +\
            '- feed_uri: ' + str(self.feed_uri) + '\n' +\
            '- element_uri: ' + str(self.element_uri) + '\n' +\
            '- element_uri_same: ' + str(self.element_uri_same) + '\n' +\
            '- element_type: ' + str(self.element_type) + '\n' +\
            '- element_type_short: ' + str(self.element_type_short) + '\n' +\
            '- data_concept_short: ' + str(self.data_concept_short) + '\n' +\
            '- label: ' + str(self.label) + '\n' +\
            '- label_alt: ' + str(self.label_alt) + '\n' +\
            '- holding_org: ' + str(self.holding_org) + '\n' +\
            '- shelf_mark: ' + str(self.shelf_mark) + '\n' +\
            '- media: ' + str(self.media) + '\n' +\
            '- lyrics: ' + str(self.lyrics) + '\n' +\
            '- teaser: ' + str(self.teaser) + '\n' +\
            '- incipit: ' + str(self.incipit) + '\n' +\
            '- source_file: ' + str(self.source_file) + '\n' +\
            '- publisher: ' + str(self.publisher) + '\n' +\
            '- license: ' + str(self.license) + '\n' +\
            '- byline: ' + str(self.byline) + '\n' +\
            '- vocab_element_type: ' + str(self.vocab_element_type) + '\n' +\
            '- vocab_subject_concept: ' + str(self.vocab_subject_concept) + '\n' +\
            '- vocab_classifier: ' + str(self.vocab_classifier) + '\n' +\
            '- vocab_related_location: ' + str(self.vocab_related_location) + '\n' +\
            '- vocab_related_event: ' + str(self.vocab_related_event) + '\n' +\
            '- vocab_related_organization: ' + str(self.vocab_related_organization) + '\n' +\
            '- vocab_related_person: ' + str(self.vocab_related_person) + '\n' +\
            '- vocab_further: ' + str(self.vocab_further) + '\n' +\
            '- related_item: ' + str(self.related_item) + '\n' +\
            '- birth_date: ' + str(self.birth_date) + '\n' +\
            '- death_date: ' + str(self.death_date) + '\n' +\
            '- foundation_date: ' + str(self.foundation_date) + '\n' +\
            '- dissolution_date: ' + str(self.dissolution_date) + '\n' +\
            '- start_date: ' + str(self.start_date) + '\n' +\
            '- end_date: ' + str(self.end_date) + '\n' +\
            '- creation_date: ' + str(self.creation_date) + '\n' +\
            '- creation_period: ' + str(self.creation_period) + '\n' +\
            '- destruction_date: ' + str(self.destruction_date) + '\n' +\
            '- approximate_period: ' + str(self.approximate_period) + '\n' +\
            '- existence_period: ' + str(self.existence_period)

        # Return string
        return properties


    def data(self, data:any):
        '''
        Use feed element data gathered by extraction routines

            Parameters:
                data (any): Data object to set up the feed element
        '''

        # Pass data to properties
        if data.feed_uri:
            self.feed_uri = data.feed_uri
        if data.element_uri:
            self.element_uri = data.element_uri
        if data.element_uri_same:
            self.element_uri_same = data.element_uri_same
        if data.element_type: # Deprecated, remove along with CTO2
            self.element_type = data.element_type
        if data.element_type_short != '':
            self.element_type_short = data.element_type_short
        if data.data_concept_short != '':
            self.data_concept_short = data.data_concept_short
        if data.label:
            self.label = data.label
        if data.label_alt:
            self.label_alt = data.label_alt
        if data.holding_org:
            self.holding_org = data.holding_org
        if data.shelf_mark:
            self.shelf_mark = data.shelf_mark
        if data.media:
            self.media = data.media
        if data.lyrics:
            self.lyrics = data.lyrics
        if data.teaser:
            self.teaser = data.teaser
        if data.incipit:
            self.incipit = data.incipit
        if data.source_file:
            self.source_file = data.source_file
        if data.publisher:
            self.publisher = data.publisher
        if data.license:
            self.license = data.license
        if data.byline:
            self.byline = data.byline
        if data.vocab_element_type: # Deprecated, remove along with CTO2
            self.vocab_element_type = data.vocab_element_type
        if data.vocab_subject_concept: # Deprecated, remove along with CTO2
            self.vocab_subject_concept = data.vocab_subject_concept
        if data.vocab_classifier:
            self.vocab_classifier = data.vocab_classifier
        if data.vocab_related_location:
            self.vocab_related_location = data.vocab_related_location
        if data.vocab_related_event:
            self.vocab_related_event = data.vocab_related_event
        if data.vocab_related_organization:
            self.vocab_related_organization = data.vocab_related_organization
        if data.vocab_related_person:
            self.vocab_related_person = data.vocab_related_person
        if data.vocab_further:
            self.vocab_further = data.vocab_further
        if data.related_item:
            self.related_item = data.related_item
        if data.birth_date:
            self.birth_date = data.birth_date
        if data.death_date:
            self.death_date = data.death_date
        if data.foundation_date:
            self.foundation_date = data.foundation_date
        if data.dissolution_date:
            self.dissolution_date = data.dissolution_date
        if data.start_date:
            self.start_date = data.start_date
        if data.end_date:
            self.end_date = data.end_date
        if data.creation_date:
            self.creation_date = data.creation_date
        if data.creation_period:
            self.creation_period = data.creation_period
        if data.destruction_date:
            self.destruction_date = data.destruction_date
        if data.approximate_period:
            self.approximate_period = data.approximate_period
        if data.existence_period:
            self.existence_period = data.existence_period
