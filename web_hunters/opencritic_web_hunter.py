# Game Information Searcher - by Sebastian Muylle - Version 1.0 - opencritic_web_hunter.py
import time
from bs4 import BeautifulSoup 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys  

try: 
    from ClassContainers.GameData import Game 
except:
    print("Missing the GameData Game Class type for the opencritic web hunter!")
 
try: 
    from web_hunters.webHunter import WebHunter
except:
    try:
        from webHunter import WebHunter
    except ImportError as e:
        print(e)
        print("Unable to import the WebHunter Parent Class")

#####################################
     

class OpenCriticHunter(WebHunter):
    '''
    WebHunter Class that specializes in searching and retrieving game information from OpenCritic.com.
    '''
    def __init__(self, webHeaders:dict): 
        super().__init__(webHeaders) 
        self.brand = "OpenCritic"

    def search(self, game: Game): 
        '''
        Search for a game title on OpenCritic.com and modify the game object's data with\n
        with information found on the site.
        
        :param game: Game Object to contain OpenCritic Data
        :type game: Game
        '''
        # Use Selenium to search for the game on the OpenCritic Website
        game.open_c_data.url = self.__search_opencritic(game.name)  

        # If we find a link, go ahead and use the response class to first attempt to get the information
        if game.open_c_data.url:
            res = self.reponse(game.open_c_data.url)
            if res:
                self.__get_game_page_info(res, game)
        
        border_sep_symbol = "#" * 60
        print(f"{border_sep_symbol}") 
        if game.open_c_data.found_data:
            print(game.open_c_data.url)
            print(f"OpenCritic Data has been found for {game.name}")
        else: 
            print(f"OpenCritic Data has not been found for {game.name}")
        print(f"{border_sep_symbol}") 


    #######################################################
    ### REQUEST SECTION ### 
    def __get_game_page_info(self, response, game: Game): 
        '''
        Uses the response to parse through the HTML and modifies the Game Object's OpenCritic attributes.
        '''
        web_html = response.text

        soup = BeautifulSoup(web_html, 'html.parser')
        try: 
            title_on_page_element = soup.find('h1', class_="my-2")

            if title_on_page_element:
                game.open_c_data.title_on_oc = title_on_page_element.text

            image_rating_element = soup.find("app-tier-display", class_="mighty-score")

            if image_rating_element != None: 
                
                game.open_c_data.openCriticRatingText = str(image_rating_element.img['alt'])

                app_game_scores_display_element = soup.find("app-game-scores-display")

                game_scores = app_game_scores_display_element.find_all("div", class_="col-4") 

                top_critic_average_element = game_scores[0].find("div", class_="inner-orb") 

                game.open_c_data.topCriticAverage = int(str(top_critic_average_element.text).strip())

                critics_recommend_element = game_scores[1].find("div", class_="inner-orb") 

                game.open_c_data.criticsRecommend = self.__editCriticsRecommendScore(critics_recommend_element.text)

                game.open_c_data.found_data = True

        except:
            print("Missing element from the page or possible error about the scores on opencritic.com.")
            game.open_c_data.found_data = False
    


    #######################################################
    ### SELENIUM SECTION ###

    def __search_opencritic(self, game_name):
        '''
        Utilizes OpenCritic's search box to find the game title on their website\n
        and return the url of that game title.
        
        :param game_name: Game Title to search
        '''

        url = ''

        search_url = "https://opencritic.com/search?criteria="

        wd, wait = self.browser()

        wd.get(search_url)

        try:
            elementSearchBox = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'input.ng-valid'))) 

            if elementSearchBox:

                elementSearchBox[0].clear()
                elementSearchBox[0].send_keys(game_name, Keys.ENTER) 

                resultsArea = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.results-container')))

                time.sleep(1)

                links = resultsArea.find_elements(By.TAG_NAME, 'a') 
 
                if links: 
                    for a_link in links:
                        div_title = a_link.find_element(By.CSS_SELECTOR, 'div.col-9')
                        
                        if self.check_title_match(div_title.text, game_name):
                            url = str(a_link.get_attribute('href')).strip()  
                            break 

        except Exception as e:
            print(e)
            print("OpenCritic - Failed to find or search for the game using the search url.")
            
        finally:
            wd.quit()
            return url
    
    ## General Methods Used to Modify Data ## 
    def __editCriticsRecommendScore(self, textToChange) -> int:
        '''
        Removes the percentage sign from the Open Critic - Critics Recommend category.
        It returns the integar version of the percentage score.

        :param textToChange: String containing the percentage score.
        '''
        # ' 89% '
        newTextToChange = str(textToChange).strip()
        if '?' in newTextToChange:
            return 0
        else: 
            splitText = list(newTextToChange)
            # ['8', '9', '%']
            splitText.pop()
            # ['8', '9']
            textToChange = int(str("".join(splitText)))
            return textToChange