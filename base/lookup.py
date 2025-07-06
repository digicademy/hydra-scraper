# Look up types in authority files or local storage
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
import json
import logging
from httpx import Client, HTTPError
from os.path import isfile
from rdflib import URIRef, Namespace
from validators import url

# Import script modules
from base.file import File

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
TGN = Namespace('https://vocab.getty.edu/tgn/')

# Set up logging
logger = logging.getLogger(__name__)


class Lookup:


    def __init__(self, file_path:str|None = None):
        '''
        Look up types in a cached key-value store or authority filess

            Parameters:
                file_path (File): Local key-value store to read and use or create
        '''

        # Vars
        self.file_path:str|None = None
        self.keyvalue:dict = {}

        # Read and parse existing key-value store
        if file_path:
            self.file_path = file_path + '.json'
            if isfile(self.file_path):
                with open(self.file_path, 'r') as f:
                    self.keyvalue = json.loads(f.read())
                    logger.info('Look-up store read from file ' + self.file_path)


    def save(self):
        '''
        Save content of key-value store to local file
        '''

        # Save content
        if self.file_path:
            with open(self.file_path, 'w') as f:
                f.write(json.dumps(self.keyvalue, indent = 4, sort_keys = True))
                logger.info('Look-up store saved to file ' + self.file_path)
        else:
            raise ValueError('No file name indicated to save the look-up file to.')


    def check(self, uri:str) -> str|None:
        '''
        Check an authority file URI to see which of six categories it belongs to

            Parameters:
                uri (str): Authority file URI to check

            Returns:
                str|None: Shorthand of the category the URI belong to
        '''

        # Check local key-value store as a shortcut
        output = None
        if uri in self.keyvalue:
            if url(self.keyvalue[uri]):
                uri = self.keyvalue[uri]
            output = self.keyvalue[uri]

        # CLEAR CASES

        # GeoNames
        elif URIRef(uri) in GN:
            output = 'location'

        # TGN
        elif URIRef(uri) in TGN:
            output = 'location'

        # Iconclass
        elif URIRef(uri) in IC:
            output = 'subject_concept'

        # ISIL
        elif URIRef(uri) in ISIL:
            output = 'organization'

        # ANALYSE URI

        # RISM
        elif URIRef(uri) in RISM:
            if '/sources/' in uri:
                output = 'subject_concept'
            elif '/people/' in uri:
                output = 'person'
            elif '/institutions/' in uri:
                output = 'organization'

        # USE RESOLVABLE URI

        # GND
        elif URIRef(uri) in GND:
            remote = File(uri, 'text/turtle')
            if remote.success:
                if uri != remote.location: # Follow permanent redirects as they mark old/wrong entries
                    self.keyvalue[uri] = remote.location
                    uri = remote.location
                for rdf_type in remote.rdf.objects(URIRef(uri), RDF.type):
                    if rdf_type in gnd_subject_concept:
                        output = 'subject_concept'
                    elif rdf_type in gnd_person:
                        output = 'person'
                    elif rdf_type in gnd_organization:
                        output = 'organization'
                    elif rdf_type in gnd_location:
                        output = 'location'
                    elif rdf_type in gnd_event:
                        output = 'event'
            else:
                self.keyvalue[uri] = 'invalid'

        # VIAF
        elif URIRef(uri) in VIAF:
            remote = File(uri, 'application/rdf+xml')
            if remote.success:
                #if uri != remote.location: # Cannot follow permanent redirects as 301 is misused on actual authority URIs
                #    self.keyvalue[uri] = remote.location
                #    uri = remote.location
                for rdf_type in remote.rdf.objects(URIRef(uri), RDF.type):
                    if rdf_type in schema_person:
                        output = 'person'
                    elif rdf_type in schema_organisation:
                        output = 'organization'
                    elif rdf_type in schema_location:
                        output = 'location'
                    elif rdf_type in schema_event:
                        output = 'event'
            else:
                self.keyvalue[uri] = 'invalid'

        # USE SPARQL ENDPOINT

        # Getty AAT
        elif URIRef(uri) in AAT:
            output = 'subject_concept'
            query = 'SELECT ?bool WHERE { BIND(EXISTS{<' + uri + '> <http://vocab.getty.edu/ontology#broaderExtended> <' + str(AAT) + '300264092>} AS ?bool) . }'
            check = sparql('https://vocab.getty.edu/sparql', 'bool', query)
            if check:
                output = 'element_type'

        # FactGrid
        elif URIRef(uri) in FG:
            output = 'subject_concept'
            query = 'SELECT ?obj WHERE { <' + uri + '> <https://database.factgrid.de/prop/P2>/<https://database.factgrid.de/prop/statement/P2>/<https://database.factgrid.de/prop/direct/P3>* ?obj . }'
            checks = sparql('https://database.factgrid.de/sparql', 'obj', query)
            if checks:
                for check in checks:
                    if URIRef(check) in fg_person:
                        output = 'person'
                    elif URIRef(check) in fg_organization:
                        output = 'organization'
                    elif URIRef(check) in fg_location:
                        output = 'location'
                    elif URIRef(check) in fg_event:
                        output = 'event'

        # Wikidata
        elif URIRef(uri) in WD:
            output = 'subject_concept'
            query = 'SELECT ?obj WHERE { <' + uri + '> <http://www.wikidata.org/prop/P31>/<http://www.wikidata.org/prop/statement/P31>/<http://www.wikidata.org/prop/direct/P279>* ?obj . }'
            checks = sparql('https://query.wikidata.org/bigdata/namespace/wdq/sparql', 'obj', query)
            if checks:
                for check in checks:
                    if URIRef(check) in wd_person:
                        output = 'person'
                    elif URIRef(check) in wd_organization:
                        output = 'organization'
                    elif URIRef(check) in wd_location:
                        output = 'location'
                    elif URIRef(check) in wd_event:
                        output = 'event'

        # Return result
        if output:
            self.keyvalue[uri] = output
        return output


def sparql(endpoint:str, query_type:str, query:str) -> bool|list|None:
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
        'Accept': 'application/sparql-results+json',
    }

    # Prepare params
    params = {
        'query': query,
    }

    # Make request
    try:
        with Client(headers = headers, params = params, timeout = 300.0, follow_redirects = True) as client:
            r = client.get(endpoint)

            # Check response
            if r.status_code == 200:
                checks = r.json()
                logger.info('SPARQLed authority data at ' + endpoint)

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
                logger.error('SPARQL query not successful at ' + endpoint)
                return None

    # If request fails
    except HTTPError:
        logger.error('Could not SPARQL authority data at ' + endpoint)
        return None


# TYPE LISTS AND CHECKS
# Schema.org collated on 17/4/2024 
# GND and RISM collated on 17/10/2024
# WD and FG collated on 28/10/2024

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
    SCHEMA.Season,
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

schema_book = [
    SCHEMA.Book,
    SCHEMA.Audiobook,
]

schema_sculpture = [
    SCHEMA.Sculpture,
]

schema_music = [
    SCHEMA.SheetMusic,
]

# Element type (only Getty AAT needed right now)

# Subject concept

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

schema_organisation = [
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
    FG.Q160381, # Architectural structure
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
    SCHEMA.LocalBusiness,
    SCHEMA.Residence,
    SCHEMA.ApartmentComplex,
    SCHEMA.GatedResidenceCommunity,
    SCHEMA.TouristAttraction,
    SCHEMA.TouristDestination,
]

schema_structure = [
    SCHEMA.LandmarksOrHistoricalBuildings,
]

wd_location = [
    WD.Q618123, # geographical feature
    WD.Q811979, # architectural structure
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
    SCHEMA.VisualArtsEvent,
]

schema_theater = [
    SCHEMA.TheaterEvent,
]

wd_event = [
    WD.Q67518978,
]
