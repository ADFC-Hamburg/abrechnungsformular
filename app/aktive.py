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
from drafthorse.models.note import IncludedNote as DH_IncludedNote
from drafthorse.models.party import TaxRegistration as DH_TaxRegistration
from drafthorse.models.payment import PaymentTerms as DH_PaymentTerms
from schwifty import IBAN, exceptions

from . import tools, CONTACT, PATHS


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
        return (f"{self.__class__.__name__}(name={repr(self.getname())},"
               +f"unitcount={repr(self.getunitcount())},"
               +f"unitprice={repr(self.getunitprice())},"
               +f"value={repr(self.getvalue())})")
    
    def __bool__(self):
        return bool(self._name != ""
                    or self._unitprice != 0.0
                    or self._value != 0.0)
    
    # Methods for output
    def check_complete(self) -> bool:
        """Gibt zurück, ob Name und Wert vorhanden sind."""
        return bool(self.getname() and self.getvalue())

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
        Kann nicht kleiner als 1 sein.
        """
        if value < 1:
            raise tools.BelowMinimumException
        self._unitcount = int(value)
    
    def getunitcount(self) -> int:
        """Gibt die Mengenzahl der Position zurück."""
        return self._unitcount
    
    def setunitprice(self,value=0.0):
        """Legt den Preis pro Einheit der Position fest."""
        if not Decimal(value) % Decimal('0.01') == 0:
            raise tools.DecimalsException
        self._unitprice = Decimal(value)
    
    def getunitprice(self) -> Decimal:
        """Gibt den Preis pro Einheit der Position zurück."""
        return self._unitprice
    
    def setvalue(self,value=0.0):
        """
        Legt den Gesamtpreis der Position fest.
        Einnahmen sind positiv, Ausgaben negativ.
        """
        if not Decimal(value) % Decimal('0.01') == 0:
            raise tools.DecimalsException
        self._value = Decimal(value)
    
    def getvalue(self) -> Decimal:
        """
        Gibt den Gesamtpreis der Position zurück.
        Bei vorhandendem Stückpreis wird der
        gespeicherte Gesamtpreis ignoriert.
        """
        if self._unitprice != 0:
            return Decimal(self._unitprice * self._unitcount)
        return self._value
    
    def setminusvalue(self,value=0.0):
        """
        Legt den Gesamtpreis der Position fest.
        Ausgaben sind positiv, Einnahmen negativ.
        """
        if not Decimal(value) % Decimal('0.01') == 0:
            raise tools.DecimalsException
        self._value = Decimal(value*-1)
    
    def getincome(self) -> Decimal:
        """
        Gibt die Gesamteinnahmen der Position zurück.
        Bei Ausgaben wird Null zurückgegeben.
        """
        return max(Decimal(0.0), self.getvalue())
    
    def getcost(self) -> Decimal:
        """
        Gibt die Gesamtausgaben der Position zurück.
        Bei Einnahmen wird Null zurückgegeben.
        """
        return max(Decimal(0.0), self.getvalue()*-1)
    
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
    complete = property(check_complete,None,None,
        "Ob Name und Wert vorhanden sind.")


class Abrechnung:
    """
    Beschreibt eine Aktivenabrechnung für den ADFC.
    Beinhaltet 7 Objekte der Klasse Position im Tupel positions.
    """
    
    # Class constants
    POSITIONCOUNT = 7

    _MODES_IBAN = (1,2,3)
    _MODES_SEPA = (1,2,3)
    _NAME = "Aktivenabrechnung"
    _POSITION_NAMES = ('erste','zweite','dritte','vierte',
                       'fünfte','sechste','siebte')
    _FIELD_NAMES = {'uname':'dein Name','group':'deine Arbeitsgruppe',
                    'pname':'der Name des Projekts oder der Aktion',
                    'pdate':'das Datum des Projekts oder der Aktion',
                    'dono':'die Summe der eingenommenen Spenden',
                    'iban':'deine IBAN',
                    'owner':'der Name des Kontoinhabers/der Kontoinhaberin',
                    'prtype':'die Art der Zahlungsabwicklung',
                    'prsepa':'der Stand des SEPA-Mandats'}
    _FIELD_ERRORS = {'pos':'Mindestend eine Position oder die Summe'
                     +' der Spenden muss ausgefüllt sein.',
                     'length':'Die IBAN muss die korrekte Länge haben'
                     +' (22 Zeichen bei einer deutschen IBAN).',
                     'checksum':'Die IBAN muss gültig sein.'
                     +' (Wahrscheinlich liegt ein Tippfehler vor.)'}

    # Dunder methods
    def __init__(self):
        """
        Initialisiert ein Objekt der Klasse Abrechnung.
        """
        
        self.positions = self._create_positions(self.POSITIONCOUNT)
        
        self._user = {"name": "", "group": ""}
        self._project = {"name": "", "date": None}
        self._donations = Decimal(0.0)
        self._payment = {"ibanmode": None, "sepamode": None,
                         "ibanknown": False, "iban": IBAN("",allow_invalid=True),
                         "name": ""}
    
    def __str__(self) -> str:
        """
        Gibt den Abrechnungsbetrag zurück.
        """
        return tools.euro(self.gettotal())

    def __bool__(self) -> bool:
        """
        Gibt True zurück, falls eine Position einen Wert hat
        oder eine Spendensumme angegeben wurde.
        """
        for position in self.positions:
            if position:
                return True
        return bool(self.donations)

    # Part of initialization
    def _create_positions(self,amount:int) -> tuple[Position]:
        """
        Gibt einen Tupel aus neuen Positionen zurück.
        """
        out = []
        for i in range(amount):
            out.append(Position())
        return tuple(out)

    # Methods for input
    def evaluate_query(self,query:dict) -> str:
        """
        Liest Parameter aus einem HTML-Query in Form eines Dictionary
        ein und setzt alle Variablen auf den entsprechenden Wert.

        Gibt außerdem eine Aufzählung aller Fehler als String zurück.

        Erkennt die folgenden Schlüssel:
        uname, dept, pname, pdate, p1name, p1type, p1cnt, p1ppu, p1,
        p2name, p2type, p2cnt, p2ppu, p2, p3name, p3type, p3cnt, p3ppu,
        p3, p4name, p4type, p4cnt, p4ppu, p4, p5name, p5type, p5cnt,
        p5ppu, p5, p6name, p6type, p6cnt, p6ppu, p6, p7name, p7type,
        p7cnt, p7ppu, p7, dono, prtype, known, iban, owner, prsepa
        """
        if query:
            keys = tuple(query.keys())
            missing = []
            erronous = []
            erronous_positions = []
            incomplete_positions = []
            below_minimum = []
            not_currency = []
            dono_error = None
            errormessage = []

            def check_missing(value,name:str):
                """Check if a value exists. If it does not, add an entry
                to the list of missing values."""
                if not value:
                    missing.append(name)
            
            # User name and -group, project name and date
            if 'uname' in keys:
                self.setusername(query['uname'])
            if 'dept' in keys:
                self.setusergroup(query['dept'])
            if 'pname' in keys:
                self.setprojectname(query['pname'])
            if 'pdate' in keys:
                try:
                    self.setprojectdate(query['pdate'])
                except:
                    erronous.append(self._FIELD_NAMES['pdate'])
            
            check_missing(self.getusername(),self._FIELD_NAMES['uname'])
            check_missing(self.getusergroup(),self._FIELD_NAMES['group'])
            check_missing(self.getprojectname(),self._FIELD_NAMES['pname'])
            check_missing(self.getprojectdate(),self._FIELD_NAMES['pdate'])
            
            # Position values
            for i in range(self.POSITIONCOUNT):
                pos = 'p'+str(i+1)
                if pos+'type' in keys and not query[pos+'type'] in {'0',''}:
                    if not query[pos+'type'] in {'1','-1'}:
                        erronous_positions.append(self._POSITION_NAMES[i])
                        continue
                    # Position is set to income or cost
                    try:
                        if pos+'cnt' in keys and pos+'ppu' in keys\
                        and query[pos+'cnt'] and query[pos+'ppu']:
                            # Position has amount and price per unit
                            self.positions[i].setunitcount(int(query[pos+'cnt']))
                            amount = Decimal(query[pos+'ppu'])
                            if amount < 0:
                                raise tools.BelowMinimumException
                            amount *= Decimal(query[pos+'type'])
                            self.positions[i].setunitprice(amount)
                        elif pos in keys and query[pos]:
                            # Position has a set value
                            amount = Decimal(query[pos])
                            if amount < 0:
                                raise tools.BelowMinimumException
                            amount *= Decimal(query[pos+'type'])
                            self.positions[i].setvalue(amount)
                    except tools.BelowMinimumException:
                        below_minimum.append(self._POSITION_NAMES[i])
                        continue
                    except tools.DecimalsException:
                        not_currency.append(self._POSITION_NAMES[i])
                        continue
                    except:
                        erronous_positions.append(self._POSITION_NAMES[i])
                        continue
                    if pos+'name' in keys:
                        # Set position name
                        self.positions[i].setname(query[pos+'name'])
                    if self.positions[i] and not self.positions[i].complete:
                        incomplete_positions.append(self._POSITION_NAMES[i])
            
            # Donation value
            if 'dono' in keys and query['dono']:
                try:
                    self.setdonations(query['dono'])
                except tools.BelowMinimumException:
                    dono_error = tools.BelowMinimumException
                except tools.DecimalsException:
                    dono_error = tools.DecimalsException
                except:
                    erronous.append(self._FIELD_NAMES['dono'])
            
            # Error if no position filled in
            if not self and not erronous_positions and not incomplete_positions\
            and not below_minimum and not not_currency\
            and not self._FIELD_NAMES['dono'] in erronous:
                errormessage.append(self._FIELD_ERRORS['pos'])
            
            # Payment information
            if 'prtype' in keys and query['prtype']:
                try:
                    self.setibanmode(query['prtype'])
                except:
                    erronous.append(self._FIELD_NAMES['prtype'])
                if query['prtype'] == '1':
                    # Payment mode: Transfer to user
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
                elif query['prtype'] == '2':
                    # Payment mode: debit from user
                    if 'prsepa' in keys and query['prsepa']:
                        self.setsepamode(query['prsepa'])
                    else:
                        missing.append(self._FIELD_NAMES['prsepa'])
                if (self.getibanmode() == 1 and self.gettotal() >= 0)\
                or (self.getibanmode() in (2,3) and self.gettotal() <= 0):
                    erronous.append(self._FIELD_NAMES['prtype'])
            elif self.gettotal() != 0:
                missing.append(self._FIELD_NAMES['prtype'])
            
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
            if below_minimum or dono_error is tools.BelowMinimumException:
                message = ""
                if dono_error is tools.BelowMinimumException:
                    message = self._FIELD_NAMES['dono']
                    if below_minimum:
                        message += ' sowie '
                if below_minimum:
                    message += 'die ' + tools.write_list_de(below_minimum)
                    message += ' Position'
                if below_minimum and dono_error is tools.BelowMinimumException:
                    message += ' dürfen'
                else:
                    message += ' darf'
                message += ' keine negativen Werte enthalten.'
                errorstart.append(tools.uppercase_first(message))
            if not_currency or dono_error is tools.DecimalsException:
                message = ""
                if dono_error is tools.DecimalsException:
                    message = self._FIELD_NAMES['dono']
                    if not_currency:
                        message += ' sowie '
                if not_currency:
                    message += 'die ' + tools.write_list_de(not_currency)
                    message += ' Position'
                if not_currency and dono_error is tools.DecimalsException:
                    message += ' müssen'
                else:
                    message += ' muss'
                message += ' ganze Centbeträge enthalten.'
                errorstart.append(tools.uppercase_first(message))
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
        if self.getprojectname():
            # Add project name without special characters
            out += " "+sub('[^A-Za-zÄÖÜäöüß0-9\\-_ ]','',
                           self.getprojectname())
        if self.getprojectdate():
            # Add project date
            out += " "+str(self.getprojectdate())
        return out

    def html_compose(self) -> str:
        """
        Liest eine HTML-Vorlage ein und erstellt dann aus dieser
        fertig ausgefüllte Abrechnungsformulare im HTML-Format.
        """

        template = tools.pdf_environment.get_template(PATHS.AKTIVE_HTML)
        today = format_date(date.today(),format='long',locale='de_DE')

        return template.render(abrechnung=self,today=today)

    def factur_x(self) -> bytes:
        """
        Erstellt aus der Abrechnung eine E-Rechnung,
        die dem Standard Factur-X Extended (auch bekannt als
        ZUGFeRD Extended) entspricht. Diese wird als binäre
        XML-Datei zurückgegeben.
        """

        # General information
        doc = DH_Document()
        doc.context.guideline_parameter.id = "urn:cen.eu:en16931:2017#conformant#urn:factur-x.eu:1p0:extended"
        doc.header.id = "AKTIVE"+datetime.now().strftime("%Y%m%d%H%M%S")
        doc.header.name = self._NAME.upper()
        doc.header.issue_date_time = date.today()
        doc.header.languages.add("de")
        doc.header.type_code = "380" # Commercial invoice

        if self.getprojectname():
            note = DH_IncludedNote()
            note.content_code = 'PROJECT'
            datestring = format_date(self.getprojectdate(),
                                     format="long",locale="de_DE")
            note.content.add(self.getprojectname()+" "+datestring)
            note.subject_code = "ACD" # Reason
            doc.header.notes.add(note)

        if self.getprojectname() == 'Testrechnung':
            doc.context.test_indicator = True

        # Determine seller and buyer
        if self.gettotal() > 0:
            mode = 1
            adfc = doc.trade.agreement.seller
            user = doc.trade.agreement.buyer
        else:
            mode = -1
            adfc = doc.trade.agreement.buyer
            user = doc.trade.agreement.seller

        # Seller information
        adfc.name = CONTACT['Name']
        adfc.address.line_one = CONTACT['LineOne']
        if 'LineTwo' in CONTACT.keys():
            adfc.address.line_two = CONTACT['LineTwo']
        if 'LineThree' in CONTACT.keys():
            adfc.address.line_three = CONTACT['LineThree']
        adfc.address.postcode = CONTACT['PostCode']
        adfc.address.city_name = CONTACT['City']
        #adfc.address.country_subdivision = CONTACT['State']
        adfc.address.country_id = CONTACT['Country']

        tr = DH_TaxRegistration()
        tr.id = ("VA",CONTACT['VAT']) # FC == Tax number, VA == VAT Number
        adfc.tax_registrations.add(tr)
        user.tax_registrations.add(tr)

        # Buyer information
        user.name = self.getusername()
        user.description = self.getusergroup()
        user.address.line_one = "c/o " + CONTACT['Name']
        user.address.line_two = CONTACT['LineOne']
        if 'LineTwo' in CONTACT.keys():
            user.address.line_three = CONTACT['LineTwo']
        user.address.postcode = CONTACT['PostCode']
        user.address.city_name = CONTACT['City']
        #user.address.country_subdivision = CONTACT['State']
        user.address.country_id = CONTACT['Country']

        # Positions
        for index in range(self.POSITIONCOUNT):
            position = self.positions[index]
            if not position:
                continue
            li = tools.TaxExemptLineItem()
            li.document.line_id = str(index+1)
            li.product.name = position.getname()
            li.agreement.net.amount = Decimal(abs(position.getunitprice()) or abs(position.getvalue()))
            count = Decimal(position.getunitcount() * mode)
            if position.getcost():
                count = -count
            li.agreement.net.basis_quantity = (count, "H87")  # H87 == Item
            li.delivery.billed_quantity = (count, "H87")  # H87 == Item
            li.settlement.monetary_summation.total_amount = Decimal(position.getvalue() * mode)
            doc.trade.items.add(li)

        if self.getdonations():
            li = tools.TaxExemptLineItem()
            li.document.line_id = "SP"
            li.product.name = "Spenden"
            li.agreement.net.amount = Decimal(self.getdonations())
            li.agreement.net.basis_quantity = (Decimal(mode), "H87")  # H87 == Item
            li.delivery.billed_quantity = (Decimal(mode), "H87")  # H87 == Item
            li.settlement.monetary_summation.total_amount = Decimal(self.getdonations() * mode)
            doc.trade.items.add(li)
        
        # Payment information
        if mode == 1:
            doc.trade.settlement.payment_means.payee_account.account_name = CONTACT['AccName']
            doc.trade.settlement.payment_means.payee_account.iban = CONTACT['IBAN']
            doc.trade.settlement.payment_means.payee_institution.bic = CONTACT['BIC']
        else:
            doc.trade.settlement.payment_means.payer_account.iban = CONTACT['IBAN']
        
        term = DH_PaymentTerms()

        if self.getibanmode() == 1 and self.gettotal() < 0:
            # Refund via bank transfer
            doc.trade.settlement.payment_means.type_code = "42" # Payment to bank account
            term.description = "Wir überweisen den Abrechnungsbetrag auf dein Konto."
            if self.getibanknown():
                doc.trade.settlement.payment_means.information.add(f"Meine Bankverbindung ist dem {CONTACT['NameShort']} bekannt.")
            else:
                doc.trade.settlement.payment_means.payee_account.iban = self.getaccountiban()
                if self.getaccountname():
                    doc.trade.settlement.payment_means.payee_account.account_name = self.getaccountname()
        elif self.getibanmode() == 2 and self.gettotal() > 0:
            doc.trade.settlement.payment_means.type_code = "59" # SEPA direct debit
            term.description = "Wir ziehen den Abrechnungsbetrag per SEPA-Lastschrift ein."
            if self.getsepamode() in (2,3):
                if self.getsepamode() == 2:
                    doc.trade.settlement.payment_means.information.add("Ein SEPA-Mandat liegt noch nicht vor.")
                else:
                    doc.trade.settlement.payment_means.information.add("Das vorliegende SEPA-Mandat ist veraltet.")
                note = DH_IncludedNote()
                note.content_code = "SEPA"
                note.content.add("Bitte senden Sie mir ein SEPA-Mandatsformular zu.")
                note.subject_code = "AAI" # General information
                doc.header.notes.add(note)
        elif self.getibanmode() == 3 and self.gettotal() > 0:
            term.description = "Du überweist den Abrechnungsbetrag selbst."
            doc.trade.settlement.payment_means.type_code = "42" # Payment to bank account
        else:
            # Fallback if none of the above applies
            doc.trade.settlement.payment_means.type_code = "ZZZ" # Mutually defined
        
        doc.trade.settlement.terms.add(term)

        # Tax
        total = Decimal(abs(self.gettotal()))

        trade_tax = DH_ApplicableTradeTax()
        trade_tax.calculated_amount = Decimal("0.00")
        trade_tax.basis_amount = total
        trade_tax.type_code = "VAT"
        trade_tax.category_code = 'E' # Exempt from tax
        trade_tax.exemption_reason = "Vereinsinterne Abrechnung"
        trade_tax.rate_applicable_percent = Decimal("0.00")
        doc.trade.settlement.trade_tax.add(trade_tax)

        # Total
        doc.trade.settlement.currency_code = "EUR"
        doc.trade.settlement.monetary_summation.line_total = total
        doc.trade.settlement.monetary_summation.charge_total = Decimal("0.00")
        doc.trade.settlement.monetary_summation.allowance_total = Decimal("0.00")
        doc.trade.settlement.monetary_summation.tax_basis_total = total
        doc.trade.settlement.monetary_summation.tax_total = (Decimal("0.00"),"EUR")
        doc.trade.settlement.monetary_summation.grand_total = total
        doc.trade.settlement.monetary_summation.due_amount = total

        return doc.serialize(schema="FACTUR-X_EXTENDED")

    # Variable getters and setters
    def setusername(self,value:str = ""):
        """Legt den Namen des/der Aktiven fest."""
        self._user["name"] = str(value).strip()
    
    def getusername(self) -> str:
        """Gibt den Namen des/der Aktiven zurück."""
        return self._user["name"]
    
    def setusergroup(self,value:str = ""):
        """Legt die Gruppe des/der Aktiven fest."""
        self._user["group"] = str(value).strip()
    
    def getusergroup(self) -> str:
        """Gibt die Gruppe des/der Aktiven zurück."""
        return self._user["group"]
    
    def setprojectname(self,value:str = ""):
        """Legt den Namen des Projekts fest."""
        self._project["name"] = str(value).strip()
    
    def getprojectname(self) -> str:
        """Gibt den Namen des Projekts zurück."""
        return self._project["name"]
    
    def setprojectdate(self,value:str|date|None = None):
        """
        Legt das Datum der Abrechnung fest.

        Akzepiert Datums-Objekte oder
        Strings im Format (year-month-day)
        """
        if type(value) == date:
            self._project["date"] = value
        elif value:
            temp = str(value).split("-")
            self._project["date"] = date(
                int(temp[0]), int(temp[1]), int(temp[2]))
        else:
            self._project["date"] = None
    
    def getprojectdate(self) -> date|None:
        """Gibt das Datum der Abrechnung zurück."""
        return self._project["date"]
    
    def setdonations(self,value=0.0):
        """Legt den Betrag eingenommener Spenden fest."""
        if Decimal(value) < 0:
            raise tools.BelowMinimumException
        if not Decimal(value) % Decimal('0.01') == 0:
            raise tools.DecimalsException
        self._donations = Decimal(value)
    
    def getdonations(self) -> Decimal:
        """Gibt den Betrag eingenommener Spenden zurück."""
        return self._donations
    
    def getincome(self) -> Decimal:
        """Gibt den Gesamtbetrag der Einnahmen zurück."""
        out = Decimal(0.0)
        for i in range(self.POSITIONCOUNT):
            out += self.positions[i].income
        out += self.getdonations()
        return out

    def getcost(self) -> Decimal:
        """Gibt den Gesamtbetrag der Ausgaben zurück."""
        out = Decimal(0.0)
        for i in range(self.POSITIONCOUNT):
            out += self.positions[i].cost
        return out
    
    def gettotal(self) -> Decimal:
        """Gibt den Betrag der Einnahmen minus Ausgaben zurück."""
        out = Decimal(0.0)
        for i in range(self.POSITIONCOUNT):
            out += self.positions[i].value
        out += self.getdonations()
        return out
    
    def setaccountname(self,name:str = ""):
        """Legt den Namen des Kontoinhabers fest."""
        self._payment["name"] = str(name).strip()
    
    def getaccountname(self) -> str:
        """Gibt den Namen des Kontoinhabers zurück."""
        return self._payment["name"]
    
    def setaccountiban(self,value):
        """
        Verifiziert die angegebene IBAN
        und legt sie als Überweisungskonto fest.
        """
        if value:
            self._payment["iban"] = IBAN(str(value))
        else:
            self._payment["iban"] = IBAN('', allow_invalid = True)
    
    def getaccountiban(self,spaces:bool = True) -> str:
        """Gibt die IBAN des Bankkontos zurück."""
        return self._payment["iban"].formatted if spaces else str(self._payment["iban"])

    def setibanmode(self,mode=None):
        if mode and int(mode) in self._MODES_IBAN:
            self._payment["ibanmode"] = int(mode)
        else:
            raise tools.IllegalValueException
    
    def getibanmode(self) -> int|None:
        return self._payment["ibanmode"]
    
    def setsepamode(self,mode):
        if mode and int(mode) in self._MODES_SEPA:
            self._payment["sepamode"] = int(mode)
        else:
            raise tools.IllegalValueException

    def getsepamode(self) -> int|None:
        return self._payment["sepamode"]

    def setibanknown(self,mode=False):
        self._payment["ibanknown"] = bool(mode)
    
    def getibanknown(self) -> bool:
        return self._payment["ibanknown"]

    # Properties
    username = property(getusername,setusername,None,
                        "Der Name des/der Aktiven.")
    usergroup = property(getusergroup,setusergroup,None,
                         "Der Arbeitsbereich des/der Aktiven.")
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
                           "Name des Inhabers/der Inhaberin des Bankkontos.")
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