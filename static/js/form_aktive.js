const moneyform = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }); // wird genutzt, um Geldbeträge zu formatieren
const maxPos = 7; // Maximale Anzahl an Positionen im HTML-Dokument

// Listen von IBAN-Ländercodes mit bestimmten Eigenschaften
const ibanLength = [['NO'],['BE'],[],['DK','FK','FO','FI','GL','NL','SD'],['MK','SI'],['AT','BA','EE','KZ','XK','LT','LU','MN'],['HR','LV','LI','CH'],['BH','BG','CR','GE','DE','IE','ME','RS','GB','VA'],['TL','GI','IQ','IL','OM','SO','AE'],['AD','CZ','MD','PK','RO','SA','SK','ES','SE','TN','VG'],['LY','PT','ST'],['IS','TR'],['BI','DJ','FR','GR','IT','MR','MC','SM'],['AL','AZ','BY','CY','DO','SV','GT','HU','LB','NI','PL'],['BR','EG','PS','QA','UA'],['JO','KW','MU','YE'],['MT','SC'],['LC'],['RU']];
const ibanNoLetters = ['AE','AT','BA','BE','BI','CR','CZ','DE','DJ','DK','EE','EG','ES','FI','FO','GL','HR','HU','IL','IS','LT','LY','ME','MN','MR','NO','PL','PT','RS','SD','SE','SI','SK','SO','ST','TL','TN','VA','XK'];
const iban2Letters = ['FK','GE'];
const iban4Letters = ['GB','IE','IQ','NI','NL','SV','VG'];

var multiplier = [-1,-1,-1,-1,-1,-1,-1];
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
 * und mache eine Angabe notwendig oder nicht notwendig.
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
		field[0].required = false;
		field[1].required = false;
		field[0].parentElement.classList.add ("locked");
		field[1].parentElement.classList.add ("locked");
	} else {
		field[0].disabled = false;
		field[1].disabled = false;
		field[0].required = true;
		field[1].required = true;
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

// Funktionen, die anderen Funktionen Informationen bereitstellen

/**
 * Überprüft, ob ein Geldbetrag irgendwo im Formular eingegeben wurde.
 * 
 * @since	1.3
 * 
 * @returns {bool}	Ob ein Geldbetrag eingegeben wurde
 */
function anyAmountEntered() {
	if (document.getElementById('donations').value != 0) {
		return true;
	}
	for (let i = 0; i < maxPos; i++) {
		if (document.getElementById('position'+(i+1)+'amount').value != 0) {
			return true;
		}
	}
	return false;
}

/**
 * Gibt einen Array mit allen Texteingebefeldern zurück
 * 
 * @since 1.4
 * 
 * @returns {Array}	Alle Texteingabefelder im Dokument
 */
function allTextfields() {
	return Array.from(document.querySelectorAll("input[type='text']"));
}

// Funktionen zur Validierung

/**
 * Überprüft ein Datumseingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
* 
 * @since	1.3
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateDate(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte gib hier ein Datum ein.');
	} else if (target.validity.rangeOverflow) {
		target.setCustomValidity('Bitte gib hier ein Datum ein, das nicht in der Zukunft liegt.');
	} else if (target.validity.rangeUnderflow) {
		target.setCustomValidity('Bitte gib hier ein Datum ein, das nicht vor dem '+new Date(target.min).toLocaleDateString('de-DE',{year:'numeric',month:'long',day:'numeric'})+' liegt.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Texteingabefeld und gibt gegebenenfalls
 * eine passende Fehlermeldung aus.
 * 
 * @since	1.4
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateText(target) {
	target.value = target.value.trim()
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte fülle dieses Feld aus.');
	} else if (target.validity.patternMismatch) {
		target.setCustomValidity('Bitte gib einen passenden Text ein ('+target.title+').');
	} else if (target.validity.tooLong) {
		target.setCustomValidity('Bitte gib einen Text ein, der nicht länger als '+target.maxlength+' Zeichen ist.');
	} else if (target.validity.tooShort) {
		target.setCustomValidity('Bitte gib einen Text ein, der nicht kürzer als '+target.minlength+' Zeichen ist.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Textfeld, dass für deutsche IBAN bestimmt ist,
 * auf Eingabe (falls vorausgesetzt), Länge und Prüfsumme;
 * gibt gegebenenfalls eine passende Fehlermeldung aus.
 * 
 * @since	1.5
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateIban(target) {
	target.value = target.value.toUpperCase().replace(/[^0-9A-Z]/g,'');
	if (target.validity.valueMissing) {
		// Eingabe vorrausgesetzt, aber fehlt
		target.setCustomValidity('Bitte fülle dieses Feld aus.');
	} else if ((target.value.length - 1)*(target.value.length - 4) <= 0) {
		// Länge 1-4
		target.setCustomValidity('Bitte fülle dieses Feld vollständig aus.');
	} else if (!(/^[A-Z]{2}[0-9]{2}/.test(target.value))) {
		// Fängt nicht an mit Buchstabe-Buchstabe-Zahl-Zahl
		target.setCustomValidity('Bitte schreibe eine IBAN in dieses Feld.');
	} else {

		const country = target.value.substring(0,2);
		let minLength = 15;
		let maxLength = 34;
		for (let i = 0; i < ibanLength.length; i++) {
			// Wie lang sollte eine IBAN mit diesem Ländercode sein?
			if (ibanLength[i].includes(country)) {
				minLength = i+15;
				maxLength = i+15;
				break;
			}
		}
		if (target.value.length > maxLength) {
			// IBAN zu lang
			let overflow = target.value.length - maxLength;
		if (overflow == 1) {
			overflow = 'ein';
		}
		target.setCustomValidity('Diese IBAN ist '+overflow+' Zeichen zu lang.');
		} else if (target.value.length < minLength) {
			// IBAN zu kurz
			let missing = minLength - target.value.length;
		if (missing == 1) {
			missing = 'ein';
		}
		target.setCustomValidity('Diese IBAN ist '+missing+' Zeichen zu kurz.');
		} else if (ibanNoLetters.includes(country) && /[A-Z]/.test(target.value.substring(2))) {
			// Zu viele Buchstaben (sollte nur Ländercode sein)
			target.setCustomValidity('IBAN mit Ländercode '+country+' dürfen nach dem Ländercode keine weiteren Buchstaben enthalten.');
} else if (iban2Letters.includes(country) && (/[0-9]/.test(target.value.substring(4,6)) || /[A-Z]/.test(target.value.substring(6)))) {
			target.setCustomValidity('IBAN mit Ländercode '+country+' müssen nach Ländercode und Prüfziffer genau zwei Buchstaben enthalten.');
		} else if (iban4Letters.includes(country) && (/[0-9]/.test(target.value.substring(4,8)) || /[A-Z]/.test(target.value.substring(8)))) {
			target.setCustomValidity('IBAN mit Ländercode '+country+' müssen nach Ländercode und Prüfziffer genau vier Buchstaben enthalten.');
	} else {
			// Berechne Prüfsumme
			let checksum = target.value.substring(4) + target.value.substring(0,4);
			for (let i = 0; i < 26; i++) {
				checksum = checksum.replaceAll(String.fromCharCode(65+i),(i+10).toString());
			}
		while (checksum.length>9) {
			checksum = checksum.substring(0,9) % 97 + checksum.substring(9);
		}
		if (checksum % 97 == 1) {
				// Alles OK
			target.setCustomValidity('');
		} else {
				// Schlechte Prüfsumme
			target.setCustomValidity('Dies ist keine gültige IBAN. Überprüfe deine Eingabe bitte auf Fehler.');
			}
		}
	}
}

/**
 * Überprüft ein Zahleneingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
* 
 * @since	1.3
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateNumber(target) {
	if (target.validity.rangeUnderflow) {
		if (target.min == 0 && (target.id.includes('price') || target.id.includes('amount'))) {
			target.setCustomValidity('Bitte gib hier einen Betrag ein, der nicht negativ ist; verwende stattdessen die Auswahlfelder "Einnahme" und "Ausgabe".');
		} else if (target.min == 0) {
			target.setCustomValidity('Bitte gib hier eine Zahl ein, der nicht negativ ist.');
		} else {
			target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht kleiner als '+target.min+' ist.');
		}
	} else 	if (target.validity.rangeOverflow) {
		target.setCustomValidity('Bitte gib hier eine Zahl ein, die nicht größer als '+target.max+' ist.');
	} else if (target.validity.badInput) {
		target.setCustomValidity('Bitte gib hier nur Zahlen ein.');
	} else if (target.validity.stepMismatch) {
		if (target.step == 0.01) {
			target.setCustomValidity('Bitte gib hier nur ganze Centbeträge ein.');
		} else if (target.step == 1) {
			target.setCustomValidity('Bitte gib hier nur ganze Zahlen ein.');
		} else {
			target.setCustomValidity('Bitte gib hier nur Zahlen in '+target.step+'erschritten ein.');
		}
	} else if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte fülle dieses Feld aus.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft, ob eine Position halb ausgefüllt ist
 * (d.h. Postion hat einen Namen, aber keinen Wert oder umgekehrt)
 * und gibt in diesem Fall eine Fehlermeldung aus.
 * 
 * @since	1.3
 * 
 * @param {int} position	Die ID-Nummer der zu validierenden Position
 */
function validateCompletion(position) {
	const fields = [document.getElementById("position"+position+"name"),document.getElementById("position"+position+"amount")];
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
 * 
 * @since	1.3
 */
function validateForm() {
	
	validateDate(document.getElementById("projectdate"));
	
	// Validiere alle Textfelder
	for (const element of allTextfields()) {
		if (element.id == 'processiban') {
			validateIban(element);
		} else {
			validateText(element);
		}
	}

	// Ist mindestens ein Betrag angegeben?
	if (!(anyAmountEntered())) {
		document.getElementById("submit").setCustomValidity('Bitte trage mindestens eine Position oder Spende in das Formular ein.');
	} else {
		document.getElementById("submit").setCustomValidity('');
	}
	for (let i = 0; i < maxPos; i++) {
		// Validiere jede Positionen
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
 * 
 * @since	1.3
 */
function start() {
	// Setze spätestes erlaubtes Datum auf heute
	document.getElementById("projectdate").max = new Date().toISOString().split("T")[0];

	// Gib HTML-Elementen auslösbare Ereignisse

	// Ereignisse für Texteingabefelder
	for (const element of allTextfields()) {
		if (element.id == 'processiban') {
			element.addEventListener('change',function(){ validateIban(this); });
		} else {
			element.addEventListener('change',function(){ validateText(this); });
		}
	}

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

	// Ereignisse für persönliche Angabefelder
	document.getElementById("projectdate").addEventListener('change',function(){ validateDate(this); });

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
 * @since	1.3
 *
 * Zum Aufruf durch die Reset-Schaltfläche.
 */
function restart() {
	processMem=0;
	multiplier = [-1,-1,-1,-1,-1,-1,-1];
	multiPosition = [false,false,false,false,false,false,false];

	positionDisplayInitialize(1);
	processDisplay(0);
	document.getElementById("totalamount").innerHTML = "<aside>Das Formular wurde zurückgesetzt.</aside>";

	for (let i = 1; i <= maxPos; i++) {
		updatePosition(i);
	}
}

/**
 * Überprüft, welche Elemente bereits ausgefüllt sind und bereite
 * Variablen und die Anzeige von Feldern entsprechend vor.
 * 
 * @since	1.3
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