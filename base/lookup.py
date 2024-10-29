# Look up types in authority files or local storage
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from httpx import Client
from rdflib import URIRef, Namespace

# Import script modules
from base.file import File
from base.organise import harvest_identifier

# Define namespaces
from rdflib.namespace import RDF, SDO
AAT = Namespace('http://vocab.getty.edu/aat/')
FG = Namespace('https://database.factgrid.de/entity/')
FG_API = Namespace('https://database.factgrid.de/prop/direct/')
GN = Namespace('http://sws.geonames.org/')
GND = Namespace('https://d-nb.info/gnd/')
GND_API = Namespace('https://d-nb.info/standards/elementset/gnd#')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
IC = Namespace('https://iconclass.org/')
ISIL = Namespace('https://ld.zdb-services.de/resource/organisations/')
RISM = Namespace('https://rism.online/')
RISM_API = Namespace('https://rism.online/api/v1#')
SCHEMA = Namespace('http://schema.org/')
VIAF = Namespace('http://viaf.org/viaf/')
WD = Namespace('http://www.wikidata.org/entity/')


class Lookup:


    def __init__(self, file:File|None = None):
        '''
        Look up types in authority files or local storage

            Parameters:
                file (File): Local file object to retrieve content from and save data to
        '''

        # Vars
        self.file:File|None = None

        # Include file
        if file:
            self.file = file

        # TODO Read local file if available, or start a new one
        # TODO Remember to save file after use


    def local(self):
        pass


    def sparql(self, endpoint:str, query_type:str, query:str) -> bool|list|None:
        '''
        Check whether a boolean SPARQL query returns true or false

            Parameters:
                endpoint (str): SPARQL endpoint to query
                query_type (str): Type of SPARQL query to check
                query (str): SPARQL query to send

            Returns:
                bool|list|None: Boolean or list result of the query
        '''

        # Prepare headers
        headers = {
            'User-Agent': harvest_identifier,
            'Accept': 'application/sparql-results+json',
        }

        # Prepare params
        params = {
            'query': query,
        }

        # Make request
        try:
            with Client(headers = headers, params = params, timeout = 30.0, follow_redirects = True) as client:
                r = client.get(endpoint)

                # Check response
                if r.status_code == 200:
                    checks = r.json()

                    # Boolean
                    if query_type == 'bool':
                        if checks['results']['bindings'][0]['bool']['value'] == 'true':
                            return True
                        else:
                            return False

                    # Boolean
                    if query_type == 'obj':
                        output = []
                        checks = checks['results']['bindings']
                        for check in checks:
                            output.append(check['obj']['value'])
                        return output
                    
                # If something weird happens
                else:
                    return None

        # If request fails
        except:
            return None


    def check_authority(self, uri:URIRef) -> str|None:
        '''
        Check an authority file URI to see which of six categories it belongs to

            Parameters:
                uri (URIRef): Authority file URI to check

            Returns:
                str|None: Shorthand of the category the URI belong to
        '''

        # TODO Finish authority files
        # TODO Use local first, then sparql or request per authority file
        # TODO Add labels???

        # CLEAR CASES

        # GeoNames
        if uri in GN:
            return 'location'

        # Iconclass
        elif uri in IC:
            return 'subject_concept'

        # ISIL
        elif uri in ISIL:
            return 'organization'

        # ANALYSE URI

        # RISM
        elif uri in RISM:
            output = None
            if '/sources/' in str(uri):
                output = 'subject_concept'
            elif '/people/' in str(uri):
                output = 'person'
            elif '/institutions/' in str(uri):
                output = 'organization'
            return output

        # USE RESOLVABLE URI

        # GND
        elif uri in GND:
            output = None
            remote = File(str(uri), 'text/turtle')
            if remote.success:
                for type in remote.rdf.objects(uri, RDF.type):
                    if type in gnd_subject_concept:
                        output = 'subject_concept'
                    elif type in gnd_person:
                        output = 'person'
                    elif type in gnd_organization:
                        output = 'organization'
                    elif type in gnd_location:
                        output = 'location'
                    elif type in gnd_event:
                        output = 'event'
            return output

        # VIAF
        elif uri in VIAF:
            output = None
            remote = File(str(uri), 'application/rdf+xml')
            if remote.success:
                for type in remote.rdf.objects(uri, RDF.type):
                    if type in schema_person:
                        output = 'person'
                    elif type in schema_organization:
                        output = 'organization'
                    elif type in schema_location:
                        output = 'location'
                    elif type in schema_event:
                        output = 'event'
            return output

        # USE SPARQL ENDPOINT

        # Getty AAT
        elif uri in AAT:
            object_facet = 'SELECT ?bool WHERE { BIND(EXISTS{<' + str(uri) + '> <http://vocab.getty.edu/ontology#broaderExtended> <' + str(AAT) + '300264092>} AS ?bool) . }'
            is_object_facet = self.sparql('https://vocab.getty.edu/sparql', 'bool', object_facet)
            if is_object_facet == True:
                return 'element_type'
            elif is_object_facet == False:
                return 'subject_concept'
            else:
                return None

        # FactGrid
        elif uri in FG:
            output = 'subject_concept'
            query = 'SELECT ?obj WHERE { <' + str(uri) + '> <https://database.factgrid.de/prop/P2>/<https://database.factgrid.de/prop/statement/P2>/<https://database.factgrid.de/prop/direct/P3>* ?obj . }'
            types = self.sparql('https://database.factgrid.de/sparql', 'obj', query)
            for type in types:
                if URIRef(type) in fg_person:
                    output = 'person'
                elif URIRef(type) in fg_organization:
                    output = 'organization'
                elif URIRef(type) in fg_location:
                    output = 'location'
                elif URIRef(type) in fg_event:
                    output = 'event'
            return output

        # Wikidata
        elif uri in WD:
            output = 'subject_concept'
            query = 'SELECT ?obj WHERE { <' + str(uri) + '> <http://www.wikidata.org/prop/P31>/<http://www.wikidata.org/prop/statement/P31>/<http://www.wikidata.org/prop/direct/P279>* ?obj . }'
            types = self.sparql('https://query.wikidata.org/bigdata/namespace/wdq/sparql', 'obj', query)
            for type in types:
                if URIRef(type) in wd_person:
                    output = 'person'
                elif URIRef(type) in wd_organization:
                    output = 'organization'
                elif URIRef(type) in wd_location:
                    output = 'location'
                elif URIRef(type) in wd_event:
                    output = 'event'
            return output

        # Others
        else:
            return None


# TYPE LISTS AND CHECKS
# Schema.org collated on 17/4/2024 
# GND, RISM, FG collated on 17/10/2024

# Feed (only schema.org needed right now, including variants)

schema_feed = [
    SCHEMA.DataFeed,
    SCHEMA.Dataset,
    SDO.DataFeed,
    SDO.Dataset,
    HYDRA.Collection
]

# Item (only schema.org needed right now)

schema_item = [
    SCHEMA.CreativeWork,
    SCHEMA.AmpStory,
    SCHEMA.ArchiveComponent,
    SCHEMA.Article,
    SCHEMA.AdvertiserContentArticle,
    SCHEMA.NewsArticle,
    SCHEMA.AnalysisNewsArticle,
    SCHEMA.AskPublicNewsArticle,
    SCHEMA.BackgroundNewsArticle,
    SCHEMA.OpinionNewsArticle,
    SCHEMA.ReportageNewsArticle,
    SCHEMA.ReviewNewsArticle,
    SCHEMA.Report,
    SCHEMA.SatiricalArticle,
    SCHEMA.ScholarlyArticle,
    SCHEMA.MedicalScholarlyArticle,
    SCHEMA.SocialMediaPosting,
    SCHEMA.BlogPosting,
    SCHEMA.LiveBlogPosting,
    SCHEMA.DiscussionForumPosting,
    SCHEMA.TechArticle,
    SCHEMA.APIReference,
    SCHEMA.Atlas,
    SCHEMA.Blog,
    SCHEMA.Book,
    SCHEMA.Audiobook,
    SCHEMA.Certification,
    SCHEMA.Chapter,
    SCHEMA.Claim,
    SCHEMA.Clip,
    SCHEMA.MovieClip,
    SCHEMA.RadioClip,
    SCHEMA.TVClip,
    SCHEMA.VideoGameClip,
    SCHEMA.Code,
    SCHEMA.Collection,
    SCHEMA.ProductCollection,
    SCHEMA.ComicStory,
    SCHEMA.ComicCoverArt,
    SCHEMA.Comment,
    SCHEMA.Answer,
    SCHEMA.CorrectionComment,
    SCHEMA.Question,
    SCHEMA.Conversation,
    SCHEMA.Course,
    SCHEMA.CreativeWorkSeason,
    SCHEMA.PodcastSeason,
    SCHEMA.RadioSeason,
    SCHEMA.TVSeason,
    SCHEMA.CreativeWorkSeries,
    SCHEMA.BookSeries,
    SCHEMA.MovieSeries,
    SCHEMA.Periodical,
    SCHEMA.ComicSeries,
    SCHEMA.Newspaper,
    SCHEMA.PodcastSeries,
    SCHEMA.RadioSeries,
    SCHEMA.TVSeries,
    SCHEMA.VideoGameSeries,
    SCHEMA.DataCatalog,
    SCHEMA.Dataset,
    SCHEMA.DataFeed,
    SCHEMA.CompleteDataFeed,
    SCHEMA.DefinedTermSet,
    SCHEMA.CategoryCodeSet,
    SCHEMA.Diet,
    SCHEMA.DigitalDocument,
    SCHEMA.NoteDigitalDocument,
    SCHEMA.PresentationDigitalDocument,
    SCHEMA.SpreadsheetDigitalDocument,
    SCHEMA.TextDigitalDocument,
    SCHEMA.Drawing,
    SCHEMA.EducationalOccupationalCredential,
    SCHEMA.Episode,
    SCHEMA.PodcastEpisode,
    SCHEMA.RadioEpisode,
    SCHEMA.TVEpisode,
    SCHEMA.ExercisePlan,
    SCHEMA.Game,
    SCHEMA.VideoGame,
    SCHEMA.Guide,
    SCHEMA.HowTo,
    SCHEMA.Recipe,
    SCHEMA.HowToDirection,
    SCHEMA.HowToSection,
    SCHEMA.HowToStep,
    SCHEMA.HowToTip,
    SCHEMA.HyperToc,
    SCHEMA.HyperTocEntry,
    SCHEMA.LearningResource,
    SCHEMA.Course,
    SCHEMA.Quiz,
    SCHEMA.Syllabus,
    SCHEMA.Legislation,
    SCHEMA.LegislationObject,
    SCHEMA.Manuscript,
    SCHEMA.Map,
    SCHEMA.MathSolver,
    SCHEMA.MediaObject,
    SCHEMA['3DModel'], # Alternative notation due to number
    SCHEMA.AmpStory,
    SCHEMA.AudioObject,
    SCHEMA.AudioObjectSnapshot,
    SCHEMA.Audiobook,
    SCHEMA.DataDownload,
    SCHEMA.ImageObject,
    SCHEMA.Barcode,
    SCHEMA.ImageObjectSnapshot,
    SCHEMA.LegislationObject,
    SCHEMA.MusicVideoObject,
    SCHEMA.TextObject,
    SCHEMA.VideoObject,
    SCHEMA.VideoObjectSnapshot,
    SCHEMA.MediaReviewItem,
    SCHEMA.Menu,
    SCHEMA.MenuSection,
    SCHEMA.Message,
    SCHEMA.EmailMessage,
    SCHEMA.Movie,
    SCHEMA.MusicComposition,
    SCHEMA.MusicPlaylist,
    SCHEMA.MusicAlbum,
    SCHEMA.MusicRelease,
    SCHEMA.MusicRecording,
    SCHEMA.Painting,
    SCHEMA.Photograph,
    SCHEMA.Play,
    SCHEMA.Poster,
    SCHEMA.PublicationIssue,
    SCHEMA.ComicIssue,
    SCHEMA.PublicationVolume,
    SCHEMA.Quotation,
    SCHEMA.Review,
    SCHEMA.ClaimReview,
    SCHEMA.CriticReview,
    SCHEMA.ReviewNewsArticle,
    SCHEMA.EmployerReview,
    SCHEMA.MediaReview,
    SCHEMA.Recommendation,
    SCHEMA.UserReview,
    SCHEMA.Sculpture,
    SCHEMA.Season,
    SCHEMA.SheetMusic,
    SCHEMA.ShortStory,
    SCHEMA.SoftwareApplication,
    SCHEMA.MobileApplication,
    SCHEMA.VideoGame,
    SCHEMA.WebApplication,
    SCHEMA.SoftwareSourceCode,
    SCHEMA.SpecialAnnouncement,
    SCHEMA.Statement,
    SCHEMA.TVSeason,
    SCHEMA.TVSeries,
    SCHEMA.Thesis,
    SCHEMA.VisualArtwork,
    SCHEMA.CoverArt,
    SCHEMA.ComicCoverArt,
    SCHEMA.WebContent,
    SCHEMA.HealthTopicContent,
    SCHEMA.WebPage,
    SCHEMA.AboutPage,
    SCHEMA.CheckoutPage,
    SCHEMA.CollectionPage,
    SCHEMA.MediaGallery,
    SCHEMA.ImageGallery,
    SCHEMA.VideoGallery,
    SCHEMA.ContactPage,
    SCHEMA.FAQPage,
    SCHEMA.ItemPage,
    SCHEMA.MedicalWebPage,
    SCHEMA.ProfilePage,
    SCHEMA.QAPage,
    SCHEMA.RealEstateListing,
    SCHEMA.SearchResultsPage,
    SCHEMA.WebPageElement,
    SCHEMA.SiteNavigationElement,
    SCHEMA.Table,
    SCHEMA.WPAdBlock,
    SCHEMA.WPFooter,
    SCHEMA.WPHeader,
    SCHEMA.WPSideBar,
    SCHEMA.WebSite
]

# Element type (only Getty AAT needed right now)

# Subject concept

def is_subject_concept(self, type:str) -> bool:
    '''
    Check a type URI from an authority file to see if it is a subject concept

        Parameters:
            type (str): URI of the type to check
    '''

gnd_subject_concept = [
    GND_API.AuthorityResource,
    GND_API.CharactersOrMorphemes,
    GND_API.Collection,
    GND_API.CollectiveManuscript,
    GND_API.EthnographicName,
    GND_API.Expression,
    GND_API.Family,
    GND_API.FictiveTerm,
    GND_API.GroupOfPersons,
    GND_API.Language,
    GND_API.Manuscript,
    GND_API.MeansOfTransportWithIndividualName,
    GND_API.MusicalWork,
    GND_API.NomenclatureInBiologyOrChemistry,
    GND_API.ProductNameOrBrandName,
    GND_API.ProvenanceCharacteristic,
    GND_API.SoftwareProduct,
    GND_API.SubjectHeading,
    GND_API.SubjectHeadingSensoStricto,
    GND_API.VersionOfAMusicalWork,
    GND_API.Work,
]

rism_subject_concept = [
    RISM_API.Source,
]

# Person

fg_person = [
    FG.Q7,
]

gnd_person = [
    GND_API.CollectivePseudonym,
    GND_API.DifferentiatedPerson,
    GND_API.Gods,
    GND_API.LiteraryOrLegendaryCharacter,
    GND_API.Person,
    GND_API.Pseudonym,
    GND_API.RoyalOrMemberOfARoyalHouse,
    GND_API.Spirits,
    GND_API.UndifferentiatedPerson,
]

rism_person = [
    RISM_API.Person,
]

schema_person = [
    SCHEMA.Person,
    SCHEMA.Patient
]

wd_person = [
    WD.Q5
]

# Organization

fg_organization = [
    FG.Q12,
]

gnd_organization = [
    GND_API.Company,
    GND_API.CorporateBody,
    GND_API.FictiveCorporateBody,
    GND_API.MusicalCorporateBody,
    GND_API.OrganOfCorporateBody,
    GND_API.ProjectOrProgram,
    GND_API.ReligiousAdministrativeUnit,
    GND_API.ReligiousCorporateBody,
]

rism_organization = [
    RISM_API.Institution,
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

wd_organization = [
    WD.Q43229
]

# Location

fg_location = [
    FG.Q8, # Locality
    FG.Q160381 # Architectural structure
]

gnd_location = [
    GND_API.AdministrativeUnit,
    GND_API.BuildingOrMemorial,
    GND_API.Country,
    GND_API.ExtraterrestrialTerritory,
    GND_API.FictivePlace,
    GND_API.MemberState,
    GND_API.NameOfSmallGeographicUnitLyingWithinAnotherGeographicUnit,
    GND_API.NaturalGeographicUnit,
    GND_API.PlaceOrGeographicName,
    GND_API.ReligiousTerritory,
    GND_API.TerritorialCorporateBodyOrAdministrativeUnit,
    GND_API.WayBorderOrLine,
]

schema_location = [
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

wd_location = [
    WD.Q618123, # geographical feature
    WD.Q811979 # architectural structure
]

# Event

fg_event = [
    FG.Q9,
]

gnd_event = [
    GND_API.ConferenceOrEvent,
    GND_API.HistoricSingleEventOrEra,
    GND_API.SeriesOfConferenceOrEvent,
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

wd_event = [
    WD.Q67518978
]
