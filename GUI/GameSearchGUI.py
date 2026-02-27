from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QApplication, QMainWindow, QPushButton, QLabel, QListWidget, QLineEdit, QCheckBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont, QAction
import os

try:   
    from ClassContainers.UserInput import UserInstructions 
    from ClassContainers.Options import UserSettings 
    from GUI.OptionGUI import OptionWindow
except ImportError as e:
    print(e) 
    print("Missing Modules in GameSearchGUI.py.")

########## CUSTOM Q CLASSES ##############

class CustomButton(QPushButton):
    def __init__(self, text, w, h, enableButton=True):
        super().__init__(text=text)
        self.setFixedSize(w, h) 
        self.setEnabled(enableButton)
        font = QFont()
        font.setPointSize(15)
        self.setFont(font)
        self.setStyleSheet("background-color: #3a6067")

    def set_signal_connection(self, function_to_call):
        self.clicked.connect(function_to_call)
        
class CustomLabel(QLabel):
    def __init__(self, text, size, color, wordWrap=True, boldText=False, alignment=Qt.AlignmentFlag.AlignCenter):
        super().__init__(text)
        font = QFont()
        font.setPointSize(size)
        font.setBold(boldText) 
        self.setFont(font)
        self.setStyleSheet(f"color: {color}")
        self.setWordWrap(wordWrap)
        self.setAlignment(alignment) 

class CustomCheckBox(QCheckBox):
    def __init__(self, text):
        super().__init__(text)
        self.setStyleSheet("""
                            font-size: 20px;
                            color: #FFFFFF;
                            """)
        self.setChecked(True)
 
class CustomListWidget(QListWidget):
    '''Custom List Widget to contain the game list.'''
    def __init__(self, color):
        super().__init__()

        new_palette = self.palette()
        backgroundcolor = QColor(color)
        new_palette.setColor(QPalette.Active, QPalette.Base, backgroundcolor)
        self.setPalette(new_palette)

        
############

class CustomLeftVLayout(QVBoxLayout):
    '''
    Layout Widget contains the left side of the main window where the user will input their games to search for.
    '''
    def __init__(self, parent_ref):
        super().__init__()

        self.ref_to_parent = parent_ref # Reference to the layout's parent - mainly used to connect the layout's methods to the parent's methods. 

        self.ref_to_right = None
        
        # Widget Rows # 
        # First Row Widgets 
        # Label to mark the add single game line
        self.one_label = CustomLabel("Add Single Title:", 20, "white", alignment=Qt.AlignmentFlag.AlignLeft)
        # Line edit to allow the user to type in a game to add to the game list
        self.text_inputbox = QLineEdit() 
        # Button to add one game to the list before the search
        self.single_button = CustomButton("Add Game", 200, 40, True)
        # Button signal to connect to the add_one_game method
        self.single_button.clicked.connect(self.add_one_game) 

        # Second Row Widgets  
        # Label to mark where to use the get Text file button
        self.multi_label = CustomLabel("Add Several Titles:", 20, "white", alignment=Qt.AlignmentFlag.AlignLeft)
        # Button to get a text list to add a list of games to search
        self.mult_button = CustomButton("Get Text List", 400, 40, True)
        # Connect the button clicked signal to the function browse file
        self.mult_button.clicked.connect(self.browse_file)

        # Connects the LineEdit editingFinished signal to the add_one_game method 
        # This allows the user the ability to use the enter key to add game titles to the game list. 
        self.text_inputbox.editingFinished.connect(self.add_one_game)

        # CheckBox Section
        self.checkbox_label = CustomLabel("Please Check which Sites to Search Through:", 20, "white", alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Final Row Widgets  
        # Start Search Button - used to start the search program once a user has provided a list of games to search with
        self.start_button = CustomButton("Start Search", 400, 50, False)
        self.start_button.clicked.connect(self.ref_to_parent.start_program)
        
        ## Layouts Section
        # Need to set up a main vertical or horizontal to add to this CustomLeftVLayout
        self.main_column = QVBoxLayout()
        
        ### FIRST ROW SECTION
        # First row V Box Layout to help organize the title and inputs into the a center alignment 
        self.first_row_v_layout = QVBoxLayout()
        
        # Used to set the alignment of the Layout widget 
        self.first_row_v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
       
        # Add a title label to the main_column
        self.first_row_v_layout.addWidget(self.one_label) 
        
        # Add a horizontal box
        self.first_row_input = QHBoxLayout()

        # Add the text input box and single button widgets into the first row layout widget
        self.first_row_input.addWidget(self.text_inputbox)
        self.first_row_input.addWidget(self.single_button)

        # Add this H layout to the main column
        self.first_row_v_layout.addLayout(self.first_row_input)

        self.main_column.addLayout(self.first_row_v_layout)
        ##
        
        ### SECONT ROW SECTION
        # Second row V Box Layouyt to help align the title and input button to the center of the window
        self.second_row_v_layout = QVBoxLayout()

        # Used to set the alignment of the Layout widget 
        self.second_row_v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Add a label for the multi search button section
        self.second_row_v_layout.addWidget(self.multi_label)
        
        # Add a horizontal box
        self.second_row = QHBoxLayout()

        # Used to set the alignment of the Layout widget 
        self.second_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the multi button this horizontal box
        self.second_row.addWidget(self.mult_button)

        # Add the second row of input buttons to the second row VBoxLayout
        self.second_row_v_layout.addLayout(self.second_row)

        # Add this H layout to the main column
        self.main_column.addLayout(self.second_row_v_layout)
        ##

        #### CheckBox Section ####
        self.checkbox_row_v_layout = QVBoxLayout()

        self.checkbox_row_v_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        
        self.checkbox_row_v_layout.addWidget(self.checkbox_label)

        self.checkbox_row = QHBoxLayout() 

        self.checkboxWikipedia = CustomCheckBox("Wikipedia")

        self.checkboxSteam = CustomCheckBox("Steam") 

        self.checkboxOpenCritic = CustomCheckBox("OpenCritic") 

        # Connecting the Check Boxes to their respective state change methods in the parent class
        self.checkboxSteam.checkStateChanged.connect(self.ref_to_parent.checkbox_steam_changed) 

        self.checkboxOpenCritic.checkStateChanged.connect(self.ref_to_parent.checkbox_opencritc_changed) 

        self.checkboxWikipedia.checkStateChanged.connect(self.ref_to_parent.checkbox_wiki_changed)

        self.checkbox_row.addWidget(self.checkboxWikipedia)
        
        self.checkbox_row.addWidget(self.checkboxSteam) 

        self.checkbox_row.addWidget(self.checkboxOpenCritic) 

        self.checkbox_row_v_layout.addLayout(self.checkbox_row)

        self.main_column.addLayout(self.checkbox_row_v_layout)

        ### FINAL SECTION
        # Add the start program button to the bottom of layout
        # Add a horizontal box
        self.final_row = QHBoxLayout()
        # Align the final button to the center
        self.final_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add the widget to the final row
        self.final_row.addWidget(self.start_button)
        # Add this H layout to the main column
        self.main_column.addLayout(self.final_row)
        ##

        # This is the final step in setting up the layout to the CustomLeftVLayout 
        self.addLayout(self.main_column) 

    def set_ref_to_right(self, new_ref_to_right):
        '''
        Set reference to the right layout.

        :param new_ref_to_right: Right Layout Reference.
        '''
        self.ref_to_right = new_ref_to_right

    def add_one_game(self):
        '''
        Function used to grab the text from the QLineEdit - text_inputbox and checks if it is a valid user input\n
        once it has been validated, it will be inserted into the list box on the right side of the window\n
        tied to the add game button and the editingFinished signal of the QLineEdit.
        ''' 
        game_text = self.text_inputbox.text()
        if game_text and game_text.strip(): # checks to make sure the game title that was typed in is not blank nor only contains white spaces example -> "" or "   "  
            self.ref_to_right.update_list_by_one(game_text.strip()) # Removes any extra white space from the game title text 
            self.start_button.setEnabled(True)
            self.text_inputbox.clear() 
        else: 
            self.text_inputbox.clear()
        
        self.text_inputbox.setFocus() # Sets the focus back onto the input box after the user enters a game title

    def browse_file(self):
        '''Browse for the user's text file containing the list of games to add to the list.''' 
        fileName = QFileDialog.getOpenFileName(dir=(os.path.realpath(os.path.dirname(__file__))))

        if fileName:               
            # Checks to make sure the the file path is referencing a text file
            if ".txt" in fileName[0]:
                # If it is a valid txt file then pass that file path to the right side to update and process the game list
                self.ref_to_right.getGameListFromTxtFile(fileName[0])
                # Also enable the start button as a valid file path was provided
                self.start_button.setEnabled(True) 
        
        
        
####################################################################################
 
class CustomRightVLayout(QVBoxLayout):
    '''
    Layout Widget contains the right side of the main window where the list will appear.
    '''
    def __init__(self):
        super().__init__()

        # Set variable to store all of the game names.
        self.game_list = set() 

        # Reference to the left layout widget to get data and information from it and vice versa.
        self.ref_to_left = None 
        
        # List widget reference
        self.list = CustomListWidget('light blue')

        # List signal connection for double clicked items to the method remove_item.
        self.list.itemDoubleClicked.connect(self.remove_item)
        
        # Add the list widget to the CustomRightVLayout.
        self.addWidget(self.list)
 
    # Setter method to set the reference to the left layout widget.
    def set_ref_to_left(self, new_ref_to_left):
        self.ref_to_left = new_ref_to_left 

    #########################################
    def remove_item(self, item):         
        # Uses the current selected row to remove that item from the list widget.
        self.list.takeItem(self.list.currentRow())

        # Removes the item from the game_list variable.
        self.game_list.remove(item.text()) 
       
    def clear_list(self):
        '''
        Clears the game list and resets the game_list set. 
        '''
        self.list.clear()
        self.game_list = set()
        
    def update_list_by_one(self, title):
        '''
        Update the list widget with one title. 

        :param title: Game title.   
        ''' 
        if title not in self.game_list:  
            self.game_list.add(title)
            self.list.addItem(title) 
    
    def getGameListFromTxtFile(self, txt_file_path:str):
        '''
        Get a list of game titles from a user's text file. 

        :param txt_file_path: File Path to the text file.
        :type txt_file_path: str
        '''
        links_text = open(txt_file_path, "r+",encoding='utf-8')
        text_content = links_text.read()
        if text_content == "": 
            links_text.close()
        else:
            text_list = text_content.split('\n') 
            links_text.close()
            for i in text_list:
                if i not in self.game_list: 
                    self.game_list.add(i)
                    self.list.addItem(i) 


#########################################################################################################################################
 
class CustomMainWindow(QMainWindow):
    '''Main Window Class for ths Game Search GUI Program.'''
    def __init__(self, app: QApplication, UI: UserInstructions, settings: UserSettings):
        super().__init__()  

        self.app = app  
        self.UI = UI # UserInstructions
        self.uSettings = settings # UserSettings

        # Sets the title of the window. 
        self.setWindowTitle("Game Information Searcher - by Sebastian Muylle")

        self.setGeometry(10, 10, 1000, 450)

        self.mainLayoutH = QHBoxLayout()

        self.left_layout = CustomLeftVLayout(self)
        self.right_layout = CustomRightVLayout()

        self.mainLayoutH.addLayout(self.left_layout)
        self.mainLayoutH.addLayout(self.right_layout)

        # Set stretch factor for the left widget (3 parts).
        self.mainLayoutH.setStretchFactor(self.left_layout, 3)

        # Set stretch factor for the right widget (1 part).
        self.mainLayoutH.setStretchFactor(self.right_layout, 1)

        self.mainWidget = QWidget()

        self.mainWidget.setLayout(self.mainLayoutH)

        self.setCentralWidget(self.mainWidget)

        # Sets the references to each other's widget so the two layout widgets can update each other's information.
        self.left_layout.set_ref_to_right(self.right_layout)
        self.right_layout.set_ref_to_left(self.left_layout) 

        ## QActions for ToolBar or Menu 
        # QAction for recentering the window.
        button_action = QAction(text="Re-Center Screen", parent=self)
        button_action.setStatusTip("Recenter the screen!")
        button_action.triggered.connect(self.__center) 

        # QAction to exit the program.
        button_action_two = QAction(text="Quit", parent=self)
        button_action_two.setStatusTip("Quit the Program!")
        button_action_two.triggered.connect(self.exitProgram) 

        ## Options Menu QActions
        # QAction to clear the game list.
        button_clear_action = QAction(text="Clear List", parent=self)
        button_clear_action.setStatusTip("Clear Game List")
        button_clear_action.triggered.connect(self.right_layout.clear_list) # Connected to the method that clears the game list. 

        # QAction to access the program's Settings Menu.
        button_settings_action = QAction(text="Settings", parent=self)
        button_settings_action.setStatusTip("Set User Settings")
        button_settings_action.triggered.connect(self.open_settings_menu) # Connected to the method to open the settings menu.

        # Menus for the program.
        menu = self.menuBar()
        file_menu = menu.addMenu("Menu")
        file_options = menu.addMenu("Options")

        # File menu additions to the main "Menu".
        file_menu.addAction(button_action)
        file_menu.addAction(button_action_two)

        # File menu additions to the "Options" menu.
        file_options.addAction(button_settings_action)
        file_options.addAction(button_clear_action)

        # Sets the background color of the main window and its widgets.
        self.setStyleSheet(""" 
            background-color: #33373B;
            color: white;
            """)        

        # Centers the app in the window screen.
        self.__center() 
    
    def start_program(self):
        '''
        Once the program is provided a list of games to search for and the user clicks on the start button.
        \nThe program will announce it is starting and provide a initial count of how many games it will check.
        \nThis method also sets the UserInstructions object's gamelist and call for the GameGUI to close out. 
        '''
        print("Starting the Search Program!")
        self.UI.set_start_program_value(True)
        
        # Console output to allow the user to see how many games are going to be searched through.
        count = len(self.right_layout.game_list)
        if count == 1:
            print("User provided " + str(count) + " game to search for.")
        else:
            print("User provided " + str(count) + " games to search for.") 
        self.hide() # Hide the window 

        self.UI.set_game_list(self.right_layout.game_list) # Gets the games from the game_list element and copies it to the UserInstructions's game set variable. 
        
        self.exitProgram() # Close out the application so the program can continue.
    
    def checkbox_steam_changed(self, state):
        if (Qt.CheckState.Checked == state): 
            self.UI.set_search_bValue("Steam", True)
        else:
            self.UI.set_search_bValue("Steam", False)
    
    def checkbox_opencritc_changed(self, state):
        if (Qt.CheckState.Checked == state): 
            self.UI.set_search_bValue("OpenCritic", True)
        else:
            self.UI.set_search_bValue("OpenCritic", False) 

    def checkbox_wiki_changed(self, state):
        if (Qt.CheckState.Checked == state): 
            self.UI.set_search_bValue("Wikipedia", True)
        else:
            self.UI.set_search_bValue("Wikipedia", False)  

    def __center(self):
        '''
        Centers the window to the center of the screen.
        '''
        s_width, s_height = self.app.primaryScreen().size().toTuple()

        # Calculate window center position.
        center_x = (s_width - self.width()) // 2
        center_y = (s_height - self.height()) // 2

        # Move the window to the center.
        self.move(center_x, center_y) 

    def exitProgram(self):        
        self.app.quit()

    def open_settings_menu(self):
        s_width, s_height = self.app.primaryScreen().size().toTuple()

        # Calculate window center position.
        center_x = (s_width - self.width()) // 2
        center_y = (s_height - self.height()) // 2

        self.windowOptions = OptionWindow(self.uSettings)

        self.windowOptions.show()

        self.windowOptions.move(center_x, center_y)


class GameGUI():
    '''
    Class sets up the main program's GUI and sets the UserInstructions and UserSettings objects' variables.
    ''' 
    def __init__(self, uInstructions: UserInstructions, uSettings: UserSettings):     
        self.app = QApplication()
        self.window = CustomMainWindow(self.app, uInstructions, uSettings)
        self.window.show()
        self.app.exec() 