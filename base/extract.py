# Extract data from remote or local files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries# Import libraries
import logging
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from base.data import Uri, UriList, LabelList, UriLabelList, Date, DateList, Incipit
from base.file import File
import map.beacon as beacon
import map.csv as csv
import map.cto as cto

# Set up logging
logger = logging.getLogger(__name__)


class ExtractInterface:


    def __init__(self, file:File):
        '''
        Extract data from remote or local files

            Parameters:
                file (File): File object to retrieve content from
        '''

        # Vars
        self.success:bool = False
        self.file:File

        # Retrieve file and data
        if file.success == True:
            self.file = file
            self.retrieve()

            # Log info
            self.success = True
            if hasattr(self, 'element_uri'):
                logger.info('Extracted data from feed element ' + self.element_uri.text())
            else:
                logger.info('Extracted data from feed ' + self.feed_uri.text())
        else:
            logger.error('Could not extract data because file was not available')



    def retrieve(self):
        '''
        Placeholder to extract data from files in concrete classes
        '''

        # Do nothing
        pass


    def rdf_first_object(self, s:list|BNode|Literal|URIRef, p:list|BNode|Literal|URIRef) -> BNode|Literal|URIRef|None:
        '''
        Get object of first matching RDF triple

            Parameters:
                s (list|BNode|Literal|URIRef): Subject of the requested triple
                p (list|BNode|Literal|URIRef): Predicate of the requested triple

            Returns:
                BNode|Literal|URIRef|None: Object of the requested triple
        '''

        # Unify subject and predicate to lists
        if not isinstance(s, list):
            s = [s]
        if not isinstance(p, list):
            p = [p]

        # Loop through subject and predicate
        output = []
        for sub in s:
            for pre in p:
                output_new = next(self.file.rdf.objects(sub, pre, True), None)
                if output_new != None:
                    output.append(output_new)

        # Return result
        if len(output) > 0:
            return output[0]
        else:
            return None


    def rdf_all_objects(self, s:list|BNode|Literal|URIRef, p:list|BNode|Literal|URIRef) -> list|None:
        '''
        Get objects of all matching RDF triples

            Parameters:
                s (list|BNode|Literal|URIRef): Subject of the requested triples
                p (list|BNode|Literal|URIRef): Predicate of the requested triples

            Returns:
                list|None: Objects of the requested triples
        '''

        # Unify subject and predicate to lists
        if not isinstance(s, list):
            s = [s]
        if not isinstance(p, list):
            p = [p]

        # Loop through subject and predicate
        output = []
        for sub in s:
            for pre in p:
                output_new = self.file.rdf.objects(sub, pre, True)
                if output_new != None:
                    output += list(output_new)

        # Return result
        if len(output) > 0:
            return list(set(output))
        else:
            return None


    def rdf_first_subject(self, p:list|BNode|Literal|URIRef, o:list|BNode|Literal|URIRef) -> BNode|Literal|URIRef|None:
        '''
        Get subject of first matching RDF triple

            Parameters:
                p (list|BNode|Literal|URIRef): Predicate of the requested triple
                o (list|BNode|Literal|URIRef): Object of the requested triple

            Returns:
                BNode|Literal|URIRef|None: Subject of the requested triple
        '''

        # Unify predicate and object to lists
        if not isinstance(p, list):
            p = [p]
        if not isinstance(o, list):
            o = [o]

        # Loop through predicate and object
        output = []
        for pre in p:
            for obj in o:
                output_new = next(self.file.rdf.subjects(pre, obj, True), None)
                if output_new != None:
                    output.append(output_new)

        # Return result
        if len(output) > 0:
            return output[0]
        else:
            return None


    def rdf_all_subjects(self, p:list|BNode|Literal|URIRef, o:list|BNode|Literal|URIRef) -> list|None:
        '''
        Get subjects of all matching RDF triples

            Parameters:
                p (list|BNode|Literal|URIRef): Predicate of the requested triples
                o (list|BNode|Literal|URIRef): Object of the requested triples

            Returns:
                list|None: Subjects of the requested triples
        '''

        # Unify predicate and object to lists
        if not isinstance(p, list):
            p = [p]
        if not isinstance(o, list):
            o = [o]

        # Loop through predicate and object
        output = []
        for pre in p:
            for obj in o:
                output_new = self.file.rdf.subjects(pre, obj, True)
                if output_new != None:
                    output += list(output_new)

        # Return result
        if len(output) > 0:
            return list(set(output))
        else:
            return None


    def rdf_first_triple(self, s:list|BNode|Literal|URIRef, p:list|BNode|Literal|URIRef, o:list|BNode|Literal|URIRef) -> BNode|Literal|URIRef|None:
        '''
        Get first matching RDF triple

            Parameters:
                s (list|BNode|Literal|URIRef): Subject of the requested triple
                p (list|BNode|Literal|URIRef): Predicate of the requested triple
                o (list|BNode|Literal|URIRef): Object of the requested triple

            Returns:
                BNode|Literal|URIRef|None: Subject of the requested triple
        '''

        # Unify subject, predicate, and object to lists
        if not isinstance(s, list):
            s = [s]
        if not isinstance(p, list):
            p = [p]
        if not isinstance(o, list):
            o = [o]

        # Loop through subject, predicate, and object
        output = []
        for sub in s:
            for pre in p:
                for obj in o:
                    output_new = next(self.file.rdf.triples((sub, pre, obj)), None)
                    if output_new != None:
                        output.append(output_new)

        # Return result
        if len(output) > 0:
            return output[0]
        else:
            return None


    def rdf_all_triples(self, s:list|BNode|Literal|URIRef, p:list|BNode|Literal|URIRef, o:list|BNode|Literal|URIRef, count:bool = False) -> list|int|None:
        '''
        Get all matching RDF triples

            Parameters:
                s (list|BNode|Literal|URIRef): Subject of the requested triples
                p (list|BNode|Literal|URIRef): Predicate of the requested triples
                o (list|BNode|Literal|URIRef): Object of the requested triples
                count (bool): Whether to just count the triples

            Returns:
                list|None: Subjects of the requested triples
        '''

        # Unify subject, predicate, and object to lists
        if not isinstance(s, list):
            s = [s]
        if not isinstance(p, list):
            p = [p]
        if not isinstance(o, list):
            o = [o]

        # Loop through subject, predicate, and object
        output = []
        for sub in s:
            for pre in p:
                for obj in o:
                    output_new = self.file.rdf.triples((sub, pre, obj))
                    if output_new != None:
                        output += list(output_new)

        # Return result
        if count:
            if len(output) > 0:
                return len(output)
            else:
                return 0
        else:
            if len(output) > 0:
                return list(set(output))
            else:
                return None


    def rdf_uri_label(self, uri:URIRef|BNode, p:list|BNode|Literal|URIRef) -> tuple|URIRef|Literal|None:
        '''
        Combine a URI with its labels

            Parameters:
                uri (URIRef|BNode): URI or node to generate tuples for
                labels (list|BNode|Literal|URIRef): Predicate of the requested labels

            Returns:
                tuple|URIRef|Literal|None: Tuple containing both values or just URI or just labels
        '''

        # Avoid blank URIs
        if isinstance(uri, URIRef) and str(uri).strip() == '':
            return None
        else:

            # Retrieve labels
            labels = self.rdf_all_objects(uri, p)

            # Only return labels for blank nodes
            if isinstance(uri, BNode):
                if labels != None:
                    return labels
                else:
                    return None
                
            # Return tuples or just the URI
            else:
                if labels != None:
                    return (uri, labels)
                else:
                    return uri


    def xml_first_text(self, element_path:str, get_lang:bool = False) -> str|Literal|None:
        '''
        Get text of first XML node matching an element path

            Parameters:
                element_path (str): Element path to check, i.e. a limited implementation of XPath
                get_lang (bool): Whether to also identidy language indicators in the XML tree

            Returns:
                str|Literal|None: Requested text node
        '''

        # Get element
        element_path = self.xml_paths(element_path)
        element = self.file.xml.find(element_path)

        # Optionally check for language code
        lang = None
        if get_lang:
            lang = self.xml_lang(element)

        # Produce literal with language code or string
        if element != None:
            if lang and element.text != '':
                element = Literal(element.text, lang = lang)
            elif element.text != '':
                element = element.text
            else:
                element = None

        # Return result
        return element


    def xml_all_texts(self, element_paths:str|list, get_lang:bool = False) -> list|None:
        '''
        Get text of all XML nodes matching an element path

            Parameters:
                element_paths (str|list): Element path to check, i.e. a limited implementation of XPath
                get_lang (bool): Whether to also identidy language indicators in the XML tree

            Returns:
                list|None: List of requested text nodes
        '''

        # Get elements
        element_paths = self.xml_paths(element_paths, True)
        elements = []
        for element_path in element_paths:
            new_elements = [match for match in self.file.xml.iterfind(element_path) if match != None and match.text != '']
            elements += new_elements

        # Go through elements
        for i in range(len(elements)):

            # Optionally check for language code
            lang = None
            if get_lang:
                lang = self.xml_lang(elements[i])

            # Replace element by literal with language code or string
            if lang:
                elements[i] = Literal(elements[i].text, lang = lang)
            else:
                elements[i] = elements[i].text

        # Return unique results
        if elements != []:
            return list(set(elements))
        else:
            return None


    def xml_first_element(self, element_path:str) -> str|None:
        '''
        Get first XML node matching an element path

            Parameters:
                element_path (str): Element path to check, i.e. a limited implementation of XPath

            Returns:
                str|None: Requested element node
        '''

        # Get element and return result
        element_path = self.xml_paths(element_path)
        return self.file.xml.find(element_path)


    def xml_all_elements(self, element_paths:str|list) -> list|None:
        '''
        Get all XML nodes matching an element path

            Parameters:
                element_paths (str|list): Element path to check, i.e. a limited implementation of XPath

            Returns:
                list|None: List of requested element nodes
        '''

        # Get elements
        element_paths = self.xml_paths(element_paths, True)
        elements = []
        for element_path in element_paths:
            new_elements = self.file.xml.iterfind(element_path)
            elements += new_elements

        #Return unique results
        if elements != []:
            return list(set(elements))
        else:
            return None


    def xml_first_attribute(self, element_path:str, attribute:str) -> str|None:
        '''
        Get attribute content of first XML node matching an element path

            Parameters:
                element_path (str): Element path to check, i.e. a limited implementation of XPath
                attribute (str): Attribute to get content of

            Returns:
                str|None: Requested attribute content
        '''

        # Get element
        element_path = self.xml_paths(element_path)
        attribute = self.xml_paths(attribute)
        element = self.file.xml.find(element_path)

        # Return result
        if attribute in element.attrib:
            return element.attrib[attribute]
        else:
            return None


    def xml_all_attributes(self, element_paths:str|list, attribute:str) -> list|None:
        '''
        Get attribute content of all XML nodes matching an element path

            Parameters:
                element_paths (str|list): Element path to check, i.e. a limited implementation of XPath
                attribute (str): Attribute to get content of

            Returns:
                list|None: Requested attribute content
        '''

        # Get elements
        element_paths = self.xml_paths(element_paths, True)
        attribute = self.xml_paths(attribute)
        elements = []
        for element_path in element_paths:
            new_elements = [match.attrib[attribute] for match in self.file.xml.iterfind(element_path) if attribute in match.attrib]
            elements += new_elements

        # Return unique results
        if elements != []:
            return list(set(elements))
        else:
            return None


    def xml_uri_label(self, elements:any, uri:str, label:str, is_generator:bool = False) -> list|None:
        '''
        Retrieve a URI and its label

            Parameters:
                elements (any): Elements containing URI and label
                uri (str): Element path to retrieve the URI
                label (str): Element path to retrieve the label
                is_generator (bool): Indicates whether the elements are a generator

            Returns:
                list|None: List of tuples containing both values
        '''

        # Clean up paths
        uri = self.xml_paths(uri)
        label = self.xml_paths(label)

        # Unify elements
        output = []
        if elements != None:
            if not is_generator:
                elements = [elements]
            for element in elements:

                # Element URI
                element_uri = element.findtext(uri)

                # Element label
                element_label = element.find(label)
                if element_label != None:
                    if element_label.text != '':

                        # Produce literal with language code or string
                        lang = self.xml_lang(element_label)
                        if lang and element_label.text != '':
                            element_label = Literal(element_label.text, lang = lang)
                        elif label.text != '':
                            element_label = element_label.text

                # Add tuple to ouput
                output.append((element_uri, element_label))

            # Return result
            if len(output) > 0:
                return output
            else:
                return None

        # Element does not exist
        else:
            return None


    def xml_lang(self, element:any) -> str|None:
        '''
        Retrieve the language of a given XML element

            Parameters:
                element (any): Element of a parsed XML document

            Returns:
                str|None: Language code of the element
        '''

        # Check for language attribute
        lang = None
        while lang == None and element != None:
            if '{http://www.w3.org/XML/1998/namespace}lang' in element.attrib:
                lang = element.attrib['{http://www.w3.org/XML/1998/namespace}lang']

            # Escalate inquiry to parent element
            else:
                element = element.getparent()

        # Return language code
        return lang


    def xml_paths(self, element_paths:list|str, return_list:bool = False) -> str|list:
        '''
        Substitute namespace placeholders in element paths and turn input to list or string

            Parameters:
                element_paths (list|str): Element paths that may contain placeholders
                return_list (bool): Whether to return a list of paths or a string

            Returns:
                str|list: Element path with substituted namespaces
        '''

        # Turn element path string into a list
        if isinstance(element_paths, str):
            element_paths = [element_paths]

        # Replace namespace placeholders
        element_paths = [e.replace('{L}', '{http://www.lido-schema.org}') for e in element_paths]
        element_paths = [e.replace('{S}', '{http://www.w3.org/2004/02/skos/core#}') for e in element_paths]

        # Return result(s)
        if return_list:
            return element_paths
        else:
            return element_paths[0]


    def map(self, target:str) -> any:
        '''
        Placeholder to map extracted data to another standard

            Parameters:
                target (str): Identifier of the target standard to use

            Returns:
                any: Feed or FeedElement in the target standard
        '''

        # Do nothing
        pass


    def map_and_save(self, target:str, file_path:str, format:str|None = None, prepare:str|None = None):
        '''
        Serialise triples in another standard as a file

            Parameters:
                target (str): Identifier of the target standard to use
                file_path (str): Path of the file to create
                format (str|None): Optional RDFLib file format to use
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Create and save target
        mapped = self.map(target)
        mapped.save(file_path, format, prepare)


    def map_and_turtle(self, target:str, file_path:str, prepare:str|None = None):
        '''
        Serialise triples in another standard as a Turtle file

            Parameters:
                target (str): Identifier of the target standard to use
                file_path (str): Path of the file to create
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Shorthand method
        self.map_and_save(target, file_path, 'turtle', prepare)


    def map_and_ntriples(self, target:str, file_path:str, prepare:str|None = None):
        '''
        Serialise triples in another standard as an NTriples file

            Parameters:
                target (str): Identifier of the target standard to use
                file_path (str): Path of the file to create
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Shorthand method
        self.map_and_save(target, file_path, 'nt', prepare)


    def map_and_rdfxml(self, target:str, file_path:str, prepare:str|None = None):
        '''
        Serialise triples in another standard as an RDF/XML file

            Parameters:
                target (str): Identifier of the target standard to use
                file_path (str): Path of the file to create
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Shorthand method
        self.map_and_save(target, file_path, 'xml', prepare)


    def map_and_jsonld(self, target:str, file_path:str, prepare:str|None = None):
        '''
        Serialise triples in another standard as a JSON-LD file

            Parameters:
                target (str): Identifier of the target standard to use
                file_path (str): Path of the file to create
                prepare (str|None): Prepare cto output for this NFDI4Culture feed ID
        '''

        # Shorthand method
        self.map_and_save(target, file_path, 'json-ld', prepare)


class ExtractFeedInterface(ExtractInterface):


    def __init__(self, file:File, elements_in_feed:bool = False):
        '''
        Extract data from remote or local files

            Parameters:
                file (File): File object to retrieve content from
                elements_in_feed (bool): Whether to retrieve element content from feed
        '''

        # Vars
        self.elements_in_feed = elements_in_feed

        # Content vars
        self.feed_uri:Uri = Uri()
        self.feed_uri_same:UriList = UriList()
        self.feed_uri_next:Uri = Uri()
        self.catalog_uri:Uri = Uri()
        self.catalog_uri_same:UriList = UriList()
        self.modified_date:Date = Date()
        self.element_uris:UriList = UriList()
        self.feed_elements:list = []

        # Inherit from interface class
        super().__init__(file)


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
            'Feed extract:\n' +\
            '- feed_uri: ' + str(self.feed_uri) + '\n' +\
            '- feed_uri_same: ' + str(self.feed_uri_same) + '\n' +\
            '- feed_uri_next: ' + str(self.feed_uri_next) + '\n' +\
            '- catalog_uri: ' + str(self.catalog_uri) + '\n' +\
            '- catalog_uri_same: ' + str(self.catalog_uri_same) + '\n' +\
            '- modified_date: ' + str(self.modified_date) + '\n' +\
            '- element_uris: ' + str(self.element_uris) + '\n' +\
            '- feed_elements: '

        # Add element properties
        if self.feed_elements != []:
            for feed_element in self.feed_elements:
                properties += '\n\n' + str(feed_element)
        else:
            properties += 'Empty list'

        # Return string
        return properties


    def map(self, target:str) -> beacon.Feed|csv.Feed|cto.Feed:
        '''
        Map extracted feed data to another standard

            Parameters:
                target (str): Identifier of the target standard to use

            Returns:
                beacon.Feed|csv.Feed|cto.Feed: Feed in the target standard
        '''

        # Create a feed
        if target == 'beacon':
            return beacon.Feed(self)
        elif target == 'csv':
            return csv.Feed(self)
        elif target == 'cto':
            return cto.Feed(self)
        
        # Throw error for other target strings
        else:
            raise ValueError('The target you want to map to does not exist.')


class ExtractFeedElementInterface(ExtractInterface):


    def __init__(self, file:File, feed_uri:str = None, element_uri:str = None):
        '''
        Extract data from remote or local files

            Parameters:
                file (File): File object to retrieve content from
                feed_uri (str): Feed URI to look for in file content
                element_uri (str): Element URI to look for in file content
        '''

        # Content vars
        self.feed_uri:Uri = Uri(feed_uri, normalize = False)
        self.element_uri:Uri = Uri(element_uri, normalize = False)
        self.element_uri_same:UriList = UriList()
        self.element_type:Uri = Uri()
        self.element_type_shorthand:str = ''
        self.label:LabelList = LabelList()
        self.label_alt:LabelList = LabelList()
        self.shelf_mark:LabelList = LabelList()
        self.image:Uri = Uri()
        self.lyrics:LabelList = LabelList()
        self.text_incipit:LabelList = LabelList()
        self.music_incipit:Incipit = Incipit()
        self.source_file:Uri = Uri()
        self.iiif_image_api:Uri = Uri()
        self.iiif_presentation_api:Uri = Uri()
        self.ddb_api:Uri = Uri()
        self.oaipmh_api:Uri = Uri()
        self.publisher:UriList = UriList()
        self.license:UriList = UriList()
        self.vocab_element_type:UriLabelList = UriLabelList()
        self.vocab_subject_concept:UriLabelList = UriLabelList()
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
        super().__init__(file)


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
            'Feed element extract:\n' +\
            '- feed_uri: ' + str(self.feed_uri) + '\n' +\
            '- element_uri: ' + str(self.element_uri) + '\n' +\
            '- element_uri_same: ' + str(self.element_uri_same) + '\n' +\
            '- element_type: ' + str(self.element_type) + '\n' +\
            '- element_type_shorthand: ' + str(self.element_type_shorthand) + '\n' +\
            '- label: ' + str(self.label) + '\n' +\
            '- label_alt: ' + str(self.label_alt) + '\n' +\
            '- shelf_mark: ' + str(self.shelf_mark) + '\n' +\
            '- image: ' + str(self.image) + '\n' +\
            '- lyrics: ' + str(self.lyrics) + '\n' +\
            '- text_incipit: ' + str(self.text_incipit) + '\n' +\
            '- music_incipit: ' + str(self.music_incipit) + '\n' +\
            '- source_file: ' + str(self.source_file) + '\n' +\
            '- iiif_image_api: ' + str(self.iiif_image_api) + '\n' +\
            '- iiif_presentation_api: ' + str(self.iiif_presentation_api) + '\n' +\
            '- ddb_api: ' + str(self.ddb_api) + '\n' +\
            '- oaipmh_api: ' + str(self.oaipmh_api) + '\n' +\
            '- publisher: ' + str(self.publisher) + '\n' +\
            '- license: ' + str(self.license) + '\n' +\
            '- vocab_element_type: ' + str(self.vocab_element_type) + '\n' +\
            '- vocab_subject_concept: ' + str(self.vocab_subject_concept) + '\n' +\
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


    def map(self, target:str) -> beacon.FeedElement|csv.FeedElement|cto.FeedElement:
        '''
        Map extracted feed element data to another standard

            Parameters:
                target (str): Identifier of the target to use

            Returns:
                beacon.FeedElement|csv.FeedElement|cto.FeedElement: Feed element in the target standard
        '''

        # Create CTO feed element
        if target == 'beacon':
            return beacon.FeedElement(self)
        elif target == 'csv':
            return csv.FeedElement(self)
        elif target == 'cto':
            return cto.FeedElement(self)
        
        # Throw error for other target strings
        else:
            raise ValueError('The target you want to map to does not exist.')
