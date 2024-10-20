const moneyform = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }); //wird genutzt, um Geldbeträge zu formatieren
const maxPos = 7 //Maximale Anzahl an Positionen im HTML-Dokument
var multiplier = [0,0,0,0,0,0,0];
var multiPosition = [false,false,false,false,false,false,false];
processMem = 0;

//Funktionen zur Einstellung von Variablen

function positionSetting(x,setting,evaluate=true) { //Ändere Variablen gemäß der Einstellung für Einnahme/Ausgabe für Position x
	switch(setting) {
		case true: //Einnahme
			multiplier[x-1] = 1;
			break;
		case false: //Ausgabe
			multiplier[x-1] = -1;
			break;
		default:
			multiplier[x-1] = 0;
			break;
	}
	if (evaluate) { updatePosition(x); }
}

function multiSetting(x,setting) { //Ändere Variablen gemäß der Einstellung für Multipositionen für Position x
	if (setting) {
		multiPosition[x-1] = true;
	} else {
		multiPosition[x-1] = false;
	}
	updatePosition(x);
}

//Funktionen zur Sichtbarkeit/Verwendbarkeit von HTML-Elementen

function updatePosition(x) { //Aktiviere oder deaktiviere Eingabefelder und ändere Klassen für Position x; danach calculate()
	const field = [document.getElementById("position"+x+"count"), document.getElementById("position"+x+"price"), document.getElementById("position"+x+"amount")];
	if (multiPosition[x-1]) { //Mehrfacheingabe für Position x aktiviert
		field[0].disabled = false;
		if (field[0].value == "" || field[0].value == 0) { field[0].value = 1; } //Anzahl sollte nicht leer sein, um Teilung durch Null zu vermeiden
		field[1].disabled = false;
		if (field[1].value == "") { field[1].value = Math.round( field[2].value / field[0].value * 100) / 100; }
		field[2].disabled = true;
		field[0].parentElement.classList.remove ("locked");
		field[1].parentElement.classList.remove ("locked");
	} else { //Mehrfacheingabe für Position x deaktiviert
		field[0].disabled = true;
		field[0].value = "";
		field[1].disabled = true;
		field[1].value = "";
		field[2].disabled = false;
		field[0].parentElement.classList.add ("locked");
		field[1].parentElement.classList.add ("locked");
	}
	if (multiplier[x-1] < 0) { field[2].classList.add ("negative"); } else { field[2].classList.remove ("negative"); } //Ist Position i eine Ausgabe? Dann roter Text.
	calculate();
}

function processDisplay(mode=0) { //Zeige oder verstecke Zahlungsoptionen
	const field = document.getElementById("fieldsetPayment").getElementsByTagName("section");
	const button = [document.getElementById("processtouser"), document.getElementById("processsepa"), document.getElementById("processbyuser")];
	let hide = [true,true];
	switch (mode) {
		case 1:
			hide[1] = false;
			switch (processMem) { //Stelle Wahl aus processMem wieder her
				case 0: button[0].checked = false; break;
				default: button[processMem-1].checked = true;
			}				
			break;
		case -1:
			hide[0] = false;
			button[0].checked = true;
			break;
		default:
			break;
	}
	field[1].hidden = hide[0];
	field[2].hidden = hide[1];
	field[3].hidden = hide[1];
}

function processMode(setting) { //Aktiviere oder deaktiviere Knöpfe für Angaben, ob ein SEPA-Mandat vorhanden ist
	const button = [document.getElementById("processsepaexists"), document.getElementById("processsepanew"), document.getElementById("processsepachange")];
	let disable = true;
	if (setting == 2) { disable = false; processMem = 2; } //Merke, welche Zahlungsoption gedrückt ist, in processMem
	if (setting == 3) { processMem = 3; }
	for (let i = 0; i < 3; i++) {
		button[i].disabled = disable;
	}
}
		
function ibanKnown(check) { //Zeige oder verstecke Eingabefelder zu Bankdaten
	const field = [document.getElementById("processiban"), document.getElementById("processowner")];
	if (check) {
		field[0].disabled = true;
		field[1].disabled = true;
		field[0].parentElement.classList.add ("locked");
		field[1].parentElement.classList.add ("locked");
	} else {
		field[0].disabled = false;
		field[1].disabled = false;
		field[0].parentElement.classList.remove ("locked");
		field[1].parentElement.classList.remove ("locked");
}	}

function positionDisplayInitialize(x) { //Zeige Positionen bis einschließlich x, verstecke den Rest
	for (let i = 1; i <= maxPos; i++) {
		if (i<=x) {
			positionDisplay(i);
		} else {
			positionDisplay(i,false);
		}
	}
}

function positionDisplay(x,show=true) { //Zeige oder verstecke Position x im HTML-Dokument
	document.getElementById("position"+x+"section").hidden = !(show);
}

//Funktion zur Berechnung und Anzeige des Gesamtbetrags

function calculate(notreset=true) { //Berechnung des Gesamtbetrages
	var total = 0;
	var amount = 0;

	if (notreset) {
	for (let i = 1; i <= maxPos; i++) { //Zähle alle Beträge zusammen
		const field = [document.getElementById("position"+i+"count"), document.getElementById("position"+i+"price"), document.getElementById("position"+i+"amount")];
		if (multiPosition[i-1]) { field[2].value = Math.round( field[0].value * field[1].value * 100 ) / 100; } //Falls Mengenangaben aktiviert sind, rechne den Betrag aus
		amount = field[2].value * multiplier[i-1];
		if (!(isNaN(amount))) {
			total += +amount;
		}
	}
	amount = document.getElementById("donations").value;
	if (!(isNaN(amount))) {
		total += +amount;
	}
	}
	
	//Gib den Gesamtbetrag aus und zeige passende Zahlungsoptionen an
	if (total>0.001) {
		document.getElementById("totalamount").innerHTML = "Insgesamt wurden <b>"+moneyform.format(total)+"</b> eingenommen.";
		processDisplay(1);
	} else if (total<-0.001) {
		document.getElementById("totalamount").innerHTML = "Insgesamt wurden <b class=\"negative\">"+moneyform.format(-total)+"</b> ausgegeben.";
		processDisplay(-1);
	} else {
		document.getElementById("totalamount").innerHTML = "<aside>Die Einnahmen und Ausgaben werden hier automatisch zusammengezählt.</aside>";
		processDisplay(0);
	}
}

//Beim Laden der Seite:

{	//Mach alle Elemente, die nur für das Script gedacht sind, sichtbar
	const hiddenElements = document.getElementsByClassName("scriptonly");
	for (let i = 0; i < hiddenElements.length; i++) {
		hiddenElements[i].removeAttribute("hidden");
}	}

{	//Überprüfe, welche Radio-Knöpfe und Checkboxen schon gedrückt sind, und passe Variablen und Sichtbarkeit an
for (let i = 1; i <= maxPos; i++) {
	const button = [document.getElementById("position"+i+"plus").checked, document.getElementById("position"+i+"minus").checked, document.getElementById("position"+i+"multi").checked];
	if (button[0]) {
		positionSetting(i,true,false);
	} else if (button[1]) {
		positionSetting(i,false,false);
	}
	multiSetting(i,button[2]);
}
if (document.getElementById("processuserknown").checked) { ibanKnown(true); }
if ( document.querySelector('input[name="prtype"]:checked') !== null ) {
	processMode(document.querySelector('input[name="prtype"]:checked').value); 
}
}

for (let i = maxPos; i > 0; i--) { //Überprüfe, wie viele Felder noch leer sind, und verstecke Positionen entsprechend
	const values = [document.getElementById("position"+i+"name").value, document.getElementById("position"+i+"count").value, document.getElementById("position"+i+"price").value, document.getElementById("position"+i+"amount").value];
	if (!(values[0]=="" && values[2]==0 && values[3]==0)) { //Ist schon ein Feld in Position i ausgefüllt?
		positionDisplayInitialize(i+1);
		break;
	}
	positionDisplayInitialize(1);
}
