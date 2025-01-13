"""
Modul für Klassen, die Aktivenabrechnungen repräsentieren oder
selbige als Dokument ausgeben.
"""

from datetime import date, datetime
from decimal import Decimal
from html import escape
from re import sub

from babel.dates import format_date
from drafthorse.models.accounting import ApplicableTradeTax as DH_ApplicableTradeTax
from drafthorse.models.document import Document as DH_Document
from drafthorse.models.tradelines import LineItem as DH_LineItem


from app import tools, VERSION, CONTACT


class Position:
    """
    Beschreibt eine Position in einer Aktivenabrechnung.
    """
    
    # Dunder methods
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
        self.setname(name)
        self.setunitcount(unitcount)
        self.setunitprice(unitprice)
        self.setvalue(value)
    
    def __str__(self):
        return tools.euro(self.getvalue())
    
    def __repr__(self):
        return (f"Position(name='{self.getname()}',"
               +f"unitcount={self.getunitcount()},"
               +f"unitprice={self.getunitprice()},"
               +f"value={self.getvalue()})")
    
    def __bool__(self):
        return bool(self._name != ""
                    or self._unitprice != 0.0
                    or self._value != 0.0)
    
    # Methods for output
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
        
        out.append( tools.cell( escape(self._name) ) )
        
        if self:
            out.append( tools.cell(self.getunitcount()) )
        else:
            out.append( tools.cell() )
        
        out.append( tools.cell( tools.euro(abs(self.getunitprice()),True) ) )
        out.append( tools.cell( tools.euro(self.getincome(),True) ) )
        out.append( tools.cell( tools.euro(self.getcost(),True) ) )
        
        return "\t"*indent+joiner.join(out)

    # Variable getters and setters
    def setname(self,value:str = ""):
        """Legt den Namen der Position fest."""
        self._name = str(value).strip()
    
    def getname(self) -> str:
        """Gibt den Namen der Position zurück."""
        return self._name
    
    def setunitcount(self,value:int = 1):
        """
        Legt die Mengenzahl der Position fest.
        Kann nicht kleiner als 1 sein; wird automatisch korrigiert.
        """
        self._unitcount = int(value)
        if self._unitcount < 1:
            self._unitcount = 1
    
    def getunitcount(self) -> int:
        """Gibt die Mengenzahl der Position zurück."""
        return self._unitcount
    
    def setunitprice(self,value=0.0):
        """Legt den Preis pro Einheit der Position fest."""
        self._unitprice = float(value)
    
    def getunitprice(self) -> float:
        """Gibt den Preis pro Einheit der Position zurück."""
        return self._unitprice
    
    def setvalue(self,value=0.0):
        """
        Legt den Gesamtpreis der Position fest.
        Einnahmen sind positiv, Ausgaben negativ.
        """
        self._value = float(value)
    
    def getvalue(self) -> float:
        """
        Gibt den Gesamtpreis der Position zurück.
        Bei vorhandendem Stückpreis wird der
        gespeicherte Gesamtpreis ignoriert.
        """
        if self._unitprice != 0:
            return self._unitprice * self._unitcount
        return self._value
    
    def setminusvalue(self,value=0.0):
        """
        Legt den Gesamtpreis der Position fest.
        Ausgaben sind positiv, Einnahmen negativ.
        """
        self._value = float(value)*-1
    
    def getincome(self) -> float:
        """
        Gibt die Gesamteinnahmen der Position zurück.
        Bei Ausgaben wird Null zurückgegeben.
        """
        return max(0.0, self.getvalue())
    
    def getcost(self) -> float:
        """
        Gibt die Gesamtausgaben der Position zurück.
        Bei Einnahmen wird Null zurückgegeben.
        """
        return max(0.0, self.getvalue()*-1)
    
    # Properties
    name = property(getname,setname,None,
        "Der Name der Position.")
    unitcount = property(getunitcount,setunitcount,None,
        "Anzahl der Einheiten in der Position.")
    unitprice = property(getunitprice,setunitprice,None,
        "Preis pro Einheit der Position.")
    value = property(getvalue,setvalue,None,
        "Der Gesamtwert der Position in Euro.")
    income = property(getincome,setvalue,None,
        "Die Einnahmen der Position; gibt bei Ausgaben 0 aus.")
    cost = property(getcost,setminusvalue,None,
        "Die Kosten der Position; gibt bei Einnahmen 0 aus.")


class Abrechnung:
    """
    Beschreibt eine Aktivenabrechnung für den ADFC Hamburg.
    Beinhaltet 7 Objekte der Klasse Position im Tupel positions.
    """
    
    # Class constants
    _IBANSPACES = range(32,0,-4)
    _MODES_IBAN = (1,2,3)
    _MODES_SEPA = (2,3)
    _NAME = "Aktivenabrechnung"
    _POSITIONCOUNT = 7
    
    # Dunder methods
    def __init__(self):
        """
        Initialisiert ein Objekt der Klasse Abrechnung.
        """
        
        self.positions = self._create_positions(self._POSITIONCOUNT)
        
        self._user = {"name": "", "group": ""}
        self._project = {"name": "", "date": None}
        self._donations = 0.0
        self._payment = {"ibanmode": None, "sepamode": None,
                         "ibanknown": False, "iban": "", "name": ""}
    
    def __str__(self):
        """
        Gibt den Abrechnungsbetrag zurück.
        """
        return tools.euro(self.gettotal())

    def __bool__(self):
        """
        Gibt True zurück, falls eine Position einen Wert hat
        oder eine Spendensumme angegeben wurde.
        """
        for position in self.positions:
            if position:
                return True
        return bool(self.donations)

    # Part of initialization
    def _create_positions(self,amount:int):
        """
        Gibt einen Tupel aus neuen Positionen zurück.
        """
        out = []
        for i in range(amount):
            out.append(Position())
        return tuple(out)
    
    # Methods for input
    def evaluate_query(self,query:dict):
        """
        Liest Parameter aus einem HTML-Query in Form eines Dictionary
        ein und setzt alle Variablen auf den entsprechenden Wert.

        Erkennt die folgenden Schlüssel:
        uname, dept, pname, pdate, p1name, p1type, p1cnt, p1ppu, p1,
        p2name, p2type, p2cnt, p2ppu, p2, p3name, p3type, p3cnt, p3ppu,
        p3, p4name, p4type, p4cnt, p4ppu, p4, p5name, p5type, p5cnt,
        p5ppu, p5, p6name, p6type, p6cnt, p6ppu, p6, p7name, p7type,
        p7cnt, p7ppu, p7, dono, prtype, known, iban, owner, prsepa
        """
        if query:
            keys = tuple(query.keys())
            
            # User name and -group, project name and date
            if 'uname' in keys:
                self.setusername(query['uname'])
            if 'dept' in keys:
                self.setusergroup(query['dept'])
            if 'pname' in keys:
                self.setprojectname(query['pname'])
            if 'pdate' in keys:
                self.setprojectdate(query['pdate'])
            
            # Position values
            for i in range(self._POSITIONCOUNT):
                pos = 'p'+str(i+1)
                if pos+'type' in keys and query[pos+'type'] in {'1','-1'}:
                    # Position is set to income or cost
                    if pos+'cnt' in keys and pos+'ppu' in keys\
                        and query[pos+'cnt'] and query[pos+'ppu']:
                        # Position has amount and price per unit
                        self.positions[i].setunitcount(int(query[pos+'cnt']))
                        amount = float(query[pos+'ppu'])
                        amount *= float(query[pos+'type'])
                        self.positions[i].setunitprice(amount)
                    elif pos in keys and query[pos]:
                        # Position has a set value
                        amount = float(query[pos])
                        amount *= float(query[pos+'type'])
                        self.positions[i].setvalue(amount)
                    else:
                        # Position has no value; ignore name
                        continue
                    if pos+'name' in keys:
                        # Set position name
                        self.positions[i].setname(query[pos+'name'])
            
            # Donation value
            if 'dono' in keys and query['dono']:
                self.setdonations(query['dono'])
            
            # Payment information
            if 'prtype' in keys and query['prtype']:
                self.setibanmode(query['prtype'])
                if query['prtype'] == '1':
                    # Payment mode: Transfer to user
                    if 'known' in keys and query['known'] == '1':
                        # Payment info is known
                        self.setibanknown(True)
                    else:
                        # Payment info not known
                        self.setibanknown(False)
                        if 'iban' in keys:
                            self.setaccountiban(query['iban'])
                        if 'owner' in keys:
                            self.setaccountname(query['owner'])
                if query['prtype'] == '2':
                    # Payment mode: debit from user
                    if 'prsepa' in keys and query['prsepa']:
                        self.setsepamode(query['prsepa'])
    
    # Methods for output
    def suggest_filename(self) -> str:
        """
        Gibt eine Empfehlung für einen Dateinamen aus für Dateien, die
        aus diesem Objekt generiert werden.
        """
        # Use constant _NAME as filename
        out = self._NAME
        if self.getprojectname():
            # Add project name without special characters
            out += " "+sub('[^A-Za-zÄÖÜäöüß0-9\\-_ ]','',
                           self.getprojectname())
        if self.getprojectdate():
            # Add project date
            out += " "+str(self.getprojectdate())
        return out

    def factur_x(self):

        doc = DH_Document()
        doc.context.guideline_parameter.id = "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"
        doc.header.id = "AKTIVE"+datetime.now().strftime("%Y%m%d%H%M%S")
        doc.header.name = self._NAME.upper()
        doc.header.type_code = "751" # Invoice information for accounting purposes
        doc.header.issue_date_time = date.today()
        doc.header.languages.add("de")

        doc.trade.agreement.seller.name = CONTACT['Name']
        doc.trade.agreement.seller.address.line_one = CONTACT['LineOne']
        if 'LineTwo' in CONTACT.keys():
            doc.trade.agreement.seller.address.line_two = CONTACT['LineTwo']
        if 'LineThree' in CONTACT.keys():
            doc.trade.agreement.seller.address.line_three = CONTACT['LineThree']
        doc.trade.agreement.seller.address.postcode = CONTACT['PostCode']
        doc.trade.agreement.seller.address.city_name = CONTACT['City']
        #doc.trade.agreement.seller.address.country_subdivision = CONTACT['State']
        doc.trade.agreement.seller.address.country_id = CONTACT['Country']

        for index in range(self._POSITIONCOUNT):
            position = self.positions[index]
            if not position:
                continue
            li = DH_LineItem()
            li.document.line_id = str(index)
            li.product.name = position.getname()
            li.agreement.net.amount = Decimal(position.getunitprice())
            li.agreement.net.basis_quantity = (Decimal(position.getunitcount()), "H87")  # H87 == Item
            li.delivery.billed_quantity = (Decimal(position.getunitcount()), "H87")  # H87 == Item
            li.settlement.trade_tax.category_code = "K" # VAT exempt for intra community supply of goods
            li.settlement.monetary_summation.total_amount = Decimal(position.getvalue())
            doc.trade.items.add(li)

        tax = DH_ApplicableTradeTax()
        tax.category_code = "K" # VAT exempt for intra community supply of goods
        doc.trade.settlement.trade_tax.add(tax)

        # Return test file (for now)
        with open('static/test.xml','rb') as file:
            xml = file.read()
        return xml
    
    # Variable getters and setters
    def setusername(self,value:str = ""):
        """Legt den Namen des Aktiven fest."""
        self._user["name"] = str(value).strip()
    
    def getusername(self) -> str:
        """Gibt den Namen des Aktiven zurück."""
        return self._user["name"]
    
    def setusergroup(self,value:str = ""):
        """Legt die Gruppe des Aktiven fest."""
        self._user["group"] = str(value).strip()
    
    def getusergroup(self) -> str:
        """Gibt die Gruppe des Aktiven zurück."""
        return self._user["group"]
    
    def setprojectname(self,value:str = ""):
        """Legt den Namen des Projekts fest."""
        self._project["name"] = str(value).strip()
    
    def getprojectname(self) -> str:
        """Gibt den Namen des Projekts zurück."""
        return self._project["name"]
    
    def setprojectdate(self,value=None):
        """
        Legt das Datum der Abrechnung fest.

        Akzepiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._project["date"] = value
        else:
            try:
                temp = str(value).split("-")
                self._project["date"] = date(
                    int(temp[0]), int(temp[1]), int(temp[2]))
            except:
                self._project["date"] = None
    
    def getprojectdate(self) -> date|None:
        """Gibt das Datum der Abrechnung zurück."""
        return self._project["date"]
    
    def setdonations(self,value=0.0):
        """Legt den Betrag eingenommener Spenden fest."""
        self._donations = float(value)
        if self._donations < 0:
            self._donations = 0.0
    
    def getdonations(self) -> float:
        """Gibt den Betrag eingenommener Spenden zurück."""
        return self._donations
    
    def getincome(self) -> float:
        """Gibt den Gesamtbetrag der Einnahmen zurück."""
        out = 0.0
        for i in range(self._POSITIONCOUNT):
            out += self.positions[i].income
        out += self.getdonations()
        return out

    def getcost(self) -> float:
        """Gibt den Gesamtbetrag der Ausgaben zurück."""
        out = 0.0
        for i in range(self._POSITIONCOUNT):
            out += self.positions[i].cost
        return out
    
    def gettotal(self) -> float:
        """Gibt den Betrag der Einnahmen minus Ausgaben zurück."""
        out = 0.0
        for i in range(self._POSITIONCOUNT):
            out += self.positions[i].value
        out += self.getdonations()
        return out
    
    def setaccountname(self,name:str = ""):
        """Legt den Namen des Kontoinhabers fest."""
        self._payment["name"] = str(name).strip()
    
    def getaccountname(self) -> str:
        """Gibt den Namen des Kontoinhabers zurück."""
        return self._payment["name"]
    
    def setaccountiban(self,value=""):
        """
        Legt die IBAN des Bankkontos fest.
        Entfernt dabei alle Zeichen außer Buchstaben und Ziffern.
        """
        value = sub('[\\W_]+', '',value.upper())
        if len(value) > 34:
            value = value[:34]
        self._payment["iban"] = str(value)
    
    def getaccountiban(self,spaces:bool = True) -> str:
        """Gibt die IBAN des Bankkontos zurück."""
        out = self._payment["iban"]
        if spaces:
            # add spaces
            for i in self._IBANSPACES:
                if len(out) > i:
                    out = out[:i] + " " + out[i:]
        return out

    def setibanmode(self,mode=None):
        if mode and int(mode) in self._MODES_IBAN:
            self._payment["ibanmode"] = int(mode)
        else:
            self._payment["ibanmode"] = None
    
    def getibanmode(self) -> int|None:
        return self._payment["ibanmode"]
    
    def setsepamode(self,mode=None):
        if mode and int(mode) in self._MODES_SEPA:
            self._payment["sepamode"] = int(mode)
        else:
            self._payment["sepamode"] = None
    
    def getsepamode(self) -> int|None:
        return self._payment["sepamode"]

    def setibanknown(self,mode=False):
        self._payment["ibanknown"] = bool(mode)
    
    def getibanknown(self) -> bool:
        return self._payment["ibanknown"]

    # Properties
    username = property(getusername,setusername,None,
                        "Der Name des Aktiven.")
    usergroup = property(getusergroup,setusergroup,None,
                         "Der Arbeitsbereich des Aktiven.")
    projectname = property(getprojectname,setprojectname,None,
                           "Der Name der Aktion oder des Projekts.")
    projectdate = property(getprojectdate,setprojectdate,None,
                           "Das Datum der Aktion oder des Projekts.")
    donations = property(getdonations,setdonations,None,
                         "Eingenommene Spenden in Euro.")
    income = property(getincome,None,None,
                      "Gesamteinnahmen in Euro.")
    cost = property(getcost,None,None,
                      "Gesamtausgaben in Euro.")
    total = property(gettotal,None,None,
                     "Gesamtwert Einnahmen minus Ausgaben, in Euro.")
    accountname = property(getaccountname,setaccountname,None,
                           "Der Name des Bankkontoimhabers.")
    iban = property(getaccountiban,setaccountiban,None,
                    "Die IBAN (ohne einleitendes DE) des Bankkontos.")
    accountiban = iban
    ibanmode = property(getibanmode,setibanmode,None,"""
                        Wie die Zahlung abgehandelt wird:

                        1 – Ausgaben werden auf Konto überwiesen.
                        2 – Einnahmen werden von Konto abgebucht.
                        3 – Einnahmen werden von Benutzer überwiesen.
                        """)
    sepamode = property(getsepamode,setsepamode,None,"""
                        Ob ein SEPA-Mandatsformular angefordert wird.

                        1 – Nein, Mandat ist schon erteilt.
                        2 – Ja, Mandat liegt noch nicht vor.
                        3 – Ja, Mandat ist veraltet.
                        """)
    ibanknown = property(getibanknown,setibanknown,None,
                         "Ob die IBAN dem ADFC schon vorliegt.")


class HTMLPrinter:
    """
    Ein Objekt, welches eine HTML-Vorlage einliest
    und dann aus dieser und Objekten der Klasse Abrechnung
    fertig ausgefüllte Abrechnungsformulare im HTML-Format erstellt.
    """
    
    # Class constants
    _CHECKBOXES = {False:"&#9744;",True:"&#9746;"}
    _PLACEHOLDER = "<!--PLACEHOLDER-->"
    _POSITIONCOUNT = 7
    _SPLIT = "<!--SPLIT-->\n"
    
    # Dunder methods
    def __init__(self,path):
        """
        Initialisiert ein Objekt der Klasse HTMLPrinter.
        Im Rahmen dessen wird eine HTML-Datei als Template geladen.

        Parameter:
        path - Der Dateipfad der HTML-Vorlage
        """
        self._template = self._fetch_html(path)
    
    def __str__(self):
        return self.html_compose()
    
    def __repr__(self):
        return __class__.__name__+"()"
    
    # Template loading
    def _fetch_html(self,path) -> tuple:
        """
        Öffnet das HTML-Template, teilt den Inhalt in Sektionen auf
        und gibt das Ergebnis als Tupel zurück.
        """
        with open(path) as f:
            sections = f.read().split(self._SPLIT)
        out = []
        for i in sections:
            out.append (i)
        return tuple(out)
    
    # Order of fields in sections of the document
    _USER_FIELDS = (lambda obj: obj.username, lambda obj: obj.usergroup,
                    lambda obj: obj.projectname, lambda obj: obj.projectdate)
    _TOTAL_FIELDS = ((lambda obj: obj.donations, True),
                     (lambda obj: obj.income, True),
                     (lambda obj: obj.cost, True),
                     (lambda obj: obj.total, False))
    _PAYMENT_FIELDS = (None,None,None,
                       lambda obj: obj.iban or 'DE', lambda obj: obj.accountname)
    _PAYMENT_BOXES = (lambda obj: obj.ibanmode == 1,
                      lambda obj: obj.ibanmode==1 and obj.ibanknown==True,
                      lambda obj: obj.ibanmode==1 and obj.ibanknown==False,
                      None,
                      None,
                      lambda obj: obj.ibanmode == 2,
                      lambda obj: obj.ibanmode==2 and obj.sepamode==2,
                      lambda obj: obj.ibanmode==2 and obj.sepamode==3,
                      lambda obj: obj.ibanmode == 3)
    _DATE_FIELDS = (lambda: format_date(date.today(), format="long",
                                          locale="de_DE"),
                    lambda: "v"+VERSION)

    # Methods for template sections
    def _fill_user(self,text:str,input:Abrechnung|None = None):
        """
        Ersetzt Platzhalter im String text durch Felder in der
        Abrechnung input. Falls kein input vorhanden ist, entferne
        die Platzhalter einfach.

        Platzhalter werden gemäß der Konstante _USER_FIELDS ersetzt.
        """
        segments = text.split(self._PLACEHOLDER)

        if type(input) == Abrechnung:
            # input is Abrechnung; replace all placeholders
            for index in range(len(segments)):
                if index < len(self._USER_FIELDS):
                    # Replace with what? Use _USER_FIELDS
                    data = self._USER_FIELDS[index](input)
                    if type(data) == date:
                        # This is a date; apply german format
                        data = format_date(data, format="long", locale="de_DE")
                    elif data == None:
                        data = ""
                    else:
                        # Remove HTML special characters
                        data = escape(str(data))
                    segments[index] += data

        return "".join(segments)
    
    def _fill_positions(self,text:str,input:Abrechnung|None = None):
        """
        Gibt HTML-Tabellenreihen mit 8 Spalten aus und fügt
        gegebenenfalls Positionsdaten mit ein.

        Spalte 1: Index (1 bis 7)
        Spalten 2-6: Siehe Positions.htmlcells()
        Spalten 7,8: leer
        """
        # text should be empty and will be ignored
        TAB = "\t"
        NL = "\n"
        output = []

        for index in range(self._POSITIONCOUNT):
            # One table row for each potential position
            line=""
            line += TAB*4+"<tr>"+NL
            line += TAB*5+tools.cell(str(index+1))+NL

            if (type(input) == Abrechnung and index < len(input.positions)):

                # Position exists, use htmlcells
                line += input.positions[index].htmlcells(indent=5)+NL
                line += TAB*5+tools.cell()*2+NL
            
            else:
                # No position, empty cells
                line += TAB*5+tools.cell()*7+NL
            
            line += TAB*4+"</tr>"+NL
            output.append(line)
        
        return "".join(output)

    def _fill_total(self,text:str,input:Abrechnung|None = None):
        """
        Ersetzt Platzhalter im String text durch Felder in der
        Abrechnung input. Falls kein input vorhanden ist, entferne
        die Platzhalter einfach.

        Platzhalter werden gemäß der Konstante _TOTAL_FIELDS ersetzt.
        """
        segments = text.split(self._PLACEHOLDER)

        if type(input) == Abrechnung and input:
            # input is non-empty Abrechnung; replace all placeholders
            for index in range(len(segments)):
                if index < len(self._TOTAL_FIELDS):
                    # Replace with what? Use _TOTAL_FIELDS
                    data = self._TOTAL_FIELDS[index][0](input)
                    # Format as Euros
                    data = tools.euro(data,self._TOTAL_FIELDS[index][1])
                    segments[index] += data

        return "".join(segments)
    
    def _fill_payment(self,text:str,input:Abrechnung|None = None):
        """
        Ersetzt Platzhalter im String text durch Felder und Checkboxen
        in der Abrechnung input. Falls kein input vorhanden ist,
        entferne die Platzhalter und füge leere Checkboxen ein.

        Platzhalter werden gemäß der Konstante _PAYMENT_FIELDS ersetzt,
        Checkboxen gemäß der Konstante _PAYMENT_CHECKBOXES eingesetzt.
        """
        segments = text.split(self._PLACEHOLDER)

        if type(input) == Abrechnung:
            # input is Abrechnung; replace all placeholders
            for index in range(len(segments)):
                if (index < len(self._PAYMENT_FIELDS)
                    and self._PAYMENT_FIELDS[index] != None
                    and input.ibanmode == 1 and input.ibanknown == False):
                    # Place account IBAN and account name
                    # according to _PAYMENT_FIELDS
                    data = self._PAYMENT_FIELDS[index](input)
                    segments[index] += escape(str(data))
                if (index < len(self._PAYMENT_BOXES)
                    and self._PAYMENT_BOXES[index] != None):
                    # Insert a checkbox. Use _PAYMENT_BOXES to
                    # determine whether it is checked or not.
                    data = self._PAYMENT_BOXES[index](input)
                    segments[index] += self._CHECKBOXES[data]
        else:
            # input is not Abrechnung; place empty checkboxes
            for index in range(len(segments)):
                if (index < len(self._PAYMENT_BOXES)
                    and self._PAYMENT_BOXES[index] != None):
                    # Insert a checkbox wherever
                    # _PAYMENT_BOXES is not None.
                    segments[index] += self._CHECKBOXES[False]

        return "".join(segments)
    
    def _fill_date(self,text:str,input:Abrechnung|None = None):
        """
        Ersetzt Platzhalter im String durch Datum und Versionsnummer.

        Platzhalter werden gemäß der Konstante _DATE_FIELDS ersetzt.
        """
        # input will be ignored
        segments = text.split(self._PLACEHOLDER)
        
        # Replace all placeholders
        for index in range(len(segments)):
            if (index < len(self._DATE_FIELDS)):
                segments[index] += self._DATE_FIELDS[index]()
        
        return "".join(segments)
    
    # Section keywords and corresponding methods
    _SECTIONS = (("USERDATA", _fill_user), ("POSITIONS", _fill_positions),
                 ("TOTAL", _fill_total), ("PAYMENT", _fill_payment),
                 ("DATE", _fill_date))
    
    # Callable methods
    def html_compose(self,input:Abrechnung|None = None):
        """
        Füllt die HTML-Vorlage mit Angaben aus einer Abrechnung aus.
        
        Argumente:
        input: Ein Objekt der Klasse Abrechnung (optional)
        """
        
        out = ""
        
        for section in self._template:
            # Does this section start with a keyword?
            for key in self._SECTIONS:
                if section.startswith("<!--"+key[0]+"-->\n"):
                    # Keyword found; use corresponding method
                    out += key[1](self,
                        text=section.removeprefix("<!--"+key[0]+"-->\n"),
                        input=input)
                    break
            else:
                # No keyword; use string as is
                out += section
        
        return out
