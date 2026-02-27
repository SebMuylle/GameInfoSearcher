# Game Information Searcher - by Sebastian Muylle - Version 1.0 - main.py
# Purpose: This is a script to start the program and provide instructions between the various program's class objects
 
import os

try:  
    from ClassContainers.Options import UserSettings 
    
    from ClassContainers.UserInput import UserInstructions   

except ImportError as e:
    print(e)
    print("Missing Modules in the main.py!")

try:         
    from Managers.xlsx_exporter import XlsxExporter

    from Managers.GameSearchManager import GameSearchManager

    from GUI.GameSearchGUI import GameGUI 
  
except ImportError as e:
    print(e) 
    print("Missing Modules in the main.py!") 


def main():  
    '''
    Main Function of the program. Sets up and runs all of the major components of the program.
    '''
    pathToMainFolder = str(os.path.realpath(os.path.dirname(__file__)))

    userInstructs = UserInstructions()
    userSettings = UserSettings(pathToMainFolder)
    GameGUI(userInstructs, userSettings)

    if (userInstructs.get_gameList() and userInstructs.get_start_program_value()):
        if (userInstructs.get_steam_bValue() or userInstructs.get_wiki_bValue() or userInstructs.get_opencritic_bValue()):

            gameSearcher = GameSearchManager(userInstructs, pathToMainFolder, userSettings)

            gameObjectsList, database = gameSearcher.start_search()

            xlsxExporter = XlsxExporter()

            if gameObjectsList and database:
                if xlsxExporter.export_database_games(gameObjectsList, userSettings, database):    
                    print("Xlsx File Created.\nSpread Sheet produced and saved to the following folder:")
                    print(pathToMainFolder) 


if __name__ == '__main__':
    main()
    
    
