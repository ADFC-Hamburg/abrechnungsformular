const moneyform = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }); // wird genutzt, um Geldbeträge zu formatieren
const maxPos = 7 // Maximale Anzahl an Positionen im HTML-Dokument
var multiplier = [0,0,0,0,0,0,0];
var multiPosition = [false,false,false,false,false,false,false];
var processMem = 0;

// Funktionen zur Einstellung von Variablen

/**
 * Ändere den Multiplikator (Variable multiplier) für Position x.
 * 
 * Wird im HTML-Dokument von den Radio-Tasten aufgerufen, mit denen
 * Einnahme oder Ausgabe gewählt wird.
 *  
 * @param {number} x 			Die Position, die geändert wird
 * @param {boolean} setting 	true für Einnahme, false für Ausgabe
 * @param {boolean} [evaluate]	Ob updatePosition ausgeführt wird; Standardmäßig true
 */
function positionSetting(x,setting,evaluate=true) { 
	switch(setting) {
		case true:
			// Einnahme
			multiplier[x-1] = 1;
			break;
		case false:
			// Ausgabe
			multiplier[x-1] = -1;
			break;
		default:
			multiplier[x-1] = 0;
			break;
	}
	if (evaluate) { updatePosition(x); }
}

/**
 * Legt fest, ob Position x eine Mehrfachposition ist; danach updatePosition
 * @param {number} x		Die Position, die geändert wird
 * @param {boolean} setting	Ob x eine Mehrfachposition ist
 */
function multiSetting(x,setting) {
	if (setting) {
		multiPosition[x-1] = true;
	} else {
		multiPosition[x-1] = false;
	}
	updatePosition(x);
}

// Funktionen zur Sichtbarkeit/Verwendbarkeit von HTML-Elementen

/**
 * Aktualisiere Eingabefelder und ändere Klassen für Position x.
 * 
 * @param {number} x	Die Position, die geändert wird
 */
function updatePosition(x) {
	const field = [document.getElementById("position"+x+"count"), document.getElementById("position"+x+"price"), document.getElementById("position"+x+"amount")];
	if (field[0].value == "" || field[0].value == 0) {
		// Anzahl sollte nicht leer sein, um Teilung durch Null zu vermeiden
		field[0].value = 1;
	}
	if (multiPosition[x-1]) {
		// Mehrfacheingabe für Position x aktiviert
		field[2].value = Math.round( field[0].value * field[1].value * 100 ) / 100;
	} else {
		// Mehrfacheingabe für Position x deaktiviert
		field[1].value = "";
	}
	// Ist Position x eine Ausgabe? Dann roter Text.
	if (multiplier[x-1] < 0) {
		field[1].classList.add ("negative");
		field[2].classList.add ("negative");
	} else {
		field[1].classList.remove ("negative");
		field[2].classList.remove ("negative");
	}
}

/**
 * Zeige oder verstecke Zahlungsoptionen
 * @param {number} mode	1 für Gesamteinnahmen, -1 für Gesamtausgaben, andere Werte verstecken alles
 */
function processDisplay(mode=0) {
	const field = document.getElementById("fieldsetPayment").getElementsByTagName("section");
	const button = [document.getElementById("processtouser"), document.getElementById("processsepa"), document.getElementById("processbyuser")];
	let hide = [true,true];
	switch (mode) {
		case 1:
			// Einnahmen
			hide[1] = false;
			switch (processMem) {
				// Stelle Wahl aus processMem wieder her
				case 0: button[0].checked = false; break;
				default: button[processMem-1].checked = true;
			}				
			break;
		case -1:
			// Ausgaben
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

/**
 * Aktiviere oder deaktiviere Knöpfe für Angaben, ob ein SEPA-Mandat
 * vorhanden ist, abhängig davon, welche Zahlungsart gewählt wurde.
 * 
 * Wird im HTML-Dokument von den Radio-Tasten aufgerufen, mit denen
 * die Überweisungsmethode gewählt wird.
 * 
 * @param {number} setting	Welche Zahlungsoption gewählt wurde
 */
function processMode(setting) {
	const button = [document.getElementById("processsepaexists"), document.getElementById("processsepanew"), document.getElementById("processsepachange")];
	let disable = true;
	// Merke, welche Zahlungsoption gedrückt ist, in processMem
	if (setting == 2) { disable = false; processMem = 2; } 
	if (setting == 3) { processMem = 3; }
	for (let i = 0; i < 3; i++) {
		button[i].disabled = disable;
	}
}

/**
 * Sperre oder entsperre Eingabefelder zu Bankdaten (IBAN und Inhaber)
 * 
 * Wird im Dokument von der Checkbox aufgerufen, die wählt, ob die
 * IBAN dem ADFC schon bekannt ist.
 * 
 * @param {boolean} check	Ob Eingabefelder gesperrt sein sollen
 */
function ibanKnown(check) {
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

/**
 * Zeige Eingabefelder für die ersten x Positionen und verstecke den Rest.
 * 
 * Wird im Dokument vom Reset-Knopf aufgerufen.
 * 
 * @param {number} x	Die letzte anzuzeigende Position
 */
function positionDisplayInitialize(x) {
	for (let i = 1; i <= maxPos; i++) {
		if (i<=x) {
			positionDisplay(i);
		} else {
			positionDisplay(i,false);
		}
	}
}

/**
 * Zeige oder verstecke die Eingabefelder für Position x
 * 
 * Wird im Dokument von Eingabefeldern für Positionsname, -Anzahl,
 * -Stückpreis und -Betrag aufgerufen.
 * 
 * @param {number} x		Die fragliche Position
 * @param {boolean} show	Ob die Position angezeigt werden soll
 */
function positionDisplay(x,show=true) { //Zeige oder verstecke Position x im HTML-Dokument
	document.getElementById("position"+x+"section").hidden = !(show);
}

// Funktion zur Berechnung und Anzeige des Gesamtbetrags

/**
 * Berechne den Gesamtbetrag und gib ihn aus.
 * 
 * Wird im Dokument von allen Geld- und Anzahlfeldern sowie vom
 * Reset-Knopf aufgerufen.
 * 
 * @param {boolean} [notreset]	Falls false: Ergebnis ist 0
 */
function calculate(notreset=true) {
	var total = 0;
	var amount = 0;

	if (notreset) {
	for (let i = 1; i <= maxPos; i++) {
		// Zähle alle Beträge zusammen
		const field = [document.getElementById("position"+i+"count"), document.getElementById("position"+i+"price"), document.getElementById("position"+i+"amount")];

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
	
	// Gib den Gesamtbetrag aus und zeige passende Zahlungsoptionen an
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

// Beim Laden der Seite:

/*
// Mach alle Elemente, die nur für das Script gedacht sind, sichtbar
const hiddenElements = document.getElementsByClassName("scriptonly");
for (let i = 0; i < hiddenElements.length; i++) {
	hiddenElements[i].removeAttribute("hidden");
}	
*/

// Setze spätestes erlaubtes Datum auf heute
document.getElementById("projectdate").max = new Date().toISOString().split("T")[0];
	
// Überprüfe, welche Radio-Knöpfe und Checkboxen schon gedrückt sind, und passe Variablen und Sichtbarkeit an
for (let i = 1; i <= maxPos; i++) {
	const button = [document.getElementById("position"+i+"plus").checked, document.getElementById("position"+i+"minus").checked];
	// Überprüfe, wo bereits zwischen Einnahme und Ausgabe gewählt wurde
	if (button[0]) {
		positionSetting(i,true,false);
	} else if (button[1]) {
		positionSetting(i,false,false);
	}

	// Überprüfe, welche Positionen einen Stückpreis haben
	if ( document.getElementById("position"+i+"price").value > 0) {
		multiSetting(i,true);
	} else {
		multiSetting(i,false);
	}

	// Berechne den aktuellen Gesamtbetrag.
	calculate();
}
if (document.getElementById("processuserknown").checked) {
	ibanKnown(true);
}
if ( document.querySelector('input[name="prtype"]:checked') !== null ) {
	// Eine Zahlungsoption wurde bereits ausgewählt
	processMode(document.querySelector('input[name="prtype"]:checked').value); 
}

for (let i = maxPos; i > 0; i--) {
	// Überprüfe, welche Felder noch leer sind, und verstecke Positionen entsprechend
	const values = [document.getElementById("position"+i+"name").value, document.getElementById("position"+i+"count").value, document.getElementById("position"+i+"price").value, document.getElementById("position"+i+"amount").value];
	if (!(values[0]=="" && values[2]==0 && values[3]==0)) {
		// Ein Feld in Position i ist bereits ausgefüllt
		positionDisplayInitialize(i+1);
		break;
	}
	positionDisplayInitialize(1);
}
