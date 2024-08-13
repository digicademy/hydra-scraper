# LIDO file ingest
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from lxml import etree
from rdflib import Namespace
from rdflib.term import Literal

# Define namespaces
SCHEMA = Namespace('http://schema.org/')


# FEED ELEMENT ################################################################


class FeedElement:

    # Vars
    success = False
    feed_uri = None
    element_type = None
    element_uri = None
    element_uri_same = None
    label = None
    label_alt = None
    shelf_mark = None
    image = None
    lyrics = None
    text_incipit = None
    music_incipit = None
    source_file = None
    iiif_image_api = None
    iiif_presentation_api = None
    ddb_api = None
    oaipmh_api = None
    publisher = None
    license = None
    vocab_element_type = None
    vocab_subject_concept = None
    vocab_related_location = None
    vocab_related_event = None
    vocab_related_organization = None
    vocab_related_person = None
    vocab_further = None
    related_item = None
    birth_date = None
    death_date = None
    foundation_date = None
    dissolution_date = None
    start_date = None
    end_date = None
    creation_date = None
    creation_period = None
    destruction_date = None
    approximate_period = None
    existence_period = None


    def __init__(self, content:str):
        '''
        Class that extracts feed element data from single LIDO files

            Parameters:
                content (str): content of the LIDO file
        '''

        # Parse content as XML
        try:
            lido_root = etree.parse(content)
            self.success = True

            # Feed URI
            #self.feed_uri = 

            # Element type
            self.element_type = SCHEMA.VisualArtwork

            # Element URI
            self.element_uri = lido_root.findtext('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordInfoSet/{http://www.lido-schema.org}recordInfoLink')

            # Same as element URI
            #self.element_uri_same = 

            # Label
            self.label = set()
            labels = lido_root.iterfind('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}titleWrap/{http://www.lido-schema.org}titleSet/{http://www.lido-schema.org}appellationValue')
            for label in labels:
                language = self.__get_lang(label)
                if language != None:
                    self.label.add(Literal(label.text, lang = language))
                else:
                    self.label.add(label.text)
            self.label = list(self.label)

            # Alternative label
            #self.label_alt = 

            # Shelf mark
            #self.shelf_mark = 

            # Image (select largest, not first)
            width = 0
            elements = lido_root.iterfind('.//{http://www.lido-schema.org}resourceWrap/{http://www.lido-schema.org}resourceSet/{http://www.lido-schema.org}resourceRepresentation/{http://www.lido-schema.org}resourceMeasurementsSet/{http://www.lido-schema.org}measurementValue')
            for element in elements:
                if int(element.text) > width:
                    width = int(element.text)
                    self.image = element.getparent().getparent().findtext('.//{http://www.lido-schema.org}linkResource')

            # Lyrics
            #self.lyrics = 

            # Text incipit
            #self.text_incipit = 

            # Music incipit
            #self.music_incipit = 

            # Source file
            #self.source_file = 

            # IIIF image API
            #self.iiif_image_api = 

            # IIIF presentation API
            #self.iiif_presentation_api = 

            # DDB API
            #self.ddb_api = 

            # OAI-PMH API
            #self.oaipmh_api = 

            # Publisher
            self.publisher = lido_root.findtext('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordSource/{http://www.lido-schema.org}legalBodyID[@{http://www.lido-schema.org}source="ISIL (ISO 15511)"]')
            if 'info:isil/' in self.publisher:
                self.publisher.replace('info:isil/', 'https://ld.zdb-services.de/resource/organisations/')

            # License (include work, record, and image resource)
            self.license = set()
            self.license.update(self.__get_concepts(lido_root, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
            self.license.update(self.__get_concepts(lido_root, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
            self.license.update(self.__get_concepts(lido_root, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))
            self.license = list(self.license)

            # Vocabulary: element type
            self.vocab_element_type = self.__get_concepts(lido_root, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType')

            # Vocabulary: subject concept
            self.vocab_subject_concept = self.__get_concepts(lido_root, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept')

            # Vocabulary: related location (prefer URI, use label as backup)
            self.vocab_related_location = set()
            self.vocab_related_location.add(lido_root.findtext('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}repositoryWrap/{http://www.lido-schema.org}repositorySet/{http://www.lido-schema.org}repositoryLocation/{http://www.lido-schema.org}placeID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]'))
            if len(self.vocab_related_location) == 0:
                self.vocab_related_location = lido_root.findtext('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}repositoryWrap/{http://www.lido-schema.org}repositorySet/{http://www.lido-schema.org}repositoryLocation/{http://www.lido-schema.org}namePlaceSet/{http://www.lido-schema.org}appellationValue')
            locations = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventPlace/{http://www.lido-schema.org}place/{http://www.lido-schema.org}placeID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
            if locations == None:
                locations = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventPlace/{http://www.lido-schema.org}place/{http://www.lido-schema.org}displayPlace')
            for location in locations:
                self.vocab_related_location.add(location.text)
            self.vocab_related_location = list(self.vocab_related_location)

            # Vocabulary: related event (prefer URI, use label as backup)
            #self.vocab_related_event = 

            # Vocabulary: related organization (prefer URI, use label as backup)
            self.vocab_related_organization = set()
            organizations = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventActor/{http://www.lido-schema.org}actorInRole/{http://www.lido-schema.org}actor[@{http://www.lido-schema.org}type="organization"]/{http://www.lido-schema.org}actorID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
            if organizations == None:
                organizations = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventActor/{http://www.lido-schema.org}actorInRole/{http://www.lido-schema.org}actor[@{http://www.lido-schema.org}type="organization"]/{http://www.lido-schema.org}nameActorSet/{http://www.lido-schema.org}appellationValue')
            for organization in organizations:
                self.vocab_related_organization.add(organization.text)
            self.vocab_related_organization = list(self.vocab_related_organization)

            # Vocabulary: related person (prefer URI, use label as backup)
            self.vocab_related_person = set()
            persons = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventActor/{http://www.lido-schema.org}actorInRole/{http://www.lido-schema.org}actor[@{http://www.lido-schema.org}type="person"]/{http://www.lido-schema.org}actorID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
            if persons == None:
                persons = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventActor/{http://www.lido-schema.org}actorInRole/{http://www.lido-schema.org}actor[@{http://www.lido-schema.org}type="person"]/{http://www.lido-schema.org}nameActorSet/{http://www.lido-schema.org}appellationValue')
            for person in persons:
                self.vocab_related_person.add(person.text)
            self.vocab_related_person = list(self.vocab_related_person)

            # Further vocabulary terms
            self.vocab_further = self.__get_concepts(lido_root, './/{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventMaterialsTech/{http://www.lido-schema.org}materialsTech/{http://www.lido-schema.org}termMaterialsTech')

            # Related item
            self.related_item = set()
            related_items = lido_root.iterfind('.//{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}relatedWorksWrap/{http://www.lido-schema.org}relatedWorkSet/{http://www.lido-schema.org}relatedWork/{http://www.lido-schema.org}object/{http://www.lido-schema.org}objectWebResource')
            for related_item in related_items:
                self.related_item.add(related_item.text)
            self.label = list(self.label)

            # Birth date
            #self.birth_date = 

            # Death date
            #self.death_date = 

            # Foundation date
            #self.foundation_date = 

            # Dissolution date
            #self.dissolution_date = 

            # Start date
            #self.start_date = 

            # End date
            #self.end_date = 

            # Creation date
            creation_terms = [
                'creation',
                'Creation',
                'production',
                'Production',
                'Herstellung'
            ]
            events = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventType/{http://www.lido-schema.org}term')
            for event in events:
                if event.text in creation_terms:
                    self.creation_date = date.fromisoformat(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}earliestDate'))

            # Creation period
            creation_terms = [
                'creation',
                'Creation',
                'production',
                'Production',
                'Herstellung'
            ]
            events = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventType/{http://www.lido-schema.org}term')
            for event in events:
                if event.text in creation_terms:
                    self.creation_period = date.fromisoformat(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}displayDate'))

            # Destruction date
            destruction_terms = [
                'destruction',
                'Destruction',
                'loss',
                'Verlust',
                'Zerstörung',
                'Verlust'
            ]
            events = lido_root.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventType/{http://www.lido-schema.org}term')
            for event in events:
                if event.text in destruction_terms:
                    self.destruction_date = date.fromisoformat(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}latestDate'))

            # Approximate period
            #self.approximate_period = 

            # Existence period
            #self.existence_period = 

        # Leave empty if content could not be parsed
        except:
            pass


    def __get_lang(self, lang_element:any) -> str:
        '''
        Retrieve the language of a given LIDO element

            Parameters:
                lang_element (any): Element of a parsed LIDO document

            Returns:
                str: Language code of the element
        '''

        # Set up empty language variable
        lang = None

        # Check for language tags and escalate inquiry to parent elements if necessary
        while lang == None and lang_element != None:
            if '{http://www.w3.org/XML/1998/namespace}lang' in lang_element.attrib:
                lang = lang_element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            else:
                lang_element = lang_element.getparent()

        # Return language variable
        return lang


    def __get_concepts(self, lido_root:any, element_path:str) -> set:
        '''
        Find LIDO concept IDs in an element tree according to both LIDO 1.0 and 1.1

            Parameters:
                lido_root (any): The parsed LIDO document
                element_path (str): The initial segment of the element path to look for concept IDs

            Returns:
                set: A list of concept IDs
        '''

        # Set up empty set
        concept_ids = set()

        # Find concept IDs according to LIDO 1.0
        concept_list = lido_root.iterfind(element_path + '/{http://www.lido-schema.org}conceptID')
        for concept_entry in concept_list:
            concept_entry_text = concept_entry.text
            if '{http://www.lido-schema.org}source' in concept_entry.attrib:
                if concept_entry.attrib['{http://www.lido-schema.org}source'] == 'Iconclass':
                    concept_entry_text = 'https://iconclass.org/' + concept_entry_text
            concept_ids.add(concept_entry_text)

        # Find concept IDs according to LIDO 1.1
        concept_list = lido_root.iterfind(element_path + '/{http://www.w3.org/2004/02/skos/core#}Concept[@{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about]')
        for concept_entry in concept_list:
            concept_ids.add(concept_entry.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'])

        # Return the set of IDs
        return concept_ids
