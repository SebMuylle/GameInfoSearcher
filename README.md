# GameInfoSearcher
GameInfoSearcher is a project created to demonstrate my programming skills in the areas of object-oriented design, file management, database management, web navigation, data mangement (gathering and modifying data), multi-processing, and Graphics User Interface (GUI) design and implemention. 

This project is not intended for any commerical purposes, and is intended purely for educational/personal purposes to demonstrate one's programming skillsets.
 

# Project Details:

This program utilizes web tools to search for and gather information based on a list of games inputted by a user.

Once the program completes searching for the games' data, it will store them in a database, for example "Games.db",

and output a .Xlsx file with the list of games' data for the user to copy and paste from.    

It utilizes tools such as Selenium (specifially GeckoDriver - a FireFox web bot) and Python's Requests libraries to handle gathering and parsing website data. 

The Database Manager utilizes the sqlite3 library, and Xlsx Exporter utilizes the openpyxl library. 

Python's multiprocessing library is utilized to speed up the web tools and the program as a whole.

The GUI interface utilizes the PySide6 library.  

This program is designed to work on both Windows and Linux Platforms. 
 

# Installtion and Set-Up Steps: 
# (Important! Don't skip any steps)

1.) 
Download the source files from the GitHub repository and place the folder in any folder on your computer. 


2.)
Download the lastest geckodriver file from the following link: 

https://github.com/mozilla/geckodriver 

For Windows users, you can just place the geckodriver.exe file within the program's Driver folder located at the following path -> "..\GameInfoSearcherV1\web_hunters\Drivers".

For Linux users, please search for specific instructions on how to install geckodriver for your Linux Distro. 

Here are some articles that can help with installing geckodriver on your Linux platform:

https://www.baeldung.com/linux/geckodriver-installation

https://stackoverflow.com/questions/41190989/how-do-i-install-geckodriver

Please note: Placement of where you install your geckdriver file on your Linux machine is crucial to the operation of this program.

Typically, it is installed into the '/usr/local/bin' folder on your Linux machine. But this may differ depending on each Linux machine.


2a.)
Optionally, if you are familiar with FireFox and wish to utilize any web plugins/extensions, you can place XPI files (*.xpi) 

into the following folder - "..\GameInfoSearcherV1\web_hunters\firefoxprofile"


3.)
While this third step is optional, users should enter their own web headers into settings of the program.

This ensures better search results because the requests library in python by default utilizes web headers that shows the web request is being made by a web bot.  

Searching online for "what are my web headers" should help to provide details what your current web headers are.

Link to one such web header tool:

https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending/

Once you have found your web headers, please enter as a dictionary style list within your program's settings menu or typed into the UserSettings text file. 

The format should be as follows:

{ 'User-Agent': 'Replace-me-Mozilla/5.0...',

  'Accept-Language': 'Replace-me-en-US...' }

Where you will change the User-Agent and Accept-Language's values with what is shown by the web header tool.


4.)
If there are any missing Python Libraries such as Selenium or Pyside6, please ensure these are installed onto your computer by using Python's pip console tool or by other means.  

Libraries/Packages used in this program:
PySide6
requests
urllib3
selenium
openpyxl
cydifflib
beautifulsoup4
 

# Operation (How To Use):

1.)
Start the program by using your platform's preferred Command Console/Terminal and run the following python command to start the program:

Windows Command:

python PATH:\TO\FOLDER\GameInfoSearcherV1\main.py

Linux Command:

python3 /PATH/TO/FOLDER/GameInfoSearcherV1/main.py


2.)
Upon launching the program, the user will be presented with the Game Information Searcher Window. 

Here the user will be given the choice to add a single game title to the list on the right, or utilize the 'Get Test List' button to get several titles from a text file. (Please see the F.A.Q. Section below to see how to format the Text List.) 
As well as, the ability to choose to check off which website to search for data from. 

To remove a single game from the list on the right, double click the item in the list. To clear the list of all game titles, select the Options Menu Button towards the top of the window, and select the button option "Clear List".


2a.)
In addition, the program's settings can be accessed via the "Settings" button under the Options Menu Button. Here you can change the wait time between searches, the program's web headers, as well as where the database file or where spreadsheet will be exported out to. 


3.)
After you have added a list of games to search for and selected your website options, the "Start Search" button will become available to click on. 

Once you click this "Start Search" button, the Game Information Searcher Window will close out and your computer's console will begin reporting the program's process and activities as it searches for each game's data on each website.  


4.) 
Once the program has completed all data searches, it will report where the data has been saved to. If it is the first time running the program, a database will generated and saved to the path set in the Settings. 

Finally, the program will generate a .Xlsx file and export out the spreadsheet with the title, which is set in the settings, followed by the date the program completed its search. For example, "Game Excel Result - 01-01-2025".

 

# F.A.Q.

* How do I make the program search for games' data faster? 

You may either change the wait times within the settings menu on the program's window/GUI, or manually in the Settings.txt file contained within the "..\GameInfoSearcherV1\UserSettings" Folder. 

Within the GUI window, select the Options Menu Button from the top left of the window. Then from that menu, click on the Settings menu option to open the settings menu and navigate to the wait time settings.  

To change the settings within the Settings.txt file, open the text file in any text editor and change the values for the Min-WaitTime and Max-WaitTime to any values. Floating point numbers such "3.333" will not be accepted and will be converted to an integar.

Please note when changing the wait times: 

The program's default time settings ensures the program is able to successfully retrieve data from the various websites it searches. 

Otherwise, if set to a lower speed such as one second, it can result in websites denying the program's web requests, prevent the program from gathering data from the website, and possibly blacklist your web access to that website. 

The 'slow' random wait times help to prevent these roadblocks and ensures accurate results. 

* How do I use the "Get Text List" button option listed on the Window/GUI? 

Create a text file and title it whatever you want it to be, for example 'GameList.txt'.

In the text file, write each game title on a new line. (Typically this done by pressing the 'Enter' key to create a newline.) 

For example:

Game Title 1
Game Title 2
Game Title 3 

There are no limits on how many titles are read from the text file, so you can add as many as you desire. Just note, the more game titles you add, the more time it will take to retrieve their information depending on the wait time. 
