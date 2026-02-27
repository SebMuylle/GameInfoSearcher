from pathlib import Path
from openpyxl import Workbook
from openpyxl.utils import column_index_from_string
import time 
import datetime

try:      
    from ClassContainers.GameData import Game # type: ignore ##

    from ClassContainers.Options import UserSettings 

    from Managers.database_manager import DataBaseManager # type: ignore ##

except ImportError as e:
    print(e) 
    print("Missing Modules in xlsx_exporter.py")    

class XlsxExporter():
   '''Exports the data gathered and stored in the database into a Xlsx Spreadsheet'''
   def __init__(self): 
      # Column Key #
      self.colum_key_dict = {'Game Title' : 'A1',
                              'Modes' : 'B1', 
                              'Genres' : 'C1',
                              'Platforms' : 'D1',
                              'Steam: All Reviews Text': 'E1',
                              'Steam: Recent Reviews - Text': 'F1',
                              'OpenCritic Rating': 'G1',
                              'Steam: All Reviews - Data': 'H1',
                              'Steam: Recent Reviews - Data': 'I1',
                              'Steam: All Reviews - Score' : 'J1',
                              'Steam: Recent Reviews - Score' : 'K1', 
                              'OC: Top Critic Average' : 'L1',
                              'OC: Critics Recommend' : 'M1', 
                              'Wikipedia: Reviews' : 'N1',
                              'Steam: Release Date' : 'O1',
                              'Wikipedia: Release Date' : 'P1',
                              'Steam: Image URL' : 'Q1',
                              'Wikipedia: Image URL' : 'R1',
                              'Wikipedia: Game URL' : 'S1',
                              'Steam: Game URL' : 'T1', 
                              'OpenCritic: Game URL' : 'U1',
                              'Wikipedia: Title' : 'V1',
                              'Steam: Title' : 'W1',
                              'OpenCritic: Title' : 'X1',
                              'Series' : 'Y1',
                              'Developers' : 'Z1',
                              'Publishers' : 'AA1',
                              'Directors' : 'AB1',
                              'Producers' : 'AC1',
                              'Designers' : 'AD1',
                              'Programmers' : 'AE1',
                              'Artists' : 'AF1',
                              'Writers' : 'AG1',
                              'Composers' : 'AH1',
                              'Engine' : 'AI1',
                              'Wikipedia: Extra Info': 'AJ1'
                        }

   def export_database_games(self, gameList: list[Game], settings:UserSettings, database:DataBaseManager):
      '''
      Export a list of game's data to a XLSX file. 
       
      :param gameList: List of Game Objects.
      :type gameList: list[Game]
      :param settings: To get the XLSX file path. 
      :type settings: UserSettings
      :param database: To access database.
      :type database: DataBaseManager
      '''
      try: 
         print("Creating the XLSX File Now with all of the Game Information.")
         # Title of the spreadsheet using today's date
         xlsxGameSheet = f"{settings.xlsx_filename} - {self.__getCurrentDate()}.xlsx" 
         # Complete path to the location of the xlsx spreadsheet
         pathToExampleXLSX = Path(settings.export_xlsx_file_path, xlsxGameSheet)

         # Game Titles Starting Row Integar 
         row_two_start_int = 2 

         # Create a new xlsx spreadsheet 
         wb = Workbook()
         
         # Get the active workbook worksheet
         ws = wb.active
         ws.title = settings.xlsx_worksheet_title
      
         # Need to create the first row
         ws = self.__fill_first_row(ws) 

         # Starting position for the rows
         numY = 0
         for game in gameList: 
            currentRowNum = numY + row_two_start_int 

            ws = self.__updateSheetRow(ws, currentRowNum, game, database)

            numY += 1 # Add to the row number to increase it by one for next game title
         
         # Add a time delay to allow time for the sheet to be updated and saved.
         time.sleep(1)

         wb.save(pathToExampleXLSX)

         time.sleep(2)

         return True 

      except Exception as e:
         print(e)
         print("Program failed to generate a .Xlsx File to path:")
         print(pathToExampleXLSX)
         return False

   def __updateSheetRow(self, ws, currentRowNum: int, game: Game, database:DataBaseManager): 
      '''
      Updates a Sheet Row based on a current row number utilizing a game object's data and the database.
       
      :param ws: Workbook sheet
      :param currentRowNum: Number of Row.
      :type currentRowNum: int
      :param game: Game Object
      :type game: Game
      :param database: To access database.
      :type database: DataBaseManager
      '''
      for key in self.colum_key_dict.keys():
         ws = self.__updateColumnValue(ws, key, currentRowNum, database.get_data_from_table_by_column(key, game.name)) 

      return ws

   def __updateColumnValue(self, ws, key:str, currentRow, newValue): 
      '''
      Updates the cell in a row by a new value.
       
      :param ws: Workbook sheet
      :param key: Key to access the column key
      :type key: str
      :param currentRow: Number of Row.
      :param newValue: Value to put into the cell.
      '''
      columnLetter = (self.colum_key_dict[key]).split('1')[0]

      columnNumToUse = column_index_from_string(columnLetter)

      # Add the information to the correct column and row
      ws.cell(row=currentRow, 
               column=columnNumToUse, 
               value=newValue)  
      return ws

   def __getCurrentDate(self):
      '''
      Returns a string of today's date.
      '''
      d = datetime.datetime.today()
      return d.strftime('%m-%d-%Y') 

   def __fill_first_row(self, wsheet):
      '''Fill in the first row of the exported XLSX file.'''  
      for key, value in self.colum_key_dict.items():
         wsheet[value] = key

      return wsheet # Return the modified work sheet