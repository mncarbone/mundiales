#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      mcarbone
#
# Created:     28/08/2012
# Copyright:   (c) mcarbone 2012
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import sys, os, subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import Qsci, QtCore, QtGui, uic

#1#from ui.main import Ui_MainWindow

#( Ui_MainWindow, QMainWindow ) = uic.loadUiType( 'ui/main.ui' )

class MainWindow(QMainWindow):#1#, Ui_MainWindow):

    def __init__(self, file):

        QMainWindow.__init__(self)
##        self.ui = Ui_MainWindow()
        self.ui = uic.loadUi(os.path.dirname(os.path.realpath(sys.argv[0]))+"/main.ui", self)
        self.fileName = file

        self.lastDir = os.path.dirname(self.fileName)
       # set up User Interface (widgets, layout...)
##        self.ui.setupUi(self)
        
        
        self.setupEditor()
        
        if self.fileName != '':
            self.fileOpen(self.fileName)

        # custom slots connections

        QObject.connect(self.ui.pushButton,SIGNAL("released()"),self.run) # signal/slot connection
        QObject.connect(self.ui.actionNuevo,SIGNAL("triggered()"),self.new) # signal/slot connection
        QObject.connect(self.ui.actionAbrir,SIGNAL("triggered()"),self.open) # signal/slot connection
        QObject.connect(self.ui.actionGuardar,SIGNAL("triggered()"),self.save) # signal/slot connection
        QObject.connect(self.ui.actionGuardar_Como,SIGNAL("triggered()"),self.saveAs) # signal/slot connection
        QObject.connect(self.ui.treeView,SIGNAL("doubleClicked(QModelIndex)"),self.openFromTree) # signal/slot connection

        
        #self.ui.show()
        
    def new(self):
        self.fileName = ''
        self.ui.textEdit.setText('')

        
    def openFromTree(self, index):

        indexItem = self.ui.treeView.model().index(index.row(), 0, index.parent())

        fileName = self.ui.treeView.model().filePath(indexItem)        

        if fileName != '':

            self.fileOpen(fileName)

            
    def fileOpen(self, fileName):
##        try:        
            self.fileName = fileName
            self.lastDir = os.path.dirname(self.fileName)

            self.ui.treeView.setRootIndex(self.ui.treeView.model().index(self.lastDir))
            file = open(self.fileName, 'r')
            contents = file.read()
            fn, ext = os.path.splitext(self.fileName)
            self.changeLexer(ext.lower())
            self.ui.textEdit.setText(contents)
            file.close()
##        except:
##            pass
        
    def fileSave(self, fileName):
##        try:
            self.fileName = fileName

            self.lastDir = os.path.dirname(self.fileName)

            self.ui.treeView.setRootIndex(self.ui.treeView.model().index(self.lastDir))
            file = open(self.fileName, 'w')
            file.write(self.ui.textEdit.text())            
            file.close()
##        except:
##            pass

        
    def open(self):

        fileName = QFileDialog.getOpenFileName(self.ui, "Open File",self.lastDir,"Files (*.*)");

        if fileName != '':

            self.fileOpen(fileName)
        
    def saveAs(self):
        fileName = QFileDialog.getSaveFileName(self.ui, "Save File",self.lastDir,"Files (*.*)");
        if fileName != '':

            self.fileSave(fileName)
        
    def save(self):
        if self.fileName == '':
            fileName = QFileDialog.getSaveFileName(self.ui, "Save File",'',"Files (*.*)");
        else:
            fileName = self.fileName

        if fileName != '':

            self.fileSave(self.fileName)
        
    def run(self):
        command = 'python "{0}"'.format(self.fileName)
        subprocess.Popen(command, shell=True)
        
    def changeLexer(self, ext='.py'):
        lexs={
            '.py':Qsci.QsciLexerPython,
            '.html':Qsci.QsciLexerHTML,
            '.cpp':Qsci.QsciLexerCPP
        }
        try:
            self.lexer = lexs[ext]()
                            ##QsciLexer
                            ##QsciLexerBash
                            ##QsciLexerBatch
                            ##QsciLexerCMake
                            ##QsciLexerCPP *
                            ##QsciLexerCSS
                            ##QsciLexerCSharp
                            ##QsciLexerCustom
                            ##QsciLexerD
                            ##QsciLexerDiff
                            ##QsciLexerFortran
                            ##QsciLexerFortran77
                            ##QsciLexerHTML *
                            ##QsciLexerIDL
                            ##QsciLexerJava
                            ##QsciLexerJavaScript
                            ##QsciLexerLua
                            ##QsciLexerMakefile
                            ##QsciLexerMatlab
                            ##QsciLexerOctave
                            ##QsciLexerPOV
                            ##QsciLexerPascal
                            ##QsciLexerPerl
                            ##QsciLexerPostScript
                            ##QsciLexerProperties
                            ##QsciLexerPython *
                            ##QsciLexerRuby
                            ##QsciLexerSQL
                            ##QsciLexerSpice
                            ##QsciLexerTCL
                            ##QsciLexerTeX
                            ##QsciLexerVHDL
                            ##QsciLexerVerilog
                            ##QsciLexerXML
                            ##QsciLexerYAML
            api = Qsci.QsciAPIs(self.lexer)
            # Add autocompletion strings
            api.add("def")
            api.add("class")
            api.add("print")
            api.add("import")
            api.add("from")
            api.add("try")
            api.add("except")
            api.add("self")
            ## Compile the api for use in the lexer
            api.prepare()
            #self.lexer.setFont(self.font)
            self.lexer.setDefaultFont(self.font)
            self.ui.textEdit.setLexer(self.lexer)
        except:
            pass
        
    def setupEditor(self):
       
        # Create an API for us to populate with our autocomplete terms
        self.font = QFont()
        self.font.setFamily('Inconsolata')
        self.font.setFixedPitch(True)
        self.font.setPointSize(12)
        self.ui.textEdit.setFont(self.font)
        self.ui.textEdit.setMarginsFont(self.font)
        
        self.ui.textEdit.setAutoCompletionThreshold(1)
        ## Tell the editor we are using a QsciAPI for the autocompletion
        self.ui.textEdit.setAutoCompletionSource(Qsci.QsciScintilla.AcsAll)
        

        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_SETHSCROLLBAR, 0)
        self.ui.textEdit.setBraceMatching(Qsci.QsciScintilla.SloppyBraceMatch)
        self.ui.textEdit.setCaretLineVisible(True)
        self.ui.textEdit.setIndentationWidth(4)
        self.ui.textEdit.setTabWidth(4)
        self.ui.textEdit.setIndentationsUseTabs(False)
        self.ui.textEdit.setAutoIndent(True)
        self.ui.textEdit.setCaretLineBackgroundColor(QtGui.QColor("#f0f0ff"))
        
        self.ui.textEdit.setUnmatchedBraceBackgroundColor(QtGui.QColor('#FF0000'))
        self.ui.textEdit.setUnmatchedBraceForegroundColor(QtGui.QColor('#FFFFFF'))
        self.ui.textEdit.setMatchedBraceForegroundColor(QtGui.QColor('#FF0000'))
        
        self.ui.textEdit.setFolding(Qsci.QsciScintilla.BoxedTreeFoldStyle)
        self.ui.textEdit.setMarginWidth(0, 15)
        self.ui.textEdit.setMarginWidth(1, 15)
        self.ui.textEdit.setMarginLineNumbers(0, False)
        self.ui.textEdit.setMarginLineNumbers(1, True)

##
##        self.ui.centralwidget.layout().setContentsMargins(0,0,0,0)
##
##        self.ui.dockWidgetContents.layout().setContentsMargins(0,0,0,0)


        self.changeLexer()


        #self.ui.dockWidget.hide()

        model = QFileSystemModel()

        # You can setRootPath to any path.

        model.setRootPath(QDir.rootPath())
        self.ui.treeView.setModel(model)

        self.ui.treeView.hideColumn(1)
        self.ui.treeView.hideColumn(3)


        # Set the root index of the view as the user's home directory.

        #self.ui.treeView.setRootIndex(model.index(QDir.homePath()))
        if self.lastDir != '':
##            self.ui.treeView.setModel(model)
            print('<<',self.lastDir,'>>')
            self.ui.treeView.setRootIndex(self.ui.treeView.model().index(self.lastDir))

        
def cantar(palabra):
    print(palabra*3)
    
# Main entry to program.  Sets up the main app and create a new window.
def main(argv):

    # create Qt application
    app = QApplication(argv,True)

    # create main window
    file = argv[1] if len(argv)>1 else ''
    wnd = MainWindow(file) # classname
    wnd.show()

    # Connect signal for app finish
    app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))

    # Start the app up
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(sys.argv)
