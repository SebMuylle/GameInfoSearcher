# Class Container to hold the instructions needed for search program.

class UserInstructions():
    '''
    Stores the list of games from the user and also instructions for which sites to search thorugh. 
    '''
    def __init__(self):
        self.gameList = set()
        self.searchSteam = True
        self.searchOC = True
        self.searchWiki = True

        self.startProgram = False

    # Getter Methods #
    def get_gameList(self):
        return self.gameList
    
    def get_wiki_bValue(self):
        return self.searchWiki

    def get_steam_bValue(self):
        return self.searchSteam

    def get_opencritic_bValue(self):
        return self.searchOC

    def get_start_program_value(self):
        return self.startProgram

    # Setter Methods # 
    def set_game_list(self, gameNewList: set):
        self.gameList = gameNewList.copy()
    
    def set_start_program_value(self, value:bool):
        self.startProgram = value

    def set_search_bValue(self, site: str, bValue: bool):
        '''
        Sets the Boolean values for the UserInstructions Class Variables.\n 
        Used to instruct the program what site to search through.  
 
        :param site: website name to determine the boolean variable to change.
        :type site: str
        :param bValue: boolean value.
        :type bValue: bool
        '''

        match site:
            case "Steam":
                self.searchSteam = bValue
            case "OpenCritic":
                self.searchOC = bValue
            case "Wikipedia":
                self.searchWiki = bValue

        
        
