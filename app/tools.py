"""
Sammelmodul für diverse Funktionen, die im Ausgabeprogramm
der Aktivenabrechnung zum Einsatz kommen.
"""

from decimal import Decimal

from babel.dates import format_date, format_time
from drafthorse.models.tradelines import LineItem
from jinja2 import Environment, FileSystemLoader, select_autoescape

from . import CONTACT, PATHS, VERSION


class BelowMinimumException(Exception):
    pass

class DecimalsException(Exception):
    pass

class IllegalValueException(Exception):
    pass

class TaxExemptLineItem(LineItem):
    """Drafthorse line item with tax exemption."""
    def __init__(self):
        super().__init__()
        self.settlement.trade_tax.type_code = "VAT"
        self.settlement.trade_tax.category_code = 'E' # Exempt from tax
        self.settlement.trade_tax.rate_applicable_percent = Decimal()


def checkbox(checked) -> str:
    """
    Gibt eine Checkbox als HTML-Zeichen zurück.

    Parameter:
    checked     Ob die Checkbox ein Häckchen haben soll.
    """
    return "&#9746;" if bool(checked) else "&#9744;"

def euro(value = 0, empty = False, shorten = False) -> str:
    """
    Gibt eine Zahl als Eurobetrag zurück.

    Ist empty True, wird statt 0,00 € ein leerer String zurückgegeben.

    Ist shorten True, werden Nachkommastellen von Ganzbeträgen abgeschnitten.
    """
    if empty and not value:
        return ""
    out = format_decimal(value,2,False) + u'\N{no-break space}\N{euro sign}'
    if shorten:
        out = out.removesuffix(',00')
    return out

def format_decimal(number, decimals:int = 3, shorten = False) -> str:
    """
    Gibt eine Zahl als String mit Tausendtrennerpunkten und
    Dezimalkomma zurück.

    decimals legt die Anzahl der Nachkommastellen fest; ist shorten
    True, werden Nullen am Ende des Bruchteils entfernt.
    """
    DECIMAL_SEPARATOR = ','
    out = format(Decimal(number),f'.{str(decimals)}f').split('.')
    out[0] = format_digits(out[0])
    if shorten and len(out) > 1:
        out[1] = out[1].rstrip('0')
        if out[1] == '': out.pop(1)
    return DECIMAL_SEPARATOR.join(out)

def format_digits(number) -> str:
    """
    Gibt eine Ganzzahl als String mit Tausendtrennerpunkten zurück.
    """
    DIGIT_GROUP_SEPARATOR = '.'
    DIGIT_GROUP_LENGTH = 3
    out = format(Decimal(number),'.0f')
    if len(out) > DIGIT_GROUP_LENGTH:
        for i in range(len(out)-DIGIT_GROUP_LENGTH,0,-DIGIT_GROUP_LENGTH):
            out = out[:i] + DIGIT_GROUP_SEPARATOR + out[i:]
    return out

def uppercase_first(text:str) -> str:
    """
    Gibt den angegebenen String mit dem ersten Buchstaben
    als Großbuchstaben zurück.
    """
    return text[0].upper() + text[1:]

def write_list_de(list:list[str]) -> str:
    """
    Gibt alle Einträge der angegebenen Liste als einen String zurück,
    getrennt durch Kommas und einem "und".
    """
    text = ''
    if len(list) > 1:
        text = ', '.join(list[:-1]) + ' und '
    if list:
        text += list[-1]
    return text


pdf_environment = Environment(loader=FileSystemLoader(PATHS.PDF_TEMPLATE_FOLDER),
                              autoescape=True)
pdf_environment.globals.update(address=CONTACT,checkbox=checkbox,euro=euro,
                               format_date=format_date,format_decimal=format_decimal,
                               format_time=format_time,version=VERSION)
