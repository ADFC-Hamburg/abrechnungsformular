"""
Modul für Klassen, die Reisekostenabrechnungen repräsentieren oder
selbige als Dokument ausgeben.
"""

from datetime import date
from decimal import Decimal
from html import escape

from schwifty import IBAN, exceptions

from babel.dates import format_date
from app import tools


class Position:
    """
    Beschreibt eine Position in einer Reisekostenabrechnung.
    """

    # Dunder methods
    def __init__(self,receiptnumber:str = "",reason:str = "",
                 date:date|None = None,value=Decimal('0.00')):
        """
        Initialisiert ein Objekt der Klasse Position.

        Argumente:
        receipt: Nummer des zur Position gehörenden Belegs
        reason: Kostengrund
        date: Datum der Geldausgabe
        value: Ausgegebenes Geld
        """
        self.setreason(reason)
        self.setreceiptnumber(receiptnumber)
        self.setdate(date)
        self.setvalue(value)

    def __str__(self) -> str:
        return tools.euro(self.getvalue())

    def __repr__(self) -> str:
        return str (f"{self.__class__.__name__}"
                   +f"(receiptnumber={repr(self.getreceiptnumber())},"
                   +f"reason={repr(self.getreason())},"
                   +f"date={repr(self.getdate())},"
                   +f"value={repr(self.getvalue())})")

    def __bool__(self) -> str:
        return bool(self.getvalue())
    
    # Methods for output
    def htmlcells(self,indent:int = 0) -> str:
        """
        Gibt vier Zellen im HTML-Format aus.
        Jede Zelle hat eine eigene Zeile.

        Die Reihenfolge lautet:
        Datum, Beleg-Nr., Kostengrund, Betrag
        """
        out = []

        joiner = "\n" + "\t"*indent

        out.append( tools.cell( format_date(self.getdate(),locale="de_DE") ) )
        out.append( tools.cell( escape(self.getreceiptnumber()) ) )
        out.append( tools.cell( escape(self.getreason()) ) )
        out.append( tools.cell( tools.euro(self.getvalue()) ) )

        return "\t"*indent + joiner.join(out)

    def check_complete(self) -> bool:
        """Gibt zurück, ob alle Felder ausgefüllt sind."""
        return bool(self.getvalue() and self.getdate()
                    and self.getreason() and self.getreceiptnumber())

    # Variable getters and setters
    def setreceiptnumber(self,value:str):
        """Legt die Belegnummer der Position fest."""
        self._receipt_nr = str(value).strip()

    def getreceiptnumber(self) -> str:
        """Gibt die Belegnummer der Position zurück."""
        return self._receipt_nr

    def setreason(self,value:str):
        """Legt den Kostengrund fest."""
        self._reason = str(value).strip()
    
    def getreason(self) -> str:
        """Gibt den Kostengrund zurück."""
        return self._reason
    
    def setdate(self,value:str|date|None):
        """
        Legt das Datum der Position fest.
        
        Akzeptiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._date = value
        elif value:
            temp = str(value).split("-")
            self._date = date(
                int(temp[0]), int(temp[1]), int(temp[2]))
        else:
            self._date = None
    
    def getdate(self) -> date|None:
        """Gibt das Datum der Position zurück."""
        return self._date
    
    def setvalue(self,value):
        """Legt den Geldwert der Position fest."""
        if Decimal(value) < 0:
            raise tools.BelowMinimumException
        elif not Decimal(value) % Decimal('0.01') == 0:
            raise tools.DecimalsException
        self._value = Decimal(value)
    
    def getvalue(self) -> Decimal:
        """Gibt den Geldwert der Position zurück."""
        return self._value

    # Properties
    receiptnumber = property(getreceiptnumber,setreceiptnumber,None,
                             "Die Nummer des Belegs für die Position.")
    reason = property(getreason,setreason,None,
                      "Der Kostengrund der Position.")
    date = property(getdate,setdate,None,
                    "Das Datum der Position.")
    value = property(getvalue,setvalue,None,
                     "Der Geldwert der Position.")
    complete = property(check_complete,None,None,
                        "Ob sämtliche Felder ausgefüllt sind.")


class Abrechnung():
    """
    Beschreibt eine Reisekostenabrechnung für den ADFC Hamburg.
    """

    # Class constants
    POSITIONCOUNT = 12
    MAXDATES = 10

    # Dunder methods
    def __init__(self):
        """
        Initialisiert ein Objekt der Klasse Abrechnung.
        """

        self.positions = self._create_positions(self.POSITIONCOUNT)

        self._user_name = self._user_street = self._user_postcode\
            = self._user_city = self._payment_name = self._cause = ""
        self._payment_iban = IBAN("",allow_invalid=True)
        self._date_begin = self._date_end = None
    
    # Part of initialization
    def _create_positions(self,amount:int) -> tuple[Position]:
        """
        Gibt einen Tupel aus neuen Positionen zurück.
        """
        out = []
        for i in range(amount):
            out.append(Position())
        return tuple(out)
    
    # Variable getters and setters
    def setusername(self,value:str = ""):
        """Legt den Namen des Aktiven fest."""
        self._user_name = str(value).strip()
    
    def getusername(self) -> str:
        """Gibt den Namen des Aktiven zurück."""
        return self._user_name
    
    def setuserstreet(self,value:str = ""):
        """Legt die Straße und Hausnummer des Aktiven fest."""
        self._user_street = str(value).strip()
    
    def getuserstreet(self) -> str:
        """Gibt die Straße und Hausnummer des Aktiven zurück."""
        return self._user_street

    def setuserpostcode(self,value:str = ""):
        """Legt die Postleitzahl des Aktiven fest."""
        self._user_postcode = str(value).strip()
    
    def getuserpostcode(self) -> str:
        """Gibt die Postleitzahl des Aktiven zurück."""
        return self._user_postcode

    def setusercity(self,value:str = ""):
        """Legt die Stadt des Aktiven fest."""
        self._user_city = str(value).strip()
    
    def getusercity(self) -> str:
        """Gibt die Stadt des Aktiven zurück."""
        return self._user_city

    def setaccountname(self,value:str = ""):
        """Legt den Namen des Kontoinhabers fest."""
        self._payment_name = str(value).strip()
    
    def getaccountname(self) -> str:
        """Gibt den Namen des Kontoinhabers zurück."""
        return self._payment_name

    def setaccountiban(self,value):
        """
        Verifiziert die angegebene IBAN
        und legt sie als Überweisungskonto fest.
        """
        if value:
            self._payment_iban = IBAN(str(value))
        else:
            self._payment_iban = IBAN('', allow_invalid = True)
    
    def getaccountiban(self,spaces:bool = True) -> str:
        """Gibt die IBAN des Bankkontos zurück."""
        return self._payment_iban.formatted

    def setcause(self,value:str = ""):
        """Legt den Grund für die Reise fest."""
        self._cause = str(value).strip()
    
    def getcause(self) -> str:
        """Gibt den Grund für die Reise zurück."""
        return self._cause

    def setbegindate(self,value:str|date|None = None):
        """
        Legt das Datum des Beginns der Reise fest.

        Akzepiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._date_begin = value
        elif value:
            temp = str(value).split("-")
            self._date_begin = date(
                int(temp[0]), int(temp[1]), int(temp[2]))
        else:
            self._date_begin = None
    
    def getbegindate(self) -> date|None:
        """Gibt das Datum des Beginns der Reise zurück."""
        return self._date_begin

    def setenddate(self,value:str|date|None = None):
        """
        Legt das Datum des Endes der Reise fest.

        Akzepiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._date_end = value
        elif value:
            temp = str(value).split("-")
            self._date_end = date(
                int(temp[0]), int(temp[1]), int(temp[2]))
        else:
            self._date_end = None
    
    def getenddate(self) -> date|None:
        """Gibt das Datum des Endes der Reise zurück."""
        return self._date_end
    
    # Properties
    username = property(getusername,setusername,None,
                        "Der Name des Aktiven.")
    userstreet = property(getuserstreet,setuserstreet,None,
                          "Die Straße und Hausnummer des Aktiven.")
    userpostcode = property(getuserpostcode,setuserpostcode,None,
                          "Die Postleitzahl des Aktiven.")
    usercity = property(getusercity,setusercity,None,
                          "Die Heimatstadt des Aktiven.")
    accountname = property(getaccountname,setaccountname,None,
                           "Der Inhaber des Überweisungskontos.")
    iban = property(getaccountiban,setaccountiban,None,
                    "Die IBAN des Überweisungskontos.")
    cause = property(getcause,setcause,None,
                     "Der Grund für die Reise.")
    begindate = property(getbegindate,setbegindate,None,
                         "Das Datum, an dem die Reis begann.")
    enddate = property(getenddate,setenddate,None,
                       "Das Datum, an dem die Reise endete.")