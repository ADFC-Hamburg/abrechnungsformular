"""
Modul für Klassen, die Reisekostenabrechnungen repräsentieren oder
selbige als Dokument ausgeben.
"""

from datetime import date
from decimal import Decimal

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

