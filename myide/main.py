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
        self.uiTitle = self.ui.windowTitle()
        self.fileName = file
        self.lastDir = os.path.dirname(self.fileName)
       # set up User Interface (widgets, layout...)
##        self.ui.setupUi(self)
        self.highlightedBrackets = [0,0,0,0]
        self.highlightTags = False
        self.tagsResaltados = []
        self.setupEditor()
        
        if self.fileName != '':
            self.fileOpen(self.fileName)

        # custom slots connections

        QObject.connect(self.ui.pushButton, SIGNAL("released()"),self.run) # signal/slot connection
        QObject.connect(self.ui.actionNuevo, SIGNAL("triggered()"),self.new) # signal/slot connection
        QObject.connect(self.ui.actionAbrir, SIGNAL("triggered()"),self.open) # signal/slot connection
        QObject.connect(self.ui.actionGuardar, SIGNAL("triggered()"),self.save) # signal/slot connection
        QObject.connect(self.ui.actionGuardar_Como, SIGNAL("triggered()"),self.saveAs) # signal/slot connection
        QObject.connect(self.ui.actionBuscar_siguiente, SIGNAL("triggered()"),self.searchNext) # signal/slot connection
        QObject.connect(self.ui.actionBuscar_Seleccionado, SIGNAL("triggered()"), self.searchSelected) # signal/slot connection
        QObject.connect(self.ui.treeView,SIGNAL("doubleClicked(QModelIndex)"),self.openFromTree) # signal/slot connection
        QObject.connect(self.ui.textEdit,SIGNAL("textChanged()"),self.setUnsaved) # signal/slot connection
        QObject.connect(self.ui.textEdit,SIGNAL("cursorPositionChanged(int, int)"),self.onCursorPosition) # signal/slot connection
        
##**********************************

    def findMatchingClosingTag(self, lineNumber, text, tagName, closingBracket=0, level=1):
        if lineNumber <= self.ui.textEdit.lines():
            newLevel = level
            closeTag = '</'+tagName+'>'
            found = text.find(closeTag, closingBracket+1 if closingBracket>0 else 0)
            newLevel -= 1 if found >= 0 else 0
            openTag = '<'+tagName+' '
            other = text.find(openTag, closingBracket+1 if closingBracket>0 else 0)
            if other>0:
                closingBracketOther = self.findBracket(other, text, '>', '<', reverse=True);
                if not self.is_tag_self_closing(text, closingBracketOther):
                    newLevel += 1 if other < found or found < 0 else 0
            print(tagName, lineNumber, found, other, newLevel)
            if newLevel == 0 and found > 0:
                openingBracketInLine = found
                closingBracketInLine = found + len(closeTag)
                openingBracket = self.ui.textEdit.positionFromLineIndex(lineNumber, openingBracketInLine) if openingBracketInLine != -1 else -1
                closingBracket = self.ui.textEdit.positionFromLineIndex(lineNumber, closingBracketInLine) if closingBracketInLine != -1 else -1
                self.highlight_tag(openingBracket, closingBracket)
            else:
                text = self.ui.textEdit.text(lineNumber+1)
                self.findMatchingClosingTag(lineNumber+1, text, tagName, level=newLevel)
        
    def findBracket(self, index, text, searchedBracket, breakBracket, reverse=False):
        foundBracket = -1
        if not reverse:
            posSearch = text.rfind(searchedBracket, 0, index)
            posBreack = text.rfind(breakBracket, 0, index)
            if posBreack < posSearch :
                foundBracket = posSearch
        else:
            posSearch = text.find(searchedBracket, index)
            posBreack = text.find(breakBracket, index)
            if posBreack > posSearch or posBreack == -1:
                foundBracket = posSearch    
        return foundBracket

    def is_tag_opening(self, text, openingBracket):
        return text[openingBracket+1] != '/'

    def get_tag_name(self, text, openingBracket, closingBracket, isTagOpening):
        start = openingBracket + (1 if isTagOpening else 2)
        return text[start : closingBracket].split()[0]

    def findMatchingTag(self, line, text, openingBracket, closingBracket):
        isTagOpening = self.is_tag_opening(text, openingBracket);
        tagName = self.get_tag_name(text, openingBracket, closingBracket, isTagOpening);
        
        if(isTagOpening):
            self.findMatchingClosingTag(line, text, tagName, closingBracket);
##        else
##            self.findMatchingOpeningTag(tagName, openingBracket);        
        
    def is_tag_self_closing(self, text, closingBracket):
        isTagSelfClosing = False;
        charBeforeBracket = text[closingBracket-1];
        if('/' == charBeforeBracket):
            isTagSelfClosing = True;
        return isTagSelfClosing;

        
    def clear_previous_highlighting(self, rangeStart, rangeEnd):
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_INDICATORCLEARRANGE, rangeStart, rangeEnd+1); ####        

    def run_tag_highlighter(self, lineNumber, index):
        print('resaltando')
##        position = self.ui.textEdit.positionFromLineIndex(lineNumber, index)
        lineText = self.ui.textEdit.text(lineNumber)
        
        openingBracketInLine = self.findBracket(index, lineText, '<', '>');
        closingBracketInLine = self.findBracket(index, lineText, '>', '<', reverse=True);

##        openingBracket = position - index + openingBracketInLine if openingBracketInLine != -1 else -1
##        closingBracket = position - index + closingBracketInLine if closingBracketInLine != -1 else -1
        openingBracket = self.ui.textEdit.positionFromLineIndex(lineNumber, openingBracketInLine) if openingBracketInLine != -1 else -1
        closingBracket = self.ui.textEdit.positionFromLineIndex(lineNumber, closingBracketInLine) if closingBracketInLine != -1 else -1

        if (-1 == openingBracket or -1 == closingBracket):
            self.clear_previous_highlighting(self.highlightedBrackets[0], self.highlightedBrackets[1])
            self.clear_previous_highlighting(self.highlightedBrackets[2], self.highlightedBrackets[3])
            self.highlightedBrackets = [0,0,0,0]
            return 0

##        #/* If the cursor jumps from one tag into another, clear previous highlighted tags*/
        if(openingBracket != self.highlightedBrackets[0] or  closingBracket != self.highlightedBrackets[1]):
            self.clear_previous_highlighting(self.highlightedBrackets[0], self.highlightedBrackets[1])
            self.clear_previous_highlighting(self.highlightedBrackets[2], self.highlightedBrackets[3])

##        /* Highlight current tag. Matching tag will be highlighted from
##         * findMatchingTag() functiong */
        if(openingBracket != -1 and closingBracket != -1):
            self.highlightedBrackets[0] = openingBracket;
            self.highlightedBrackets[1] = closingBracket;
            self.highlight_tag(openingBracket, closingBracket);

##        /* Find matching tag only if a tag is not self-closing */
        if(not self.is_tag_self_closing(lineText, closingBracketInLine)):        
            self.findMatchingTag(lineNumber, lineText, openingBracketInLine, closingBracketInLine)
##            print('line:',lineNumber, 'index:',index, 'pos:',position)
##            print('lineText:',lineText)
##            print('openingBracket:',openingBracket)
##            print('closingBracket:',closingBracket)

        
    def highlight_tag(self, openingBracket, closingBracket):
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_INDICSETSTYLE, 0, Qsci.QsciScintilla.INDIC_STRAIGHTBOX) ####        
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_INDICSETFORE, 0, 0xFF0000) ####        
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_INDICSETALPHA, 0, 25) ####        
        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_INDICATORFILLRANGE, openingBracket, closingBracket-openingBracket+1) ####        

    def buscarTag(self, linea, index):
        tag = None
        lineText = self.ui.textEdit.text(linea)
        inicio = self.findBracket(index, lineText, '<', '>');
        fin = self.findBracket(index, lineText, '>', '<', reverse=True);        
        if inicio>=0 and fin>=0:
            isTagOpening = lineText[inicio+1] != '/'
            isTagSelfClosing = isTagOpening and lineText[fin-1] == '/'
            tagcontent = lineText[(inicio +(1 if isTagOpening else 2)) : fin].split()
            if len(tagcontent)>0:
                tag = {
                        'linea':linea,
                        'inicioEnLinea':inicio,
                        'finEnLinea':fin,
                        'inicio':self.ui.textEdit.positionFromLineIndex(linea, inicio),
                        'fin':self.ui.textEdit.positionFromLineIndex(linea, fin),
                        'apertura':isTagOpening,
                        'cerrada': isTagSelfClosing,
                        'tag': tagcontent[0]
                }
        return tag

    def buscarTagCierre(self, tag, linea, desde=0, nivel=0):
        tagC = None
        if linea <= self.ui.textEdit.lines():
            lineText = self.ui.textEdit.text(linea)
            tagCierre = '</' + tag['tag'] + '>'
            tagApertura1 = '<' + tag['tag'] + ' '
            tagApertura2 = '<' + tag['tag'] + '>'
            indexCierre = lineText.find(tagCierre, desde)
            index = -1
            indexApertura = -1
            indexApertura1 = lineText.find(tagApertura1, desde)
            if indexApertura1 >= 0:
                indexApertura = indexApertura1
            indexApertura2 = lineText.find(tagApertura2, desde)
            if indexApertura2 >= 0:
                indexApertura = indexApertura if indexApertura>=0 and indexApertura<indexApertura2 else indexApertura2
            if indexCierre >=0:
                index = indexCierre
            if indexApertura>=0:
                index = index if index>=0 and index<indexApertura else indexApertura
            if index >= 0:
                tagE = self.buscarTag(linea, index+1)
                if not tagE['apertura']:
                    if nivel == 0:
                        tagC = tagE
                    else:
                        tagC = self.buscarTagCierre(tag, linea, tagE['finEnLinea'], nivel - 1)
                else:
                    tagC = self.buscarTagCierre(tag, linea, tagE['finEnLinea'], nivel + (0 if tagE['cerrada'] else 1))
            else:
                tagC = self.buscarTagCierre(tag, linea+1, nivel=nivel)
        return tagC
           
    def buscarTagApertura(self, tag, linea, hasta=None, nivel=0):
        tagC = None
        
        if linea >= 0:
            lineText = self.ui.textEdit.text(linea)
            hasta = len(lineText) if hasta is None else hasta
            tagCierre = '</' + tag['tag'] + '>'
            tagApertura1 = '<' + tag['tag'] + ' '
            tagApertura2 = '<' + tag['tag'] + '>'
            
            index = -1
            indexCierre = lineText.find(tagCierre, 0, hasta)
            indexApertura1 = lineText.find(tagApertura1, 0, hasta)
            indexApertura2 = lineText.find(tagApertura2, 0, hasta)
            indexApertura = max(indexApertura1, indexApertura2)
                
            if indexApertura >= 0:
                index = max(indexApertura, indexCierre)
            print(linea)
            
            if index >= 0:
                tagE = self.buscarTag(linea, index+1)
                if tagE['apertura']:
                    if nivel == 0:
                        tagC = tagE
                    else:
                        tagC = self.buscarTagApertura(tag, linea, tagE['inicioEnLinea'], nivel - (0 if tagE['cerrada'] else 1))
                else:
                    tagC = self.buscarTagApertura(tag, linea, tagE['inicioEnLinea'], nivel + 1)
            else:
                
                tagC = self.buscarTagApertura(tag, linea-1, nivel=nivel)
        return tagC
                   
    def buscarCompaniero(self, tag):
        tagC = None
        if not tag['cerrada']:
            if tag['apertura']:
                tagC = self.buscarTagCierre(tag, tag['linea'], tag['finEnLinea'])
            else:
                tagC = self.buscarTagApertura(tag, tag['linea'], tag['inicioEnLinea'])
        return tagC
        
    def borrarTagsResaltados(self):
        for tag in self.tagsResaltados:
            self.clear_previous_highlighting(tag['inicio'], tag['fin'])
            
    def resaltarTags(self, tags):
        self.borrarTagsResaltados()
        for tag in tags:
            self.highlight_tag(tag['inicio'], tag['fin'])
            self.tagsResaltados.append(tag)
        
    def buscarYResaltarTags(self, linea, index):
        tags = []
        tag1 = self.buscarTag(linea, index)
        if tag1 is not None:
            tags.append(tag1)
            tag2 = self.buscarCompaniero(tag1)
            if tag2 is not None:
                tags.append(tag2)
            self.resaltarTags(tags)
        else:
            self.borrarTagsResaltados()
##**********************************
        
    def onCursorPosition(self, line, index):
        if self.highlightTags:
##            self.run_tag_highlighter(line, index)##
            self.buscarYResaltarTags(line, index)##


    def setUnsaved(self):
        title = ('<nuevo>' if self.fileName == '' else self.fileName) + ' - ' + self.uiTitle 
        self.ui.setWindowTitle('*' + title)

    def setSaved(self):
        title = self.fileName + ' - ' + self.uiTitle 
        self.ui.setWindowTitle(title)

    def searchSelected(self):

        text = ''
        if(self.ui.lineEdit.hasFocus() and self.ui.lineEdit.text() != ''):

            text = self.ui.lineEdit.text()

        else:

            if self.ui.textEdit.hasSelectedText():
                text = self.ui.textEdit.selectedText()

        if(text != ''):

            self.ui.textEdit.findFirst(

                    text, 
                    False,
                    False,
                    False,
                    True)
    #                ,
    ##                forward = True, #opt
    ##                line=-1, #opt
    ##                index=-1, #opt
    ##                show=True, #opt
    ##                posix=False  #opt
    ##            )

    def searchNext(self):
        self.ui.textEdit.findNext()

    def new(self):
        self.fileName = ''
        self.ui.textEdit.setText('')
        
    def openFromTree(self, index):
        indexItem = self.ui.treeView.model().index(index.row(), 0, index.parent())
        fileName = self.ui.treeView.model().filePath(indexItem)        
        if fileName != '':
            self.fileOpen(fileName)

    def fileOpen(self, fileName):
        try:        
            self.fileName = fileName
            self.lastDir = os.path.dirname(self.fileName)

            self.changeFolder(self.lastDir)
            file = open(self.fileName, 'r')
            contents = file.read()
            fn, ext = os.path.splitext(self.fileName)
            self.changeLexer(ext.lower())
            self.ui.textEdit.setText(contents)
            file.close()

            self.setSaved()
        except:
            pass
        
    def fileSave(self, fileName):
        try:
            self.fileName = fileName

            self.lastDir = os.path.dirname(self.fileName)

            self.changeFolder(self.lastDir)

            file = open(self.fileName, 'w')
            file.write(self.ui.textEdit.text())            
            file.close()
            self.setSaved()
        except:
            pass

        
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
        p = subprocess.Popen(command, shell=True)

            
    def changeLexer(self, ext='.py'):
        lexs={
            '.py':Qsci.QsciLexerPython,
            '.html':Qsci.QsciLexerHTML,
            '.cpp':Qsci.QsciLexerCPP,
            '.c':Qsci.QsciLexerCPP,
            '.css':Qsci.QsciLexerCSS,
            '.java':Qsci.QsciLexerJava,
            '.js':Qsci.QsciLexerJavaScript,
            '.json':Qsci.QsciLexerJavaScript,
            '.pas':Qsci.QsciLexerPascal,
            '.sql':Qsci.QsciLexerSQL,
            '.xml':Qsci.QsciLexerXML,
            '.ui':Qsci.QsciLexerXML,
            '.cs':Qsci.QsciLexerCSharp,
            '.sh':Qsci.QsciLexerBash,
            '.bat':Qsci.QsciLexerBatch
        }
        self.highlightTags = ext in ['.html', '.xml', '.ui']
        try:
            self.lexer = lexs[ext]()
                            ##QsciLexer
                            ##QsciLexerBash
                            ##QsciLexerBatch *
                            ##QsciLexerCMake
                            ##QsciLexerCPP *
                            ##QsciLexerCSS *
                            ##QsciLexerCSharp *
                            ##QsciLexerCustom
                            ##QsciLexerD
                            ##QsciLexerDiff
                            ##QsciLexerFortran
                            ##QsciLexerFortran77
                            ##QsciLexerHTML *
                            ##QsciLexerIDL
                            ##QsciLexerJava *
                            ##QsciLexerJavaScript *
                            ##QsciLexerLua
                            ##QsciLexerMakefile
                            ##QsciLexerMatlab
                            ##QsciLexerOctave
                            ##QsciLexerPOV
                            ##QsciLexerPascal *
                            ##QsciLexerPerl
                            ##QsciLexerPostScript
                            ##QsciLexerProperties
                            ##QsciLexerPython *
                            ##QsciLexerRuby
                            ##QsciLexerSQL *
                            ##QsciLexerSpice
                            ##QsciLexerTCL
                            ##QsciLexerTeX
                            ##QsciLexerVHDL
                            ##QsciLexerVerilog
                            ##QsciLexerXML *
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
            self.lexer.setFont(self.font)
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
        

        #self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_SETHSCROLLBAR, 0)

        self.ui.textEdit.SendScintilla(Qsci.QsciScintilla.SCI_SETINDICATORCURRENT, 0, 0) ####
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

        # Set the root index of the view as the user's home directory.

        #self.ui.treeView.setRootIndex(model.index(QDir.homePath()))
        if self.lastDir != '':

            self.changeFolder(self.lastDir)

            
    def changeFolder(self, folder):

        if self.ui.treeView.model() is None:

            model = QFileSystemModel()

            model.setRootPath(QDir.rootPath())

            self.ui.treeView.setModel(model)
            self.ui.treeView.hideColumn(1)
            self.ui.treeView.hideColumn(2)
            self.ui.treeView.hideColumn(3)

        self.ui.treeView.setRootIndex(self.ui.treeView.model().index(folder))
        
 
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
