"""
Modul für Klassen, die Reisekostenabrechnungen repräsentieren oder
selbige als Dokument ausgeben.
"""

from datetime import date, time, timedelta
from decimal import Decimal
from html import escape
from re import sub

from babel.dates import format_date
from schwifty import IBAN, exceptions

from . import tools, REISE_RATE


class Position:
    """
    Beschreibt eine Position in einer Reisekostenabrechnung.
    """

    # Dunder methods
    def __init__(self,reason:str = "",
                 date:date|None = None,value=Decimal('0.00')):
        """
        Initialisiert ein Objekt der Klasse Position.

        Argumente:
        reason: Kostengrund
        date: Datum der Geldausgabe
        value: Ausgegebenes Geld
        """
        self.setreason(reason)
        self.setdate(date)
        self.setvalue(value)

    def __str__(self) -> str:
        return tools.euro(self.getvalue())

    def __repr__(self) -> str:
        return str (f"{self.__class__.__name__}"
                   +f"reason={repr(self.getreason())},"
                   +f"date={repr(self.getdate())},"
                   +f"value={repr(self.getvalue())})")

    def __bool__(self) -> str:
        return bool(self.getvalue())

    # Methods for output
    def check_filled(self) -> bool:
        """Gibt zurück, ob mindestens ein Feld ausgefüllt ist."""
        return bool(self.getvalue() or self.getdate()
                    or self.getreason())

    def check_complete(self) -> bool:
        """Gibt zurück, ob alle Felder ausgefüllt sind."""
        return bool(self.getvalue() and self.getdate()
                    and self.getreason())

    # Variable getters and setters
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
    reason = property(getreason,setreason,None,
                      "Der Kostengrund der Position.")
    date = property(getdate,setdate,None,
                    "Das Datum der Position.")
    value = property(getvalue,setvalue,None,
                     "Der Geldwert der Position.")
    complete = property(check_complete,None,None,
                        "Ob sämtliche Felder ausgefüllt sind.")


class Day:
    """
    Beschreibt die Abrechnung des Tagesgeldes für einen einzelnen Tag
    in einer Reisekostenabrechnung.
    """

    # Class constants
    ALLOWANCE_FULL = Decimal(REISE_RATE['Tagessatz']['GanzerTag'])
    ALLOWANCE_REDUCED = Decimal(REISE_RATE['Tagessatz']['AnAbreise'])
    MEAL_DEDUCTION = (ALLOWANCE_FULL*Decimal('0.2'),
                      ALLOWANCE_FULL*Decimal('0.4'),
                      ALLOWANCE_FULL*Decimal('0.4'))
    MEALS = 3

    # Dunder methods
    def __init__(self):
        """Initialisiert ein Objekt der Klasse Day."""

        self._breakfast = self._lunch = self._dinner = False

    def __getitem__(self,key:int) -> bool:
        return self.getmeal(key)

    def __setitem__(self,key:int,newvalue:bool):
        self.setmeal(key,newvalue)

    def __len__(self) -> int:
        return self.MEALS

    # Variable getters and setters
    def setmeal(self,index:int,check:bool):
        """Legt fest, ob eine Mahlzeit bereitgestellt wurde."""
        match int(index):
            case 0:
                self._breakfast = bool(check)
            case 1:
                self._lunch = bool(check)
            case 2:
                self._dinner = bool(check)
            case _:
                raise IndexError(f"{self.__class__.__name__} index out of range")

    def getmeal(self,index:int) -> bool:
        """Gibt zurück, ob eine Mahlzeit bereitgestellt wurde."""
        match int(index):
            case 0:
                return self._breakfast
            case 1:
                return self._lunch
            case 2:
                return self._dinner
            case _:
                raise IndexError(f"{self.__class__.__name__} index out of range")

    def getmealcost(self,reduced:bool = False) -> Decimal:
        """
        Gibt zurück, wie viel Tagesgeld durch bereitgestellte Verpflegung
        gekürzt wird.
        """
        cost = Decimal(0)
        for i in range(self.MEALS):
            if self[i]:
                cost += self.MEAL_DEDUCTION[i]
        return min(cost,self.getallowance(reduced))
    
    def getallowance(self,reduced:bool = False) -> Decimal:
        """
        Gibt den Tagessatz ohne Kürzungen durch Verpflegung zurück.

        Argumente:
        reduced:    Ob der reduzierte Tagessatz greift.
        """
        allowance = self.ALLOWANCE_REDUCED if reduced else self.ALLOWANCE_FULL
        return allowance

    def getbenefits(self,reduced:bool = False) -> Decimal:
        """
        Gibt den Tagessatz mit Kürzungen durch Verpflegung zurück.

        Argumente:
        reduced:    Ob der reduzierte Tagessatz greift.
        """
        return self.getallowance(reduced) - self.getmealcost(reduced)


class SingleDay(Day):
    """
    Bescheibt die Abrechnung des Tagesgeldes für eine 
    Reisekostenabrechnung für eine Tagesreise.
    """

    # Class constants
    ALLOWANCE_REDUCED = Decimal(REISE_RATE['Tagessatz']['Einzeltag'])
    THRESHOLD = timedelta(hours=8)

    # Dunder methods
    def __init__(self):
        """Initialisiert ein Objekt der Klasse SingleDay."""
        self._timedelta = timedelta()
        super().__init__()
    
    # Variable getters and setters
    def settimedelta(self,begin:time,end:time):
        """
        Berechnet die Dauer der Tagesreise.

        Argumente:
        begin:  Uhrzeit des Beginns der Reise.
        end:    Uhrzeit des Endes der Reise.
        """
        self._timedelta = timedelta(hours = end.hour-begin.hour,
                                    minutes = end.minute-begin.minute,
                                    seconds = end.second-begin.second)

    def getmealcost(self) -> Decimal:
        """
        Gibt zurück, wie viel Tagesgeld durch bereitgestellte Verpflegung
        gekürzt wird.
        Liegt die Länge der Reise unter dem Grenzwert, beträgt der
        Tagessatz 0.
        """
        if self.THRESHOLD > self._timedelta:
            return Decimal('0')
        cost = Decimal(0)
        for i in range(self.MEALS):
            if self[i]:
                cost += self.MEAL_DEDUCTION[i]
        return min(cost,self.getallowance())

    def getallowance(self) -> Decimal:
        """
        Gibt den Tagessatz ohne Kürzungen durch Verpflegung zurück.
        Liegt die Länge der Reise unter dem Grenzwert, beträgt der
        Tagessatz 0.
        """
        if self.THRESHOLD > self._timedelta:
            return Decimal('0')
        else:
            return self.ALLOWANCE_REDUCED
        
    def getbenefits(self) -> Decimal:
        """
        Gibt den Tagessatz mit Kürzungen durch Verpflegung zurück.
        Liegt die Länge der Reise unter dem Grenzwert, beträgt der
        Tagessatz 0.
        """
        if self.THRESHOLD > self._timedelta:
            return Decimal('0')
        else:
            return self.getallowance() - self.getmealcost()


class Abrechnung():
    """
    Beschreibt eine Reisekostenabrechnung für den ADFC Hamburg.
    """

    # Class constants
    POSITIONCOUNT = 10
    MAXDATES = 5
    CAR_RATE_PER_KM = Decimal(REISE_RATE['PKWproKM'])
    CAR_MAXRATE = Decimal(REISE_RATE['PKWMaximum'])
    OVERNIGHT_MIN = Decimal(REISE_RATE['UebernachtMin'])

    _NAME = "Reisekostenabrechnung"
    _FIELD_NAMES = {'uname':'dein Name','group':'deine Arbeitsgruppe',
                    'reason':'der Anlass der Reise','iban':'deine IBAN',
                    'owner':'der Name des Kontoinhabers/der Kontoinhaberin',
                    'begin':'Anfangsdatum der Reise',
                    'end':'Enddatum der Reise',
                    'begintime':'Anfangszeit der Reise',
                    'endtime':'Endzeit der Reise',
                    'car':'die im Privatauto zurückgelegte Strecke'}
    _FIELD_ERRORS = {'length':'Die IBAN muss die korrekte Länge haben'
                     +' (22 Zeichen bei einer deutschen IBAN).',
                     'checksum':'Die IBAN muss gültig sein.'
                     +' (Wahrscheinlich liegt ein Tippfehler vor.)',
                     'timetravel':'Die Reise darf nicht enden, '
                     +'bevor sie angefangen hat.','maxdates':
                     f'Es können maximal {MAXDATES} Tage abgerechnet werden.'}

    # Dunder methods
    def __init__(self):
        """
        Initialisiert ein Objekt der Klasse Abrechnung.
        """

        self.positions = self._create_positions(self.POSITIONCOUNT)
        self.days: tuple[Day|SingleDay] = tuple()

        self._user_name = self._user_group\
            = self._payment_name = self._cause = ""
        self._payment_iban = IBAN("",allow_invalid=True)
        self._date_begin = self._date_end\
            = self._time_begin = self._time_end = None
        self._car_distance = Decimal('0')
        self._overnight_flat = self._payment_iban_known = False

    def __bool__(self) -> bool:
        """Gibt True zurück, falls Tage vorhanden sind
        oder Positionen oder andere Felder eingegeben wurden."""

        for position in self.positions:
            if position:
                return True
        return bool(self.getovernightflat() or self.getcardistance() or len(self.days))

    # Part of initialization
    def _create_positions(self,amount:int) -> tuple[Position]:
        """
        Gibt einen Tupel aus neuen Positionen zurück.
        """
        out = []
        for i in range(amount):
            out.append(Position())
        return tuple(out)

    # Internal methods
    def _apply_time(self):
        """
        Gibt Anfangs- und Endzeit an das SingleDay-Objekt weiter.
        
        Macht nichts, falls eine der Zeiten fehlt oder die Reise nicht
        genau einen Tag lang ist.
        """
        if len(self.days) == 1 and self.getbegintime() and self.getendtime():
            self.days[0].settimedelta(self.getbegintime(),self.getendtime())

    def _create_days(self):
        """
        Berechnet die Länge der Reise aus Anfangs- und Enddatum
        und erstellt einen Tupel, der aus einer entsprechenden
        Anzahl aus Day- oder SingleDay-Objekten besteht.

        Dabei werden bestehende Objekte gegebenenfalls
        wiederverwendet.
        """
        if not (self._date_begin and self._date_end)\
        or (self._date_begin > self._date_end):
            # Zero days
            self.days = ()
        elif (self._date_begin == self._date_end):
            # One day
            if not len(self.days) == 1:
                self.days = (SingleDay(),)
                self._apply_time()
        else:
            # Multiple days
            number_days = (self.enddate-self.begindate).days + 1
            if number_days > self.MAXDATES:
                raise tools.IllegalValueException
            current_length = len(self.days)
            out = []
            if current_length > 1:
                # Reuse existing days
                out.extend(self.days[:min(current_length,number_days)])
            for i in range(len(out),number_days):
                out.append(Day())
            self.days = tuple(out)

    # Methods for input
    def evaluate_query(self,query:dict) -> str:
        """
        Liest Parameter aus einem HTML-Query in Form eines Dictionary
        ein und setzt alle Variablen auf den entsprechenden Wert.

        Gibt außerdem eine Aufzählung aller Fehler als String zurück.

        Erkennt die folgenden Schlüssel:
        uname, ugroup, reason, known, iban, owner, begin, end, begintime,
        endtime, car, night
        
        px, pxname, pxdate (x zwischen 1 und MAXPOSITIONS),
        
        dxmy (x zwischen 1 und MAXDATES, y zwischen 1 und 3)
        """
        if query:
            keys = tuple(query.keys())
            missing = []
            erronous = []
            erronous_positions = []
            below_minimum = []
            mileage_negative = False
            not_currency = []
            incomplete_positions = []
            errormessage = []

            # User name and -group, cause of travel
            if 'uname' in keys:
                self.setusername(query['uname'])
            if 'ugroup' in keys:
                self.setusergroup(query['ugroup'])
            if 'reason' in keys:
                self.setcause(query['reason'])

            # Date of travel
            try:
                if 'begin' in keys and query['begin']:
                    self.setbegindate(query['begin'])
            except Exception:
                erronous.append(self._FIELD_NAMES['begin'])
            try:
                if 'end' in keys and query['end']:
                    self.setenddate(query['end'])
            except tools.IllegalValueException:
                errormessage.append(self._FIELD_ERRORS['maxdates'])
            except Exception:
                erronous.append(self._FIELD_NAMES['end'])
            if self._date_begin and self._date_end\
            and self._date_begin > self._date_end:
                errormessage.append(self._FIELD_ERRORS['timetravel'])

            # Check if always required values were provided
            for name in ('uname','ugroup','reason','begin','end'):
                if not name in keys or not query[name]:
                    missing.append(self._FIELD_NAMES[name])

            # Time of travel
            try:
                if 'begintime' in keys and query['begintime']:
                    self.setbegintime(query['begintime'])
                elif len(self.days)==1:
                    missing.append(self._FIELD_NAMES['begintime'])
            except Exception:
                erronous.append(self._FIELD_NAMES['begintime'])
            try:
                if 'endtime' in keys and query['endtime']:
                    self.setendtime(query['endtime'])
                elif len(self.days)==1:
                    missing.append(self._FIELD_NAMES['endtime'])
            except Exception:
                erronous.append(self._FIELD_NAMES['endtime'])
            if self._time_begin and self._time_end and len(self.days)==1\
            and self._time_begin > self._time_end:
                errormessage.append(self._FIELD_ERRORS['timetravel'])

            # Payment information
            if 'known' in keys and query['known'] == '1':
                # Payment info is known
                self.setibanknown(True)
            else:
                # Payment info not known
                self.setibanknown(False)
                if 'iban' in keys and query['iban']:
                    try:
                        self.setaccountiban(query['iban'])
                    except exceptions.InvalidChecksumDigits:
                        errormessage.append(self._FIELD_ERRORS['checksum'])
                    except exceptions.InvalidLength:
                        errormessage.append(self._FIELD_ERRORS['length'])
                    except exceptions.InvalidStructure:
                        erronous.append(self._FIELD_NAMES['iban'])
                else:
                    missing.append(self._FIELD_NAMES['iban'])
                if 'owner' in keys and query['owner']:
                    self.setaccountname(query['owner'])
                else:
                    missing.append(self._FIELD_NAMES['owner'])

            # Days information
            for day in range(len(self.days)):
                for meal in range(3):
                    name = f'd{day+1}m{meal+1}'
                    self.days[day][meal] = bool(name in query and query[name]=='1')

            # Positions
            for i, position in enumerate(self.positions,start=1):
                if f'p{i}name' in query:
                    position.setreason(query[f'p{i}name'])
                if f'p{i}date' in query:
                    try:
                        position.setdate(query[f'p{i}date'])
                    except Exception:
                        erronous_positions.append(f'{i}.')
                        continue
                if f'p{i}' in query and query[f'p{i}']:
                    try:
                        position.setvalue(query[f'p{i}'])
                    except tools.BelowMinimumException:
                        below_minimum.append(f'{i}.')
                        continue
                    except tools.DecimalsException:
                        not_currency.append(f'{i}.')
                        continue
                    except Exception:
                        erronous_positions.append(f'{i}.')
                        continue
                if position.check_filled() and not position.check_complete():
                    incomplete_positions.append(f'{i}.')
                

            # Car mileage and overnight flat rate
            try:
                if 'car' in query:
                    self.setcardistance(query['car'] or '0')
            except tools.BelowMinimumException:
                mileage_negative = True
            except Exception:
                erronous.append(self._FIELD_NAMES['car'])
            self.setovernightflat('night' in query and query['night']=='1')

            # Finalize error message
            missing = [item for item in missing if item not in erronous]
            errorstart = []
            if missing:
                message = tools.write_list_de(missing)
                if len(missing) > 1:
                    message += ' müssen'
                else:
                    message += ' muss'
                message += ' mit angegeben werden.'
                errorstart.append(tools.uppercase_first(message))
            if incomplete_positions:
                message = 'Die ' + tools.write_list_de(incomplete_positions)
                message += ' Position muss vollständig ausgefüllt sein.'
                errorstart.append(message)
            if not_currency:
                message = 'Die ' + tools.write_list_de(not_currency)
                message += ' Position muss ganze Centbeträge enthalten.'
                errorstart.append(message)
            if erronous or erronous_positions:
                message = ""
                if erronous:
                    message = tools.write_list_de(erronous)
                    if erronous_positions:
                        message += ' sowie '
                if erronous_positions:
                    message += 'die ' + tools.write_list_de(erronous_positions)
                    message += ' Position'
                if len(erronous) > 1 or (erronous and erronous_positions):
                    message += ' müssen'
                else:
                    message += ' muss'
                message += ' korrekt ausgefüllt werden.'
                errorstart.append(tools.uppercase_first(message))
            if below_minimum or mileage_negative:
                message = ""
                if mileage_negative:
                    message = self._FIELD_NAMES['car']
                    if below_minimum:
                        message += ' sowie '
                if below_minimum:
                    message += 'die ' + tools.write_list_de(below_minimum)
                    message += ' Position'
                if below_minimum and mileage_negative:
                    message += ' dürfen'
                else:
                    message += ' darf'
                message += ' keine negativen Werte enthalten.'
                errorstart.append(tools.uppercase_first(message))

            errormessage = errorstart + errormessage
            return '\n'.join(errormessage)

    # Methods for output
    def suggest_filename(self) -> str:
        """
        Gibt eine Empfehlung für einen Dateinamen aus für Dateien, die
        aus diesem Objekt generiert werden.
        """
        # Use constant _NAME as filename
        out = self._NAME
        if self.getusername():
            # Add project name without special characters
            out += " "+sub('[^A-Za-zÄÖÜäöüß0-9\\-_ ]','',
                           self.getusername())
        if self.getbegindate():
            # Add project date
            out += " "+str(self.getbegindate())
        return out


    # Variable getters and setters
    def setusername(self,value:str = ""):
        """Legt den Namen des Aktiven fest."""
        self._user_name = str(value).strip()

    def getusername(self) -> str:
        """Gibt den Namen des Aktiven zurück."""
        return self._user_name

    def setusergroup(self,value:str = ""):
        """Legt die Arbeitsgruppe des Aktiven fest."""
        self._user_group = str(value).strip()

    def getusergroup(self) -> str:
        """Gibt die Arbeitsgruppe des Aktiven zurück."""
        return self._user_group

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

    def setibanknown(self,mode=False):
        self._payment_iban_known = bool(mode)
    
    def getibanknown(self) -> bool:
        return self._payment_iban_known

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
        self._create_days()

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
        self._create_days()

    def getenddate(self) -> date|None:
        """Gibt das Datum des Endes der Reise zurück."""
        return self._date_end

    def setbegintime(self,value:str|time|None = None):
        """Gibt die Uhrzeit des Beginns der Reise zurück."""
        if type(value) == time:
            self._time_begin = value
        elif value:
            self._time_begin = time.fromisoformat(value)
        else:
            self._time_begin = None
        self._apply_time()

    def getbegintime(self) -> time|None:
        """Gibt die Uhrzeit des Beginns der Reise zurück."""
        return self._time_begin

    def setendtime(self,value:str|time|None = None):
        """Gibt die Uhrzeit des Endes der Reise zurück."""
        if type(value) == time:
            self._time_end = value
        elif value:
            self._time_end = time.fromisoformat(value)
        else:
            self._time_end = None
        self._apply_time()

    def getendtime(self) -> time|None:
        """Gibt die Uhrzeit des Endes der Reise zurück."""
        return self._time_end

    def setcardistance(self,value):
        """
        Legt die Wegstrecke fest, die während der Dienstreise
        mit einem privaten PKW zurückgelegt wurde.
        """
        distance = Decimal(value)
        if distance < 0:
            raise tools.BelowMinimumException
        else:
            self._car_distance = distance

    def getcardistance(self) -> Decimal:
        """
        Gibt die Wegstrecke zurück, die während der Dienstreise
        mit einem privaten PKW zurückgelegt wurde.
        """
        return self._car_distance
    
    def getmileage(self) -> Decimal:
        """
        Gibt die Höhe der Wegstreckenentschädigung für Fahrten
        im privaten PKW zurück.
        """
        return self.CAR_MAXRATE.min(self.CAR_RATE_PER_KM * self._car_distance)

    def setovernightflat(self,value:bool):
        """
        Legt fest, ob der Pauschalbetrag für Übernachtungen ausgezahlt wird.
        """
        self._overnight_flat = bool(value)

    def getovernightflat(self) -> bool:
        """
        Gibt zurück, ob der Pauschalbetrag für Übernachtungen ausgezahlt wird.
        """
        return self._overnight_flat
    
    def getovernightpay(self) -> Decimal:
        """
        Gibt den Geldbetrag zurück,
        der als Übernachtungspauschale ausgezahlt wird.
        """
        if not self._overnight_flat or len(self.days) < 2:
            return Decimal('0')
        return self.OVERNIGHT_MIN * (len(self.days) - 1)

    def getpositiontotal(self) -> Decimal:
        """
        Gibt den Gesamtwert aller Positionen zurück.
        """
        return sum(position.value for position in self.positions)

    def getdayallowancetotal(self) -> Decimal:
        """
        Gibt die Gesamtmenge an Tagesgeld ohne Abzüge zurück.
        """
        number_days = len(self.days)
        if number_days == 0:
            return Decimal()
        if number_days == 1:
            return self.days[0].getallowance()
        return sum (self.days[i].getallowance(i==0 or i==number_days)
                    for i in range(number_days))

    def getdaycosttotal(self) -> Decimal:
        """
        Gibt den Gesamtwert der Abzüge vom Tagesgeld zurück.
        """
        number_days = len(self.days)
        if number_days == 0:
            return Decimal()
        if number_days == 1:
            return self.days[0].getmealcost()
        return sum (self.days[i].getmealcost(i==0 or i==number_days)
                    for i in range(number_days))

    def getdaytotal(self) -> Decimal:
        """
        Gibt die Gesamtmenge an Tagesgeld zurück.
        """
        number_days = len(self.days)
        if number_days == 0:
            return Decimal()
        if number_days == 1:
            return self.days[0].getbenefits()
        return sum (self.days[i].getbenefits(i==0 or i==number_days-1)
                    for i in range(number_days))
    
    def gettotal(self) -> Decimal:
        """
        Gibt den gesamten Geldbetrag der Reisekostenabrechnung zurück.
        """
        return self.getmileage() + self.getovernightpay()\
               + self.getpositiontotal() + self.getdaytotal()

    # Properties
    username = property(getusername,setusername,None,
                        "Der Name des Aktiven.")
    usergroup = property(getusergroup,setusergroup,None,
                          "Die Arbeitsgruppe des Aktiven.")
    accountname = property(getaccountname,setaccountname,None,
                           "Der Inhaber des Überweisungskontos.")
    iban = property(getaccountiban,setaccountiban,None,
                    "Die IBAN des Überweisungskontos.")
    ibanknown = property(getibanknown,setibanknown,None,
                         "Ob die IBAN dem ADFC schon vorliegt.")
    cause = property(getcause,setcause,None,
                     "Der Grund für die Reise.")
    begindate = property(getbegindate,setbegindate,None,
                         "Das Datum, an dem die Reis begann.")
    enddate = property(getenddate,setenddate,None,
                       "Das Datum, an dem die Reise endete.")
    begintime = property(getbegintime,setbegintime,None,
                         "Die Uhrzeit, zu der die Reis begann.")
    endtime = property(getendtime,setendtime,None,
                       "Die Uhrzeit, zu der die Reise endete.")
    cardistance = property(getcardistance,setcardistance,None,
                           "Die mit dem PKW zurückgelegte Wegstrecke.")
    overnightflat = property(getovernightflat,setovernightflat,None,
                             "Ob Übernachtungspauschale ausgezahlt wird.")