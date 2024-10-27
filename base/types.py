# Retrieve and extract data from schema.org triples
#
# This file is part of the Hydra Scraper package.
#
# For the full copyright and license information, please read the
# LICENSE.txt file that was distributed with this source code.


# Import libraries
from rdflib import Namespace

# Define namespaces
from rdflib.namespace import SDO
#AAT = Namespace('http://vocab.getty.edu/aat/')
FG = Namespace('https://database.factgrid.de/entity/')
FG_ONT = Namespace('https://database.factgrid.de/prop/direct/')
GND = Namespace('https://d-nb.info/gnd/')
HYDRA = Namespace('http://www.w3.org/ns/hydra/core#')
RISM_ONT = Namespace('https://rism.online/api/v1#')
SCHEMA = Namespace('http://schema.org/')
WD = Namespace('http://www.wikidata.org/entity/')
WD_ONT = Namespace('http://www.wikidata.org/prop/direct/')


# - GN are location
# - IC are subject_concept
# - ISIL are organization
# - GND uses its own set of classes -> text/turtle
# - VIAF uses schema.org classes -> application/rdf+xml
# - RISM uses three own classes -> text/turtle, application/n-triples, application/ld+json

# USE SPARQL?
# - FG uses its own types and classes, FG_ONT.P2 instead of RDF.type -> text/turtle, application/n-triples, application/ld+json, application/rdf+xml
# - WD uses its own types and classes, WD_ONT.P31 instead of RDF.type -> text/turtle, application/n-triples, application/ld+json, application/rdf+xml

# Lists of GND classes collated on 17/10/2024
# TODO: WD, AAT
authority_location = [ # Plus all GN and schema_location
    GND.AdministrativeUnit,
    GND.BuildingOrMemorial,
    GND.Country,
    GND.ExtraterrestrialTerritory,
    GND.FictivePlace,
    GND.MemberState,
    GND.NameOfSmallGeographicUnitLyingWithinAnotherGeographicUnit,
    GND.NaturalGeographicUnit,
    GND.PlaceOrGeographicName,
    GND.ReligiousTerritory,
    GND.TerritorialCorporateBodyOrAdministrativeUnit,
    GND.WayBorderOrLine,
    FG.Q8,
    WD.Q486972,
]
authority_event = [ # Plus schema_event
    GND.ConferenceOrEvent,
    GND.HistoricSingleEventOrEra,
    GND.SeriesOfConferenceOrEvent,
    FG.Q9,
    WD.Q1190554,
]
authority_organization = [ # Plus all ISIL and schema_organization
    GND.Company,
    GND.CorporateBody,
    GND.FictiveCorporateBody,
    GND.MusicalCorporateBody,
    GND.OrganOfCorporateBody,
    GND.ProjectOrProgram,
    GND.ReligiousAdministrativeUnit,
    GND.ReligiousCorporateBody,
    RISM_ONT.Institution,
    FG.Q12,
    WD.Q43229,
]
authority_person = [ # Plus schema_person
    GND.CollectivePseudonym,
    GND.DifferentiatedPerson,
    GND.Gods,
    GND.LiteraryOrLegendaryCharacter,
    GND.Person,
    GND.Pseudonym,
    GND.RoyalOrMemberOfARoyalHouse,
    GND.Spirits,
    GND.UndifferentiatedPerson,
    RISM_ONT.Person,
    FG.Q7,
    WD.Q5,
]
authority_subject_concept = [ # Plus all IC and all other FG
    GND.AuthorityResource,
    GND.CharactersOrMorphemes,
    GND.Collection,
    GND.CollectiveManuscript,
    GND.EthnographicName,
    GND.Expression,
    GND.Family,
    GND.FictiveTerm,
    GND.GroupOfPersons,
    GND.Language,
    GND.Manuscript,
    GND.MeansOfTransportWithIndividualName,
    GND.MusicalWork,
    GND.NomenclatureInBiologyOrChemistry,
    GND.ProductNameOrBrandName,
    GND.ProvenanceCharacteristic,
    GND.SoftwareProduct,
    GND.SubjectHeading,
    GND.SubjectHeadingSensuStricto,
    GND.VersionOfAMusicalWork,
    GND.Work,
    RISM_ONT.Source,
]
authority_element_type = [ # Plus parts of AAT???
]


# Lists of schema.org classes collated on 17/4/2024
schema_feed = [
    SCHEMA.DataFeed,
    SCHEMA.Dataset,
    SDO.DataFeed,
    SDO.Dataset,
    HYDRA.Collection
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