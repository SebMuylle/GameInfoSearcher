from PySide6.QtWidgets import QWidget, QFileDialog, QVBoxLayout, QHBoxLayout, QApplication, QPushButton, QLabel, QListWidget, QLineEdit, QCheckBox, QSplitter, QTextEdit, QSpinBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import os   

try:
    from ClassContainers.Options import UserSettings 
except ImportError as e:
    print(e) 
    print("Missing Modules in OptionGUI.py.")

class CustomButton(QPushButton):
    def __init__(self, text, w, h, enableButton=True):
        super().__init__(text=text)
        self.setFixedSize(w, h) 
        self.setEnabled(enableButton)
        font = QFont()
        font.setPointSize(10)
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
        self.setChecked(False)

        self.setCheckable(False)

class XLSXBlock(QWidget):
    '''XLSX Block Widget - presents and allows the user to change the XLSX spread sheet settings for this program.'''
    def __init__(self, fontsize, settings:UserSettings):
        super().__init__()

        self.settings = settings

        self.mainWidgetLayout = QVBoxLayout()

        self.mainWidgetLayout.setSpacing(10)
        self.mainWidgetLayout.setContentsMargins(0, 0, 0, 0)
 
        self.xlsx_title = CustomLabel("Export Folder\nFolder in which to generate a\nSpreadsheet-XLSX File in.", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft)

        self.xlsx_button = CustomButton("Set File Path", 200, 30, True)

        self.xlsx_button.clicked.connect(self.setFilePath)

        self.mainWidgetLayout.addWidget(self.xlsx_title)
         
        self.lineEditExportFolder = QLineEdit() 

        self.lineEditExportFolder.setStyleSheet("""
                        font-size: 18px
                        """)

        self.mainWidgetLayout.addWidget(self.lineEditExportFolder)

        self.mainWidgetLayout.addWidget(self.xlsx_button)

        self.xlsx_filename_label = CustomLabel("XLSX File Name", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft)

        self.mainWidgetLayout.addWidget(self.xlsx_filename_label)

        self.lineEditFileName = QLineEdit()

        self.lineEditFileName.setStyleSheet("""
                        font-size: 18px
                        """)

        self.mainWidgetLayout.addWidget(self.lineEditFileName)

        self.xlsx_worksheet_title_label = CustomLabel("XLSX Worksheet Title", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft)

        self.mainWidgetLayout.addWidget(self.xlsx_worksheet_title_label)

        self.lineEditWorkSheet = QLineEdit()

        self.lineEditWorkSheet.setStyleSheet("""
                        font-size: 18px
                        """)
        
        self.mainWidgetLayout.addWidget(self.lineEditWorkSheet)

        self.mainWidgetLayout.addStretch(1)

        self.setLayout(self.mainWidgetLayout) 

        self.lineEditFileName.textChanged.connect(self.setSettings)
        self.lineEditWorkSheet.textChanged.connect(self.setSettings)
        self.lineEditExportFolder.textChanged.connect(self.setSettings)

        self.getSettings()

    def setFilePath(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder") 
        if folder_path:                
            if os.path.isdir(folder_path): 
                self.lineEditExportFolder.setText(folder_path)
                self.setSettings() 

    def getSettings(self):
        if self.settings.tempChangesMadeAny and self.settings.xlsxTempChange:  
            filename, worksheet, filepath = self.settings.getXlsxTempDict()

            self.lineEditExportFolder.setText(filepath) 

            self.lineEditFileName.setText(filename)

            self.lineEditWorkSheet.setText(worksheet)

        else:
            self.lineEditExportFolder.setText(self.settings.export_xlsx_file_path) 

            self.lineEditFileName.setText(self.settings.xlsx_filename)

            self.lineEditWorkSheet.setText(self.settings.xlsx_worksheet_title)

    def setSettings(self):
        self.settings.setXlsxTempDict(self.lineEditFileName.text(), self.lineEditWorkSheet.text(), self.lineEditExportFolder.text()) 


class DataBaseBlock(QWidget):
    '''DataBase Block Widget - presents and allows the user to change the Database settings for this program.'''
    def __init__(self, fontsize, settings:UserSettings):
        super().__init__()

        self.settings = settings

        self.mainWidgetLayout = QVBoxLayout()

        self.mainWidgetLayout.setSpacing(10)
        self.mainWidgetLayout.setContentsMargins(0, 0, 0, 0)

        # First Row - DataBase File Name
        self.layoutFirstRow = QVBoxLayout()

        self.firstRowTitle = CustomLabel("Database File Name", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft)

        self.firstRowLineEdit = QLineEdit("Games.db")

        self.firstRowLineEdit.setStyleSheet("""
                        font-size: 18px
                        """)

        self.layoutFirstRow.addWidget(self.firstRowTitle)
        self.layoutFirstRow.addWidget(self.firstRowLineEdit)

        # Second Row - DataBase Folder Path
        self.layoutSecondRow = QVBoxLayout() 

        self.secondRowTitle = CustomLabel("Database Folder\nFolder in which to access or\ncreate the database file in.", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 

        self.setPathButton = CustomButton("Set File Path", 200, 30, True)

        self.setPathButton.clicked.connect(self.setFilePath)

        self.layoutSecondRow.addWidget(self.secondRowTitle)

        self.secondRowLineEdit = QLineEdit("C:\\")

        self.secondRowLineEdit.setStyleSheet("""
                        font-size: 18px
                        """)
        
        self.layoutSecondRow.addWidget(self.secondRowLineEdit)

        self.layoutSecondRow.addWidget(self.setPathButton)

        # Third Row - DataBase Table Name  
        self.layoutThirdRow = QVBoxLayout()

        self.thirdRowTitle = CustomLabel("Database Table Name", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 

        self.thirdRowLineEdit = QLineEdit("GAMES")

        self.thirdRowLineEdit.setStyleSheet("""
                        font-size: 18px
                        """)

        self.layoutThirdRow.addWidget(self.thirdRowTitle)
        self.layoutThirdRow.addWidget(self.thirdRowLineEdit)       
 
        self.mainWidgetLayout.addLayout(self.layoutSecondRow)
        
        self.mainWidgetLayout.addLayout(self.layoutFirstRow)      

        self.mainWidgetLayout.addLayout(self.layoutThirdRow)

        self.mainWidgetLayout.addStretch(1)

        self.setLayout(self.mainWidgetLayout)

        self.firstRowLineEdit.editingFinished.connect(self.setSettings)
        self.secondRowLineEdit.editingFinished.connect(self.setSettings)
        self.thirdRowLineEdit.editingFinished.connect(self.setSettings)

        self.getSettings()

    def setFilePath(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder") 
        if folder_path:                
            if os.path.isdir(folder_path): 
                self.secondRowLineEdit.setText(folder_path) 
                self.setSettings()
 
    def getSettings(self):
        if self.settings.tempChangesMadeAny and self.settings.databaseTempChange: 
            databaseName, pathTo, tableName = self.settings.getDataBaseTempDict()

            self.firstRowLineEdit.setText(databaseName)
            self.secondRowLineEdit.setText(pathTo)
            self.thirdRowLineEdit.setText(tableName)
 
        else:
            self.firstRowLineEdit.setText(self.settings.gameDataBaseName)
            self.secondRowLineEdit.setText(self.settings.path_to_database)
            self.thirdRowLineEdit.setText(self.settings.database_table_name)

    def setSettings(self):
        self.settings.setDataBaseTempDict(self.firstRowLineEdit.text(), self.secondRowLineEdit.text(), self.thirdRowLineEdit.text())
        

class HeadersBlock(QWidget):
    '''Headers Block Widget - presents and allows the user to change the web headers settings for this program.'''
    def __init__(self, fontsize, settings:UserSettings):
        super().__init__()

        self.settings = settings

        self.mainWidgetLayout = QVBoxLayout()

        self.mainWidgetLayout.setSpacing(10)
        self.mainWidgetLayout.setContentsMargins(0, 0, 0, 0)

        self.innerLayout = QVBoxLayout()

        self.headersTitle = CustomLabel("Request Headers\nUsed for the program's web requests.\nFormatted as a 'key' : 'values' dictionary.", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 

        self.headersTextBox = QTextEdit('''{}''')

        self.headersTextBox.setStyleSheet("""
                    font-size: 15px    
                """)
        
        self.headersTextBox.resize(500, 300)
        
        self.innerLayout.addWidget(self.headersTitle)
        self.innerLayout.addWidget(self.headersTextBox)

        self.mainWidgetLayout.addLayout(self.innerLayout)

        self.mainWidgetLayout.addStretch(1)

        self.setLayout(self.mainWidgetLayout)

        self.headersTextBox.textChanged.connect(self.setSettings)

        self.getSettings()

    def getSettings(self):
        if self.settings.tempChangesMadeAny and self.settings.webHeadersTempChange: 
            self.headersTextBox.setText(self.settings.getWebHeadersTempDict())
        else:
            self.headersTextBox.setText(str(self.settings.web_tool_headers))
    
    def setSettings(self):
        self.settings.setWebHeadersTempDict(self.headersTextBox.toPlainText())

class WaitTimeBlock(QWidget):
    '''WaitTime Block Widget - presents and allows the user to change the wait time settings for this program.'''
    def __init__(self, fontsize, settings:UserSettings):
        super().__init__()

        self.settings = settings
 
        self.mainWidgetLayout = QVBoxLayout()

        self.mainWidgetLayout.setSpacing(10)
        self.mainWidgetLayout.setContentsMargins(0, 0, 0, 0)
 
        self.waitTimeTitle = CustomLabel("Wait Time\nUsed to set how long the program\npauses between web searches.", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 
        #  - Used to set how long the Game Searcher\npauses between web searches
 
        self.minLabel = CustomLabel("Minimum Seconds:", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 

        self.minSpinBox = QSpinBox()

        self.minSpinBox.setMinimum(1)

        self.minSpinBox.setMaximum(119)     

        self.minSpinBox.setSingleStep(1)

        self.minSpinBox.setValue(9)

        self.minSpinBox.setStyleSheet("""
                            font-size: 15px
                            """) 

        self.maxLabel = CustomLabel("Maximum Seconds:", fontsize, "white", False, True, Qt.AlignmentFlag.AlignLeft) 

        self.maxSpinBox = QSpinBox()

        self.maxSpinBox.setMinimum(2)

        self.maxSpinBox.setMaximum(160)        

        self.maxSpinBox.setSingleStep(1)

        self.maxSpinBox.setValue(12)

        self.maxSpinBox.setStyleSheet("""
                            font-size: 15px
                            """) 

        self.mainWidgetLayout.addWidget(self.waitTimeTitle)
        
        self.mainWidgetLayout.addWidget(self.minLabel)

        self.mainWidgetLayout.addWidget(self.minSpinBox)

        self.mainWidgetLayout.addWidget(self.maxLabel)       

        self.mainWidgetLayout.addWidget(self.maxSpinBox)

        self.mainWidgetLayout.addStretch(1)

        self.setLayout(self.mainWidgetLayout)

        self.minSpinBox.valueChanged.connect(self.setSettings)
        self.maxSpinBox.valueChanged.connect(self.setSettings)

        self.getSettings()


    def getSettings(self):
        if self.settings.tempChangesMadeAny and self.settings.waitTimeTempChange:
            min, max = self.settings.getWaitTimeTempDict()
            
            self.minSpinBox.setValue(min)

            self.maxSpinBox.setValue(max)
        else:
            self.minSpinBox.setValue(self.settings.minTimeSeconds)

            self.maxSpinBox.setValue(self.settings.maxTimeSeconds)

        self.checkMinMaxRange(self.minSpinBox.value(), self.maxSpinBox.value())

    def setSettings(self): 

        self.checkMinMaxRange(self.minSpinBox.value(), self.maxSpinBox.value())

        self.settings.setWaitTimeTempDict(self.minSpinBox.value(), self.maxSpinBox.value())

    def checkMinMaxRange(self, min:int, max:int):
        '''
        Ensures whenever the user inputs a min and max values for the program that it always defaults to a reasonable range, 
        such as min = 9 and max = 10, whenever the user temps to make min to be greater than max by setting min to
        9 whereas max was at a lesser value such as 8. 
        '''
        # min 4 max 3
        # 4-3 = 1 
        # 1 + 1 = 2
        # max + 2 = 5
        # 55 min - 10 max = 45
        # 45 + 1 = 46
        # max + 46 = 56
        # if the minimum is greater than the max, automatically substract the two to find the difference
        # then add one to that difference before adding it back into the max.
        
        if min > max:
            diffNum = min - max 
            addToMax = diffNum + 1
            max = max + addToMax

            self.maxSpinBox.setValue(max)
   
    
class LeftColumn(QVBoxLayout):
    '''
    Left Column Layout - contains the list of options to allow the user to pick from. 
    '''
    def __init__(self, fontsize, parentWindow:QWidget):
        super().__init__()

        self.ref_to_right_column = None

        self.labelTitle = CustomLabel("Select Option:", fontsize, "white", False, False, alignment=Qt.AlignmentFlag.AlignLeft)

        self.addWidget(self.labelTitle)

        self.settingsList = QListWidget()

        self.settingsList.addItem("Time Management")
        self.settingsList.addItem("DataBase Management")
        self.settingsList.addItem("Export Management") 
        self.settingsList.addItem("Web Headers")

        self.settingsList.setStyleSheet(""" font-size: 16px """)

        self.addWidget(self.settingsList)

        self.okButton = CustomButton("OK", 240, 30, True)

        self.cancelButton = CustomButton("Cancel", 240, 30, True)

        self.addWidget(self.okButton)

        self.addWidget(self.cancelButton)

        self.cancelButton.clicked.connect(parentWindow.dropChanges)

        self.okButton.clicked.connect(parentWindow.acceptChanges)

    def connectRightColumnToList(self, ref):
        self.ref_to_right_column = ref

        self.settingsList.itemClicked.connect(self.ref_to_right_column.showSettingPage)

 

class RightColumn(QVBoxLayout):
    '''
    Right Column Layout - Presents the selected option for the user to interact with and change settings. 
    '''
    def __init__(self, fontsize, settings:UserSettings):
        super().__init__()

        self.font_size = fontsize

        self.settings = settings 

        self.currentWidget = None

        # # WaitTime Block 
        self.waitTimeBlock = WaitTimeBlock(self.font_size, self.settings)   

        self.addCurrentWidget(self.waitTimeBlock) 
 
    def removeCurrentWidget(self):
        self.currentWidget.hide()
        self.removeWidget(self.currentWidget)
        self.currentWidget.deleteLater()

    def addCurrentWidget(self, newCurrentWidget):
        self.addWidget(newCurrentWidget)
        self.currentWidget = newCurrentWidget
        
    def showSettingPage(self, item): 
        if item.text() == "Time Management":
            self.removeCurrentWidget()

            # # WaitTime Block 
            self.waitTimeBlock = WaitTimeBlock(self.font_size, self.settings)   

            self.addCurrentWidget(self.waitTimeBlock) 

        elif item.text() == "Export Management":
            self.removeCurrentWidget()
             
            # Xlsx Layout Block
            ## will contain the widgets and GUI elements to show the Export File Path and buttons for CSV Exports 
            self.xlsxBlock = XLSXBlock(self.font_size, self.settings) 

            self.addCurrentWidget(self.xlsxBlock) 

        elif item.text() == "DataBase Management":
            self.removeCurrentWidget()
             
            # Database Layout Block
            ## will contain the widgets and GUI Elements to show the Database elements such as its name and path
            self.databaseBlock = DataBaseBlock(self.font_size, self.settings)    

            self.addCurrentWidget(self.databaseBlock) 
        
        elif item.text() == "Web Headers":
            self.removeCurrentWidget()

            # Headers Layout Block
            ## will contain the widgets and GUI Elements that show the headers used in the Requests porition
            self.headersBlock = HeadersBlock(self.font_size, self.settings) 

            self.addCurrentWidget(self.headersBlock) 
 


class OptionWindow(QWidget):
    """
    Option Window that allows the user to change the settings of the program.
    """
    def __init__(self, userSettings: UserSettings):
        super().__init__()

        self.changes = False

        self.inLineFontSize = 12

        self.userSettings = userSettings

        self.setWindowTitle("Settings")

        self.setGeometry(10, 10, 590, 600)

        self.setFixedSize(590, 600)
        
        self.separator = QSplitter()

        self.separator.setFixedHeight(30)

        self.layoutMain = QVBoxLayout()
 
        self.layoutColumns = QHBoxLayout()

        self.leftColumnList = LeftColumn(self.inLineFontSize, self)

        self.layoutColumns.addLayout(self.leftColumnList)

        self.rightColumnWindow = RightColumn(self.inLineFontSize, self.userSettings) 

        self.layoutColumns.addLayout(self.rightColumnWindow)

        self.layoutColumns.setStretchFactor(self.leftColumnList, 1)

        self.layoutColumns.setStretchFactor(self.rightColumnWindow, 3)
        
        self.layoutMain.addLayout(self.layoutColumns)

        self.setLayout(self.layoutMain)

        self.leftColumnList.connectRightColumnToList(self.rightColumnWindow)

        # Sets the background color of the window and its widgets.
        self.setStyleSheet(""" 
            background-color: #33373B;
            color: white;
            """)    

    def center(self, app: QApplication):
        s_width, s_height = app.primaryScreen().size().toTuple()

        # Calculate window center position
        center_x = (s_width - self.width()) // 2
        center_y = (s_height - self.height()) // 2

        # Move the window to the center
        self.move(center_x, center_y)
    
    def closeEvent(self, event): 

        # If the changes are 
        if self.changes: 
            self.userSettings.saveTempDictChange()
            event.accept() 
        else: 
            self.userSettings.clearTempChangesMade()
            event.accept() 

    def acceptChanges(self): 
        self.changes = True
        self.close() 
    
    def dropChanges(self):
        self.changes = False
        self.close()