# Game Information Searcher - by Sebastian Muylle - Version 1.0 -
import time, requests
from bs4 import BeautifulSoup 
  
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select 
from selenium.webdriver import Firefox
 
try: 
    from ClassContainers.GameData import Game 
except:  
    print("Missing the GameData Game Class type for the Steam Web hunter.")
 
try: 
    from web_hunters.webHunter import WebHunter
except:
    try:
        from webHunter import WebHunter
    except ImportError as e:
        print(e)
        print("Unable to import the WebHunter Parent Class")

#####################################

class SteamHunter(WebHunter):
    '''
    WebHunter Class that specializes in searching and retrieving game information from Steam.com.
    '''
    def __init__(self, webHeaders:dict):
        ### Main Variables ### 
        super().__init__(webHeaders)
        self.__MAIN_GAME_SITE_URL = "store.steampowered.com"
        self.__GAME_SITE_URL_TO_MATCH = f"{self.__MAIN_GAME_SITE_URL}/app" # string to locate the correct url when searching through a search engine results 
        self.brand = "Steam"

    def search(self, game: Game):
        '''
        Search for a game title on Steam.com and modify the game object's data with\n
        with information found on the site.
        
        :param game: Game Object to contain Steam Data
        :type game: Game
        ''' 

        # Use Steam's Search Tool to find the game
        game.steam_data.url = self.__search_steam(game.name)  

        # If the program finds a link, go ahead and use the response class to first attempt to get the information
        if game.steam_data.url:             
            res = self.reponse(game.steam_data.url)
            if res:
                self.__get_game_page_info(res, game)
        
        if game.steam_data.url and game.steam_data.found_data and game.steam_data.releaseDate == "":
            print("Error in Retrieving Steam Data.\nPossible M+ rated game.")
            print("Checking Steam store page again.")

            self.__use_selenium_method(game) 

        # If we do not find the information with the response class method, we'll manually search for the webpage 
        ## via the selenium method. 
        if not game.steam_data.found_data:            
            if not game.steam_data.url: 
                # Use DuckDuckGo with Selenium to find the URL 
                time.sleep(1) # Wait before using the searchDuck method to prevent bot road blocks 
                game.steam_data.url = self.searchDuck(self.__MAIN_GAME_SITE_URL, game.name, self.__GAME_SITE_URL_TO_MATCH, self.brand) 

                if game.steam_data.url:
                    self.__use_selenium_method(game)  
            else:
                self.__use_selenium_method(game) 
        
        border_sep_symbol = "#" * 60
        print(f"{border_sep_symbol}")
        if game.steam_data.found_data:  
            print(game.steam_data.url)
            print(f"Steam Data has been found for {game.name}")
        else:
            print(f"Steam Data has not been found for {game.name}")
        print(f"{border_sep_symbol}")

    #######################################################
    ### REQUEST SECTION ###
    def __search_steam(self, game_name: str):
        '''
        Utilizes Steam's search tool to find the game title on their website\n
        and return the url of that game title.
        
        :param game_name: Game Title to search
        '''
        url = ''

        search_url = "https://store.steampowered.com/search?term="

        search_response = self.reponse(self.create_website_search_link(search_url, game_name)) 

        soup = BeautifulSoup(search_response.text, 'html.parser') 

        try:
            if soup.find('div', class_="search_results", id="search_results"):
                # print(search_response.url) # Uncomment to check response url 
                search_box_area = soup.find('div', class_="search_results", id="search_results")
                if search_box_area.find_all('a', class_="search_result_row"): 
                    search_a_links = search_box_area.find_all('a', class_="search_result_row") 
                    for a_link in search_a_links:
                        if not url:
                            for span_element in a_link.find_all('span', class_="title"):
                                span_title_text = span_element.text 
                                if self.check_title_match(span_title_text, game_name): 
                                    url = str(a_link['href']).split("?snr=")[0] 
                                    break
                        else:
                            break  

        except:
            print("Steam search failed.")

        return url
 
    def __get_game_page_info(self, response:requests.Response, game: Game):
        '''
        Uses the response to parse through the HTML and return the data for the Steam store data.
         
        :param response: Response of the web page.
        :type response: Response
        :param game: Game Object that will be modified.
        :type game: Game
        '''

        steam_release_date = ""
        image_url = "NO IMAGE URL FOUND"

        web_html = response.text

        soup = BeautifulSoup(web_html, 'html.parser') 
        try:

            if soup.find('div', id="appHubAppName", class_="apphub_AppName"):
                game.steam_data.title_on_steam = str(soup.find('div', id="appHubAppName", class_="apphub_AppName").text)
            
            # Gets the review text on the steam store page - such as 'Overwhelmingly Postive' 
            for text in soup.find_all('span', class_='game_review_summary'):
                if text.get('data-tooltip-html'):
                    if "last 30 days" in str(text.get('data-tooltip-html')):
                        game.steam_data.recentReviewsText = text.string
                    else:
                        game.steam_data.allReviewsText = text.string
            
            # Gets the Data Summary Text stored in the review text on the steam store page - such as '95% of 500 users...
            for text in soup.find_all('span', class_='responsive_reviewdesc'):
                if "last 30 days" in str(text.text):
                    fixedTextRecent = str(text.text).strip()
                    game.steam_data.recentReviewsData = fixedTextRecent[2:] 
                else:
                    fixedTextTotal = str(text.text).strip()
                    game.steam_data.allReviewsData = fixedTextTotal[2:] 

            # Section to get the Summary Text of the All Languages Area - such as '95% of 500 users...
            for div_outlier in soup.find_all('div', class_="outlier_totals"):
                if "Total reviews in all languages:" in str(div_outlier).strip(): 
                    for span_in in div_outlier.find_all('span', class_="game_review_summary"): 
                        game.steam_data.allReviewsText = str(span_in.string)
 
                        fixedTextTotal = str(span_in.get('data-tooltip-html')) 
                        game.steam_data.allReviewsData = fixedTextTotal

            release_date = soup.find('div', class_='date')

            game_header_image_url = soup.find('img', class_='game_header_image_full')

            if release_date: 
                game.steam_data.releaseDate = str(release_date.text) 
            else:
                game.steam_data.releaseDate = steam_release_date 

            if game_header_image_url: 
                game.steam_data.imageURL = game_header_image_url['src'] 
            else: 
                game.steam_data.imageURL = image_url

            # get the recent user reviews information
            if game.steam_data.recentReviewsData != "No user review":
                game.steam_data.recentReviewsScore = self.__getScoreOutOfData(game.steam_data.recentReviewsData)

            # get all user reviews information
            if game.steam_data.allReviewsData != "No user review": 
                game.steam_data.allReviewsScore = self.__getScoreOutOfData(game.steam_data.allReviewsData)
            
            game.steam_data.found_data = True

        except:
            game.steam_data.found_data = False        
            
    # ### SELENIUM SECTION ###
    def __use_selenium_method(self, game:Game):
        '''
        Primarily utilizes the Selenium Web Tool to check the game's data on the Steam web page. 
        '''
        wd, wait = self.browser() # creates a new selenium firefox browser and returns the web driver wd and the wait version of that web driver
        wd.get(game.steam_data.url) # if the link was found during the google search, use that URL to load the browser 
        if not self.__checkingForErrorPage(wd):
            if self.__checkingForAgeCheck(wd): 
                self.__setAgeToAdult(wd)
            self.__getSteamData(wd, game) 
        wd.quit() # Close out the web browser bot

    def __checkingForAgeCheck(self, wd: Firefox):
        '''
        Checks if the page is asking for age verification. 
        '''
        time.sleep(0.5)
        element = wd.find_elements(By.CSS_SELECTOR, '.agegate_birthday_desc')
        if element:
            return True
        else:
            return False
        
    def __setAgeToAdult(self, wd: Firefox):
        '''
        Sets the age verification to a older age to pass the age verification check. 
        '''
        time.sleep(1)
        element = wd.find_element(By.CSS_SELECTOR, '#ageYear')
        
        select = Select(element)
        select.select_by_visible_text('1980')

        elementNew = wd.find_element(By.CSS_SELECTOR, '#view_product_page_btn')
        elementNew.click()

    def __checkingForErrorPage(self, wd: Firefox):
        '''
        Checks if the Steam Web Page is giving an error message.
        '''
        element = wd.find_elements(By.CSS_SELECTOR, '#error_box')
        if element:
            return True
        else: 
            return False

    def __findSteamReviews(self, wd: Firefox):
        '''
        Checks if there are user reviews on the steam web page.
        '''
        element = wd.find_elements(By.CSS_SELECTOR, '#userReviews')
        if element:
            return True
        else:
            return False    
        
    def __hasSteamAppTitle(self, wd: Firefox):
        '''
        Checks if the steam web page has a title.
        '''
        elements = wd.find_elements(By.CSS_SELECTOR, '#appHubAppName')
        if elements:
            return True
        else:
            return False

    def __getSteamData(self, wd: Firefox, game: Game):
        '''
        Gets the Data out of the Steam Web Page and stores it in the Game Object's Variables. 
        '''
        time.sleep(1.5) 
        
        self.__get_steam_title(wd, game)

        dataFound = self.__reviews_from_page(wd, game) 

        hasReleaseDate = self.__get_release_date(wd, game) 

        hasImageURL = self.__get_image_url(wd, game)  

        if dataFound or hasReleaseDate or hasImageURL:
            game.steam_data.found_data = True


    def __get_steam_title(self, wd:Firefox, game:Game):
        '''
        Gets the Game's title off of the Steam store web page.
        '''
        try:
            if self.__hasSteamAppTitle(wd): 
                elementTitle = wd.find_element(By.CSS_SELECTOR, '#appHubAppName')
                game.steam_data.title_on_steam = str(elementTitle.text) 
        except:
            print("No Title elements present on this steam web page.")


    def __reviews_from_page(self, wd:Firefox, game:Game):
        '''
        Checks and gets the Data from the Steam web page.
        '''
        dataFound = False 

        try:            
            dataFound = self.__findSteamReviews(wd)

            if dataFound:
                self.__get_overall_text_rating(wd, game)
                self.__get_steam_meta_text_data(wd, game)
                self.__get_all_languages_data(wd, game) # This method is primarily used to check if there is an all languages reviews section on the web page. 
        except:
            print("No reviews or score elements present on this steam web page.")

        return dataFound

    def __get_overall_text_rating(self, wd:Firefox, game:Game) -> bool:
        '''
        Gets the overall positive, mixed, negative user rating text from each game review summary category.
        ''' 
        hasAllReviews = False
        hasRecentReviews = False

        try:
            reviews_elements = wd.find_elements(By.CSS_SELECTOR, "span.game_review_summary")
            for review in reviews_elements:
                if review.get_attribute('data-tooltip-html'):
                    if "last 30 days" in str(review.get_attribute('data-tooltip-html')): 
                        game.steam_data.recentReviewsText = review.text
                        hasRecentReviews = True 
                    else:
                        game.steam_data.allReviewsText = review.text
                        hasAllReviews = True  
        except:
            print("Unable to find the overall text ranting for this game.")

        if not hasAllReviews:
            # set the default steam all reviews data to the ones belows 
            game.steam_data.allReviewsText = "No user review" 
            game.steam_data.allReviewsData = "No user review"  
            game.steam_data.allReviewsScore = 0

        if not hasRecentReviews:             
            game.steam_data.recentReviewsText = "No user review" 

            game.steam_data.recentReviewsData = "No user review" 

            game.steam_data.recentReviewsScore = 0 

    def __get_steam_meta_text_data(self, wd:Firefox, game:Game):
        '''
        Gets the meta text data out of the user reviews on the page.
        '''
        try:            
            user_reviews_section_element = wd.find_element(By.CSS_SELECTOR, '#userReviews')

            review_data_elements = user_reviews_section_element.find_elements(By.CSS_SELECTOR, "a.user_reviews_summary_row")

            for data_element in review_data_elements:
                if "RECENT REVIEWS:" in str(data_element.text).upper(): 

                    dataText = str(data_element.get_attribute("data-tooltip-html")).strip() 

                    game.steam_data.recentReviewsData = dataText 
                    
                    game.steam_data.recentReviewsScore = self.__getScoreOutOfData(dataText)

                elif "ALL REVIEWS:" in str(data_element.text).upper(): 

                    dataText = str(data_element.get_attribute("data-tooltip-html")).strip() 

                    game.steam_data.allReviewsData = dataText 

                    game.steam_data.allReviewsScore = self.__getScoreOutOfData(dataText)

        except:
            print("Unable to get the ranting data from this steam page.")

    def __get_all_languages_data(self, wd:Firefox, game:Game):      
        '''
        Section to get the Summary Text of the All Languages Area.
        '''
        try:
            all_language_section_div = wd.find_element(By.CSS_SELECTOR, '.outlier_totals') 

            if game.steam_data.allReviewsData == "No user review" and all_language_section_div: 
                if "Total reviews in all languages:" in str(all_language_section_div.text).strip(): 

                    span_element = all_language_section_div.find_element(By.CSS_SELECTOR, '.game_review_summary') 

                    if span_element: 

                        game.steam_data.allReviewsText = span_element.text

                        # print(span_element.get_attribute("data-tooltip-html")) # Uncomment to check span_element data

                        dataText = str(span_element.get_attribute("data-tooltip-html")).strip() 

                        game.steam_data.allReviewsData = dataText 

                        game.steam_data.allReviewsScore = self.__getScoreOutOfData(dataText) 
        except:
            print("No all languages reviews present on this Steam web page.") 


    def __get_release_date(self, wd:Firefox, game:Game):
        '''
        Section to get the date element text out of the Steam web page.
        '''
        hasReleaseDate = False
        steam_release_date = ""

        try:
            release_date_element = wd.find_element(By.CSS_SELECTOR, "div.date")
            if release_date_element: 
                
                game.steam_data.releaseDate = str(release_date_element.text)
                
                hasReleaseDate = True
        except:
            print("No Date elements present on this Steam web page.")

        if not hasReleaseDate: 
            game.steam_data.releaseDate = steam_release_date

        return hasReleaseDate
    
    def __get_image_url(self, wd:Firefox, game:Game):
        '''
        Get the image url out of the Steam web page.
        '''
        image_url = "NO IMAGE URL FOUND"
        hasImageURL = False

        try:
            game_header_image_url_element = wd.find_element(By.CSS_SELECTOR, "img.game_header_image_full")
            if game_header_image_url_element: 
                game.steam_data.imageURL = str(game_header_image_url_element.get_attribute('src'))
                hasImageURL = True
        except:
            print("No Image URL Element present on this Steam web page.")

        if not hasImageURL: 
            game.steam_data.imageURL = image_url

        return hasImageURL
    
        ## General Methods Used to Modify Data ##  
    def __getScoreOutOfData(self, dataText):
        '''
        Gets Data out of text from the Steam page. 
        
        :param dataText: Text containing data.
        '''
        # Need more user reviews to generate a score
        if 'Need more user reviews' in dataText:
            dataText = 1
        elif 'No user reviews' in dataText:
            dataText = 0
        else:
            dataNewText = dataText[0:3]
            if dataNewText[2] == '0':
                if dataNewText[1] == '0': 
                    dataText = int(dataNewText)
            elif dataNewText[2] == '%':
                dataNewText = list(dataNewText)
                dataNewText.pop()
                dataNewText = str(''.join(dataNewText))
                dataText = int(dataNewText)
            else:
                if dataNewText[2] == ' ':
                    dataNewText = list(dataNewText)
                    dataNewText.pop()
                    if dataNewText[1] == '%':
                        dataNewText.pop()
                    dataNewText = str(''.join(dataNewText))
                    dataText = int(dataNewText)
    
        return dataText