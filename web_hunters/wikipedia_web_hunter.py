
# Game Information Searcher - by Sebastian Muylle - Version 1.0 - wikipedia_web_hunter.py
import requests 
import bs4
from bs4 import BeautifulSoup
   
from urllib.parse import quote

try: 
    from ClassContainers.GameData import Game, WikipediaData
except:
    print("Missing the GameData Game Class type for the Wikipedia Web Hunter.")
 
try: 
    from web_hunters.webHunter import WebHunter
except:
    try:
        from webHunter import WebHunter
    except ImportError as e:
        print(e)
        print("Unable to import the WebHunter Parent Class")
 
class WikipediaHunter(WebHunter):
    '''
    WebHunter Class that specializes in searching and retrieving game information from Wikipedia.com.
    '''
    def __init__(self, webHeaders:dict):
        ### Main Variables ### 
        super().__init__(webHeaders) 
        self.brand = "Wikipedia"

    def search(self, game:Game): 
        '''
        Search for a game title on Wikipedia.com and modify the game object's data with\n
        with information found on the site.
        
        :param game: Game Object to contain Wikipedia Data
        :type game: Game
        '''
        wikiLink = self.__create_wiki_search_link(game.name) 

        response = self.reponse(wikiLink)

        if response: 
            wikipage_cat, correct_url = self.__check_results(response, game.name) 

            if wikipage_cat == 'Series':
                response = self.reponse(correct_url)

                game.wiki_data = self.__set_game_info(response, game.wiki_data)
                
            if wikipage_cat == 'Found Page': 

                game.wiki_data = self.__set_game_info(response, game.wiki_data) 

        border_sep_symbol = "#" * 60
        print(f"{border_sep_symbol}") 
        if game.wiki_data.found_data:      
            print(response.url)
            print(f"Wikipedia Data has been found for {game.name}")
            
        else:
            print(f"Wikipedia Data has not been found for {game.name}")      
        print(f"{border_sep_symbol}")  
    
    def __set_game_info(self, response:requests.Response, wikiDataObj:WikipediaData): 
        '''
        Initial method to obtain and then set the page information/data\n
        into the Wikipedia Data Object contained in the Game Object.
        '''
        infobox_dict, reception_dict = self.__get_page_info(response) 

        if infobox_dict or reception_dict:
            wikiDataObj = self.__set_game_object_wiki_values(wikiDataObj, response.url, infobox_dict, reception_dict) 

        return wikiDataObj

    def __set_game_object_wiki_values(self, wikiDataObj:WikipediaData, url:str, infobox:dict, reception:dict):
        '''
        Sets the Wiki Data Object's Attributes with the data found in the search.
        '''
        wikiDataObj.found_data = True
        wikiDataObj.url = url

        if infobox:
            wikiDataObj.set_infobox_section(infobox)

        if reception: 
            wikiDataObj.set_reception_section(reception)
        
        return wikiDataObj

         
    def __create_wiki_search_link(self, game_name:str) -> str:
        '''
        Create a Wikipedia Search link for the requests library to use.
        '''
        encoded = quote(game_name) 

        return f"https://en.wikipedia.org/w/index.php?search={encoded}&title=Special:Search&ns0=1"
 

    def __get_page_info(self, response:requests.Response):
        '''
        Main Get method to get the web page information from Wikipedia from the Response Object.\n 
        
        Note: Wikipedia tends to be not consistent with their layout of web elements in their infoboxes or reception tables.\n
        If there is missing information in the wiki_data object but is present on the web page,\n
        there is a good chance the format of the elements might be unique and couldn't be detected by the Get methods.\n  
        '''
        web_html = response.text

        soup = BeautifulSoup(web_html, 'html.parser')  

        infobox_dict = self.__get_top_table_box_info(soup)
 
        reception_dict = self.__get_scores_info(soup)
 
        if infobox_dict or reception_dict:
            return infobox_dict, reception_dict
        else:
            return {}, {}

    def __get_top_table_box_info(self, soup:BeautifulSoup):
        '''
        Gets the Data out of the infobox from Wikipedia web page.
        '''
        infobox_dict = {}

        title_key = "Game Title On Wiki"
        try:
            if soup.find('table', class_='ib-video-game'): 
                for table in soup.find_all('table', class_='ib-video-game'):

                    infobox_dict[title_key] = table.find_all('tr')[0].text

                    for table_row in table.find_all('tr'):

                        if table_row.find('th') and table_row.find('td'):
                            # th element tends to represent the Category Type of Information - such as "Genre(s)" or "Release" date     
                            # td element is the element that contains the information about the game's category such as the "Director's name"
                            # print(element.find(text=True, recursive=False)) # Print Test to check text found in the table row. 
                            text_in_row = table_row.find('th').text 

                            if str(text_in_row).lower() == 'release':
                                infobox_dict = self.__get_release_date_info(table_row, infobox_dict) 
                            else:
                                if table_row.find('td').find('ul'):
                                    tempList = []
                                    for li_element in table_row.find('td').find_all('li'): 
                                        tempList.append(li_element.text)
                                    infobox_dict[table_row.find('th').text] = tempList
                                
                                elif table_row.find('td').find('br'):
                                    tempListBr = []
                                    td_contents = table_row.find('td').contents 
                                    for element in td_contents:
                                        if str(element) != '<br/>':
                                            tempListBr.append(element.text)
                                    infobox_dict[table_row.find('th').text] = tempListBr        
                                    
                                else:
                                    infobox_dict[table_row.find('th').text] = self.__check_for_citation(table_row.find('td').text)  

                        img_file_element = table_row.find('img', class_='mw-file-element')
                        if img_file_element: 
                            infobox_dict['Image'] = img_file_element['src'] 
        except:
            print("No Game Info Table on this page.")
        finally: 
            return infobox_dict

    def __get_release_date_info(self, table_row:bs4.element.Tag, infobox_dict:dict):
        '''
        Gets the Release Date Data out of the Release Category of the InfoBox.\n
        ''' 

        # Lambda Functions -
        # Sometimes there will be only a single release date assigned to the game
        # therefore, we should go ahead and get it out of the list object that is generated in this method
        # so the result will be "Release" : "1-1-2001" instead of "Release" ["1-1-2001"]
        single_item_list_check = lambda li: li[0] if (len(li) == 1) > 0 else li

        complex_date = False

        date_found = False

        try:
            text_in_row = table_row.find('th').text 
            td_element = table_row.find('td')
            
            # print(element.find(text=True, recursive=False)) # Print Test to check text found in the table row. 

            # Check if it is a complex release date format 
            # Test Check - TD -> B Platform
            if td_element.find('b'): # Complex release dates tend to have a bold 'b' element in them 
                # Test Check - TD -> Div -> Div:class_='plainlist' -> UL -> LI
                if td_element.find('div'):

                    if td_element.find('div').find('div', class_='plainlist'):
                        if td_element.find('div').find('div', class_='plainlist').find('ul').find('li'): 
                            complex_date = True
                            complex_release_dict = {}
                            
                            if td_element.find('div').find('div').find('div').find('span'):
                                top_release_date_element = td_element.find('div').find('div').find('div').find('span')
                                if top_release_date_element:
                                    complex_release_dict['Main Release Date'] = top_release_date_element.text 
                            
                            plaform_count = len(td_element.find_all('b'))

                            for i in range(plaform_count): 
                                tempPlatformList = []
                                platform_name = td_element.find_all('b')[i].text 

                                pf_release_dates_elements = td_element.find('ul').find('li').find_all('div', class_="plainlist")[i].find_all('li') 

                                for release_date_ele in pf_release_dates_elements: 
                                    tempPlatformList.append(self.__check_for_citation(release_date_ele.text))

                                complex_release_dict[platform_name] = single_item_list_check(tempPlatformList)
                                    
                            infobox_dict[text_in_row] = complex_release_dict
                            date_found = True 

                    # TD -> Div:class_='plainlist' -> UL -> Li 
                    # release_date_elements = td_element.find('div', class_='plainlist').find('ul').find_all('li')
                    # print(release_date_elements[0].find(string=True, recursive=False))
                    elif td_element.find('div', class_='plainlist').find('ul').find('li'):

                        if len(td_element.find_all('div', class_='plainlist')) > 1:                         
                            # some pages do not have a Bold and Div separtion between release dates and platforms
                            # B -> Platforms
                            # Div -> Release Dates 
                            #       -> li
                            #       -> li
                            # but other pages have only a LI list where it will do the following pattern -
                            # LI -> Platforms
                            # LI -> Release Date
                            # LI -> Platforms
                            # LI -> Release Date
                            # etc, etc...
  
                            complex_date = True
                            complex_release_dict = {}                            

                            plaform_count = len(td_element.find_all('b')) 

                            for i in range(plaform_count): 
                                tempPlatformList = []
                                platform_name = td_element.find_all('b')[i].text  

                                pf_release_dates_elements = td_element.find_all('div', class_="plainlist")[i].find_all('li')  

                                for release_date_ele in pf_release_dates_elements: 
                                    tempPlatformList.append(self.__check_for_citation(release_date_ele.text)) 

                                complex_release_dict[platform_name] = single_item_list_check(tempPlatformList)
                            
                            infobox_dict[text_in_row] = complex_release_dict
                            date_found = True 
                        else:
                            if td_element.find('div', class_='plainlist').find('ul').find('li').find('b'):
                                # LI -> Platforms
                                #   -> B platform titles
                                # LI -> Release Date
                                # LI -> Platforms
                                #   -> B platform titles
                                # LI -> Release Date
                                # etc, etc...

                                li_elements = td_element.find_all('li')

                                if li_elements and len(li_elements) % 2 == 0: 

                                    complex_date = True
                                    complex_release_dict = {}

                                    total_pairs_count = int(len(li_elements) / 2)
                                    # 0 - platform 
                                    # 1 - date
                                    # 2 - platform
                                    # 3 - date
                                    platform_index_start = 0
                                    date_index_start = 1
                                    for i in range(total_pairs_count):
                                        platform_name = li_elements[platform_index_start].text
                                        date_text = li_elements[date_index_start].text 
                                        complex_release_dict[platform_name] = self.__check_for_citation(date_text)
                                        platform_index_start += 2
                                        date_index_start += 2

                                    infobox_dict[text_in_row] = complex_release_dict
                                    date_found = True

                                    # tempList = []
                                    # for li_ele in li_elements:
                                    #     tempList.append(citation_check(li_ele.text))
                                    # infobox_dict[text_in_row] = single_item_list_check(tempList)

            # Test Check - TD -> Div:class_'plainlist' -> UL -> LI
            # Simple with multiple rows
            # TR - Table Row
            #   TH - Table Head -> 'Release'
            #   TD - Table Data
            #       Div - class="plainlist"
            #           UL -
            #               LI - 'Date -1'
            #                   SPAN - 'Country - NA'
            #               LI - 'Date -2'
            #                   SPAN - 
            if not complex_date and td_element.find('div', class_="plainlist"):
                li_elements = td_element.find_all('li')
                if li_elements:
                    tempList = []
                    for li_ele in li_elements:
                        tempList.append(self.__check_for_citation(li_ele.text))
                    infobox_dict[text_in_row] = single_item_list_check(tempList)
                    date_found = True
            
            # Test Check - TD -> None - just text
            # Simple 
            # TR - Table Row
            #   TH - Table Head -> 'Release'
            #   TD - Table Data -> '29 January 2025'
            elif not complex_date:
                tempList = []
                for li_element in td_element.find_all('li'):                         
                    tempList.append(self.__check_for_citation(li_element.text))
                infobox_dict[text_in_row] = single_item_list_check(tempList) 
                date_found = True

            if not date_found:
                infobox_dict[text_in_row] = "No Confirmed Release Date"

        except Exception as e:
            print(e)
            print("Failed to get the Release Date - Element Data on this Wikipedia page.") 
        finally:
            return infobox_dict

    def __get_scores_info(self, soup:BeautifulSoup):
        '''
        Gets the Scores and Aggregate Scores out of the Review Box on the Wikipedia page.
        '''
        reception_dict = {} 

        try:  
            if soup.find('div', class_="video-game-reviews"):
                reviewDiv = soup.find('div', class_="video-game-reviews")
                for table in reviewDiv.find_all("table"):
                    reception_dict = self.__get_aggregator_scores_info(table, reception_dict)
                    reception_dict = self.__get_review_scores_info(table, reception_dict) 
        except:
            print("Error - Reception Info Table Method failed to retrieve information on this page.")
        finally:
            return reception_dict

    def __get_aggregator_scores_info(self, table:bs4.element.Tag, reception_dict:dict):
        '''
        Specifically gets the Aggregate Scores out of the Review Box.
        '''
        try:
            if "vgr-aggregators" in str(table['class']):  
                tr_rows = table.find_all("tr")
                if tr_rows: 
                    for tr_row in tr_rows:
                        if "Aggregator" not in tr_row.text and '<th' not in str(tr_row.contents): 
                            tempList = []                                      

                            td_elements_in_row = tr_row.find_all('td')       

                            if td_elements_in_row:    
                                row_title = td_elements_in_row[0].text

                                for element in td_elements_in_row[1:]: 
                                    # print(element.find(text=True, recursive=False)) # Print Test to check text found in the table row.
                                    tempList.append(element.find(string=True, recursive=False))        

                                reception_dict[row_title] = tempList                  
        except Exception as e:
            print("Error Thrown - Searching for Aggregator scores failed.")
            print(e)
        finally:
            return reception_dict

    def __get_review_scores_info(self, table:bs4.element.Tag, reception_dict:dict):
        '''
        Specifically gets the Review Scores out of the Review Box.
        '''
        try:
            if "vgr-reviews" in str(table['class']): 
                for tr_row in table.find_all("tr"):
                    if "Publication" not in tr_row.text:
                        tempList = []
                        if tr_row.find_all('td'):
                            if len(tr_row.find_all('td')) > 2:
                                # There are more than two columns for this game's reviews
                                # One for the reviewers, and two or more others for the game's scores
                                row_name = tr_row.find_all('td')[0].text

                                score_elements = tr_row.find_all('td')

                                for score in score_elements: 

                                    tempList = self.__get_score_element_info(score, tempList) 

                                reception_dict[row_name] = tempList[1:] 
                            else:
                                # There are only two columns for this game's reviews
                                # One for the reviewer and One for the score
                                row_name = tr_row.find_all('td')[0].text

                                score_element = tr_row.find_all('td')[1]

                                tempList = self.__get_score_element_info(score_element, tempList)                            
                                
                                reception_dict[row_name] = tempList[0]
        except Exception as e:
            print("Error Thrown - Searching for Review scores failed.")
            print(e)
        finally:
            return reception_dict


    def __get_score_element_info(self, score, tempList:list):
        '''
        Checks the Score Eleemnt if it is a Star review or a normal string/number score, and return that score element data.
        '''
        has_stars = False

        if score.find_all("span"):
            for span_inner_element in score.find_all("span"):
                if span_inner_element.has_attr('title'):
                    tempList.append(str(span_inner_element['title']))
                    has_stars = True
                    break

        if not has_stars:
            for element in score.contents:
                if "<sup" in str(element) or "<br" in str(element):
                    pass
                else:
                    tempList.append(element.text)
        
        return tempList


    def __check_results(self, response:requests.Response, game_title:str):
        '''
        Checks the first response result from using the first search Wikipedia URL.\n 
        Either the search URL will take us directly to the game's Wikpedia page,\n
        or to a page of multiple search results that may contain the game's series or game's specific Wikipedia page.
        '''
        correct_wikipage_link = ''
        wikipage_result_type = ""

        web_html = response.text

        soup = BeautifulSoup(web_html, 'html.parser')  

        try:
            # Search results in the game's series/franchise wikipage
            if soup.find("table", class_="release-timeline") and soup.find('table', class_="hproduct"):

                wikipage_result_type, correct_wikipage_link = self.__check_series_page(soup, game_title)

            # Search results in a list of results 
            # Will need to check through it to find the game's series page or the game page itself
            elif soup.find('h2', id="Most_commonly"): 

                wikipage_result_type, correct_wikipage_link = self.__check__most_commonly_page(soup, game_title)          
            
            # Search results in a 'does not exist' wikipage
            elif soup.find('p', class_="mw-search-createlink"):
                if "does not exist" in soup.find('p', class_="mw-search-createlink").text:
                    wikipage_result_type = 'No Results'
                    # print("No search results for this game.")
            
            # Search results in a successful and correct wikipage for the game 
            elif soup.find('table', class_='ib-video-game'):
                wikipage_result_type = 'Found Page'
            
            else:
                # print("Wikipage does not match any game page type.")
                wikipage_result_type = 'No Results'

        except:
            # print("Wiki page search failed.")
            wikipage_result_type = 'No Results'

        return wikipage_result_type, correct_wikipage_link

    def __check__most_commonly_page(self, soup:BeautifulSoup, game_title:str):
        '''
        Checks the most common section of the search results page.\n
        Will typically contain the game's series or game's Wikipedia page that is needed to complete this search.
        '''
        # print(f"Search resulted in multiple result types for the game: {game.name}")
        # print("Checking the Most Commonly section for the game.")

        correct_wikipage_link = '' 

        li_elements = soup.find_all('li')
        if li_elements:
            for list_element in li_elements:
                if "video game series" in list_element.text:
                    #  or "video game" in list_element.text
                    # print(list_element.text)
                    series_page_link = "https://en.wikipedia.org" + str(list_element.find('a')['href'])  
                    inner_response = self.reponse(series_page_link)

                    web_html = inner_response.text

                    soup = BeautifulSoup(web_html, 'html.parser')  

                    wikipage_result_type, correct_wikipage_link = self.__check_series_page(soup, game_title)
                    break
                else:
                    wikipage_result_type = "No Results"
        else:
            wikipage_result_type = "No Results"

        return wikipage_result_type, correct_wikipage_link


    def __check_series_page(self, soup:BeautifulSoup, game_title:str):
        '''
        If the search URL or page results turns out to be a series page of the game's franchise,\n
        go through this franchise Wikpedia page to locate the correct URL for the game being searched for. 
        '''
        correct_wikipage_link = "" 

        # print("It appears we might be on the game's Series/Franchise page.") 
        release_table = soup.find("table", class_="release-timeline")
        release_products: list = []
        for tr_row in release_table.find_all('tr'):
            if tr_row.find('td'):
                release_products.append(tr_row.find('td'))

        best_element = None 

        if release_products:
            for product in release_products:
                if self.check_title_match(product.text, game_title):  
                    best_element = product
                    break
        
        if best_element:
            correct_wikipage_link = "https://en.wikipedia.org" + str(best_element.find('a')['href'])
            wikipage_result_type = "Series"
        else:
            wikipage_result_type = "No Results"
        
        return wikipage_result_type, correct_wikipage_link         

    def __check_for_citation(self, text:str) -> str:
        '''
        Text will contain a citation block sometimes\n
        that we will need to remove from the string\n 
        to make the string look more presentable.
        '''
        # citation_check = lambda x: str(x).split('[')[0] if "[" in x else x
        if '[' in text:
            text = str(text).split('[')[0]
        
        return text