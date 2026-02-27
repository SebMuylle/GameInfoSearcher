# Class Container to hold various Game's data for the search program.

class Game():
    '''Data Container to hold each game's data.'''
    def __init__(self, name:str = "No Name"):
        self.name = name
        self.steam_data = SteamData()
        self.open_c_data = OpenCriticData() 
        self.wiki_data = WikipediaData()
 
class Data():
    '''Base Class Container of games data.'''
    def __init__(self):
        self.url:str = 'not_valid_example_url.com'
        self.found_data:bool = False

class SteamData(Data):
    def __init__(self):
        super().__init__() 

        # To prevent either duplicates or incorrect data, the program will also get the title of the game on the wikipage 
        self.title_on_steam = 'NO TITLE'

        self.releaseDate = "" # Example: 'Steam: Release Date': 'Aug 7, 2024'

        self.imageURL = "NO IMAGE URL FOUND" # 'Steam: Image URL': 'imageURL.com',

        self.allReviewsText = "No user review" # 'Steam: All Reviews Text': 'Positive'
        self.allReviewsData = "No user review" # 'Steam: All Reviews - Data': '97% of the 44 user reviews for this game are positive.'
        self.allReviewsScore = 0 # 'Steam: All Reviews - Score': 0

        self.recentReviewsText = "No user review" # 'Steam: Recent Reviews - Text': 'No user review'
        self.recentReviewsData = "No user review" # 'Steam: Recent Reviews - Data': 'No user review'
        self.recentReviewsScore = 0 # 'Steam: Recent Reviews - Score': 0   

class OpenCriticData(Data):
    def __init__(self):
        super().__init__()
        
        # To prevent either duplicates or incorrect data, the program will also get the title of the game on the opencritic 
        self.title_on_oc = 'NO TITLE'

        self.openCriticRatingText = "None" # 'OpenCritic Rating': 'Mighty'
        self.topCriticAverage = 0 # 'OC: Top Critic Average': 84
        self.criticsRecommend = 0 # 'OC: Critics Recommend': 87  

class WikipediaData(Data):
    def __init__(self):
        super().__init__()

        # To prevent either duplicates or incorrect data, the program will also get the title of the game on the steam 
        self.title_on_wiki = 'NO TITLE'

        # Wiki - InfoBox Section: 
        # On Wikipedia there is either a single entity or multiple entities listed on the wiki pega
        # as a result the output can be either a single string "David David" or a list ['David One', 'David Two'] 
        self.developers = '' 
        self.publisher = ''
        self.directors = ''
        self.producer = ''
        self.designers = ''
        self.programmers = ''
        self.artists = ''
        self.writers = ''
        self.composer = ''
        self.engine = ''
        self.platforms = ''
        self.release = ''
        self.genres = ''
        self.modes = ''
        self.series = ''
        self.image = ''
        # Covers any other infobox category not listed before
        self.extra_info = {}

        # Wiki - Reception (reviews) Section:
        self.reviews_dict = {}

    def set_infobox_section(self, info:dict):
        for key in info.keys():
            match key:
                case 'Developer' | 'Developers':
                    self.developers = info[key]   
                
                case 'Publisher' | 'Publishers':
                    self.publisher = info[key] 
                
                case 'Director' | 'Directors':
                    self.directors = info[key] 
                
                case 'Producer' | 'Producers':
                    self.producer = info[key]
                
                case 'Designer' | 'Designers':
                    self.designers = info[key]
                
                case 'Programmer' | 'Programmers':
                    self.programmers = info[key]
                
                case 'Artist' | 'Artists':
                    self.artists = info[key]

                case 'Writer' | 'Writers':
                    self.writers = info[key]
                
                case 'Composer' | 'Composers':
                    self.composer = info[key]
                
                case 'Engine':
                    self.engine = info[key]

                case 'Platform' | 'Platforms':
                    self.platforms = info[key]
                
                case 'Release' | 'Release Date':
                    self.release = info[key]
                
                case 'Genre' | 'Genres':
                    self.genres = info[key]

                case 'Mode' | 'Modes':
                    self.modes = info[key]
                
                case 'Image':
                    self.image = info[key]

                case 'Series':
                    self.series = info[key]
                
                case 'Game Title On Wiki':
                    self.title_on_wiki = info[key]
                    
                case _: # If there are extra categories, add them to the extra_info variable
                    self.extra_info[key] = info[key]
    
    def set_reception_section(self, reception:dict):
        self.reviews_dict = reception.copy()   
    
    def wikiPrint(self):
        print(self.title_on_wiki)  
        print(self.developers) 
        print(self.publisher)
        print(self.directors)
        print(self.producer)
        print(self.designers)
        print(self.programmers)
        print(self.artists)
        print(self.writers)
        print(self.composer)
        print(self.engine)
        print(self.platforms)
        print(self.release)
        print(self.genres)
        print(self.modes)
        print(self.series)
        print(self.image)
        print(self.extra_info)
        print(self.reviews_dict) 