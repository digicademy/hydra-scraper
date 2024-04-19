# Class to transform data to a different structure
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from datetime import date
from lxml import etree
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from classes.command import *

# Define namespaces
from rdflib.namespace import RDF
SCHEMA = Namespace('http://schema.org/')
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
CTO = Namespace('https://nfdi4culture.de/ontology#')







class HydraMorph:

    # Variables
    command = None


    def __init__(self, command:HydraCommand):
        '''
        Transform data to a different structure

            Parameters:
                command (HydraCommand): configuration object for the current scraping run
        '''

        # Register user input
        self.command = command


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        return 'Morph servive to transform data to a different structure'


    def _strip_string(self, content:str) -> str:
        '''
        Takes a string, removes quotation marks, removes newlines, and returns the string

            Parameters:
                content (str): input string to clean

            Returns:
                str: cleaned output string
        '''

        # Remove offending characters
        content = content.replace('"', '\'')
        content = content.replace('\n', '')
        content = content.replace('\r', '')

        # Return clean string
        return content


    def _convert_lido_to_cgif_with_language(self, language_element:any) -> str:
        '''
        Retrieves the language of a given LIDO element

            Parameters:
                language_element (any): Element of a parsed LIDO document

            Returns:
                str: The language code of the element
        '''

        # Set up empty language variable
        language = None

        # Check for language tags and escalate inquiry to parent elements if necessary
        while language == None and language_element != None:
            if '{http://www.w3.org/XML/1998/namespace}lang' in language_element.attrib:
                language = language_element.attrib['{http://www.w3.org/XML/1998/namespace}lang']
            else:
                language_element = language_element.getparent()

        # Return language variable
        return language


    def _convert_lido_to_cgif_with_concepts(self, lido_root:any, element_path:str) -> list:
        '''
        Finds a LIDO concept IDs in an element tree according to LIDO 1.0 or 1.1

            Parameters:
                lido_root (any): The parsed LIDO document
                element_path (str): The initial segment of the element path to look for concept IDs

            Returns:
                list: A list of concept IDs
        '''

        # Set up empty set
        concept_ids = set()

        # Find concept IDs according to LIDO 1.0
        concept_list = lido_root.iterfind(element_path + '/{http://www.lido-schema.org}conceptID')
        for concept_entry in concept_list:
            concept_ids.add(concept_entry.text)

        # Find concept IDs according to LIDO 1.1
        concept_list = lido_root.iterfind(element_path + '/{http://www.w3.org/2004/02/skos/core#}Concept[@{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about]')
        for concept_entry in concept_list:
            concept_ids.add(concept_entry.attrib['{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about'])

        # Return the set of IDs
        return concept_ids


    def _convert_triples_to_table_with_ordered_lists(self, triples:object, previous:BNode) -> list:
        '''
        Helper function to page through ordered lists when querying properties to print them as a table

            Parameters:
                triples (object): Graph object containing the triples to flick through
                previous (BNode): Previous entry in the unordered list

            Returns:
                list: Further entries of the unordered list
        '''

        # Set up empty list of results to add to
        new_line_entries = []

        # Dig one level further down the ordered list
        for s, p, o in triples.triples((previous, None, None)):
            if isinstance(o, (Literal, URIRef)) and o != URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'):
                new_line_entries.append(self._strip_string(str(o)))
            elif isinstance(o, BNode):
                new_line_entries.extend(self._convert_triples_to_table_with_ordered_lists(triples, o))

        # Return the list
        return new_line_entries


    def convert_lido_to_cgif(self, lido:str, supplement_data_feed:str = '', supplement_data_catalog:str = '', supplement_data_catalog_publisher:str = '') -> Graph:
        '''
        Converts a LIDO file to CGIF triples and returns them as a Graph object

            Parameters:
                lido (str): The content of the LIDO file to convert
                supplement_data_feed (str, optional): URI of a data feed to bind LIDO files to (defaults to none)
                supplement_data_catalog (str, optional): URI of a data catalog that the data feed belongs to (defaults to none)
                supplement_data_catalog_publisher (str, optional): URI of the publisher of the data catalog (defaults to none)

            Returns:
                Graph: object containing the CGIF triples
        '''

        # Set up an object to store CGIF triples
        cgif_triples = Graph()
        cgif_triples.bind('schema', SCHEMA)

        # Parse LIDO files as XML and retrieve resource URI
        try:
            lido_root = etree.fromstring(bytes(lido, encoding='utf8'))
            resource = URIRef(lido_root.findtext('.//{http://www.lido-schema.org}recordInfoLink'))

            # RDF.type
            cgif_triples.add((resource, RDF.type, SCHEMA.VisualArtwork))

            # SCHEMA.isPartOf
            if supplement_data_feed != '':
                cgif_triples.add((resource, SCHEMA.isPartOf, URIRef(supplement_data_feed)))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.DataFeed))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.Dataset))
                cgif_triples.add((URIRef(supplement_data_feed), RDF.type, SCHEMA.URL))
                cgif_triples.add((URIRef(supplement_data_feed), SCHEMA.url, URIRef(supplement_data_feed)))

                # Add information on data catalog
                if supplement_data_catalog != '':
                    cgif_triples.add((URIRef(supplement_data_feed), SCHEMA.includedInDataCatalog, URIRef(supplement_data_catalog)))
                    cgif_triples.add((URIRef(supplement_data_catalog), RDF.type, SCHEMA.DataCatalog))

                    # Add information on publisher of data catalog
                    if supplement_data_catalog_publisher != '':
                        cgif_triples.add((URIRef(supplement_data_catalog), SCHEMA.publisher, URIRef(supplement_data_catalog_publisher)))

            # Go into the "descriptiveMetadata" section
            for lido_descriptive in lido_root.iterfind('.//{http://www.lido-schema.org}descriptiveMetadata'):

                # SCHEMA.name
                schema_names = lido_descriptive.iterfind('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}titleWrap/{http://www.lido-schema.org}titleSet/{http://www.lido-schema.org}appellationValue')
                for schema_name in schema_names:
                    language = self._convert_lido_to_cgif_with_language(schema_name)
                    if language != None:
                        cgif_triples.add((resource, SCHEMA.name, Literal(schema_name.text, lang = language)))
                    else:
                        cgif_triples.add((resource, SCHEMA.name, Literal(schema_name.text)))

                # SCHEMA.contentLocation
                schema_content_location = lido_descriptive.findtext('.//{http://www.lido-schema.org}objectIdentificationWrap/{http://www.lido-schema.org}repositoryWrap/{http://www.lido-schema.org}repositorySet/{http://www.lido-schema.org}repositoryLocation/{http://www.lido-schema.org}placeID[@{http://www.lido-schema.org}type="http://terminology.lido-schema.org/lido00099"]')
                if schema_content_location != None:
                    cgif_triples.add((resource, SCHEMA.contentLocation, URIRef(schema_content_location)))
                    cgif_triples.add((URIRef(schema_content_location), RDF.type, SCHEMA.LandmarksOrHistoricalBuildings))

                # SCHEMA.keywords: get work type, subjects, and location
                schema_keywords = set()
                schema_keywords.update(self._convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectClassificationWrap/{http://www.lido-schema.org}objectWorkTypeWrap/{http://www.lido-schema.org}objectWorkType'))
                schema_keywords.update(self._convert_lido_to_cgif_with_concepts(lido_descriptive, './/{http://www.lido-schema.org}objectRelationWrap/{http://www.lido-schema.org}subjectWrap/{http://www.lido-schema.org}subjectSet/{http://www.lido-schema.org}subject/{http://www.lido-schema.org}subjectConcept'))
                schema_keywords.add(schema_content_location)

                # SCHEMA.keywords: write property
                for schema_keyword in schema_keywords:
                    if schema_keyword != None:
                        cgif_triples.add((resource, SCHEMA.keywords, URIRef(schema_keyword)))
                        for known_defined_term_set in self.command.known_defined_term_sets:
                            if known_defined_term_set in schema_keyword:
                                cgif_triples.add((URIRef(schema_keyword), SCHEMA.inDefinedTermSet, URIRef(known_defined_term_set)))
                                cgif_triples.add((URIRef(known_defined_term_set), RDF.type, SCHEMA.DefinedTermSet))

                # SCHEMA.temporalCoverage: get start and end of earliest event
                schema_temporal_coverage_start = None
                schema_temporal_coverage_end = None
                schema_temporal_coverage_elements = lido_descriptive.iterfind('.//{http://www.lido-schema.org}eventWrap/{http://www.lido-schema.org}eventSet/{http://www.lido-schema.org}event/{http://www.lido-schema.org}eventDate/{http://www.lido-schema.org}date/{http://www.lido-schema.org}earliestDate')
                for schema_temporal_coverage_element in schema_temporal_coverage_elements:
                    if schema_temporal_coverage_start == None:
                        schema_temporal_coverage_start = date.fromisoformat(schema_temporal_coverage_element.text)
                        schema_temporal_coverage_end = date.fromisoformat(schema_temporal_coverage_element.getparent().findtext('.//{http://www.lido-schema.org}latestDate'))
                    elif schema_temporal_coverage_start > date.fromisoformat(schema_temporal_coverage_element.text):
                        schema_temporal_coverage_start = date.fromisoformat(schema_temporal_coverage_element.text)
                        schema_temporal_coverage_end = date.fromisoformat(schema_temporal_coverage_element.getparent().findtext('.//{http://www.lido-schema.org}latestDate'))

                # SCHEMA.temporalCoverage: write property
                if schema_temporal_coverage_start != None and schema_temporal_coverage_end != None:
                    schema_temporal_coverage = schema_temporal_coverage_start.isoformat() + 'T00:00:00/' + schema_temporal_coverage_end.isoformat() + 'T23:59:59'
                    cgif_triples.add((resource, SCHEMA.temporalCoverage, Literal(schema_temporal_coverage, datatype = SCHEMA.DateTime)))

            # Go into the "descriptiveMetadata" section
            for lido_administrative in lido_root.iterfind('.//{http://www.lido-schema.org}administrativeMetadata'):

                # SCHEMA.dateModified
                schema_date_modified = lido_administrative.findtext('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordInfoSet/{http://www.lido-schema.org}recordMetadataDate')
                if schema_date_modified != None:
                    cgif_triples.add((resource, SCHEMA.dateModified, Literal(schema_date_modified, datatype = SCHEMA.Date)))

                # SCHEMA.license: get all relevant licences
                schema_licences = set()
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsWorkSet/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}recordRights/{http://www.lido-schema.org}rightsType'))
                schema_licences.update(self._convert_lido_to_cgif_with_concepts(lido_administrative, './/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}rightsType'))

                # SCHEMA.license: write property
                for schema_licence in schema_licences:
                    if schema_licence != None:
                        cgif_triples.add((resource, SCHEMA.license, URIRef(schema_licence)))
                        cgif_triples.add((URIRef(schema_licence), RDF.type, SCHEMA.URL))

                # SCHEMA.width/SCHEMA.contentUrl: identify largest representation
                schema_width = 0
                schema_width_unit = ''
                schema_content_url = None
                schema_width_elements = lido_administrative.iterfind('.//{http://www.lido-schema.org}resourceWrap/{http://www.lido-schema.org}resourceSet/{http://www.lido-schema.org}resourceRepresentation/{http://www.lido-schema.org}resourceMeasurementsSet/{http://www.lido-schema.org}measurementValue')
                for schema_width_element in schema_width_elements:
                    if int(schema_width_element.text) > schema_width:

                        # Retrieve width, its unit, and content URL
                        schema_width = int(schema_width_element.text)
                        schema_width_unit = schema_width_element.getparent().find('.//{http://www.lido-schema.org}measurementUnit').xpath('string()')
                        schema_content_url = schema_width_element.getparent().getparent().findtext('.//{http://www.lido-schema.org}linkResource')

                # SCHEMA.width/SCHEMA.contentUrl: write SCHEMA.width
                if schema_width != 0:
                    if 'px' in schema_width_unit or 'pixel' in schema_width_unit or 'Pixel' in schema_width_unit:
                        schema_width_unit = ' px'
                    else:
                        schema_width_unit = ''
                    schema_width = str(schema_width) + schema_width_unit
                    cgif_triples.add((resource, SCHEMA.width, Literal(schema_width, datatype = SCHEMA.Distance)))

                # SCHEMA.width/SCHEMA.contentUrl: write SCHEMA.contentUrl
                if schema_content_url != None:
                    cgif_triples.add((resource, SCHEMA.contentUrl, URIRef(schema_content_url)))

                # SCHEMA.creditText
                schema_credit_texts = lido_administrative.iterfind('.//{http://www.lido-schema.org}resourceWrap/{http://www.lido-schema.org}resourceSet/{http://www.lido-schema.org}rightsResource/{http://www.lido-schema.org}creditLine')
                for schema_credit_text in schema_credit_texts:
                    cgif_triples.add((resource, SCHEMA.creditText, Literal(schema_credit_text.text)))

                # SCHEMA.creator
                schema_creators = lido_administrative.iterfind('.//{http://www.lido-schema.org}recordWrap/{http://www.lido-schema.org}recordSource/{http://www.lido-schema.org}legalBodyID')
                for schema_creator in schema_creators:
                    cgif_triples.add((resource, SCHEMA.creator, URIRef(schema_creator.text)))
                    cgif_triples.add((URIRef(schema_creator.text), RDF.type, SCHEMA.Organization))
                    schema_creator_name = schema_creator.getparent().find('.//{http://www.lido-schema.org}legalBodyName/{http://www.lido-schema.org}appellationValue')
                    if schema_creator_name != None:
                        language = self._convert_lido_to_cgif_with_language(schema_creator_name)
                        if language != None:
                            cgif_triples.add((URIRef(schema_creator.text), SCHEMA.name, Literal(schema_creator_name.text, lang = language)))
                        else:
                            cgif_triples.add((URIRef(schema_creator.text), SCHEMA.name, Literal(schema_creator_name.text)))
                    schema_creator_website = schema_creator.getparent().findtext('.//{http://www.lido-schema.org}legalBodyWeblink')
                    if schema_creator_website != None:
                        cgif_triples.add((URIRef(schema_creator.text), SCHEMA.url, URIRef(schema_creator_website)))

        # Empty variable if content does not parse
        except:
            cgif_triples = None

        # Return Graph object containing CGIF triples
        return cgif_triples


    def convert_triples_to_table(self, triples:object, limit_predicates:list = []) -> list:
        '''
        Converts triples into tabular data, aka a uniform two-dimensional list

            Parameters:
                triples (object): Graph object containing the triples to convert
                limit_predicates (list, optional): List of predicates to include, defaults to all

            Returns:
                list: Uniform two-dimensional list
        '''

        # Set up output and predicate lists
        output = []
        all_predicates = []
        predicates = []

        # Collect limited predicates or get all unique ones
        all_predicates = list(triples.predicates(unique = True))
        if limit_predicates != []:
            for limit_predicate in limit_predicates:
                predicates.append(URIRef(limit_predicate))
        else:
            predicates = all_predicates
            predicates.sort()

        # List all predicates as a table header
        first_line = ['URI']
        for predicate in predicates:
            first_line.append(str(predicate))
        output.append(first_line)

        # Get unique entities used as subjects that start with 'http' and go through them
        entities = list(triples.subjects(unique = True))
        entities.sort()
        for entity in entities:
            if isinstance(entity, URIRef):
                new_line = [str(entity)]

                # Set up a query routine for each desired predicate
                for predicate in predicates:
                    new_line_entries = []

                    # Go through all predicates with this entity as a subject, find literals as objects of desired predicates, and repeat for several levels
                    # Level 1
                    for all_predicate1 in all_predicates:
                        for s1, p1, o1 in triples.triples((entity, all_predicate1, None)):
                            if all_predicate1 == predicate and isinstance(o1, (Literal, URIRef)):
                                new_line_entries.append(self._strip_string(str(o1)))

                            # Ordered list, multiple levels
                            elif all_predicate1 == predicate and isinstance(o1, BNode):
                                new_line_entries.extend(self._convert_triples_to_table_with_ordered_lists(triples, o1))

                            # Nested properties, level 2
                            else:
                                for all_predicate2 in all_predicates:
                                    for s2, p2, o2 in triples.triples((o1, all_predicate2, None)):
                                        if all_predicate2 == predicate and isinstance(o2, (Literal, URIRef)):
                                            new_line_entries.append(self._strip_string(str(o2)))

                                        # Nested properties, level 3
                                        else:
                                            for all_predicate3 in all_predicates:
                                                for s3, p3, o3 in triples.triples((o2, all_predicate3, None)):
                                                    if all_predicate3 == predicate and isinstance(o3, (Literal, URIRef)):
                                                        new_line_entries.append(self._strip_string(str(o3)))

                    # Produce entry for this predicate
                    new_line_entry = ', '.join(new_line_entries)
                    new_line.append(new_line_entry)

                # Add new line to output
                output.append(new_line)

        # Return tabular data
        return output







    def convert_cgif_to_nfdi(self, cgif:Graph) -> Graph:
        '''
        Converts an existing CGIF (or schema.org) graph to nfdicore/cto and returns it

            Parameters:
                cgif (Graph): The CGIF graph to convert

            Returns:
                Graph: The nfdicore/cto version of the graph
        '''

        # Set up nfdicore/cto graph
        nfdi = Graph()
        nfdi.bind('schema', SCHEMA)
        nfdi.bind('nfdicore', NFDICORE)
        nfdi.bind('cto', CTO)

        # Set up lists of schema.org classes for data feed, person, organization, place, and event
        # Lists collated on 17/4/2024, periodical update desirable (TODO)
        schema_data_feed = [
            SCHEMA.DataFeed,
            SCHEMA.Dataset
        ]
        schema_person = [
            SCHEMA.Person,
            SCHEMA.Patient
        ]
        schema_organization = [
            SCHEMA.Organization,
            SCHEMA.Airline,
            SCHEMA.Consortium,
            SCHEMA.Corporation,
            SCHEMA.EducationalOrganization,
            SCHEMA.CollegeOrUniversity,
            SCHEMA.ElementarySchool,
            SCHEMA.HighSchool,
            SCHEMA.MiddleSchool,
            SCHEMA.Preschool,
            SCHEMA.School,
            SCHEMA.FundingScheme,
            SCHEMA.GovernmentOrganization,
            SCHEMA.LibrarySystem,
            SCHEMA.LocalBusiness,
            SCHEMA.AnimalShelter,
            SCHEMA.ArchiveOrganization,
            SCHEMA.AutomotiveBusiness,
            SCHEMA.AutoBodyShop,
            SCHEMA.AutoDealer,
            SCHEMA.AutoPartsStore,
            SCHEMA.AutoRental,
            SCHEMA.AutoRepair,
            SCHEMA.AutoWash,
            SCHEMA.GasStation,
            SCHEMA.MotorcycleDealer,
            SCHEMA.MotorcycleRepair,
            SCHEMA.ChildCare,
            SCHEMA.Dentist,
            SCHEMA.DryCleaningOrLaundry,
            SCHEMA.EmergencyService,
            SCHEMA.FireStation,
            SCHEMA.Hospital,
            SCHEMA.PoliceStation,
            SCHEMA.EmploymentAgency,
            SCHEMA.EntertainmentBusiness,
            SCHEMA.AdultEntertainment,
            SCHEMA.AmusementPark,
            SCHEMA.ArtGallery,
            SCHEMA.Casino,
            SCHEMA.ComedyClub,
            SCHEMA.MovieTheater,
            SCHEMA.NightClub,
            SCHEMA.FinancialService,
            SCHEMA.AccountingService,
            SCHEMA.AutomatedTeller,
            SCHEMA.BankOrCreditUnion,
            SCHEMA.InsuranceAgency,
            SCHEMA.FoodEstablishment,
            SCHEMA.Bakery,
            SCHEMA.BarOrPub,
            SCHEMA.Brewery,
            SCHEMA.CafeOrCoffeeShop,
            SCHEMA.Distillery,
            SCHEMA.FastFoodRestaurant,
            SCHEMA.IceCreamShop,
            SCHEMA.Restaurant,
            SCHEMA.Winery,
            SCHEMA.GovernmentOffice,
            SCHEMA.PostOffice,
            SCHEMA.HealthAndBeautyBusiness,
            SCHEMA.BeautySalon,
            SCHEMA.DaySpa,
            SCHEMA.HairSalon,
            SCHEMA.HealthClub,
            SCHEMA.NailSalon,
            SCHEMA.TattooParlor,
            SCHEMA.HomeAndConstructionBusiness,
            SCHEMA.Electrician,
            SCHEMA.GeneralContractor,
            SCHEMA.HVACBusiness,
            SCHEMA.HousePainter,
            SCHEMA.Locksmith,
            SCHEMA.MovingCompany,
            SCHEMA.Plumber,
            SCHEMA.RoofingContractor,
            SCHEMA.InternetCafe,
            SCHEMA.LegalService,
            SCHEMA.Attorney,
            SCHEMA.Notary,
            SCHEMA.Library,
            SCHEMA.LodgingBusiness,
            SCHEMA.BedAndBreakfast,
            SCHEMA.Campground,
            SCHEMA.Hostel,
            SCHEMA.Hotel,
            SCHEMA.Motel,
            SCHEMA.Resort,
            SCHEMA.SkiResort,
            SCHEMA.VacationRental,
            SCHEMA.MedicalBusiness,
            SCHEMA.Dentist,
            SCHEMA.MedicalClinic,
            SCHEMA.CovidTestingFacility,
            SCHEMA.Optician,
            SCHEMA.Pharmacy,
            SCHEMA.Physician,
            SCHEMA.IndividualPhysician,
            SCHEMA.PhysiciansOffice,
            SCHEMA.ProfessionalService,
            SCHEMA.RadioStation,
            SCHEMA.RealEstateAgent,
            SCHEMA.RecyclingCenter,
            SCHEMA.SelfStorage,
            SCHEMA.ShoppingCenter,
            SCHEMA.SportsActivityLocation,
            SCHEMA.BowlingAlley,
            SCHEMA.ExerciseGym,
            SCHEMA.GolfCourse,
            SCHEMA.HealthClub,
            SCHEMA.PublicSwimmingPool,
            SCHEMA.SkiResort,
            SCHEMA.SportsClub,
            SCHEMA.StadiumOrArena,
            SCHEMA.TennisComplex,
            SCHEMA.Store,
            SCHEMA.AutoPartsStore,
            SCHEMA.BikeStore,
            SCHEMA.BookStore,
            SCHEMA.ClothingStore,
            SCHEMA.ComputerStore,
            SCHEMA.ConvenienceStore,
            SCHEMA.DepartmentStore,
            SCHEMA.ElectronicsStore,
            SCHEMA.Florist,
            SCHEMA.FurnitureStore,
            SCHEMA.GardenStore,
            SCHEMA.GroceryStore,
            SCHEMA.HardwareStore,
            SCHEMA.HobbyShop,
            SCHEMA.HomeGoodsStore,
            SCHEMA.JewelryStore,
            SCHEMA.LiquorStore,
            SCHEMA.MensClothingStore,
            SCHEMA.MobilePhoneStore,
            SCHEMA.MovieRentalStore,
            SCHEMA.MusicStore,
            SCHEMA.OfficeEquipmentStore,
            SCHEMA.OutletStore,
            SCHEMA.PawnShop,
            SCHEMA.PetStore,
            SCHEMA.ShoeStore,
            SCHEMA.SportingGoodsStore,
            SCHEMA.TireShop,
            SCHEMA.ToyStore,
            SCHEMA.WholesaleStore,
            SCHEMA.TelevisionStation,
            SCHEMA.TouristInformationCenter,
            SCHEMA.TravelAgency,
            SCHEMA.MedicalOrganization,
            SCHEMA.Dentist,
            SCHEMA.DiagnosticLab,
            SCHEMA.Hospital,
            SCHEMA.MedicalClinic,
            SCHEMA.Pharmacy,
            SCHEMA.Physician,
            SCHEMA.VeterinaryCare,
            SCHEMA.NGO,
            SCHEMA.NewsMediaOrganization,
            SCHEMA.OnlineBusiness,
            SCHEMA.OnlineStore,
            SCHEMA.PerformingGroup,
            SCHEMA.DanceGroup,
            SCHEMA.MusicGroup,
            SCHEMA.TheaterGroup,
            SCHEMA.PoliticalParty,
            SCHEMA.Project,
            SCHEMA.FundingAgency,
            SCHEMA.ResearchProject,
            SCHEMA.ResearchOrganization,
            SCHEMA.SearchRescueOrganization,
            SCHEMA.SportsOrganization,
            SCHEMA.SportsTeam,
            SCHEMA.WorkersUnion
        ]
        schema_place = [
            SCHEMA.Place,
            SCHEMA.Accommodation,
            SCHEMA.Apartment,
            SCHEMA.CampingPitch,
            SCHEMA.House,
            SCHEMA.SingleFamilyResidence,
            SCHEMA.Room,
            SCHEMA.HotelRoom,
            SCHEMA.MeetingRoom,
            SCHEMA.Suite,
            SCHEMA.AdministrativeArea,
            SCHEMA.City,
            SCHEMA.Country,
            SCHEMA.SchoolDistrict,
            SCHEMA.State,
            SCHEMA.CivicStructure,
            SCHEMA.Airport,
            SCHEMA.Aquarium,
            SCHEMA.Beach,
            SCHEMA.BoatTerminal,
            SCHEMA.Bridge,
            SCHEMA.BusStation,
            SCHEMA.BusStop,
            SCHEMA.Campground,
            SCHEMA.Cemetery,
            SCHEMA.Crematorium,
            SCHEMA.EducationalOrganization,
            SCHEMA.EventVenue,
            SCHEMA.FireStation,
            SCHEMA.GovernmentBuilding,
            SCHEMA.CityHall,
            SCHEMA.Courthouse,
            SCHEMA.DefenceEstablishment,
            SCHEMA.Embassy,
            SCHEMA.LegislativeBuilding,
            SCHEMA.Hospital,
            SCHEMA.MovieTheater,
            SCHEMA.Museum,
            SCHEMA.MusicVenue,
            SCHEMA.Park,
            SCHEMA.ParkingFacility,
            SCHEMA.PerformingArtsTheater,
            SCHEMA.PlaceOfWorship,
            SCHEMA.BuddhistTemple,
            SCHEMA.Church,
            SCHEMA.CatholicChurch,
            SCHEMA.HinduTemple,
            SCHEMA.Mosque,
            SCHEMA.Synagogue,
            SCHEMA.Playground,
            SCHEMA.PoliceStation,
            SCHEMA.PublicToilet,
            SCHEMA.RVPark,
            SCHEMA.StadiumOrArena,
            SCHEMA.SubwayStation,
            SCHEMA.TaxiStand,
            SCHEMA.TrainStation,
            SCHEMA.Zoo,
            SCHEMA.Landform,
            SCHEMA.BodyOfWater,
            SCHEMA.Canal,
            SCHEMA.LakeBodyOfWater,
            SCHEMA.OceanBodyOfWater,
            SCHEMA.Pond,
            SCHEMA.Reservoir,
            SCHEMA.RiverBodyOfWater,
            SCHEMA.SeaBodyOfWater,
            SCHEMA.Waterfall,
            SCHEMA.Continent,
            SCHEMA.Mountain,
            SCHEMA.Volcano,
            SCHEMA.LandmarksOrHistoricalBuildings,
            SCHEMA.LocalBusiness,
            SCHEMA.Residence,
            SCHEMA.ApartmentComplex,
            SCHEMA.GatedResidenceCommunity,
            SCHEMA.TouristAttraction,
            SCHEMA.TouristDestination
        ]
        schema_event = [
            SCHEMA.Event,
            SCHEMA.BusinessEvent,
            SCHEMA.ChildrensEvent,
            SCHEMA.ComedyEvent,
            SCHEMA.CourseInstance,
            SCHEMA.DanceEvent,
            SCHEMA.DeliveryEvent,
            SCHEMA.EducationEvent,
            SCHEMA.EventSeries,
            SCHEMA.ExhibitionEvent,
            SCHEMA.Festival,
            SCHEMA.FoodEvent,
            SCHEMA.Hackathon,
            SCHEMA.LiteraryEvent,
            SCHEMA.MusicEvent,
            SCHEMA.PublicationEvent,
            SCHEMA.BroadcastEvent,
            SCHEMA.OnDemandEvent,
            SCHEMA.SaleEvent,
            SCHEMA.ScreeningEvent,
            SCHEMA.SocialEvent,
            SCHEMA.SportsEvent,
            SCHEMA.TheaterEvent,
            SCHEMA.UserInteraction,
            SCHEMA.UserBlocks,
            SCHEMA.UserCheckins,
            SCHEMA.UserComments,
            SCHEMA.UserDownloads,
            SCHEMA.UserLikes,
            SCHEMA.UserPageVisits,
            SCHEMA.UserPlays,
            SCHEMA.UserPlusOnes,
            SCHEMA.UserTweets,
            SCHEMA.VisualArtsEvent
        ]

        # Build triples about the data feed
        for dataset in cgif.subjects((RDF.type, SCHEMA.DataCatalog, True)):
            if cgif.objects():




        for data_portal in cgif.subjects((RDF.type, SCHEMA.DataCatalog, True)):
            if cgif.objects():
            
            datafeed_element_type in schema_person:
            nfdi.add((data_portal, RDF.type, NFDICORE.DataPortal))

        # Build central data feed elements
        for datafeed_element in cgif.objects((SCHEMA.DataFeedItem, SCHEMA.item, None, True)):
            nfdi.add((datafeed_element, RDF.type, CTO.DatafeedElement))
            type_identified = False

            # Perform checks for a specific nfdicore/cto type
            for datafeed_element_type in cgif.objects(datafeed_element, RDF.type, True):

                # Person
                if type_identified == False and datafeed_element_type in schema_person:
                    nfdi.add((datafeed_element, RDF.type, NFDICORE.Person))
                    type_identified == True

                # Organization
                if type_identified == False and datafeed_element_type in schema_organization:
                    nfdi.add((datafeed_element, RDF.type, NFDICORE.Organization))
                    type_identified == True

                # Place
                elif type_identified == False and datafeed_element_type in schema_place:
                    nfdi.add((datafeed_element, RDF.type, NFDICORE.Place))
                    type_identified == True

                # Event
                elif type_identified == False and datafeed_element_type in schema_event:
                    nfdi.add((datafeed_element, RDF.type, NFDICORE.Event))
                    type_identified == True

                # Item (includes creative works)
                elif type_identified == False:
                    nfdi.add((datafeed_element, RDF.type, CTO.Item))
                    type_identified == True




        # TODO:
        # - Add properties of DatafeedElement
        # - Adapt logic to single resources in addition to lists
        # - Add research information triples

"""
cto:elementOf <https://nfdi4culture.de/id/E4229> ;
nfdicore:license <https://creativecommons.org/licenses/by-nc/4.0/> ;
nfdicore:publisher <https://nfdi4culture.de/id/E1834> ;

schema:image <https://corpusvitrearum.de/typo3temp/cvma/_processed_/pics/medium/4485.jpg> ;
schema:url <https://corpusvitrearum.de/id/F4485> ;
rdfs:label "Engel mit Dudelsack"@de ;

cto:approximatePeriod "vor 1397" ;
cto:creationPeriod "1380-01-01T00:00:00/1400-12-31T23:59:59" ;
plus others of schema:temporalCoverage

cto:aat <http://vocab.getty.edu/page/aat/300263722> ;
cto:elementType <http://vocab.getty.edu/page/aat/300263722> ;
cto:elementTypeLiteral "Glaskunst (Objektgattung)"@de ;

cto:subjectConcept <https://iconclass.org/11G21> .
cto:iconclass <https://iconclass.org/11G21> ;
cto:subjectConceptLiteral
plus others of cto:externalVocabulary

cto:relatedLocation <http://sws.geonames.org/11427995> ;
cto:geonames <http://sws.geonames.org/11427995> ;
plus others of cto:externalVocabulary

cto:relatedPerson
plus others of cto:externalVocabulary

cto:relatedItem
plus others of cto:externalVocabulary

cto:relatedEvent
plus others of cto:externalVocabulary

cto:relatedOrganisation
plus others of cto:externalVocabulary

cto:sourceFile
"""
