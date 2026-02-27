# Class Container to hold the settings needed for search program.

import os, ast
 
class UserSettings():
    '''
    Stores the program's settings and will be passed into the GameGUI and GameSearchManager Classes to apply these settings. 
    '''
    def __init__(self, pathToMainFolder):      
        # Directory to temporarily contain the settings of the game information searher
        self.__tempChangesDict = { "Min-WaitTime" : int, "Max-WaitTime" : int, "DataBase-Name" : str, "Path_to_Database" : str, 
                                "DataBase-TableName" : str, "XLSX_File_Name" : str, "XLSX_Worksheet_Name" : str, 
                                "Export_XLSX_File_Path" : str, "WebHeaders" : str}

        # Temporary Boolean Variables - to determine if a temporary change has been made in the settings
        self.tempChangesMadeAny = False

        self.waitTimeTempChange = False

        self.databaseTempChange = False

        self.xlsxTempChange = False 

        self.webHeadersTempChange = False

        # Path Variables to the Settings TextFile that stores the UserSettings for the program:
        self.pathToMainFolder = pathToMainFolder
        
        self.settingsFolderName = "UserSettings"

        self.txtName = "Settings.txt"

        # WaitTime Settings for the program:
        self.minTimeSeconds = 9

        self.maxTimeSeconds = 12 

        # Database File Name
        self.gameDataBaseName = "Games"
        # Database Table Name
        self.database_table_name = "GAMES"         
        # Database Folder Path
        self.path_to_database = self.pathToMainFolder 

        # XLSX File Name
        self.xlsx_filename = "Game Search Result"
        # XLSX Worksheet Title 
        self.xlsx_worksheet_title = "Info Sheet"  
        # XLSX Export Folder Path
        self.export_xlsx_file_path = self.pathToMainFolder 
 
        self.web_tool_headers = {}

        if self.__checkForSettingsFile():
            self.getSettingsFromFile()
        else:
            self.__setSettingsToFile()
 
    ### File Methods ###
    def __checkForSettingsFile(self) -> bool:
        pathToUserSettingsFolder = os.path.join(self.pathToMainFolder, self.settingsFolderName)
        pathToUserSettingsTxt = os.path.join(self.pathToMainFolder, self.settingsFolderName, self.txtName)

        if os.path.exists(pathToUserSettingsFolder) and os.path.exists(pathToUserSettingsTxt):
            return True 
        else:
            return False  

    def getSettingsFromFile(self):
        pathToUserSettingsTxt = os.path.join(self.pathToMainFolder, self.settingsFolderName, self.txtName)

        with open(pathToUserSettingsTxt, mode='r', encoding='utf-8') as file:
            for line in file:
                rowItem = line.strip().split(":", 1)
                rowItem[1] = str(rowItem[1].strip()) 
                if str(rowItem[1]).isdigit():
                    self.__tempChangesDict[rowItem[0]] = int(rowItem[1])
                else:
                    self.__tempChangesDict[rowItem[0]] = str(rowItem[1])
                
                if rowItem[0] == "WebHeaders":
                    convertedDict = ast.literal_eval(rowItem[1])
                    self.__tempChangesDict[rowItem[0]] = convertedDict

                if rowItem[0] == "Path_to_Database" or rowItem[0] == "Export_XLSX_File_Path":
                    try:
                        if rowItem[1].strip() == '.' or rowItem[1].strip() == '':
                            self.__tempChangesDict[rowItem[0]] = str(self.pathToMainFolder)
                    except:
                        self.__tempChangesDict[rowItem[0]] = str(self.pathToMainFolder)
            
            file.close()

        self.__tempChangesMade("All")

        self.saveTempDictChange()

    def __setSettingsToFile(self):
        pathToUserSettingsTxt = os.path.join(self.pathToMainFolder, self.settingsFolderName, self.txtName) 
        pathToUserSettingsFolder = os.path.join(self.pathToMainFolder, self.settingsFolderName)

        if not os.path.exists(pathToUserSettingsFolder):
            os.mkdir(pathToUserSettingsFolder)
        
        with open(pathToUserSettingsTxt, mode='w', encoding='utf-8') as file:
            file.write(f"Min-WaitTime: {self.minTimeSeconds}\n")
            file.write(f"Max-WaitTime: {self.maxTimeSeconds}\n")
            file.write(f"DataBase-Name: {self.gameDataBaseName}\n")
            file.write(f"DataBase-TableName: {self.database_table_name}\n")
            file.write(f"Path_to_Database: {self.path_to_database}\n")
            file.write(f"XLSX_File_Name: {self.xlsx_filename}\n")
            file.write(f"XLSX_Worksheet_Name: {self.xlsx_worksheet_title}\n")
            file.write(f"Export_XLSX_File_Path: {self.export_xlsx_file_path}\n")
            file.write(f"WebHeaders: {str(self.web_tool_headers)}")
            file.close()
     
    ### Print Methods ###
    def printSettingsPerm(self):
        print(self.pathToMainFolder)

        print(self.settingsFolderName) 

        print(self.txtName)   

        print(self.minTimeSeconds)

        print(self.maxTimeSeconds) 

        print(self.gameDataBaseName)

        print(self.database_table_name) 

        print(self.path_to_database)  

        print(self.xlsx_filename)

        print(self.xlsx_worksheet_title) 

        print(self.export_xlsx_file_path)  

        print(self.web_tool_headers) 


    def printTempDict(self):
        for key, value in self.__tempChangesDict.items():
            print(key, value)
            print(type(value))
    
    ### Setters/Getters for the Temporary Dictionary ###
    def setWaitTimeTempDict(self, min, max):

        self.__tempChangesDict["Min-WaitTime"] = min

        self.__tempChangesDict["Max-WaitTime"] = max

        self.__tempChangesMade("WaitTime")

    def getWaitTimeTempDict(self):

        return self.__tempChangesDict["Min-WaitTime"], self.__tempChangesDict["Max-WaitTime"] 

    ###
    def setDataBaseTempDict(self, database_name, new_path, table_name):

        self.__tempChangesDict["DataBase-Name"] = database_name

        self.__tempChangesDict["Path_to_Database"] = new_path

        self.__tempChangesDict["DataBase-TableName"] = table_name

        self.__tempChangesMade("DataBase")
 
    def getDataBaseTempDict(self):
        return self.__tempChangesDict["DataBase-Name"], self.__tempChangesDict["Path_to_Database"], self.__tempChangesDict["DataBase-TableName"]
    ###
    def setXlsxTempDict(self, filename, worksheet, filepath):
        self.__tempChangesDict["XLSX_File_Name"] = filename

        self.__tempChangesDict["XLSX_Worksheet_Name"] = worksheet

        self.__tempChangesDict["Export_XLSX_File_Path"] = filepath

        self.__tempChangesMade("SpreadSheet")  

    def getXlsxTempDict(self):
        return self.__tempChangesDict["XLSX_File_Name"], self.__tempChangesDict["XLSX_Worksheet_Name"], self.__tempChangesDict["Export_XLSX_File_Path"]
    ###
    def setWebHeadersTempDict(self, webDict):
        self.__tempChangesDict["WebHeaders"] = ast.literal_eval(webDict) 

        self.__tempChangesMade("WebHunters")   
    
    def getWebHeadersTempDict(self):
        return str(self.__tempChangesDict["WebHeaders"])
    ###

    ############################################## 
    ######## Temporary Dictionary Methods ########
    def clearTempChangesMade(self):
        self.tempChangesMadeAny = False

        self.waitTimeTempChange = False

        self.databaseTempChange = False

        self.xlsxTempChange = False 

        self.webHeadersTempChange = False
        
        self.__tempChangesDict.clear()       

        self.__tempChangesDict = { "Min-WaitTime" : int, "Max-WaitTime" : int, "DataBase-Name" : str, "Path_to_Database" : str, 
                                    "DataBase-TableName" : str, "XLSX_File_Name" : str, "XLSX_Worksheet_Name" : str, 
                                    "Export_XLSX_File_Path" : str, "WebHeaders" : str}

    def saveTempDictChange(self):
        '''
        Saves the Temporary Changes to the Settings Object's Member variables
        '''
        if self.tempChangesMadeAny:

            if self.waitTimeTempChange:
                self.minTimeSeconds = self.__tempChangesDict["Min-WaitTime"]

                self.maxTimeSeconds = self.__tempChangesDict["Max-WaitTime"]

            if self.databaseTempChange:
                if os.path.exists(self.__tempChangesDict["Path_to_Database"]):
                    self.path_to_database = self.__tempChangesDict["Path_to_Database"] 
                else:
                    print(f"Database Folder Path doesn't exist. Setting to default folder path:\n{self.pathToMainFolder}")
                    self.path_to_database = self.pathToMainFolder

                self.gameDataBaseName = self.__tempChangesDict["DataBase-Name"]

                self.database_table_name = self.__tempChangesDict["DataBase-TableName"]    

            if self.xlsxTempChange:              
                if os.path.exists(self.__tempChangesDict["Export_XLSX_File_Path"]):
                    self.export_xlsx_file_path = self.__tempChangesDict["Export_XLSX_File_Path"]
                else:
                    print(f"Export Folder Path doesn't exist. Setting to default folder path:\n{self.pathToMainFolder}")
                    self.export_xlsx_file_path = self.pathToMainFolder

            if self.webHeadersTempChange:
                self.web_tool_headers = self.__tempChangesDict["WebHeaders"]

            self.clearTempChangesMade()

            self.__setSettingsToFile()

    def __tempChangesMade(self, settingsChanged:str):
        '''
        Method to set which Temporary Changes have been made.

        :param settingsChanged: Name of the Temporary Setting that has been changed. 
        :type settingsChanged: str
        '''
        self.tempChangesMadeAny = True

        match settingsChanged:
            case "All":
                self.waitTimeTempChange = True

                self.databaseTempChange = True

                self.xlsxTempChange = True

                self.webHeadersTempChange = True
            case "WaitTime":
                self.waitTimeTempChange = True
            
            case "DataBase":
                self.databaseTempChange = True
            
            case "SpreadSheet":
                self.xlsxTempChange = True

            case "WebHunters":
                self.webHeadersTempChange = True