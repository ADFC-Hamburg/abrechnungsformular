"""
Sammelmodul für diverse Funktionen, die im Ausgabeprogramm
der Aktivenabrechnung zum Einsatz kommen.
"""

from babel.numbers import format_currency

class BelowMinimumException(Exception):
    pass

class DecimalsException(Exception):
    pass

class IllegalValueException(Exception):
    pass

def cell(value = "", classes="") -> str:
    """
    Gibt eine Tabellenzelle im HTML-Format (td-Tag) zurück.
    """
    out = "<td"
    if type(classes) in (list,tuple):
        out += " class=\""+" ".join(classes)+"\""
    elif classes:
        out += f" class=\"{str(classes)}\""
    out += f">{str(value)}</td>"
    return out

def euro(value = 0, empty = False) -> str:
    """
    Gibt eine Zahl als Eurobetrag zurück.
    Ist empty True, wird statt 0,00 € ein leerer String zurückgegeben.
    """
    if empty and value == 0:
        return ""
    return format_currency(value,"EUR",locale="de_DE")

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
