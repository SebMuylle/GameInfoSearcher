# Game Information Searcher - by Sebastian Muylle - Version 1.0 - GameSearchManager.py
# This class is the critical part of the program that starts and manages the search for each game's information. 
# It utilizes the Database Class and the Web Hunter Classes to get and store the data found on the internet for each game.

import time, random, multiprocessing, platform, sys
from multiprocessing import Process, get_context 

try:      
    from ClassContainers.GameData import Game # type: ignore ##

    from ClassContainers.UserInput import UserInstructions # type: ignore 

    from ClassContainers.Options import UserSettings

    from Managers.database_manager import DataBaseManager # type: ignore ##

    import ClassContainers.programConsts as PC # type: ignore ##  

except ImportError as e:
    print(e) 
    print("Missing Modules in GameSearchManager.py.") 

try: 
    from web_hunters.webHunter import WebHunter 
except ImportError as e:
    print(e)
    print("Unable to import the WebHunter Parent Class")

try:
    # class object for the opencritic web hunter
    from web_hunters.opencritic_web_hunter import OpenCriticHunter

    # class object for the steam web hunter 
    from web_hunters.steam_web_hunter import SteamHunter

    # class object for the wiki web hunter
    from web_hunters.wikipedia_web_hunter import WikipediaHunter

except ImportError as e:
    print(e)
    print("Missing Modules from web hunters!")

class GameSearchManager():
    '''Manages the search for game's data on the internet and stores this data in a database.'''
    def __init__(self, userInstructions: UserInstructions, pathToMainFolder: str, userSettings: UserSettings):  

        # Web Huntesr list to contain each WebHunter utilized in the program.
        self.web_hunters_list: list[WebHunter] = []

        # Instructions inputted by the user while using the GameGUI 
        self.instructs = userInstructions

        self.settings = userSettings

        # Path to the folder where main is stored 
        self.pathMain = pathToMainFolder

        ## Database Manager
        self.database = DataBaseManager(path_to_folder=self.settings.path_to_database, database_name=self.settings.gameDataBaseName, table_name=self.settings.database_table_name) 

        # Type Hint to establish a List that will only contain Game Objects
        self.gameObjectList: list[Game] = []

        # Create a list of Game Objects to contain information about the game 
        for gameTitle in self.instructs.get_gameList():
            self.gameObjectList.append(Game(gameTitle))

        # Section to Create the Game Hunter Objects for each major site
        if self.instructs.get_wiki_bValue(): 
            self.hunter_Wikipedia = WikipediaHunter(self.settings.web_tool_headers)
            self.web_hunters_list.append(self.hunter_Wikipedia)
            
        if self.instructs.get_opencritic_bValue(): 
            self.hunter_OpenCritic = OpenCriticHunter(self.settings.web_tool_headers)
            self.web_hunters_list.append(self.hunter_OpenCritic)

        if self.instructs.get_steam_bValue(): 
            self.hunter_Steam = SteamHunter(self.settings.web_tool_headers)
            self.web_hunters_list.append(self.hunter_Steam) 

    ### General Methods for the Class ###
    def __pause_search(self):
        print(f"Pausing Searcher from {self.settings.minTimeSeconds} to {self.settings.maxTimeSeconds} seconds to prevent bot stops...")
        time.sleep(random.randint(self.settings.minTimeSeconds,self.settings.maxTimeSeconds)) 

    def start_search(self):
        '''
        Start the GameSearchManager's main programming and get the information for the games requested by the user.  
        '''
        # Starts the DataBaseManager object to confirm the Database is present and can work
        self.database.start()

        # This DataBaseManager Class Function - handles inserting new or old games into the database
        # - it handles duplicates and makes sure only unique games are added to the data base
        # - it doesn't determine whether or not the games should be searched for 
        self.database.insert_game_list(gameList=self.instructs.get_gameList())

        # To prevent duplicate information or games that have already been searched for and added to the database
        # the section below will remove games that will not be searched for from the game list  
        # and add the games that need to be updated or are new to the gamesToGetInfoList
        self.gamesToGetInfoList: list[Game] = []
        gamesToIgnoreList: list[Game] = []

        databaseCount = 0
        
        # After getting the games dates,
        # divide the games based on whether they are new (ones without update dates) or old (ones that have a last update date).
        # If they are old, the program will check if thirty dates have past since their last update and if so, go ahead and update the game's data.
        for game in self.gameObjectList:
            databaseCount += 1
            date = self.database.get_game_data_last_update(game.name)
            print("\n")
            print(f"Game: {databaseCount}")
            print(game.name)
            print(f"Last update: {date}")

            if type(date).__name__ == 'NoneType':  
                self.gamesToGetInfoList.append(game)
            elif date == 'None': 
                self.gamesToGetInfoList.append(game)
            else:
                if self.database.compareDates(date, 30): 
                    self.gamesToGetInfoList.append(game)
                else:
                    gamesToIgnoreList.append(game)


            if databaseCount % 50 == 0:
                time.sleep(1) 
        print("\n")
        print(f"Getting data for {len(self.gamesToGetInfoList)} games!")
        print(f"Ignoring the remaining {len(gamesToIgnoreList)} games.")
        
        if gamesToIgnoreList:
            print("\n")
            print("Titles that will be ignored:")
            for gameIgnore in gamesToIgnoreList:
                print(gameIgnore.name) 

        # Start the multiprocessing method to gather games' data.
        self.get_games_data_multiprocessing()

        if self.gamesToGetInfoList:
            return self.gamesToGetInfoList, self.database
        else:
            return None, None 
    
    
    def create_and_start_process(self, game:Game, brand:str, function_to_call, processesList:list[Process]):
        '''
        Creates and starts a new process for each web hunter search method.

        Returns the processes list to ensure no processes are lost.
        
        :param game: Game Object containing game data.
        :type game: Game
        :param brand: Platform - that is being searched on.
        :type brand: str
        :param function_to_call: Method to call upon.
        :param processesList: List of Process Objects
        :type processesList: list[Process]
        '''

        processSub = Process(target=self.search_one_game_info_and_update_database, args=(game, brand, function_to_call))

        processesList.append(processSub) 

        processSub.start()

        return processesList

    def create_starmap_list(self, game:Game):
        '''
        Creates a list to be used with the Pool Method's 'starmap' method. 
        '''
        starmap = []

        for web_hunter in self.web_hunters_list:
            starmap.append((game, web_hunter.brand, web_hunter.search))

        return starmap

    def get_games_data_multiprocessing(self):
        '''
        This method searches for each game's data on all platforms at the same time utilizing multiprocessing. 
        
        Any data found on the game will then be saved to the database before continuing onto the next game. 
        ''' 
        # Used to prevent freezing on Windows Platforms.
        if sys.platform.startswith('win'):
            multiprocessing.freeze_support()                      

        gameCount = 1  

        for game in self.gamesToGetInfoList:               

            self.__print_current_place_in_game_count(gameCount, game)

            if platform.system() == 'Linux': 
                # Due to the nature of multiprocessing differing on each platform, the below code has been designed to work on most Linux Platforms.
                with get_context("spawn").Pool() as p:

                    starmap_list = self.create_starmap_list(game) 

                    results = p.starmap(self.search_one_game_info_and_update_database, starmap_list)

            else:
                # This multiprocessing section will usually occur for 'non-Linux' platforms such as Windows, 
                # where the Process class is the more friendly option to pick. 
                processesInUse: list[Process] = []    

                # For each WebHunter set up and start the search process for the game's data.
                for web_hunter in self.web_hunters_list:
                    processesInUse = self.create_and_start_process(game, web_hunter.brand, web_hunter.search, processesInUse)

                # Wait to complete all processes before proceeding onto the next step
                for proc in processesInUse: 
                    proc.join()  
 
            # Finally, now that we got all four platform's data added to the database, 
            # We'll update the the game's last update date to the current date to signify we're up to date with the latest data for this game.
            self.database.update_game_new_update_date(game.name)

            print(f"\n{gameCount} of {len(self.gamesToGetInfoList)}:\nSuccessfully updated the database with the data found for {game.name}.") 
            
            # Pauses the searcher for a random set of time if the gameCount is not equal to the total of the game list
            # otherwise if they are equal, then that means we are on the last game in the list, so we can skip this pause and go ahead the exit the method
            if gameCount != len(self.gamesToGetInfoList):
                self.__pause_search()

            gameCount += 1  
 
    def __print_current_place_in_game_count(self, gameCount:int, game:Game):
        '''
        Prints a message about the current game and game count the searcher is currently on.
        
        :param gameCount: Current Game Count.
        :type gameCount: int
        :param game: Game Object to get the name of the game.
        :type game: Game
        '''
        border_sep_symbol = "#" * 60
        print(f"\n{border_sep_symbol}\n")
        print(f"Game - {gameCount} - {game.name} - \n")
 
    def search_one_game_info_and_update_database(self, game:Game, brand:str, function_to_call):
        ''' 
        Process Method: Starts, gets, and updates information gathered from the web hunter into the database.
         
        :param game: Game Object to hold the game's data.
        :type game: Game
        :param brand: Web platform - such as Wikipedia being searched for.
        :type brand: str
        :param function_to_call: Function Object that will be called in this method. 
        '''        

        function_to_call(game) 

        self.database.update_one_game_data_with_gameobj(game, brand)     