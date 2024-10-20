from datetime import date
from html import escape

from babel.dates import format_date
from babel.numbers import format_currency

def cell(value = "", classes="") -> str:
    """
    Gibt eine Tabellenzelle im HTML-Format zurück.
    """
    out = "<td"
    if type(classes) in (list,tuple):
        out += " class=\""+" ".join(classes)+"\""
    elif classes:
        out += f" class=\"{str(classes)}\""
    if value:
        out += f">{str(value)}</td>"
    else:
        out += "/>"
    return out

def euro(value = 0) -> str:
    """
    Gibt eine Zahl als Eurobetrag zurück.
    """
    return format_currency(value,"EUR",locale="de_DE")


class Position:
    """
    Beschreibt eine Position in einer Aktivenabrechnung.
    """
    
    def __init__(self,name:str = "",unitcount:int = 1,
                 unitprice=0.0,value=0.0):
        """
        Initialisiert ein Objekt der Klasse Position.
        
        Argumente:
        name: Name der Position
        count: Anzahl der Einheiten
        unitprice: Preis pro Einheit (nur, wenn Anzahl relevant ist)
        value: Einnahmen oder (wenn negativ) Ausgaben
        """
        self._name = str(name)
        self._unitcount = int(unitcount)
        self._unitprice = float(unitprice)
        self._value = float(value)
    
    def _setname(self,value:str):
        self._name = str(value)
    
    def _getname(self) -> str:
        return self._name
    
    def _setunitcount(self,value:int):
        self._unitcount = int(value)
    
    def _getunitcount(self) -> int:
        return self._unitcount
    
    def _setunitprice(self,value):
        self._unitprice = float(value)
    
    def _getunitprice(self) -> float:
        return self._unitprice
    
    def _setvalue(self,value):
        self._value = float(value)
    
    def _getvalue(self) -> float:
        return self._value
    
    def _setunvalue(self,value):
        self._value = float(value)*-1
    
    def _getincome(self) -> float:
        if self._value > 0:
            return self._value
        return 0.0
    
    def _getcost(self) -> float:
        if self._value < 0:
            return self._value*-1
        return 0.0
    
    name = property(_getname,_setname,None,
        "Der Name der Position.")
    count = property(_getunitcount,_setunitcount,None,
        "Anzahl der Einheiten in der Position.")
    unitprice = property(_getunitprice,_setunitprice,None,
        "Preis pro Einheit der Position.")
    value = property(_getvalue,_setvalue,None,
        "Der Gesamtwert der Position in Euro.")
    income = property(_getincome,_setvalue,None,
        "Die Einnahmen der Position; gibt bei Ausgaben 0 aus.")
    cost = property(_getcost,_setunvalue,None,
        "Die Kosten der Position; gibt bei Einnahmen 0 aus.")
    
    def htmlcells(self,indent:int = 0) -> str:
        """
        Gibt fünf Zellen im HTML-Format aus.
        Jede Zelle hat eine eigene Zeile, außer indent ist negativ.
        Die Reihenfolge lautet:
        Name, Anzahl Einheiten, Kosten pro Einheit, Einnahmen, Ausgaben
        """
        out = []
        
        if indent<0:
            joiner=""
        else:
            joiner = "\n" + "\t"*indent
        
        out.append( cell( escape(self._name) ) )
        if not self._unitprice==0.0:
            out.append( cell(self._unitcount()) )
            out.append( cell( euro(self._unitprice()) ) )
        else:
            out.append( cell() )
            out.append( cell() )
        if self._value > 0:
            out.append( cell( euro(self._getincome()) ) )
        else:
            out.append( cell() )
        if self._value < 0:
            out.append( cell( euro(self._getcost()) ) )
        else:
            out.append( cell() )
        
        return joiner.join(out)


class Abrechnung:
    """
    Beschreibt eine Aktivenabrechnung für den ADFC Hamburg.
    """
    
    # Class constants
    _CHECKBOXES = ("&#9744;","&#9746;")
    _PLACEHOLDERS = ("<!--SPLIT-->\n","<!--PLACEHOLDER-->")
    _FILE = "aktive_template.html"
    _SECTIONS = {"user": 1, "positions": 3, "total": 4, "payment": 5}
    
    def __init__(self):
        """
        Initialisiert ein Objekt der Klasse Abrechnung.
        """
        
        self._positions = []
        for i in range(7):
            self._positions.append(Position())
        
        self._user = {"name": "", "group": ""}
        self._project = {"name": "", "date": None}
        self._payment = {"mode": None, "sepamode": None,
                         "ibanknown": False, "iban": "", "name": ""}
        self._template = self._fetch_html()
    
    @classmethod
    def _fetch_html(cls) -> tuple:
        """
        Öffnet das HTML-Template, teilt den Inhalt in Sektionen und
        gegebenenfalls Subsektionen auf und gibt das Ergebnis als
        Tupel zurück.
        """
        f = open(cls._FILE,"r")
        sections = f.read().split(cls._PLACEHOLDERS[0])
        out = []
        for i in sections:
            fragments = i.split(cls._PLACEHOLDERS[1])
            if len(fragments) == 1:
                out.append(fragments[0])
            else:
                out.append(tuple(fragments))
        return tuple(out)
    
    def _setusername(self,value):
        self._user["name"] = str(value)
    
    def _getusername(self) -> str:
        return self._user["name"]
    
    def _setusergroup(self,value):
        self._user["group"] = str(value)
    
    def _getusergroup(self) -> str:
        return self._user["group"]
    
    def _setprojectname(self,value):
        self._project["name"] = str(value)
    
    def _getprojectname(self) -> str:
        return self._project["name"]
    
    def _setprojectdate(self,value=None):
        """
        Akzepiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._project["date"] = value
        elif type(value) == str:
            try:
                temp = value.split("-")
                self._project["date"] = date(int(temp[0]), int(temp[1]), int(temp[2]))
            except:
                self._project["date"] = None
        else:
            self._project["date"] = None
    
    def _getprojectdate(self) -> date|None:
        return self._project["date"]
    
    username = property(_getusername,_setusername,None,
                        "Der Name des Aktiven.")
    usergroup = property(_getusergroup,_setusergroup,None,
                         "Der Arbeitsbereich des Aktiven.")
    projectname = property(_getprojectname,_setprojectname,None,
                           "Der Name der Aktion oder des Projekts.")
    projectdate = property(_getprojectdate,_setprojectdate,None,
                           "Das Datum der Aktion oder des Projekts.")

"""
print (cell())
print (cell("TEXT"))
print (cell(classes="left"))
print (cell(222,["cool","beans"]))

testpos = Position()
testpos.name = "<b>Fishies</b>"
testpos.income = 12

print (testpos.name)
print (testpos.value)
print (testpos.income)
print (testpos.cost)
print (testpos.htmlcells(indent=2))
"""

testobj = Abrechnung()
testobj.username = "Patrick Lübcke"
print (testobj.username)
testobj.projectdate = "2015-01-15"
print (testobj.projectdate)
