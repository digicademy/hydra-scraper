# Retrieve and extract data from LIDO files
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from rdflib import Namespace
from rdflib.term import Literal

# Import script modules
from base.data import Uri, UriList, Label, LabelList, UriLabelList, Date, DateList, Media
from base.extract import ExtractFeedElementInterface

# Define namespaces
SCHEMA = Namespace('http://schema.org/')
N4C = Namespace('https://nfdi4culture.de/id/')


class FeedElement(ExtractFeedElementInterface):


    def retrieve(self):
        '''
        Extract feed element data from LIDO files
        '''

        # Check for LIDO content
        if self.xml_first_element('.//{L}lido') == None:
            self.success = False
        else:

            # Feed URI
            #self.feed_uri = 

            # Element URI
            if not self.element_uri:
                self.element_uri = Uri(self.xml_first_text('.//{L}recordWrap/{L}recordInfoSet/{L}recordInfoLink'), normalize = False)

            # Same as element URI
            self.element_uri_same = UriList(self.xml_all_texts('.//{L}lido/objectPublishedID'))

            # Element type
            self.element_type = Uri(SCHEMA.VisualArtwork)

            # Element type shorthand
            self.element_type_short = 'item'

            # Data concept shorthand
            #self.data_concept_short = 
            # TODO Fill this gap

            # Label and alternative label (overflow mechanic)
            label = []
            label_langs = []
            label_alt = []
            label_alt_langs = []
            all_labels = self.xml_all_texts('.//{L}objectIdentificationWrap/{L}titleWrap/{L}titleSet/{L}appellationValue', True)
            if all_labels != None:
                for single_label in all_labels:
                    if isinstance(single_label, Literal):
                        label_lang = single_label.language
                    else:
                        label_lang = None
                    if label_lang not in label_langs:
                        label.append(single_label)
                        label_langs.append(label_lang)
                    elif label_lang not in label_alt_langs:
                        label_alt.append(single_label)
                        label_alt_langs.append(label_lang)
            self.label = LabelList(label)
            self.label_alt = LabelList(label_alt)

            # Holding organization
            #self.holding_org = 

            # Shelf mark
            #self.shelf_mark = 

            # Media (select largest or first image)
            largest_width = 0
            widths = self.xml_all_elements('.//{L}resourceWrap/{L}resourceSet/{L}resourceRepresentation/{L}resourceMeasurementsSet/{L}measurementValue')
            if widths:
                for width in widths:
                    if int(width.text) > largest_width:
                        largest_width = int(width.text)
                        self.media = Media(width.getparent().getparent().findtext('.//{http://www.lido-schema.org}linkResource'), type = 'image')
                        # TODO: Add image license and byline data
            else:
                self.media = Uri(self.xml_first_text('.//{L}resourceWrap/{L}resourceSet/{L}resourceRepresentation/{L}linkResource'), type = 'image')
                # TODO: Add image license and byline data

            # Lyrics
            #self.lyrics = 

            # Teaser
            #self.teaser = 

            # Incipit
            #self.incipit = 

            # Source file
            self.source_file = Label(self.file.location, remove_path = self.file.directory_path)

            # Publisher (auto-correct ISIL URIs)
            publishers = self.xml_all_texts('.//{L}recordWrap/{L}recordSource/{L}legalBodyID[@{L}source="ISIL (ISO 15511)"]')
            if publishers != None:
                for publisher in publishers:
                    publisher.replace('info:isil/', 'https://ld.zdb-services.de/resource/organisations/')
            self.publisher = UriList(publishers)

            # License (observe work, record, and image licenses)
            self.license = UriLabelList(self.xml_all_lido_concepts([
                './/{L}rightsWorkSet/{L}rightsType',
                './/{L}recordRights/{L}rightsType',
                './/{L}rightsResource/{L}rightsType',
            ]))

            # Byline
            #self.byline =
            # TODO Check if byline data is available

            # Vocabulary: element type
            # Deprecated, remove along with CTO2
            self.vocab_element_type = UriLabelList(self.xml_all_lido_concepts('.//{L}objectClassificationWrap/{L}objectWorkTypeWrap/{L}objectWorkType'))

            # Vocabulary: subject concept
            # Deprecated, remove along with CTO2
            self.vocab_subject_concept = UriLabelList(self.xml_all_lido_concepts('.//{L}objectRelationWrap/{L}subjectWrap/{L}subjectSet/{L}subject/{L}subjectConcept'))

            # Vocabulary: classifier
            #self.vocab_classifier = UriLabelList()
            # TODO Make sure classifiers are recognised

            # Vocabulary: related location (two distinct nodes)
            vocab_related_location = []
            repo_location = self.xml_uri_label(self.xml_first_element('.//{L}objectIdentificationWrap/{L}repositoryWrap/{L}repositorySet/{L}repositoryLocation'), './/{L}placeID[@{L}type="http://terminology.lido-schema.org/lido00099"]', './/{L}namePlaceSet/{L}appellationValue')
            if repo_location != None:
                vocab_related_location += repo_location
            event_locations = self.xml_uri_label(self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventPlace/{L}place'), './/{L}placeID[@{L}type="http://terminology.lido-schema.org/lido00099"]', './/{L}displayPlace', True)
            if event_locations != None:
                vocab_related_location += event_locations
            self.vocab_related_location = UriLabelList(list(set(vocab_related_location)))

            # Vocabulary: related event
            #self.vocab_related_event = 

            # Vocabulary: related organization
            self.vocab_related_organization = UriLabelList(self.xml_uri_label(self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventActor/{L}actorInRole/{L}actor[@{L}type="organization"]'), './/{L}actorID[@{L}type="http://terminology.lido-schema.org/lido00099"]', './/{L}nameActorSet/{L}appellationValue', True))

            # Vocabulary: related person
            self.vocab_related_person = UriLabelList(self.xml_uri_label(self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventActor/{L}actorInRole/{L}actor[@{L}type="person"]'), './/{L}actorID[@{L}type="http://terminology.lido-schema.org/lido00099"]', './/{L}nameActorSet/{L}appellationValue', True))

            # Further vocabulary terms
            self.vocab_further = UriLabelList(self.xml_all_lido_concepts('.//{L}objectIdentificationWrap/{L}objectMaterialsTechWrap/{L}objectMaterialsTechSet/{L}materialsTech/{L}termMaterialsTech'))

            # Related item
            self.related_item = UriList(self.xml_all_texts('.//{L}objectRelationWrap/{L}relatedWorksWrap/{L}relatedWorkSet/{L}relatedWork/{L}object/{L}objectWebResource'))

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

            # Creation date (check for specific event names, LIDO 1.0 and 1.1 notation)
            check_terms = [
                'creation',
                'Creation',
                'production',
                'Production',
                'Herstellung'
            ]
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{L}term')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.creation_date = Date(date.fromisoformat(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}earliestDate')))
                        except (ValueError, TypeError):
                            pass
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{S}Concept/{S}prefLabel')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.creation_date = Date(date.fromisoformat(event.getparent().getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}earliestDate')))
                        except (ValueError, TypeError):
                            pass

            # Creation period (check for specific event names, LIDO 1.0 and 1.1 notation)
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{L}term')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.creation_period = DateList(Literal(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}displayDate'), lang = self.xml_lang(event.getparent().getparent().find('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}displayDate'))))
                        except ValueError:
                            pass
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{S}Concept/{S}prefLabel')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.creation_period = DateList(Literal(event.getparent().getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}displayDate'), lang = self.xml_lang(event.getparent().getparent().getparent().find('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}displayDate'))))
                        except ValueError:
                            pass

            # Destruction date (check for specific event names, LIDO 1.0 and 1.1 notation)
            check_terms = [
                'destruction',
                'Destruction',
                'loss',
                'Verlust',
                'Zerstörung',
                'Verlust'
            ]
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{L}term')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.destruction_date = Date(date.fromisoformat(event.getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}latestDate')))
                        except (ValueError, TypeError):
                            pass
            events = self.xml_all_elements('.//{L}eventWrap/{L}eventSet/{L}event/{L}eventType/{S}Concept/{S}prefLabel')
            if events != None:
                for event in events:
                    if event.text in check_terms:
                        try:
                            self.destruction_date = Date(date.fromisoformat(event.getparent().getparent().getparent().findtext('.//{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}latestDate')))
                        except (ValueError, TypeError):
                            pass

            # Approximate period
            #self.approximate_period = 

            # Existence period
            #self.existence_period = 


    def xml_all_lido_concepts(self, element_paths:str|list) -> list|None:
        '''
        Get all LIDO concept IDs in an XML tree according to both LIDO 1.0 and 1.1

            Parameters:
                element_paths (str|list): Element path to check, i.e. a limited implementation of XPath

            Returns:
                list|None: List of requested concept IDs
        '''

        # Get elements
        element_paths = self.xml_paths(element_paths, True)
        concepts = []

        # Concepts according to LIDO 1.0
        for element_path in element_paths:
            new_elements = self.file.xml.iterfind(element_path + '/{http://www.lido-schema.org}conceptID')
            new_concepts = []
            for new_element in new_elements:
                new_concept = new_element.text

                # Fix old Iconclass notations
                if '{http://www.lido-schema.org}source' in new_element.attrib:
                    if new_element.attrib['{http://www.lido-schema.org}source'] == 'Iconclass':
                        new_concept = 'https://iconclass.org/' + new_concept

                # Revise and add entries
                new_concepts.append(new_concept)
            concepts += new_concepts

        # Concept according to LIDO 1.1
        for element_path in element_paths:
            new_concepts = [match.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'] for match in self.file.xml.iterfind(element_path + '/{http://www.w3.org/2004/02/skos/core#}Concept[@{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about]')]
            concepts += new_concepts

        #Return unique results
        if concepts != []:
            return list(set(concepts))
        else:
            return None
