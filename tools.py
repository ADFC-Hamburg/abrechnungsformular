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
