# Class to retrieve and compile graph data
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Graph, Namespace
from rdflib.term import BNode, Literal, URIRef

# Import script modules
from classes.retrieve import *

# Define namespaces
from rdflib.namespace import RDF, RDFS, SDO, OWL
NFDICORE = Namespace('https://nfdi.fiz-karlsruhe.de/ontology/')
CTO = Namespace('https://nfdi4culture.de/ontology#')
MO = Namespace('http://purl.org/ontology/mo/')


class HydraRetrieveGraph(HydraRetrieve):

    # Variables
    store = None
    nfdi = None
    csv = None


    def __init__(self, report:object, store:object):
        '''
        Retrieve and compile graph data

            Parameters:
                report (object): The report object to use
                store (object): The graph to use
        '''

        # Inherit from base class
        super().__init__(report)

        # Assign argument to object
        self.store = store


    def __str__(self):
        '''
        String representation of instances of this object
        '''

        # Put together a string
        if len(self.store) > 0:
            return 'Graph containing ' + str(len(self.store)) + ' triples.'
        else:
            return 'Empty graph without any triples.'


    def morph(self, routine:str, csv_predicates:list = None):
        '''
        Morphs the graph to a different format

            Parameters:
                routine (str): Transformation routine to use
                csv_predicates (list): List of predicates to include in CSV morph
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Routine: to CSV
        if routine == 'to-csv':
            self.report.echo_progress('Producing CSV table from graph data', 0, 100)
            if self.store == None:
                status['reason'] = 'No graph data to list in a CSV table.'
            else:
                self.__morph_to_csv(csv_predicates)
                status['success'] = True
                status['reason'] = 'Graph data listed in a CSV table.'
            self.report.echo_progress('Producing CSV table from graph data', 100, 100)

        # Routine: CGIF to NFDI
        elif routine == 'cgif-to-nfdi':
            self.report.echo_progress('Converting graph data to NFDI style', 0, 100)
            if self.store == None:
                status['reason'] = 'No graph data to convert to NFDI style.'
            else:
                self.__morph_cgif_to_nfdi()
                status['success'] = True
                status['reason'] = 'Graph data converted to NFDI style.'
            self.report.echo_progress('Converting graph data to NFDI style', 100, 100)

        # Update status
        self.report.status.append(status)


    def save(self, target_folder_path:str, file_name:str, routine:str = None):
        '''
        Saves graph data to a file

            Parameters:
                target_folder_path (str): Path of the folder to create files in
                file_name (str): Name of the file to create
                routine (str): Specific data to save
        '''

        # Provide initial status
        status = {
            'success': False,
            'reason': ''
        }

        # Construct file name
        file_path = target_folder_path + '/' + file_name

        # Routine: CSV
        if routine == 'csv':
            self.report.echo_progress('Saving CSV data', 0, 100)
            if self.csv == None:
                status['reason'] = 'No CSV data to save.'
            else:
                self.__save_file(self.csv, file_path)
                status['success'] = True
                status['reason'] = 'CSV data saved to file.'
            self.report.echo_progress('Saving CSV data', 100, 100)

        # Routine: NFDI-style triples
        elif routine == 'nfdi':
            self.report.echo_progress('Saving NFDI-style triples', 0, 100)
            if self.store == None:
                status['reason'] = 'No NFDI-style triples to save.'
            else:
                self.nfdi.serialize(destination=file_path, format='turtle')
                status['success'] = True
                status['reason'] = 'NFDI-style triples saved to file.'
            self.report.echo_progress('Saving NFDI-style triples', 100, 100)

        # Routine: Triples
        else:
            self.report.echo_progress('Saving triples', 0, 100)
            if self.store == None:
                status['reason'] = 'No triples to save.'
            else:
                self.store.serialize(destination=file_path, format='turtle')
                status['success'] = True
                status['reason'] = 'Triples saved to file.'
            self.report.echo_progress('Saving triples', 100, 100)

        # Update status
        self.report.status.append(status)


    def __morph_to_csv(self, csv_predicates:list = None):
        '''
        Converts triples into tabular CSV data

            Parameters:
                csv_predicates (list): List of predicates to include
        '''

        # Set up output
        self.csv = ''
        output = []

        # Collect predicates (limited or all unique ones)
        predicates = []
        all_predicates = list(self.store.predicates(None, None, True))
        if csv_predicates != None:
            for limit_predicate in csv_predicates:
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
        entities = list(self.store.subjects(unique = True))
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
                        for object1 in self.store.objects((entity, all_predicate1, None)):
                            if all_predicate1 == predicate and isinstance(object1, (Literal, URIRef)):
                                new_line_entries.append(self.__strip_string(str(object1)))

                            # Ordered list, multiple levels
                            elif all_predicate1 == predicate and isinstance(object1, BNode):
                                new_line_entries.extend(self.__morph_to_csv_ol(self.store, object1))

                            # Nested properties, level 2
                            else:
                                for all_predicate2 in all_predicates:
                                    for object2 in self.store.objects((object1, all_predicate2, None)):
                                        if all_predicate2 == predicate and isinstance(object2, (Literal, URIRef)):
                                            new_line_entries.append(self.__strip_string(str(object2)))

                                        # Nested properties, level 3
                                        else:
                                            for all_predicate3 in all_predicates:
                                                for object3 in self.store.objects((object2, all_predicate3, None)):
                                                    if all_predicate3 == predicate and isinstance(object3, (Literal, URIRef)):
                                                        new_line_entries.append(self.__strip_string(str(object3)))

                    # Produce entry for this predicate
                    new_line_entry = ', '.join(new_line_entries)
                    new_line.append(new_line_entry)

                # Add new line to output
                output.append(new_line)

        # Save tabular data
        for output_line in output:
            self.csv += '"' + '","'.join(output_line) + '"\n'


    def __morph_to_csv_ol(self, previous:BNode) -> list:
        '''
        Helper to page through ordered lists when querying properties to print them as a CSV table

            Parameters:
                previous (BNode): Previous entry in the unordered list

            Returns:
                list: Further entries of the unordered list
        '''

        # Set up empty list
        entries = []

        # Dig one level further down the ordered list
        for entry in self.store.objects((previous, None)):
            if isinstance(entry, (Literal, URIRef)) and entry != URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#nil'):
                entries.append(self.__strip_string(str(entry)))

            # Keep digging if there is more
            elif isinstance(entry, BNode):
                entries.extend(self.__morph_to_csv_ol(entry))

        # Return list
        return entries


    def __morph_cgif_to_nfdi(self):
        '''
        Converts CGIF (or schema.org) triples to nfdicore/cto ones
        '''

        # Set up variable
        nfdi = None

        # Set up lists of schema.org classes for data feed, person, organization, place, and event
        # Lists collated on 17/4/2024, periodical update desirable (TODO)
        schema_data_feed = [
            SDO.DataFeed,
            SDO.Dataset
        ]
        schema_person = [
            SDO.Person,
            SDO.Patient
        ]
        schema_organization = [
            SDO.Organization,
            SDO.Airline,
            SDO.Consortium,
            SDO.Corporation,
            SDO.EducationalOrganization,
            SDO.CollegeOrUniversity,
            SDO.ElementarySchool,
            SDO.HighSchool,
            SDO.MiddleSchool,
            SDO.Preschool,
            SDO.School,
            SDO.FundingScheme,
            SDO.GovernmentOrganization,
            SDO.LibrarySystem,
            SDO.LocalBusiness,
            SDO.AnimalShelter,
            SDO.ArchiveOrganization,
            SDO.AutomotiveBusiness,
            SDO.AutoBodyShop,
            SDO.AutoDealer,
            SDO.AutoPartsStore,
            SDO.AutoRental,
            SDO.AutoRepair,
            SDO.AutoWash,
            SDO.GasStation,
            SDO.MotorcycleDealer,
            SDO.MotorcycleRepair,
            SDO.ChildCare,
            SDO.Dentist,
            SDO.DryCleaningOrLaundry,
            SDO.EmergencyService,
            SDO.FireStation,
            SDO.Hospital,
            SDO.PoliceStation,
            SDO.EmploymentAgency,
            SDO.EntertainmentBusiness,
            SDO.AdultEntertainment,
            SDO.AmusementPark,
            SDO.ArtGallery,
            SDO.Casino,
            SDO.ComedyClub,
            SDO.MovieTheater,
            SDO.NightClub,
            SDO.FinancialService,
            SDO.AccountingService,
            SDO.AutomatedTeller,
            SDO.BankOrCreditUnion,
            SDO.InsuranceAgency,
            SDO.FoodEstablishment,
            SDO.Bakery,
            SDO.BarOrPub,
            SDO.Brewery,
            SDO.CafeOrCoffeeShop,
            SDO.Distillery,
            SDO.FastFoodRestaurant,
            SDO.IceCreamShop,
            SDO.Restaurant,
            SDO.Winery,
            SDO.GovernmentOffice,
            SDO.PostOffice,
            SDO.HealthAndBeautyBusiness,
            SDO.BeautySalon,
            SDO.DaySpa,
            SDO.HairSalon,
            SDO.HealthClub,
            SDO.NailSalon,
            SDO.TattooParlor,
            SDO.HomeAndConstructionBusiness,
            SDO.Electrician,
            SDO.GeneralContractor,
            SDO.HVACBusiness,
            SDO.HousePainter,
            SDO.Locksmith,
            SDO.MovingCompany,
            SDO.Plumber,
            SDO.RoofingContractor,
            SDO.InternetCafe,
            SDO.LegalService,
            SDO.Attorney,
            SDO.Notary,
            SDO.Library,
            SDO.LodgingBusiness,
            SDO.BedAndBreakfast,
            SDO.Campground,
            SDO.Hostel,
            SDO.Hotel,
            SDO.Motel,
            SDO.Resort,
            SDO.SkiResort,
            SDO.VacationRental,
            SDO.MedicalBusiness,
            SDO.Dentist,
            SDO.MedicalClinic,
            SDO.CovidTestingFacility,
            SDO.Optician,
            SDO.Pharmacy,
            SDO.Physician,
            SDO.IndividualPhysician,
            SDO.PhysiciansOffice,
            SDO.ProfessionalService,
            SDO.RadioStation,
            SDO.RealEstateAgent,
            SDO.RecyclingCenter,
            SDO.SelfStorage,
            SDO.ShoppingCenter,
            SDO.SportsActivityLocation,
            SDO.BowlingAlley,
            SDO.ExerciseGym,
            SDO.GolfCourse,
            SDO.HealthClub,
            SDO.PublicSwimmingPool,
            SDO.SkiResort,
            SDO.SportsClub,
            SDO.StadiumOrArena,
            SDO.TennisComplex,
            SDO.Store,
            SDO.AutoPartsStore,
            SDO.BikeStore,
            SDO.BookStore,
            SDO.ClothingStore,
            SDO.ComputerStore,
            SDO.ConvenienceStore,
            SDO.DepartmentStore,
            SDO.ElectronicsStore,
            SDO.Florist,
            SDO.FurnitureStore,
            SDO.GardenStore,
            SDO.GroceryStore,
            SDO.HardwareStore,
            SDO.HobbyShop,
            SDO.HomeGoodsStore,
            SDO.JewelryStore,
            SDO.LiquorStore,
            SDO.MensClothingStore,
            SDO.MobilePhoneStore,
            SDO.MovieRentalStore,
            SDO.MusicStore,
            SDO.OfficeEquipmentStore,
            SDO.OutletStore,
            SDO.PawnShop,
            SDO.PetStore,
            SDO.ShoeStore,
            SDO.SportingGoodsStore,
            SDO.TireShop,
            SDO.ToyStore,
            SDO.WholesaleStore,
            SDO.TelevisionStation,
            SDO.TouristInformationCenter,
            SDO.TravelAgency,
            SDO.MedicalOrganization,
            SDO.Dentist,
            SDO.DiagnosticLab,
            SDO.Hospital,
            SDO.MedicalClinic,
            SDO.Pharmacy,
            SDO.Physician,
            SDO.VeterinaryCare,
            SDO.NGO,
            SDO.NewsMediaOrganization,
            SDO.OnlineBusiness,
            SDO.OnlineStore,
            SDO.PerformingGroup,
            SDO.DanceGroup,
            SDO.MusicGroup,
            SDO.TheaterGroup,
            SDO.PoliticalParty,
            SDO.Project,
            SDO.FundingAgency,
            SDO.ResearchProject,
            SDO.ResearchOrganization,
            SDO.SearchRescueOrganization,
            SDO.SportsOrganization,
            SDO.SportsTeam,
            SDO.WorkersUnion
        ]
        schema_place = [
            SDO.Place,
            SDO.Accommodation,
            SDO.Apartment,
            SDO.CampingPitch,
            SDO.House,
            SDO.SingleFamilyResidence,
            SDO.Room,
            SDO.HotelRoom,
            SDO.MeetingRoom,
            SDO.Suite,
            SDO.AdministrativeArea,
            SDO.City,
            SDO.Country,
            SDO.SchoolDistrict,
            SDO.State,
            SDO.CivicStructure,
            SDO.Airport,
            SDO.Aquarium,
            SDO.Beach,
            SDO.BoatTerminal,
            SDO.Bridge,
            SDO.BusStation,
            SDO.BusStop,
            SDO.Campground,
            SDO.Cemetery,
            SDO.Crematorium,
            SDO.EducationalOrganization,
            SDO.EventVenue,
            SDO.FireStation,
            SDO.GovernmentBuilding,
            SDO.CityHall,
            SDO.Courthouse,
            SDO.DefenceEstablishment,
            SDO.Embassy,
            SDO.LegislativeBuilding,
            SDO.Hospital,
            SDO.MovieTheater,
            SDO.Museum,
            SDO.MusicVenue,
            SDO.Park,
            SDO.ParkingFacility,
            SDO.PerformingArtsTheater,
            SDO.PlaceOfWorship,
            SDO.BuddhistTemple,
            SDO.Church,
            SDO.CatholicChurch,
            SDO.HinduTemple,
            SDO.Mosque,
            SDO.Synagogue,
            SDO.Playground,
            SDO.PoliceStation,
            SDO.PublicToilet,
            SDO.RVPark,
            SDO.StadiumOrArena,
            SDO.SubwayStation,
            SDO.TaxiStand,
            SDO.TrainStation,
            SDO.Zoo,
            SDO.Landform,
            SDO.BodyOfWater,
            SDO.Canal,
            SDO.LakeBodyOfWater,
            SDO.OceanBodyOfWater,
            SDO.Pond,
            SDO.Reservoir,
            SDO.RiverBodyOfWater,
            SDO.SeaBodyOfWater,
            SDO.Waterfall,
            SDO.Continent,
            SDO.Mountain,
            SDO.Volcano,
            SDO.LandmarksOrHistoricalBuildings,
            SDO.LocalBusiness,
            SDO.Residence,
            SDO.ApartmentComplex,
            SDO.GatedResidenceCommunity,
            SDO.TouristAttraction,
            SDO.TouristDestination
        ]
        schema_event = [
            SDO.Event,
            SDO.BusinessEvent,
            SDO.ChildrensEvent,
            SDO.ComedyEvent,
            SDO.CourseInstance,
            SDO.DanceEvent,
            SDO.DeliveryEvent,
            SDO.EducationEvent,
            SDO.EventSeries,
            SDO.ExhibitionEvent,
            SDO.Festival,
            SDO.FoodEvent,
            SDO.Hackathon,
            SDO.LiteraryEvent,
            SDO.MusicEvent,
            SDO.PublicationEvent,
            SDO.BroadcastEvent,
            SDO.OnDemandEvent,
            SDO.SaleEvent,
            SDO.ScreeningEvent,
            SDO.SocialEvent,
            SDO.SportsEvent,
            SDO.TheaterEvent,
            SDO.UserInteraction,
            SDO.UserBlocks,
            SDO.UserCheckins,
            SDO.UserComments,
            SDO.UserDownloads,
            SDO.UserLikes,
            SDO.UserPageVisits,
            SDO.UserPlays,
            SDO.UserPlusOnes,
            SDO.UserTweets,
            SDO.VisualArtsEvent
        ]

        # Identify main data feed
        datafeed = next(self.store.subjects((RDF.type, schema_data_feed, True)), None)
        if datafeed != None:
            if len(self.store.triples((datafeed, SDO.dataFeedElement, None, True))) > 0 or len(self.store.triples((None, SDO.isPartOf, datafeed, True))) > 0:

                # Set up nfdicore/cto graph
                nfdi = Graph()
                nfdi.bind('rdf', RDF)
                nfdi.bind('rdfs', RDFS)
                nfdi.bind('owl', OWL)
                nfdi.bind('schema', SDO)
                nfdi.bind('nfdicore', NFDICORE)
                nfdi.bind('cto', CTO)
                nfdi.bind('mo', MO)

                # Build statements about data feed
                nfdi.add((datafeed, RDF.type, NFDICORE.Dataset))
                for datafeed_same in self.store.objects((datafeed, SDO.sameAs, True)):
                    nfdi.add((datafeed, OWL.sameAs, datafeed_same))

                # Set up empty lists for higher-level metadata to use later
                datafeed_element_publishers = []
                datafeed_element_licenses = []
                datafeed_elements = []

                # Build statements about data portal
                dataportal = next(self.store.objects((datafeed, SDO.includedInDataCatalog, True)), None)
                if dataportal != None:
                    nfdi.add((dataportal, RDF.type, NFDICORE.DataPortal))
                    nfdi.add((dataportal, NFDICORE.dataset, datafeed))
                    for dataportal_same in self.store.objects((dataportal, SDO.sameAs, True)):
                        nfdi.add((dataportal, OWL.sameAs, dataportal_same))

                    # Grab portal-level metadata to use later
                    for datafeed_element_publisher in self.store.objects((dataportal, SDO.publisher, True)):
                        datafeed_element_publishers.append(datafeed_element_publisher)
                
                # Grab feed-level metadata to use later
                for datafeed_element_license in self.store.objects((datafeed, SDO.licence, True)):
                    datafeed_element_licenses.append(datafeed_element_license)

                # Collect data feed elements in lists
                for datafeed_element_schema in self.store.objects((datafeed, SDO.dataFeedElement, True)):
                    if (datafeed_element_schema, RDF.type, SDO.DataFeedItem) in self.store:
                        datafeed_element = next(self.store.objects((datafeed_element_schema, SDO.item, True)), None)
                        if datafeed_element != None:
                            datafeed_elements.append(datafeed_element)

                # Collect individual data feed elements
                for datafeed_element in self.store.subjects((SDO.isPartOf, datafeed, True)):
                    datafeed_elements.append(datafeed_element)

                # Build statements about data feed element
                for datafeed_element in datafeed_elements:
                    nfdi.add((datafeed_element, CTO.elementOf, datafeed))
                    nfdi.add((datafeed_element, RDF.type, CTO.DatafeedElement))

                    # Check for additional, specific nfdicore/cto type
                    datafeed_element_type = next(self.store.objects(datafeed_element, RDF.type, True), None)
                    if datafeed_element_type != None:
                        if datafeed_element_type in schema_person:         # Person
                            nfdi.add((datafeed_element, RDF.type, NFDICORE.Person))
                        elif datafeed_element_type in schema_organization: # Organization
                            nfdi.add((datafeed_element, RDF.type, NFDICORE.Organization))
                        elif datafeed_element_type in schema_place:        # Place
                            nfdi.add((datafeed_element, RDF.type, NFDICORE.Place))
                        elif datafeed_element_type in schema_event:        # Event
                            nfdi.add((datafeed_element, RDF.type, NFDICORE.Event))
                        else:                                              # Item (incl. creative works)
                            nfdi.add((datafeed_element, RDF.type, CTO.Item))

                    # Build statements for label
                    for datafeed_element_label in self.store.objects((datafeed_element, SDO.name, True)):
                        nfdi.add((datafeed_element, RDFS.label, datafeed_element_label))

                    # Build statements for URL
                    nfdi.add((datafeed_element, SDO.url, datafeed_element))

                    # Build statements for publisher
                    for datafeed_element_publisher in datafeed_element_publishers:
                        nfdi.add((datafeed_element, NFDICORE.publisher, datafeed_element_publisher))

                    # Build statements for license
                    if len(self.store.objects((datafeed_element, SDO.license, True))) > 0:
                        for datafeed_element_license in self.store.objects((datafeed_element, SDO.license, True)):
                            nfdi.add((datafeed_element, NFDICORE.license, datafeed_element_license))
                    else:
                        for datafeed_element_license in datafeed_element_licenses:
                            nfdi.add((datafeed_element, NFDICORE.license, datafeed_element_license))

                    # Build statements for image
                    for datafeed_element_image in self.store.objects((datafeed_element, SDO.image, True)):
                        nfdi.add((datafeed_element, SDO.image, datafeed_element_image))

                    # Build statements for lyrics
                    for datafeed_element_lyrics_schema in self.store.objects((datafeed_element, SDO.lyrics, True)):
                        datafeed_element_lyrics = next(self.store.objects((datafeed_element_lyrics_schema, SDO.text, True)), None)
                        if datafeed_element_lyrics != None:
                            nfdi.add((datafeed_element, MO.lyrics, datafeed_element_lyrics))
                            nfdi.add((datafeed_element_lyrics, RDF.type, MO.Lyrics))

                    # Build statements for date
                    for datafeed_element_date in self.store.objects((datafeed_element, SDO.temporalCoverage, True)):
                        if len(self.store.triples((datafeed_element_date, RDF.type, SDO.DateTime, True))) > 0:
                            nfdi.add((datafeed_element, CTO.creationPeriod, datafeed_element_date))
                        else:
                            nfdi.add((datafeed_element, CTO.approximatePeriod, datafeed_element_date))

                    # Build statements for external vocabularies
                    # External queries desirable to add extra triples (TODO): CTO.elementType, CTO.subjectConcept,
                    # CTO.relatedPerson, CTO.relatedOrganisation, CTO.relatedEvent, CTO.relatedLocation, CTO.relatedItem
                    for datafeed_element_vocab in self.store.objects((datafeed_element, SDO.keywords, True)):
                        if str(datafeed_element_vocab).startswith('http://sws.geonames.org/'):                  # GeoNames
                            nfdi.add((datafeed_element, CTO.geonames, datafeed_element_vocab))
                            nfdi.add((datafeed_element, CTO.relatedLocation, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('https://iconclass.org/'):                  # Iconclass
                            nfdi.add((datafeed_element, CTO.iconclass, datafeed_element_vocab))
                            nfdi.add((datafeed_element, CTO.subjectConcept, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('http://vocab.getty.edu/page/aat/'):        # Getty AAT
                            nfdi.add((datafeed_element, CTO.aat, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('https://d-nb.info/gnd/'):                  # GND
                            nfdi.add((datafeed_element, CTO.gnd, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('http://www.wikidata.org/entity/'):         # Wikidata
                            nfdi.add((datafeed_element, CTO.wikidata, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('https://viaf.org/viaf/'):                  # VIAF
                            nfdi.add((datafeed_element, CTO.viaf, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('https://rism.online/'):                    # RISM
                            nfdi.add((datafeed_element, CTO.rism, datafeed_element_vocab))
                        elif str(datafeed_element_vocab).startswith('https://database.factgrid.de/wiki/Item:'): # FactGrid
                            nfdi.add((datafeed_element, CTO.factgrid, datafeed_element_vocab))

        # Save result
        if nfdi != None:
            self.nfdi = nfdi
