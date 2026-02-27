# Game Information Searcher - by Sebastian Muylle - Version 1.0 - webHunter.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import Firefox 
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By 

from urllib.parse import quote

from pathlib import Path

import os, platform, requests 

try: 
    from ClassContainers.GameData import Game 
except:  
    print("Missing the GameData Game Class type for the Web Hunter parent class.")

try:    
    from cydifflib import SequenceMatcher # Used to help compare strings for similarity 
 
except ImportError: 
    print("Missing Web Modules in webHunter.py.")

class WebHunter():
    '''
    Parent Class to be inhertied by Children Web Hunters.\n
    Offers methods to create responses or set up a selenium browser, and other helpful methods to compare strings.
    '''
    def __init__(self, webHeaders:dict):
        self.__timeToWait = 8 # Time to wait for a response from the webpage
        self.__SCORE_NEEDED_TO_PASS_PARTIAL_STRING_TEST = 0.5 # Testing Score to ensure a partial to near string match
        self.__headless = True # Determines whether the Selenium Browser is available
        self.__web_tool_headers = webHeaders # User's Web Headers for the methods using the requests library 
        # String Variables used to check which brand the caller is for - used to help with URL construction purposes
        self.brand = 'n/a' # The Brand of the Child - will be overwritten by the child class.
        self.__steam_brand = "Steam" 
        self.__opencritic_brand = "OpenCritic" 

    def search(self, game:Game):
        '''
        Search function to be overwritten by child classes of the WebHunter. 
        '''
        print(game.name)

    def search_linux(self, game_title:str):
        '''
        Search function to be overwritten by child classes of the WebHunter.
        Specifically for Linux platforms to account for the nature of multithreading.
        '''

    ## Request Functions ##
    def reponse(self, url) -> requests.Response:
        '''
        Attempts to get a response from the URL the caller provides and either returns a response object,\n
        reporting a success status of 200, or None if the response failed. 
        
        :param url: URL passed in by the caller to a website: https://www.example.com
        '''
        try:
            if self.__web_tool_headers:
                response = requests.get(url, headers=self.__web_tool_headers, timeout=self.__timeToWait, allow_redirects=True)  
            else:
                response = requests.get(url, timeout=self.__timeToWait, allow_redirects=True)  

            if response.status_code == 200: 
                return response
            else:                  
                return None
        except:
            print("Response failed completely.") 
            print("Status Code:", response.status_code)
            return None
        
    ## Selenium Functions ##
    def browser(self):
        '''
        Creates and returns a Firefox WebDriver and WebDriverWait objects.        
        '''
        pathToFolder = str(os.path.realpath(os.path.dirname(__file__)))

        pathToFireFoxAddons = os.path.join(pathToFolder, 'firefoxprofile')

        xpiExt = "*.xpi"

        xpi_addons: list[Path] = []

        for path in Path(pathToFireFoxAddons).rglob(xpiExt):
            xpi_addons.append(path)  

        # Path to the Chrome/FireFox Drivers
        path_to_driver = os.path.join(pathToFolder, "Drivers", "geckodriver.exe")

        path_webdriver_source = Path(path_to_driver) 

        # Start the Web Driver and set the preferences- FireFox
        options = Options()

        options.set_preference("media.volume_scale", "0.0")
        if self.__headless:
            options.add_argument("--headless") # Comment out this line if you wish to see the browser appear for debugging purposes
        options.set_preference("browser.download.folderList", 2)
        options.set_preference("browser.download.manager.showWhenStarting", False)

        if platform.system() == 'Linux':
            try:
                linux_path = "/usr/local/bin/geckodriver"
                service_config = Service(executable_path=linux_path)             
                wd = Firefox(options=options, service=service_config)   
            except:
                wd = Firefox(options=options)
        else:
            service = Service(path_webdriver_source)
            wd = Firefox(options=options, service=service)

        if xpi_addons:
            for xpiPath in xpi_addons:  
                wd.install_addon(xpiPath.absolute(), temporary=True)

        wait = WebDriverWait(wd, self.__timeToWait)
     
        return wd, wait
    
    def searchDuck(self, main_game_site_url:str, game_name:str, game_site_url_to_match:str, platform_brand:str):
        ''' 
        Searches on DuckDuckGo Website for the video game website's URL
         
        :param main_game_site_url: the brand's main site url -  "store.steampowered.com"
        :type main_game_site_url: str
        :param game_name: name of the game to be searched for
        :type game_name: str
        :param game_site_url_to_match: the specific string within the game site url to look for - "store.steampowered.com/app" 
        :type game_site_url_to_match: str
        :param platform_brand: specific brand to look for, example: steam
        :type platform_brand: str
        '''
        
        wd, wait = self.browser()

        resultsLinkURL = self.__createDuckSearchURL(game_name, main_game_site_url)

        wd.get(resultsLinkURL) 

        linkFound, url_result = self.__selDuckSearchMultiResults(game_site_url_to_match, wait, game_name)

        wd.quit()
        
        if linkFound: # if the link is found, make sure to fix it before being returned to the caller
            return self.__fixGameURL(url_result, platform_brand)
        else:
            return ''
         
    def __createDuckSearchURL(self, game_name:str, website_to_search_url:str):
        '''
        Generates a DuckDuckGo search url for a requests or selenium web tool. 
         
        :param game_name: Game Title to be encoded and embedded into the duckduckgo URL
        :type game_name: str
        :param website_to_search_url: Website or Platform that should be searched for on
        :type website_to_search_url: str
        '''

        encoded = quote(game_name)  

        return f"https://duckduckgo.com/?t=ffab&q=site%3A{website_to_search_url}+{encoded}&ia=web"
    

    def __selDuckSearchMultiResults(self, url_to_match:str, wait:WebDriverWait, game_title:str):
        '''
        Used to parse through the search results to find the correct URL link.
        
        :param url_to_match: URL site to match
        :type url_to_match: str
        :param wait: WebDriverWait 
        :type wait: WebDriverWait
        :param game_title: name of the game
        :type game_title: str
        ''' 

        try:
            myElem = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.wLL07_0Xnd1QZpzpfR4W'))) 

            link_found, final_url_result = self.__checkDuckDuckGoLink(myElem, 0, game_title, url_to_match)

            if not link_found:             
                link_found, final_url_result = self.__checkDuckDuckGoLink(myElem, 1, game_title, url_to_match)

            if not link_found: 
                link_found, final_url_result = self.__checkDuckDuckGoLink(myElem, 2, game_title, url_to_match)
            
        except:  
            link_found = False
            final_url_result = ''

        return link_found, final_url_result    


    def __checkDuckDuckGoLink(self, myElem, urlNum:int, game_title:str, url_to_match:str):
        '''
        Checks the text in the search block for a game title and makes sure it is a valid link that the search tool is looking for.
         
        :param myElem: Web Element List
        :param urlNum: Index Number to pass in to the Web Element List
        :type urlNum: int
        :param game_title: Game Title to search for in the link text.
        :type game_title: str
        :param url_to_match: URL site in the link to match against. 
        :type url_to_match: str
        '''
        try:  
            # Get the span tags and check if the game title is in this link before proceeding in getting the URL
            span_tags = myElem[urlNum].find_elements(By.TAG_NAME, 'span')

            # First we will do a literal exact string match check to see if the title of the game is in this link block's text
            correct_url_block_found = self.__exactStringMatchCheck(span_tags, game_title)

            # if there were no exact matches in this link block, we will perform a partial string match to see if there title is in the link block's text
            if not correct_url_block_found:
                correct_url_block_found = self.__partialStringMatchCheck(span_tags, game_title)
            
            # if the span tag had the title of the game in it, then this should be the correct URL we need,
            # go ahead and check A tags and see if the URL to Match is present
            if correct_url_block_found:
                a_tags = myElem[urlNum].find_elements(By.TAG_NAME, 'a')
            
                for tag in a_tags: 
                    if url_to_match in tag.get_attribute('href'):
                        url_result = str(tag.get_attribute('href')) 
                        inner_link_found = True 
                        break 
        except:  
            inner_link_found = False
            url_result = ''

        return inner_link_found, url_result
    
    def __exactStringMatchCheck(self, span_tags, game_title:str):
        '''Exact String Match Check - checks if the game title is in the text body.'''
        correct_url_block_found = False
        try:
            for span_tag in span_tags:
                if game_title.lower() in str(span_tag.text).lower(): 
                    correct_url_block_found = True
                    break
        except Exception as e:
            print(e)
            print("Error - when checking the text with the exact string match method.")
        return correct_url_block_found
    
    def __partialStringMatchCheck(self, span_tags, game_title:str):
        '''Partial String Match Check - checks if there is a partial game title match in the text body.'''
        correct_url_block_found = False
        try:
            for span_tag in span_tags:
                best_match, best_score = self.__find_title_in_paragraph(str(span_tag.text), game_title)
                if best_score > self.__SCORE_NEEDED_TO_PASS_PARTIAL_STRING_TEST: 
                    correct_url_block_found = True
                    break
        except Exception as e:
            print(e)
            print("Error - when checking the text with the parital string match method.")
        return correct_url_block_found
    
    def __find_title_in_paragraph(self, paragraph:str, title:str):
        """
        Finds the best match for the game title within a given paragraph.

        Args:
            paragraph: The paragraph of text to search.
            book_title: The title of the game to find.

        Returns:
            A tuple containing:
            - The best matching substring in the paragraph.
            - The similarity score (between 0 and 1) 
                where 1 is an exact match.
        """
        best_match = ""
        best_score = 0

        # Split the paragraph into sentences for better matching
        sentences = paragraph.split('. ')

        for sentence in sentences:
            # Create a SequenceMatcher object
            matcher = SequenceMatcher(None, sentence, title)
            score = matcher.ratio() 

            if score > best_score:
                best_score = score
                best_match = sentence

        return best_match, best_score
    
    def __fixGameURL(self, gameToFix: str, brand:str) -> str: 
        '''
       This Function takes the URL found in the search engine and returns a proper game url.  
         
        :param gameToFix: URL that will be modified.
        :type gameToFix: String
        :param brand: Platform the url belongs to determine which string modification will be used.
        :type brand: String
        '''
        try:
            splitText = gameToFix.split('/')

            if brand == self.__steam_brand or brand == self.__opencritic_brand:
                newURL = splitText[0] + "//" + splitText[2] + "/" + splitText[3] + "/" + splitText[4] + "/" + splitText[5] 
        except: 
            newURL = ''

        return newURL
    
    def simplify_string_for_comparion(self, title:str): 

        titleNew = title.replace("&", "and")

        res = ''.join([char for char in titleNew if char.isalnum()]) 

        return res.lower()
    
    def create_website_search_link(self, search_url, game_title) -> str:

        encoded = quote(game_title) 

        return f"{search_url}{encoded}"

    def check_title_match(self, title_result:str, game_title:str) -> bool:
        """
        Compares the game's title on the website versus the title provided by the user.
        If it is a strong match, it will return True. 

        Args:
            title_result: The title of the game found on the website.
            game_title: The title of the game that the user provided.
        """ 

        SCORE_NEEDED_TO_PASS_PARTIAL_STRING_TEST = 0.5
        best_title_match = False

        matcher = SequenceMatcher(None, self.simplify_string_for_comparion(title_result), self.simplify_string_for_comparion(game_title))
        best_score = matcher.ratio()   

        if best_score > SCORE_NEEDED_TO_PASS_PARTIAL_STRING_TEST: 
            best_title_match = True 

        return best_title_match