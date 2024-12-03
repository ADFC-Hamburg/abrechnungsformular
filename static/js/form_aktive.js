const moneyform = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }); // wird genutzt, um Geldbeträge zu formatieren
const maxPos = 7 // Maximale Anzahl an Positionen im HTML-Dokument
var multiplier = [1,1,1,1,1,1,1];
var multiPosition = [false,false,false,false,false,false,false];
var processMem = 0;

// Funktionen zur Einstellung von Variablen

/**
 * Ändere den Multiplikator (Variable multiplier) für Position x.
 * 
 * Zum Aufruf durch Radio-Tasten,
 * mit denen Einnahme oder Ausgabe gewählt wird.
 *  
 * @param {number} x 			Die Position, die geändert wird
 * @param {boolean} setting 	true für Einnahme, false für Ausgabe
 * @param {boolean} [evaluate]	Ob updatePosition und calculate ausgeführt werden; Standardmäßig true
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
	if (evaluate) {
		updatePosition(x);
		calculate();
	}
}

/**
 * Legt fest, ob Position x eine Mehrfachposition ist;
 * danach updatePosition
 * 
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
	// Should IBAN field be disabled?
	if (hide[0] || document.getElementById("processuserknown").checked) {
		ibanLock(true);
	} else {
		ibanLock(false);
	}
	// Zeige und verstecke Zahlungsoptionen
	field[1].hidden = hide[0];
	field[2].hidden = hide[1];
	field[3].hidden = hide[1];
}

/**
 * Aktiviere oder deaktiviere Knöpfe für Angaben, ob ein SEPA-Mandat
 * vorhanden ist, abhängig davon, welche Zahlungsart gewählt wurde.
 * 
 * Zum Aufruf durch Radio-Tasten,
 * mit denen die Überweisungsmethode gewählt wird.
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
		button[i].parentElement.classList.toggle ("locked",disable);
	}
}

/**
 * Sperre oder entsperre Eingabefelder zu Bankdaten (IBAN und Inhaber)
 * 
 * Zum Aufruf durch die Checkbox, die wählt,
 * ob die IBAN dem ADFC schon bekannt ist.
 * 
 * @param {boolean} check	Ob Eingabefelder gesperrt sein sollen
 */
function ibanLock(check) {
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
 * Zum Aufruf durch Eingabefelder für Positionsname, -Anzahl,
 * -Stückpreis und -Betrag.
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
 * Zum Aufruf durch alle Geld- und Anzahlfelder.
 */
function calculate() {
	var total = 0;
	var amount = 0;

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

// Funktionen zur Validierung

/**
 * Überprüft ein Zahleneingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateNumber(target) {
	if (target.validity.rangeUnderflow) {
		if (target.min == 0 && target.id.includes('position')) {
			target.setCustomValidity('Bitte gib hier einen Betrag ein, der nicht negativ ist; verwende stattdessen die Auswahlfelder "Einnahme" und "Ausgabe".');
		} else if (target.min == 0) {
			target.setCustomValidity('Bitte gib hier einen Betrag ein, der nicht negativ ist.');
		} else {
			target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht kleiner als '+target.min+' ist.');
		}
	} else 	if (target.validity.rangeOverflow) {
		target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht größer als '+target.max+' ist.');
	} else if (target.validity.stepMismatch) {
		if (target.step == 0.01) {
			target.setCustomValidity('Bitte gib hier nur ganze Centbeträge ein.')
		} else if (target.step == 1) {
			target.setCustomValidity('Bitte gib hier nur ganze Zahlen ein.')
		} else {
			target.setCustumValidity('Bitte gib hier nur Zahlen in '+target.step+'erschritten ein.')
		}
	} else if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte fülle dieses Feld aus.')
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft, ob eine Position halb ausgefüllt ist
 * (d.h. Postion hat einen Namen, aber keinen Wert oder umgekehrt)
 * und gibt in diesem Fall eine Fehlermeldung aus.
 * 
 * @param {int} position	Die ID-Nummer der zu validierenden Position
 */
function validateCompletion(position) {
	const fields = [document.getElementById("position"+position+"name"),document.getElementById("position"+position+"amount")]
	if (fields[0].value == "" && fields[1].value != 0) {
		fields[0].setCustomValidity('Bitte fülle diese Position vollständig aus.');
	} else {
		fields[0].setCustomValidity('');
	}
	if (fields[0].value != "" && fields[1].value == 0) {
		fields[1].setCustomValidity('Bitte fülle diese Position vollständig aus.');
	} 
}

/**
 * Validiert das gesamte Formular.
 */
function validateForm() {
	for (let i = 0; i < maxPos; i++) {
		const id = "position"+(i+1);
		validateNumber(document.getElementById(id+"count"));
		validateNumber(document.getElementById(id+"price"));
		validateNumber(document.getElementById(id+"amount"));
		validateCompletion(i+1);
	}
	validateNumber(document.getElementById("donations"));
}

// Funktionen zum grundlegenden Ablauf

/**
 * Funktion zum Aufruf beim Starten dieses Scripts
 */
function start() {
	// Setze spätestes erlaubtes Datum auf heute
	document.getElementById("projectdate").max = new Date().toISOString().split("T")[0];

	// Gib HTML-Elementen auslösbare Ereignisse
	for (let i = 0; i < maxPos; i++) {
		// Ereignisse für Positionsfelder-input
		const id = "position"+(i+1);
		const displayFields = ["name","count","price","amount"];

		// Auswertung von Eingaben
		document.getElementById(id+"plus").addEventListener('input',function(){ positionSetting(i+1,true); });
		document.getElementById(id+"minus").addEventListener('input',function(){ positionSetting(i+1,false); });
		document.getElementById(id+"count").addEventListener('input',function(){ updatePosition(i+1); calculate(); });
		document.getElementById(id+"price").addEventListener('input',function(){ multiSetting(i+1,true); calculate(); });
		document.getElementById(id+"amount").addEventListener('input',function(){ multiSetting(i+1,false); calculate(); });

		// Validierung von Eingaben
		document.getElementById(id+"count").addEventListener('change',function(){ validateNumber(this); });
		document.getElementById(id+"price").addEventListener('change',function(){ validateNumber(this); });
		document.getElementById(id+"amount").addEventListener('change',function(){ validateNumber(this); });

		if (i < maxPos-1) {
			// Anzeige weiterer Positionen bei Eingabe
			for (let j = 0; j < displayFields.length; j++) {
				document.getElementById(id+displayFields[j]).addEventListener('input',function(){ positionDisplay(i+2); });
			}
		}
	}
	document.getElementById("donations").addEventListener('input',calculate);
	document.getElementById("donations").addEventListener('change',function(){ validateNumber(this); });

	// Ereignisse für Zahlungsoptionen-input
	document.getElementById("processtouser").addEventListener('input',function(){ processMode(1); });
	document.getElementById("processsepa").addEventListener('input',function(){ processMode(2); });
	document.getElementById("processbyuser").addEventListener('input',function(){ processMode(3); });
	document.getElementById("processuserknown").addEventListener('input',function(){ ibanLock(this.checked); });

	// Ereignisse für Schaltflächen
	document.getElementById("submit").addEventListener('click',validateForm);
	document.getElementById("reset").addEventListener('click',restart);

	// Ereignis beim Anzeigen der Seite
	window.addEventListener("pageshow", display);
}

/**
 * Setze manche Variablen und Klassen zurück.
 *
 * Zum Aufruf durch die Reset-Schaltfläche.
 */
function restart() {
	processMem=0;
	multiplier = [1,1,1,1,1,1,1];
	const negatives = document.querySelectorAll(".negative")

	positionDisplayInitialize(1);
	processDisplay(0);
	document.getElementById("totalamount").innerHTML = "<aside>Das Formular wurde zurückgesetzt.</aside>";

	for (const field of negatives) {
		field.classList.remove ("negative");
	}
}

/**
 * Überprüft, welche Elemente bereits ausgefüllt sind und bereite
 * Variablen und die Anzeige von Feldern entsprechend vor.
 *
 * Zum Aufruf durch ein pageshow-Ereignis.
 */
function display() {
	for (let i = 1; i <= maxPos; i++) {
		const button = [document.getElementById("position"+i+"plus").checked, document.getElementById("position"+i+"minus").checked];
		// Überprüfe, wo bereits zwischen Einnahme und Ausgabe gewählt wurde
		if (button[1]) {
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
		// IBAN ist bereits als bekannt angegeben
		ibanLock(true);
	}
	if ( document.querySelector('input[name="prtype"]:checked') !== null ) {
		// Eine Zahlungsoption wurde bereits ausgewählt
		processMode(document.querySelector('input[name="prtype"]:checked').value); 
	}

	// Überprüfe, welche Felder noch leer sind, und verstecke Positionen entsprechend
	for (let i = maxPos; i > 0; i--) {
		const values = [document.getElementById("position"+i+"name").value, document.getElementById("position"+i+"count").value, document.getElementById("position"+i+"price").value, document.getElementById("position"+i+"amount").value];
		if (!(values[0]=="" && values[2]==0 && values[3]==0)) {
			// Ein Feld in Position i ist bereits ausgefüllt
			positionDisplayInitialize(i+1);
			break;
		}
		positionDisplayInitialize(1);
	}
}

// Beim Starten dieses Scripts
start();