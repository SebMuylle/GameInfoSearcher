import sqlite3, os, datetime  

try:  
    import ClassContainers.programConsts as PC # type: ignore ##
    
    from ClassContainers.GameData import Game # type: ignore ##

except ImportError as e:
    print(e) 
    print("Missing Modules in database_manager.py.") 


class DataBaseManager():
    '''
    This database manager class imports and exports game's data to a database\n
    and handles managing and updating the database whenever a search is completed.\n  
    '''
    def __init__(self, path_to_folder:str, database_name:str="default", table_name:str="default"):
        
        self.path_to_database = os.path.join(path_to_folder, (database_name + ".db")) 

        self.table_name = table_name

        self.primary_key = "ID"

        self.database_game_to_id_key = {}
        # Spreadsheet To Database Column Name Key Guide
        self.spreadsheet_to_database_dict = {
            'Game Title' : 'Title',
            'Modes' : 'Modes', 
            'Genres' : 'Genres',
            'Platforms' : 'Platforms',
            'Steam: All Reviews Text': 'SteamAllText',
            'Steam: Recent Reviews - Text': 'SteamRecentText',
            'OpenCritic Rating': 'OpenCriticRating',
            'Steam: All Reviews - Data': 'SteamAllData',
            'Steam: Recent Reviews - Data': 'SteamRecentData',
            'Steam: All Reviews - Score' : 'SteamAllScore',
            'Steam: Recent Reviews - Score' : 'SteamRecentScore', 
            'OC: Top Critic Average' : 'OpenCriticAverage',
            'OC: Critics Recommend' : 'OpenCriticRecommend', 
            'Wikipedia: Reviews' : 'WikiReviews',
            'Steam: Release Date' : 'SteamReleaseDate',
            'Wikipedia: Release Date' : 'WikiReleaseDate',
            'Steam: Image URL' : 'SteamImageURL',
            'Wikipedia: Image URL' : 'WikiImageURL',
            'Wikipedia: Game URL' : 'WikiURL',
            'Steam: Game URL' : 'SteamURL', 
            'OpenCritic: Game URL' : 'OpenCriticURL',
            'Wikipedia: Title' : 'WikiTitle',
            'Steam: Title' : 'SteamTitle',
            'OpenCritic: Title' : 'OpenCriticTitle',
            'Series' : 'Series',
            'Developers' : 'Developers',
            'Publishers' : 'Publishers',
            'Directors' : 'Directors',
            'Producers' : 'Producers',
            'Designers' : 'Designers',
            'Programmers' : 'Programmers',
            'Artists' : 'Artists',
            'Writers' : 'Writers',
            'Composers' : 'Composers',
            'Engine' : 'Engine',
            'Wikipedia: Extra Info': 'ExtraWikiInfo'
        }
 
    def start(self):
        '''
        Checks if there is a database for the DataBaseManager class to connect to,
        otherwise it will create a new database.
        '''
        if self.__check_for_database(): 
            print("Connected to database.")
        else: 
            self.__create_sqlite_database()
            print("Database created.")
    
    def __check_for_database(self):
        '''Checks if the database exists based on a path.'''
        return os.path.isfile(self.path_to_database) 

    def get_database_version():
        '''Used to get the current version of the SQL database.'''
        print(sqlite3.sqlite_version)
    
    def __create_sqlite_database(self):
        '''Create a database file and set up a table.'''  
        try:   
            conn = sqlite3.connect(self.path_to_database)

            conn.execute(f'''CREATE TABLE {self.table_name}
                        (
                        {self.primary_key} INT PRIMARY KEY NOT NULL,
                        Title TEXT, 
                        Modes TEXT,
                        Genres TEXT,
                        Platforms TEXT,
                        SteamAllText TEXT,
                        SteamRecentText TEXT,
                        OpenCriticRating CHAR(6),
                        SteamAllData TEXT,
                        SteamRecentData TEXT,
                        SteamAllScore TINYINT,
                        SteamRecentScore TINYINT,
                        OpenCriticAverage TINYINT,
                        OpenCriticRecommend TINYINT,
                        WikiReviews TEXT,
                        SteamReleaseDate TEXT,
                        WikiReleaseDate TEXT,
                        SteamImageURL TEXT,
                        WikiImageURL TEXT,
                        WikiURL TEXT,
                        SteamURL TEXT,
                        OpenCriticURL TEXT,
                        WikiTitle TEXT,
                        SteamTitle TEXT,
                        OpenCriticTitle TEXT,
                        Series TEXT,
                        Developers TEXT,
                        Publishers TEXT,
                        Directors TEXT,
                        Producers TEXT,
                        Designers TEXT,
                        Programmers TEXT,
                        Artists TEXT,
                        Writers TEXT,
                        Composers TEXT,
                        Engine TEXT,
                        ExtraWikiInfo TEXT,
                        LastUpdate TEXT
                        ); 
    ''')
        except sqlite3.Error as e:
            print(e) 
        finally:
            print("Table created successfully!")
            conn.close()            

    def insert_game_list(self, gameList: list):
        '''
        Insert games into the database.\n
        Checks if the game title is in the database, before inserting them.
         
        :param gameList: List of game titles 
        :type gameList: list
        ''' 
        lastIndex = self.__get_last_game_id() # Gets the last index ID of the games database.
        indexCount = 0
        dataToAdd = []

        if lastIndex == 0: 
            # If the last Index is zero then that means there is no existing data,  
            # so it's ok to insert all games into the database 
            for game in gameList:
                indexCount += 1

                self.database_game_to_id_key[game] = indexCount

                one_game_data = (indexCount, game)
                dataToAdd.append(one_game_data) 
            
            converted_data_list = tuple(dataToAdd)

            sql_command = f""" INSERT INTO {self.table_name} ({self.primary_key}, Title) VALUES (?, ?) """

            self.__executemany_commit_sql_command(sql_command, converted_data_list)  
        
        else:            
            gamesNotInDataBase = []

            gamesInDataBase = []

            completeSQLGameList = self.__get_all_games_by_id_and_title_list()
            # example list - [(1, 'Game1'), (2, 'Game2'), (3, "Game3")]

            # First grab every game title in the database and its ID 
            for gameData in completeSQLGameList:
                gamesInDataBase.append(gameData[1]) # Gets the title of the game from the SQL data row and adds it to the gamesInDataBase list
                self.database_game_to_id_key[gameData[1]] = gameData[0] # Sets the game title to its ID key for easier insert operations  
            
            # Check each game in the provided game list if it is in the database or not
            for gameTitle in gameList:
                if gameTitle not in gamesInDataBase: # if the game isn't in the database, then go ahead and aded it to the gamesNotInDataBase list
                    gamesNotInDataBase.append(gameTitle)

            # If there are games that are not in the database, go ahead and add them to the database
            if gamesNotInDataBase: 
                print(f"New Games Added - Adding {len(gamesNotInDataBase)} games to the database now.")

                indexCount = lastIndex 

                for gameTitle in gamesNotInDataBase:
                    indexCount += 1

                    self.database_game_to_id_key[gameTitle] = indexCount

                    one_game_data = (indexCount, gameTitle)
                    dataToAdd.append(one_game_data) 
                
                print(f"New index account is {indexCount}")
                converted_data_list = tuple(dataToAdd)

                sql_command = f""" INSERT INTO {self.table_name} ({self.primary_key}, Title) VALUES (?, ?) """

                self.__executemany_commit_sql_command(sql_command, converted_data_list) 

            else:
                print("There are no new games to add to the database.")

    #############################################################################################################
    ######### EXECUTE SQL COMMANDS ######################
    def __executemany_commit_sql_command(self, sql_command:str, converted_data_list):
        '''
        Execute multiple line commands to modify and change data in the database.
         
        :param sql_command: SQL Query Command instructing the database what to do with the data.
        :type sql_command: str
        :param converted_data_list: List containing the data that will be inserted, added, or changed.
        ''' 
        try:  
            conn = sqlite3.connect(self.path_to_database) 

            cursor = conn.cursor() 

            cursor.executemany(sql_command, converted_data_list)

            conn.commit()

        except sqlite3.Error as e:
            print(e)
            print("Failed to excecute the executemany command and add the new list of data into the database!")
        
        finally:
            conn.close()
 
    def __execute_commit_sql_command(self, sql_command:str):
        '''
        Execute a single line command to modify and change data in the database.
         
        :param sql_command: SQL Query Command instructing the database what to do with the data.
        :type sql_command: str 
        '''  
        try:  
            conn = sqlite3.connect(self.path_to_database) 

            cursor = conn.cursor() 

            cursor.execute(sql_command) 

            conn.commit() 

        except sqlite3.Error as e:
            print(e) 
            print(f"Failed to update the database with the following command:\n{sql_command}") 

        finally: 
            conn.close()

    #############################################################################################
    ############################################################################
    # Data Conversion Section #
    # Each function checks the type of data being inputted into the database
    # and converts or changes it to be more friendly to the database when it is added.

    def __string_value_check(self, value):
        '''
        Checks if the value is a string and if it is not, returns a zero.\n
        Used for whenever adding numbers to the database.
        
        :param value: String or other type of data.
        '''
        newValue = 0
        if not type(value).__name__ == 'str':
            newValue = value 
        return newValue

    def check_container_type(self, container:dict|list):
        '''
        Checks the data type of the container and converts it to a friendly string statement\n 
        for it to be inserted into the database.

        :param container: Data List Container. 
        :type container: dict | list
        '''
        if type(container).__name__ == "dict":
            return self.convert_dict_to_str(container)
        if type(container).__name__=='list':
            return self.convert_list_to_str(container)
        if type(container).__name__=='str':
            return str(container)

    def convert_dict_to_str(self, value:dict) -> str:
        '''
        Converts a Dictionary Container into a friendly string statement\n
        for it to be inserted into the database.
        
        :param value: Dictionary containing data to be inserted into the database.
        :type value: dict
        :return: String Statement
        :rtype: str
        '''
        newString = ' | '
        listStr: list[str] = []

        for key, item in value.items():
            if type(item).__name__ == 'list':
                convertedListStr = self.convert_list_to_str(item)
                line = key + " : " + convertedListStr
            if type(item).__name__=='str': 
                line = key + " : " + item
            listStr.append(line)
    
        return newString.join(listStr)

    def convert_list_to_str(self, value:list) -> str:
        '''
        Converts a Dictionary Container into a friendly string statement\n
        for it to be inserted into the database.
        
        :param value: List containing data to be inserted into the database.
        :type value: list
        :return: String Statement
        :rtype: str
        '''
        newString = ' | ' 
        listStr: list[str] = []
        for item in value:
            if not type(item).__name__ == 'str':
                pass
            else: 
                listStr.append(item) 
        return newString.join(listStr) 
    
    def apostrophe_string_check(self, value:str) -> str:
        '''
        Checks for any Apostrophes -> ' and replaces them with a Dash.
        This is to prevent insertion errors when inserting into the Database.
        '''
        if "\'" in value:
            value = value.replace('\'', '-')

        return value

    ########################################################################################################################################
    ########################################################################################################################################
    ############################# UPDATING DATABASE WITH ONE GAME SECTION #################################################################
    ########################################################################################################################################
    ########################################################################################################################################

    #################################################
    ###    Update DataBase with Game Object       ###
    #################################################
    def update_one_game_data_with_gameobj(self, gameObject: Game, brand: str):
        '''
        Updates the database using a game object's data and indicting which brand to update for.
         
        :param gameObject: Game Object containing data on the game. 
        :type gameObject: Game
        :param brand: Website Brand/Platform to update the database on.
        :type brand: str
        '''
        if brand == PC.OPENCRITIC_BRAND:
            line_info = self.__create_set_and_where_one_gameObj_opencritic_data(gameObject)

        elif brand == PC.STEAM_BRAND: 
            line_info = self.__create_set_and_where_one_gameObj_steam_data(gameObject)

        elif brand == PC.WIKIPEDIA_BRAND:
            line_info = self.__create_set_and_where_one_gameObj_wiki_data(gameObject)

        # SQL Command to update the one game
        sql_command = f""" UPDATE {self.table_name} {line_info}"""

        self.__execute_commit_sql_command(sql_command)
 
    def __create_set_and_where_one_gameObj_wiki_data(self, gameObj: Game) -> str:     
        '''
        Utilizes the Game Object to get the Wikipedia Data from the object\n
        to create the necessary set and where sql string command line.
         
        :param gameObj: Game Object containing data on the game. 
        :type gameObj: Game
        :return: SQL Command Statement
        :rtype: str
        '''   

        # Lambda Function to insert a 'n/a' whenever there is no data or valid data contained within the Game Object's variable
        empty_value_check = lambda x: 'n/a' if x == '' or x == [] or x == {} or x == None else x  

        if gameObj.wiki_data.found_data:
            mode = empty_value_check(self.check_container_type(gameObj.wiki_data.modes))
            genres = empty_value_check(self.check_container_type(gameObj.wiki_data.genres))
            platforms = empty_value_check(self.check_container_type(gameObj.wiki_data.platforms))
            wikiReviews = empty_value_check(self.check_container_type(gameObj.wiki_data.reviews_dict))
            releaseDate = empty_value_check(self.check_container_type(gameObj.wiki_data.release))
            imageURL = empty_value_check(self.check_container_type(gameObj.wiki_data.image))
            titleOnWebsite = self.apostrophe_string_check(empty_value_check(self.check_container_type(gameObj.wiki_data.title_on_wiki)))
            series = empty_value_check(self.check_container_type(gameObj.wiki_data.series))
            developers = empty_value_check(self.check_container_type(gameObj.wiki_data.developers))
            publishers = empty_value_check(self.check_container_type(gameObj.wiki_data.publisher))
            directors = empty_value_check(self.check_container_type(gameObj.wiki_data.directors))
            producers = empty_value_check(self.check_container_type(gameObj.wiki_data.producer))
            designers = empty_value_check(self.check_container_type(gameObj.wiki_data.designers))
            programmers = empty_value_check(self.check_container_type(gameObj.wiki_data.programmers))
            artists = empty_value_check(self.check_container_type(gameObj.wiki_data.artists))
            writers = empty_value_check(self.check_container_type(gameObj.wiki_data.writers))
            composers = empty_value_check(self.check_container_type(gameObj.wiki_data.composer))
            engine = empty_value_check(self.check_container_type(gameObj.wiki_data.engine))
            extraInfo = empty_value_check(self.check_container_type(gameObj.wiki_data.extra_info))
            gameURL = empty_value_check(self.check_container_type(gameObj.wiki_data.url)) 
        else: 
            mode = 'n/a'
            genres = 'n/a'
            platforms = 'n/a'
            wikiReviews = 'n/a'
            releaseDate = 'n/a'
            imageURL = 'n/a'
            titleOnWebsite = 'Not Found'
            series = 'n/a'
            developers = 'n/a'
            publishers = 'n/a'
            directors = 'n/a'
            producers = 'n/a'
            designers = 'n/a'
            programmers = 'n/a'
            artists = 'n/a'
            writers = 'n/a'
            composers = 'n/a'
            engine = 'n/a'
            extraInfo = 'n/a'
            gameURL = 'No URL'

        # SQL Command to update the one game
        line_info = f"""SET Modes = '{mode}', Genres = '{genres}', Platforms = '{platforms}', WikiReviews = '{wikiReviews}', WikiReleaseDate = '{releaseDate}', WikiImageURL = '{imageURL}', WikiTitle = '{titleOnWebsite}', Series = '{series}', Developers = '{developers}', Publishers = '{publishers}', Directors = '{directors}', Producers = '{producers}', Designers = '{designers}', Programmers = '{programmers}', Artists = '{artists}', Writers = '{writers}', Composers = '{composers}', Engine = '{engine}', ExtraWikiInfo = '{extraInfo}', WikiURL = '{gameURL}' {self.__create_where_id_line(gameObj.name)} """
    
        return line_info    

    def __create_set_and_where_one_gameObj_opencritic_data(self, gameObject: Game) -> str:
        '''
        Utilizes the Game Object to get the OpenCritic Data from the object\n
        to create the necessary set and where sql string command line.
         
        :param gameObj: Game Object containing data on the game. 
        :type gameObj: Game
        :return: SQL Command Statement
        :rtype: str
        '''  
        if gameObject.open_c_data.found_data:
            rating = gameObject.open_c_data.openCriticRatingText
            top_critic_average = self.__string_value_check(gameObject.open_c_data.topCriticAverage)
            critics_recommend = self.__string_value_check(gameObject.open_c_data.criticsRecommend)
            gameURL = gameObject.open_c_data.url             
            titleOnWebsite = self.apostrophe_string_check(gameObject.open_c_data.title_on_oc)
        else: 
            rating = "None"
            top_critic_average = 0
            critics_recommend = 0 
            gameURL = 'No URL'  
            
            titleOnWebsite = 'Not Found'
  
        # SQL Command to update the one game
        line_info = f"""SET OpenCriticRating = '{rating}', OpenCriticAverage = {top_critic_average}, OpenCriticRecommend = {critics_recommend}, OpenCriticTitle = '{titleOnWebsite}', OpenCriticURL = '{gameURL}' {self.__create_where_id_line(gameObject.name)} """

        return line_info 

    def __create_set_and_where_one_gameObj_steam_data(self, gameObject: Game) -> str:
        '''
        Utilizes the Game Object to get the Steam Data from the object\n
        to create the necessary set and where sql string command line.
         
        :param gameObj: Game Object containing data on the game. 
        :type gameObj: Game
        :return: SQL Command Statement
        :rtype: str
        '''  
        if gameObject.steam_data.found_data:
            
            allReviewsText = gameObject.steam_data.allReviewsText
            recentReviewsText = gameObject.steam_data.recentReviewsText
            
            allReviewsData = gameObject.steam_data.allReviewsData
            recentReviewsData = gameObject.steam_data.recentReviewsData

            allReviewsScore = self.__string_value_check(gameObject.steam_data.allReviewsScore)
            recentReviewsScore = self.__string_value_check(gameObject.steam_data.recentReviewsScore)

            releaseDate = gameObject.steam_data.releaseDate
            imageURL = gameObject.steam_data.imageURL

            gameURL = gameObject.steam_data.url
            
            titleOnWebsite = self.apostrophe_string_check(gameObject.steam_data.title_on_steam)
        else: 
            allReviewsText = 'No user review'
            recentReviewsText = 'No user review'
            allReviewsData = 'No user review'
            recentReviewsData = 'No user review'
            
            allReviewsScore = 0
            recentReviewsScore = 0

            releaseDate = 'No Date'
            imageURL = 'No URL'
            gameURL = 'No URL'              
            titleOnWebsite = "Not Found"
        
        # SQL Command to update the one game
        line_info = f"""SET SteamAllText = '{allReviewsText}', SteamRecentText = '{recentReviewsText}', SteamAllData = '{allReviewsData}', SteamRecentData = '{recentReviewsData}', SteamAllScore = {allReviewsScore}, SteamRecentScore = {recentReviewsScore}, SteamReleaseDate = '{releaseDate}', SteamImageURL = '{imageURL}', SteamTitle = '{titleOnWebsite}', SteamURL = '{gameURL}' {self.__create_where_id_line(gameObject.name)} """

        return line_info 

    def __create_where_id_line(self, gameTitle) -> str:
        '''
        Creates the where line part of the SQL Command. 
        
        :param gameTitle: Game Title used to find the correct ID.
        :type gameTitle: str
        :return: 'Where' Part of the SQL Command to be appended to the final SQL Command.
        :rtype: str
        '''
        where_line = f"WHERE {self.primary_key} = {self.database_game_to_id_key[gameTitle]}"
        return where_line


    ########################################################################################################################################
    ########################################################################################################################################
    #### Get and Set Data Methods ####

    ### Getter Methods ###
    def get_game_id_by_title(self, game_title: str): #
        '''
        Returns the ID of a game title from the database.

        :param game_title: Title to search for in the database
        :type game_title: str
        '''
        dataList = []
        try: 
            conn = sqlite3.connect(self.path_to_database)
                
            cursor = conn.cursor()
            
            data=cursor.execute(f''' SELECT {self.primary_key} FROM {self.table_name} WHERE Title = '{game_title}' ''') 
            
            for row in data: 
                dataList.append(row)
            
            conn.close()

            return dataList[0][0]
        except: 
            print(f"Unable to get the ID by Title: {game_title}")
            return None

    def get_data_from_table_by_column(self, spColumnName: str, gameName: str): #
        '''
        Returns the data contained in the database by column name and game title.
        
        :param spColumnName: Column Name 
        :type spColumnName: str
        :param gameName: Game Title
        :type gameName: str
        '''        
        dataList = []
        try: 
            conn = sqlite3.connect(self.path_to_database)
                
            cursor = conn.cursor() 
            
            command = f''' SELECT {self.spreadsheet_to_database_dict[spColumnName]} FROM {self.table_name} {self.__create_where_id_line(gameName)} ''' 

            data = cursor.execute(command) 
            
            for row in data: 
                dataList.append(row)  

            conn.close()

            return dataList[0][0]
        except: 
            print(f"Failed to excecute the command: Unable to get data from the {self.table_name} table by column name: {spColumnName}.")
            return '' 
 
    def __get_all_games_by_id_and_title_list(self):
        '''
        Gets all the game titles and IDs from the database.
        '''  
        sql_command = f""" SELECT {self.primary_key}, Title FROM {self.table_name}""" 

        try:
            conn = sqlite3.connect(self.path_to_database)
            
            cursor = conn.cursor() 

            cursor.execute(sql_command) 
            
            sqlList = cursor.fetchall()
        
            conn.close()

            return sqlList

        except sqlite3.Error as e:
            print(e)
            print("Failed to excecute the command: Unable to get all games by id and title list.")
            conn.close() 

    def __get_last_game_id(self):
        '''
        Gets the last index ID of the database.
        '''
        dataList = []
        try: 
            conn = sqlite3.connect(self.path_to_database)
                
            cursor = conn.cursor() 
            
            data = cursor.execute(f''' SELECT {self.primary_key} FROM {self.table_name} ORDER BY {self.primary_key} ASC''') 
            
            for row in data: 
                dataList.append(row) 

            print(f"Last Index ID is {dataList[-1][0]}")

            conn.close()

            return dataList[-1][0]
        except: 
            print(f"Unable to get the last ID!")
            return 0


    def get_game_data_last_update(self, gameTitle: str):
        '''
        Gets the last data column for a game title.
        '''
        gameDate = 'None'
        dataList = []
        sql_command = f''' SELECT LastUpdate FROM {self.table_name} WHERE ID = {self.database_game_to_id_key[gameTitle]} '''

        # Connect to the SQ Database and update it with the command
        try:  
            conn = sqlite3.connect(self.path_to_database) 

            cursor = conn.cursor() 

            data = cursor.execute(sql_command) 

            for row in data: 
                dataList.append(row)  

            gameDate = dataList[0][0]

        except sqlite3.Error as e:
            print(e) 
            print(f"Failed to get the last game data update for the game: {gameTitle}") 
        finally:    
            conn.close()
            return gameDate
   

    ### Setter Methods ###
    def update_game_new_update_date(self, gameTitle: str):
        '''Sets the LastUpdate column for a game title to the current date.'''
        # SQL Command to update the one game
        sql_command = f""" UPDATE {self.table_name} 
                            SET LastUpdate = '{self.__getCurrentDateDataBase()}' 
                            WHERE {self.primary_key} = {self.database_game_to_id_key[gameTitle]}; """
        print(f"Game ID:{self.database_game_to_id_key[gameTitle]}")
        
        # Connect to the SQ Database and update it with the command
        self.__execute_commit_sql_command(sql_command)

    # Used for bulk updates
    def update_multiple_games_with_new_update_date(self, gameList: set):
        '''Sets a list of game titles to the current date in their LastUpdate column.'''
        converted_data_list = tuple(gameList)

        # SQL Command to update the one game
        sql_command = f""" UPDATE {self.table_name} 
                            SET LastUpdate = '{self.__getCurrentDateDataBase()}' 
                            WHERE {self.primary_key} = ? """ 

        self.__executemany_commit_sql_command(sql_command, converted_data_list) 


    def update_single_data_by_ID(self, columnName: str, ID: int, dataInput): #
        ''' Updates a data point by Column Name, ID, and dataInput.\n
            For example, update 'Title' to 'Game1' where ID is 1
        '''
        if type(dataInput).__name__ == 'str':
            sql_command = f""" UPDATE {self.table_name} 
                            SET {columnName} = '{dataInput}' 
                            WHERE ID = {ID} """
        else: 
            sql_command = f""" UPDATE {self.table_name} 
                            SET {columnName} = {dataInput} 
                            WHERE ID = {ID} """

        self.__execute_commit_sql_command(sql_command)


    def insert_new_single_line_database(self, rowID: int, columnName: str, dataInput): #  
        ''' Inserts a new line by Column Name, ID, and dataInput.\n
            For example, insert 'Game1-title' and 1 (where 1 is the ID of the row) to the database. 
        '''
        if type(dataInput).__name__ == 'str':
            sql_command = f""" INSERT INTO {self.table_name} (ID,{columnName}) VALUES ({rowID}, '{dataInput}') """
        else:
            sql_command = f""" INSERT INTO {self.table_name} (ID,{columnName}) VALUES ({rowID}, {dataInput}) """

        self.__execute_commit_sql_command(sql_command)




    #############################################################################
    # Date Functions that help to set or determine the dates of each data entry #

    def __getDateNumbers(self, dateSTR:str):
        '''Gets the year, month, and day from a string.'''
        date = str(dateSTR).split('-')
        month = int(date[0])
        day = int(date[1])
        year = int(date[2])
        return year, month, day

    def compareDates(self, datePast: str, daysToAdd: int) -> bool:
        '''
        Checks the date of the game's LastUpdate column by adding a specific number of days.\n
        And determines whether the game's LastUpdate date is less than or greater than the number of days passed in.\n

        This method is used to determine if a game in the database should be updated based on the last date it was updated.\n
        For example, if the game's data was last updated on 1-1-2024, and the user wants to update any game's data after 364 days,\n
        then this method would compare the old date to the current date for example 1-1-2025 and determine if enough time \n
        has passed to warrant a new search for the game's data.
         
        :param datePast: Game's LastUpdate date. 
        :type datePast: str
        :param daysToAdd: Number of days to check since the last update.
        :type daysToAdd: int
        :return: Boolean value that indicates if the game's data should updated.
        :rtype: bool
        '''
        isDateOld = False 

        dateCurrent = datetime.datetime.today()
        print("Comparing dates...")
        print(f"Current day is {dateCurrent.strftime('%m-%d-%Y')} !\n")

        y, m, d = self.__getDateNumbers(datePast)

        newPastDate = datetime.datetime(y, m, d)+ datetime.timedelta(days=daysToAdd)

        print(f"Past date {datetime.datetime(y, m, d).strftime('%m-%d-%Y')} plus {daysToAdd} days is {newPastDate.strftime('%m-%d-%Y')} !\n")

        if dateCurrent > newPastDate:
            print(f"The current date is greater than {daysToAdd} days!\n")
            print("We can update this game!")
            isDateOld = True
        else:
            print(f"The current date is not greater than {daysToAdd} days!\n")
            print("We will not update this game!")

        return isDateOld

    def __getCurrentDateDataBase(self):
        '''Returns a string of today's date.'''
        d = datetime.datetime.today()
        return d.strftime('%m-%d-%Y') 

 