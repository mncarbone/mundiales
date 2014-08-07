import sys,os
from gettext import textdomain, bindtextdomain, gettext as _
from tkinter import Text, Pack, Grid, Place #, Frame, Scrollbar
from tkinter import  Tk, Menu, Frame, Button, Label, Scrollbar, END, IntVar #, N,S,E,W,NONE,HORIZONTAL
from tkinter.constants import RIGHT, LEFT, X, Y, BOTH, NONE, HORIZONTAL, BOTTOM
from sqlite3 import connect
from tkinter.filedialog import askopenfilename, asksaveasfilename 
import webbrowser
from tkinter.messagebox import showerror, showinfo

class ScrolledText(Text):
    """Modified version of tkinter.scrolledtext width horizontal scrollbar"""
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)
        #>>>MNC: For horizontal scrollbar 
        try:
            self.hbar = None
            if kw['wrap'] == NONE:
                self.hbar = Scrollbar(self.frame, orient=HORIZONTAL)
                self.hbar.pack(side=BOTTOM, fill=X)
                kw.update({'xscrollcommand': self.hbar.set})
        except KeyError:
            self.hbar = None
        #<<<MNC
        kw.update({'yscrollcommand': self.vbar.set})
        Text.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview
        #>>>MNC: For horizontal scrollbar 
        if self.hbar is not None:
            self.hbar['command'] = self.xview
        #<<<MNC
        # Copy geometry methods of self.frame without overriding Text
        # methods -- hack!
        text_meths = vars(Text).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(text_meths)
        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))

    def __str__(self):
        return str(self.frame)
    
    def setText(self, text):
        self.delete(1.0, END)
        self.insert(END, text)
            
    def getText(self):
        return self.get(1.0, END)
    
class TextResult(ScrolledText):

    def __init__(self, root):
        super().__init__(root,wrap=NONE)
        self.configure(state='disabled')
        
    def setText(self, text):
        self.configure(state='normal')
        super().setText(text)
        self.configure(state='disabled')

class TextSQL(ScrolledText):
    KEYWORDS = [
        'ABORT', 'ACTION', 'ADD', 'AFTER', 'ALL', 'ALTER', 'ANALYZE', 'AND', 'AS', 'ASC', 'ATTACH','AUTOINCREMENT',
        'BEFORE', 'BEGIN', 'BETWEEN', 'BLOB', 'BY', 'CASCADE', 'CASE', 'CAST', 'CHECK', 'COLLATE','COLUMN', 'COMMIT',
        'CONFLICT', 'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME', 'CURRENT_TIMESTAMP',
        'DATABASE', 'DEFAULT', 'DEFERRABLE', 'DEFERRED', 'DELETE', 'DESC', 'DETACH', 'DISTINCT', 'DROP',
        'EACH', 'ELSE', 'END', 'ESCAPE', 'EXCEPT', 'EXCLUSIVE', 'EXISTS', 'EXPLAIN',
        'FAIL', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'GLOB', 'GROUP', 'HAVING', 'IF', 'IGNORE', 'IMMEDIATE', 'IN',
        'INDEX', 'INDEXED', 'INITIALLY', 'INNER', 'INSERT', 'INSTEAD', 'INTEGER', 'INTERSECT', 'INTO', 'IS','ISNULL',
        'JOIN', 'KEY', 'LEFT', 'LIKE', 'LIMIT', 'MATCH', 'NATURAL', 'NO', 'NOT', 'NOTNULL', 'NULL',
        'OF', 'OFFSET', 'ON', 'OR', 'ORDER', 'OUTER', 'PLAN', 'PRAGMA', 'PRIMARY', 'QUERY', 'RAISE', 'REAL', 'RECURSIVE',
        'REFERENCES', 'REGEXP', 'REINDEX', 'RELEASE', 'RENAME', 'REPLACE', 'RESTRICT', 'RIGHT', 'ROLLBACK', 'ROW',
        'SAVEPOINT', 'SELECT', 'SET', 'TABLE', 'TEMP', 'TEMPORARY', 'TEXT', 'THEN', 'TO', 'TRANSACTION', 'TRIGGER',
        'UNION', 'UNIQUE', 'UPDATE', 'USING', 'VACUUM', 'VALUES', 'VIEW', 'VIRTUAL', 'WHEN', 'WHERE', 'WITH', 'WITHOUT',
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._patterns = {}
        self._rpatterns = {}
        self.tag_configure("blue", foreground="#0000DD")
        self.add_patterns(self.KEYWORDS, 'blue')
        self.tag_configure("comment", foreground="#FF0000")
        self.add_pattern(r'/\*[a-zA-Z0-9_ \t\n\r\f\v]*\*/', 'comment',regexp=True)
        self.tag_configure("string", foreground="#008800")
        self.add_pattern(r"'[a-zA-Z0-9_ \t\n\r\f\v]*'", 'string',regexp=True)
        self.add_pattern(r'"[a-zA-Z0-9_ \t\n\r\f\v]*"', 'string',regexp=True)
        self.tag_configure("complete", foreground="#BBBBBB")
        self.add_pattern(r'<[a-zA-Z0-9_ \t\n\r\f\v]*>', 'complete',regexp=True)
        self.bind("<KeyRelease>", self.keypress)

    def keypress(self, event):
        self.highlight()
        
    def add_patterns(self, patterns, tag):
        for pattern in patterns:
            self.add_pattern(pattern, tag)
            
    def add_pattern(self, pattern, tag, regexp=False):
        if(regexp):
            self._rpatterns[pattern] = tag
        else:
            self._patterns[pattern] = tag
            self._patterns[' '+pattern.lower()+' '] = tag

    def highlight(self):
        for pattern in self._patterns:
            self.highlight_pattern(pattern, self._patterns[pattern])
        for pattern in self._rpatterns:
            self.highlight_pattern(pattern, self._rpatterns[pattern], regexp=True)
        self.highlighted = True
        
    def setText(self, text):
        super().setText(text)
        self.highlight()
    
    def highlight_pattern(self, pattern, tag, start="1.0", end="end", regexp=False):
        '''Apply the given tag to all text that matches the given pattern
        If 'regexp' is set to True, pattern will be treated as a regular expression
        '''
        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart",start)
        self.mark_set("matchEnd",start)
        self.mark_set("searchLimit", end)
        count = IntVar()
        while True:
            index = self.search(pattern, "matchEnd","searchLimit", count=count, regexp=regexp)
            if index == "": break
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index,count.get()))
            self.tag_add(tag, "matchStart","matchEnd")


class QueryBrowserUI(Tk):
    appName = "PySQLiTk3 - query browser"
    initSize = "900x600"
    configFile = 'conf.ini'
    sqlSqliteUrl = "http://www.sqlite.org/lang.html"
    tablesAtLeft = True
    selectedTable = ''
        
    def __init__(self, app):
        self.app = app
        super().__init__()
        self.configureLocale()
        self.title(self.appName)
        self.geometry(self.initSize)
        self.createMenu()
        self.createContent()
        self.loadLastDataBaseFile()
        
    def configureLocale(self):
        if sys.platform.startswith('win'):
            import locale
            if os.getenv('LANG') is None:
                lang, enc = locale.getdefaultlocale()
                os.environ['LANG'] = lang
        textdomain("app")
        bindtextdomain("app","./locale")

    def start(self):
        self.mainloop()
        
    def createMenu(self):
        menu = Menu(self)
        self.config(menu=menu)
        #File
        mnFile = Menu(menu, tearoff=0)
        menu.add_cascade(label=_("File"), underline=0, menu=mnFile)
        mnFile.add_command(label=_("New..."), underline=0, command=lambda cmd='NEW':  self.onCommand(cmd))
        mnFile.add_command(label=_("Open..."), underline=0, command=lambda cmd='OPEN': self.onCommand(cmd))
        mnFile.add_separator()
        mnFile.add_command(label=_("Quit"), underline=0, command=lambda cmd='EXIT': self.onCommand(cmd))
        #View
        self.mnView = Menu(menu, tearoff=0)
        menu.add_cascade(label=_("View"), underline=0, menu=self.mnView)
        self.mnView.add_command(label=_("Tables at %s") % _('right'), underline=0, command=lambda cmd='TABLES_RL': self.onCommand(cmd))
        #Help
        mnHelp = Menu(menu, tearoff=0)
        menu.add_cascade(label=_("Help"), underline=0, menu=mnHelp)
        mnHelp.add_command(label=_("SQL by SQLite..."), underline=0, command=lambda: webbrowser.open(self.sqlSqliteUrl))
        mnHelp.add_command(label=_("About..."), underline=0, command=lambda cmd='ABOUT': self.onCommand(cmd))
        
    def createContent(self):
    # Top Panel: ---------------------------------
        pnlTop = Frame(self)
        pnlTop.pack(side="top", fill="both", pady=10, padx=10)
        self.btnDB = Button(pnlTop, text=_("Open Data Base..."), command=lambda cmd='OPEN': self.onCommand(cmd))
        self.btnDB.grid(row=1, column=2, padx=5)

    # Query Panel: -----------------------------------
        self.pnlQuery = Frame(self)
        self.pnlQuery.pack(side="right", fill="both", expand=True, padx=10)
        #-- SQL Panel: 
        pnlSQL = Frame(self.pnlQuery)
        pnlSQL.pack(side="top", fill="both")
        Label(pnlSQL, text = "SQL:").grid(row=1, column=1, padx=5)
        self.txtSQL = TextSQL(pnlSQL, height=10, width = 60)
        self.txtSQL.grid(row=1, column=2, padx=5, pady=10)
        Button(pnlSQL, text = _("Run"), command=lambda cmd='RUN': self.onCommand(cmd)).grid(row=1, column=3, padx=5)
        #-- Buttons Panel
        pnlBtns = Frame(pnlSQL)
        pnlBtns.grid(row=2, column=2)
        Button(pnlBtns, text='INSERT', width = 12, command=lambda cmd='QUERY',query='INSERT': self.onCommand(cmd,query=query)).grid(row=1, column=1)
        Button(pnlBtns, text='SELECT', width = 12, command=lambda cmd='QUERY',query='SELECT': self.onCommand(cmd,query=query)).grid(row=1, column=2)
        Button(pnlBtns, text='UPDATE', width = 12, command=lambda cmd='QUERY',query='UPDATE': self.onCommand(cmd,query=query)).grid(row=1, column=3)
        Button(pnlBtns, text='DELETE', width = 12, command=lambda cmd='QUERY',query='DELETE': self.onCommand(cmd,query=query)).grid(row=1, column=4)        
        #-- Result Panel:
        self.pnlResult = Frame(self.pnlQuery)
        self.pnlResult.pack(side="top", fill="both", expand=True, pady=10, padx=10)
        self.resultGrid = TextResult(self.pnlResult)
        self.resultGrid.pack(side="top", fill="both", expand=True)
                
    #Table List Panel: ---------------------------------------
        self.pnlTables = Frame(self)
        self.pnlTables.pack(side="left", fill="both", pady=10, padx=10)
        #---Tables Buttons Panel: 
        self.pnlTableList = Frame(self.pnlTables)
        self.pnlTableList.pack(side="top", fill="both", pady=10)
        #---Panel Nueva: Button
        pnlNewTable = Frame(self.pnlTables)
        pnlNewTable.pack(side="bottom", pady=10, padx=10)
        Button(pnlNewTable, text=_("New Table"), command=lambda cmd='QUERY',query='CREATE': self.onCommand(cmd,query=query,table='<table>')).grid(row=1, column=2, padx=5)

    def tableContextMenu(self, event, table=''):
        popup = Menu(self, tearoff=0)
        popup.add_command(label=_("Add Column"), command=lambda cmd='QUERY',query='ADD', table=table: self.onCommand(cmd,query=query,table=table))
        popup.add_command(label=_("Rename Table"), command=lambda cmd='QUERY',query='RENAME', table=table: self.onCommand(cmd,query=query,table=table))
        popup.add_command(label=_("Drop Table"), command=lambda cmd='QUERY',query='DROP', table=table: self.onCommand(cmd,query=query,table=table))
        popup.post(event.x_root, event.y_root)

    def showTables(self):
        tables = self.app.getTables()
        self.pnlTableList.destroy()
        self.pnlTableList = Frame(self.pnlTables)
        self.pnlTableList.pack(side="top", fill="both", pady=10)
        self.btnTables = {}
        Label(self.pnlTableList, text=_('Tables')).grid(row=0, column=1)
        for n,table in enumerate(tables):
            self.btnTables[table] = Button(self.pnlTableList, text=table,width=20, command=lambda cmd='QUERY',query='SELECT',table=table: self.onCommand(cmd,query=query,table=table))
            self.btnTables[table].grid(row=n+1, column=1)
            self.btnTables[table].bind("<Button-3>", lambda event, table=table:self.tableContextMenu(event, table))
            if table == self.selectedTable:
                self.markTable(table)
        
    def onCommand(self, comando, **args):
        comandos = {
            'NEW':self.newDataBaseFile,
            'OPEN':self.openDataBaseFile,
            'EXIT':self.exitApp,
            'ABOUT':self.about,
            'QUERY':self.showQuery,
            'RUN':self.run,
            'TABLES_RL': self.showTablesAtRightOrLeft
        }
        try:
            comandos[comando](**args)
        except KeyError:
            showerror(_('Error'), _('Unknown command: ')+ comando)
            
    def exitApp(self):
        self.destroy()
        
    def about(self):
        showinfo(_('About...'), self.appName+'\n'+_('Desarrollado por:')+'\n'+_('Martín Nicolás Carbone')+'\n'+_('Agosto 2014'))

    def showTablesAtRightOrLeft(self):
        self.tablesAtLeft = not self.tablesAtLeft
        querySide, tablesSide = ("right", "left") if self.tablesAtLeft else ("left", "right")
        self.pnlTables.pack(side=tablesSide, fill="both", pady=10, padx=10)
        self.pnlQuery.pack(side=querySide, fill="both", expand=True, padx=10)
        self.mnView.entryconfigure(0, label=_("Tables at %s") % _(querySide))

    def selectTable(self, table):
        self.unMarkTable(self.selectedTable)
        self.selectedTable = table if table != '' else self.selectedTable
        self.markTable(self.selectedTable)
        return self.selectedTable

    def unMarkTable(self, table):
        try:
            self.btnTables[table].config(relief='raised')
        except KeyError:
            pass
    def markTable(self, table):
        try:
            self.btnTables[table].config(relief='sunken')
        except KeyError:
            pass
        
    def newDataBaseFile(self):
        path = asksaveasfilename(defaultextension=".db")
        if path != '':
            self.openDataBase(path)

    def openDataBaseFile(self):
        path = askopenfilename(filetypes=((_("Data base files"), "*.db;*.dat;*.sqlite;*.sqlite3;*.sql;"),(_("All files"), "*.*") ))
        if path != '':
            self.openDataBase(path)

    def loadLastDataBaseFile(self):
        path = self.readPath()
        if path != '':
            self.openDataBase(path) 
        
    def savePath(self, path):
        with open(self.configFile, 'w') as f:
            f.write(str(path))
        
    def readPath(self):
        try:
            with open(self.configFile, 'r') as f:
                return str(f.read())
        except IOError:
            return ''

    def openDataBase(self, path):
        self.basePath = path if path != '' else self.basePath
        try:
            self.app.openDataBase(self.basePath)
            self.savePath(self.basePath)
            self.btnDB.config(text=self.basePath)
            self.selectedTable = ''
            self.showTables()
        except IOError:
            showerror(_('Error'),_('Error')+' '+_("Open Data Base..."))

    def showQuery(self, query, table=''):
        table = self.selectTable(table)       
        sql=self.app.createQuery(query, table)
        self.txtSQL.setText(sql)

    def run(self):
        query = self.txtSQL.getText()
        result = self.app.runQuery(query)
        self.resultGrid.setText(result)
        if result == '':
            self.showTables()

class DataBase:

    def __init__(self, path=''):
        if path != '':
            self.open(path)

    def open(self, path):
        self.path = path
        try:
            self.conexion = connect(path)
            self.cursor = self.conexion.cursor()
            self.executeQuery("PRAGMA foreign_keys = ON;")
        except IOError:
            print('Invalid Path')

    def getTables(self):
        sql = "SELECT name FROM sqlite_master WHERE type='table';";
        res = self.executeQuery(sql)
        tables = []
        for rec in res:
            tables.append(rec[0])
        return tables
    
    def executeQuery(self, sql):
        self.cursor.execute(sql)
        self.conexion.commit()
        return [r for r in self.result()]
        
    def result(self):
        record =  self.cursor.fetchone()
        while record is not None:
            yield record
            record = self.cursor.fetchone()

    def getColumns(self, table=''):
        try:
            if table != '':
                sql='SELECT * FROM ' + table
                self.executeQuery(sql)
            return list(map(lambda x: x[0], self.cursor.description))
        except:
            return []

    def getInfo(self,table):
        sql = "PRAGMA table_info("+table+");"#-->(cid|name|type|notnull|dflt_value|pk)
        self.executeQuery(sql)

class QueryBrowser:
    db = None
    
    def run(self):
        self.ui = QueryBrowserUI(self)
        self.ui.start()
    
    def openDataBase(self, path):
        self.db = DataBase(path)
        
    def runQuery(self, query):
        try:
            rb = ResultBuilder()
            res = self.db.executeQuery(query)
            cols = self.db.getColumns()
            return rb.getGrid(cols, res)
        except:
            return ' <<< %s (%s) %s >>> ' % (_("Error"),sys.exc_info()[0].__name__,sys.exc_info()[1])
    
    def getTables(self):
        return self.db.getTables()
    
    def createQuery(self, query, table='<table>'):
        qb = QueryBuilder()
        columns = self.db.getColumns(table) if table != '' else []
        return qb.getQuery(statement=query, table=table, columns=columns)
    
class ResultBuilder:
    def __init__(self):
        self.colWidts = []
        
    def getGrid(self, columns, result):
        if columns == []:
            return ''
        self.appendRow(columns)
        for row in result:
            self.appendRow(row)
        text = self.getRow(columns, header=True)
        for row in result:
            text += self.getRow(row)
        return text
    
    def getRow(self, rowValues, header=False):
        data = [(' {value:<'+str(l)+'} ').format(value=v) for v,l in zip(rowValues,self.colWidts)]
        if header:
            text =  "╔" + ('╤'.join(['═'*(w+2) for w in self.colWidts])) + "╗\n"
            text += "║" + ('│'.join(data)                               ) + "║\n"
            text += "╠" + ('╪'.join(['═'*(w+2) for w in self.colWidts])) + "╣\n"
        else:
            text  = "║" + ('│'.join(data)                               ) + "║\n"
            text += "╟" + ('┼'.join(['─'*(w+2) for w in self.colWidts])) + "╢\n"
        return text
    
    def appendRow(self, rowValues):
        if self.colWidts == []:
           self.colWidts= [len(x) for x in rowValues]
        else:
            self.colWidts = [max(len(str(x)), y) for x,y in zip(rowValues,self.colWidts)]
        
class QueryBuilder:
    def getQuery(self, statement, **args):
        commands = {
            #DDL
            'CREATE':self.create,
            'ADD':self.add,
            'RENAME':self.rename,
            'DROP':self.drop,
            #DML
            'SELECT':self.select,
            'INSERT':self.insert,
            'UPDATE':self.update,
            'DELETE':self.delete,
        }
        try:
            return commands[statement.upper()](**args)
        except KeyError:
            return 'ERROR'
        
    def insert(self, table, columns):
        sql = 'INSERT INTO %s ' % table
        sql+= ('('+', '.join(columns) + ')') if columns!=[] else ''
        sql+= '\nVALUES (\n' 
        sep = ''
        for col in columns:
            sql+= sep + "'<data>' /*%s*/" % col
            sep = ', \n'
        sql+= '\n);'
        return sql

    def select(self, table, columns):
        sql = 'SELECT '
        sql+= ', '.join(columns) if columns!=[] else '*'
        sql+= '\nFROM %s;' % table
        return sql

    def update(self, table, columns):
        sql = 'UPDATE %s SET \n' % table
        sql+= "<field> = '<value>'\n"
        sql+= "WHERE <field> = '<value>';"
        return sql

    def delete(self, table, columns):
        sql = "DELETE FROM %s \n" % table
        sql+= "WHERE <field> = '<value>';\n"
        return sql

    def create(self, table, columns):
        sql = "CREATE TABLE %s (\n" % table
        sql+= "   id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        sql+= "   <field> TEXT,\n"
        sql+= "   <field> INTEGER,\n"
        sql+= "   <field> REAL,\n"
        sql+= "   <field> BLOB\n"
        sql+= ");"
        return sql
        
    def add(self, table, columns):
        sql = "ALTER TABLE %s \n" % table
        sql+= "ADD COLUMN \n"
        sql+= "<field> <type> /*INTEGER|REAL|TEXT|BLOB*/ \n"
        sql+= "DEFAULT <value>;"
        return sql
        
    def rename(self, table, columns):
        sql = "ALTER TABLE %s \n" % table
        sql+= "RENAME TO <new_table_name>;"
        return sql
        
    def drop(self, table, columns):
        sql = 'DROP TABLE %s;' % table
        return sql
        
if __name__ == '__main__':
    app = QueryBrowser()
    app.run()
