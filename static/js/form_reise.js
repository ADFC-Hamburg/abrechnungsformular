const moneyform = new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }); // wird genutzt, um Geldbeträge zu formatieren
const daylength = 86400000 // Millisekunden pro Tag
const earliestdate = new Date ("1989-11-27");
const minHours = 8; // Mindeststundenzahl zur Auszahlung von Tagesgeld

const maxDates = parseInt(document.forms[0].dataset.maxdates); // Maximale Anzahl an Tagen für Angabe der Mahlzeiten im HTML-Dokument
const maxPos = parseInt(document.forms[0].dataset.maxpositions); // Maximale Anzahl an Positionen im HTML-Dokument

const dailyRate = parseFloat(document.getElementById('mealsummary').dataset.dailyrate);
const dailyRateReduced = parseFloat(document.getElementById('mealsummary').dataset.dailyratereduced);
const dailyRateSingle = parseFloat(document.getElementById('mealsummary').dataset.dailyratesingle);
const mealCost = [dailyRate/5, 2*dailyRate/5, 2*dailyRate/5];
const carMoneyPerKM = parseFloat(document.getElementById('extrasummary').dataset.carmoneyperkm);
const carMoneyMax = parseFloat(document.getElementById('extrasummary').dataset.carmoneymax);
const moneyPerNight = parseFloat(document.getElementById('extrasummary').dataset.moneypernight);

// Listen von IBAN-Ländercodes mit bestimmten Eigenschaften
const ibanLength = [['NO'],['BE'],[],['DK','FK','FO','FI','GL','NL','SD'],['MK','SI'],['AT','BA','EE','KZ','XK','LT','LU','MN'],['HR','LV','LI','CH'],['BH','BG','CR','GE','DE','IE','ME','RS','GB','VA'],['TL','GI','IQ','IL','OM','SO','AE'],['AD','CZ','MD','PK','RO','SA','SK','ES','SE','TN','VG'],['LY','PT','ST'],['IS','TR'],['BI','DJ','FR','GR','IT','MR','MC','SM'],['AL','AZ','BY','CY','DO','SV','GT','HU','LB','NI','PL'],['BR','EG','PS','QA','UA'],['JO','KW','MU','YE'],['MT','SC'],['LC'],['RU']];
const ibanNoLetters = ['AE','AT','BA','BE','BI','CR','CZ','DE','DJ','DK','EE','EG','ES','FI','FO','GL','HR','HU','IL','IS','LT','LY','ME','MN','MR','NO','PL','PT','RS','SD','SE','SI','SK','SO','ST','TL','TN','VA','XK'];
const iban2Letters = ['FK','GE'];
const iban4Letters = ['GB','IE','IQ','NI','NL','SV','VG'];

// Array of fields
const fieldsDate = Array.from(document.querySelectorAll("input[type='date']"));
const fieldsNumber = Array.from(document.querySelectorAll("input[type='number']"));
const fieldsText = Array.from(document.querySelectorAll("input[type='text']"));
const fieldsTime = Array.from(document.querySelectorAll("input[type='time']"));

var days = 0;
var daymoney = 0;
var positionmoney = 0;
var carmoney = 0;
var sleepmoney = 0;

// Funktionen zur Sichtbarkeit/Verwendbarkeit von HTML-Elementen

/**
 * Zeige oder verstecke die Auswahlfelder für Tag x
 * 
 * @since	2.0
 * 
 * @param {number} x		Die fragliche Position
 * @param {boolean} show	Ob die Position angezeigt werden soll
 */
function dateDisplay(x,show=true) {
	document.getElementById("day"+x).parentElement.hidden = !(show);
	document.getElementById("day"+x+"breakfast").disabled = !(show);
	document.getElementById("day"+x+"lunch").disabled = !(show);
	document.getElementById("day"+x+"dinner").disabled = !(show);
}

/**
 * Zeige Auswahlfelder für die ersten x Tage und verstecke den Rest;
 * bei keinen oder zu vielen Tagen zeige einen Eingabehinweis.
 * 
 * @since	2.0
 * 
 * @param {number} x	Die letzte anzuzeigende Position
 */
function dateDisplayInitialize(x) {
	let inRange = (x <= maxDates && x >= 0);
	if (x == 1) {
		inRange = checkHours(minHours);
	}
	for (let i = 1; i <= maxDates; i++) {
		if (i<=x) {
			dateDisplay(i,inRange===true);
		} else {
			dateDisplay(i,false);
		}
	}

	let display = (Boolean(x) && inRange===true);
	if (x==0 || inRange===null) {
		document.getElementById("mealhint").innerHTML = "Gib zunächst den Zeitraum der Reise ein.";
	} else if (x==1 && !(inRange)) {
		document.getElementById("mealhint").innerHTML = "Für Tagesreisen unter "+minHours.toLocaleString('de-DE')+" Stunden wird kein Tagesgeld ausgezahlt."
	} else if (!(inRange)) {
		document.getElementById("mealhint").innerHTML = "Es können höchstens "+String(maxDates)+" Reisetage abgerechnet werden.";
	}
	document.getElementById("mealhint").hidden = display;
	document.getElementById("mealdays").hidden = !(display);
	document.getElementById("mealinstruct").hidden = !(display);
	document.getElementById("nightsection").hidden = !(inRange) || (x<2);

	const plurals = document.getElementsByClassName("nightplural");
	for (let i = 0; i < plurals.length; i++) {
		plurals[i].hidden = (x == 2);
	}

	calculateDayMoney();
}

/**
 * Sperre oder entsperre Eingabefelder zu Bankdaten (IBAN und Inhaber)
 * und mache eine Angabe notwendig oder nicht notwendig.
 * 
 * Zum Aufruf durch die Checkbox, die wählt,
 * ob die IBAN dem ADFC schon bekannt ist.
 * 
 * @since	2.0
 * 
 * @param {boolean} check	Ob Eingabefelder gesperrt sein sollen
 */
function ibanLock(check) {
	const field = [document.getElementById("processiban"), document.getElementById("processowner")];
	field[0].disabled = check;
	field[1].disabled = check;
	field[0].required = !(check);
	field[1].required = !(check);
	if (check) {
		field[0].parentElement.classList.add ("locked");
		field[1].parentElement.classList.add ("locked");
	} else {
		field[0].parentElement.classList.remove ("locked");
		field[1].parentElement.classList.remove ("locked");
}	}

/**
 * Berechne die Dauer der Reise in Tagen und zeige die entsprechende
 * Anzahl an Auswahlfeldern an; berechne gegebenenfalls
 * Übernachtungsgeld neu.
 * 
 * @since	2.0
 */
function listDates() {
	const values = [document.getElementById("journeybegindate").value,document.getElementById("journeyenddate").value];
	if (values[0] && values[1]) {
		const start = new Date(values[0]);
		const end = new Date(values[1]);
		days = Math.round((end.getTime() - start.getTime()) / daylength) + 1;
		dateDisplayInitialize(days);
		if (days <= maxDates){
			// Labels für Verpflegungs-Checkboxen
			for (let i = 1; i <= Math.min(days,maxDates); i++) {
				const labeldate = new Date(start.getTime()+(i-1)*daylength);
				const labeltext = labeldate.toLocaleDateString('de-DE',{weekday:'long',month:'long',day:'numeric'});
				document.getElementById("day"+i).innerHTML = labeltext+':';
			}
		}
	} else {
		days = 0;
		dateDisplayInitialize(0);
	}
	// Übernachtungsgeld neu berechnen
	if (document.getElementById("overnightcheck").checked) {
		calculateExtra();
	}
}

/**
 * Zeige oder verstecke die Eingabefelder für Position x
 * 
 * Zum Aufruf durch Eingabefelder für Positionsname, -Anzahl,
 * -Stückpreis und -Betrag.
 * 
 * @since	2.0
 * 
 * @param {number} x		Die fragliche Position
 * @param {boolean} show	Ob die Position angezeigt werden soll
 */
function positionDisplay(x,show=true) {
	document.getElementById("position"+x+"section").hidden = !(show);
}

/**
 * Zeige Eingabefelder für die ersten x Positionen und verstecke den Rest.
 * 
 * @since	2.0
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
 * Zeige oder verstecke die Eingabefelder für die Uhrzeit der Reise.
 * 
 * @since	2.0
 * 
 * @param {boolean} check	Ob die Felder angezeigt werden sollen.
 */
function timeDisplay(show) {
	const field = [document.getElementById("journeybegintime"),document.getElementById("journeyendtime")];

	document.getElementById("timesection").hidden = !(show);
	field[0].disabled = !(show);
	field[1].disabled = !(show);
	field[0].required = show;
	field[1].required = show;
}

/**
 * Vergleiche die Datumsangaben zum Anfang und zum Ende der Reise und
 * zeige oder verstecke die Angebefelder zur Uhrzeit entsprechend.
 * 
 * @since	2.0
 */
function timeDisplayCheck() {
	const field = [document.getElementById("journeybegindate"),document.getElementById("journeyenddate")];

	if (field[0].value != 0 && field[0].value == field[1].value) {
		timeDisplay(true);
	} else {
		timeDisplay(false);
	}
}

// Funktionen zur Begrenzung von Eingabewerten

/**
 * Gleiche das früheste erlaubte Datum der meisten Datumsfelder dem
 * Datum des Anfangs der Reise an.
 * 
 * Sollte dieses Datum noch nicht eingegeben worden sein, nutze
 * stattdessen einen Standartwert.
 * 
 * @since	2.0
 */
function updateMinDate() {
	let value = document.getElementById("journeybegindate").value;
	if (value == "") {
		value = earliestdate.toISOString().split("T")[0];
	}
	updateDateRange(value,null);
}

/**
 * Gleiche das späteste erlaubte Datum der meisten Datumsfelder dem
 * Datum des Endes der Reise an.
 * 
 * Sollte dieses Datum noch nicht eingegeben worden sein, nutze
 * stattdessen das heutige Datum.
 * 
 * @since	2.0
 */
function updateMaxDate() {
	let value = document.getElementById("journeyenddate").value;
	if (value == "") {
		value = new Date().toISOString().split("T")[0];
	}
	updateDateRange(null,value);
}

/**
 * Gleiche die früheste erlaubte Enduhrzeit der Anfangsuhrzeit an.
 * 
 * Sollte die Anfangsuhrzeit noch nicht eingegeben worden sein,
 * setze sie auf 0:00
 * 
 * @since	2.0
 */
function updateMinTime() {
	let value = document.getElementById("journeybegintime").value;
	if (value == "") {
		value = "0:00";
	}
	document.getElementById("journeyendtime").min = value;
}

/**
 * Gleiche die späteste erlaubte Anfangsuhrzeit der Enduhrzeit an.
 * 
 * Sollte die Enduhrzeit noch nicht eingegeben worden sein,
 * setze sie auf 23:59
 * 
 * @since	2.0
 */
function updateMaxTime() {
	let value = document.getElementById("journeyendtime").value;
	if (value == "") {
		value = "23:59";
	}
	document.getElementById("journeybegintime").max = value;
}

/**
 * Begrenze den erlaubten Bereich aller Datumsfelder auf den
 * per Parameter angegebenen Mindest- und Höchstwert. (Ausgenommen sind
 * der Höchstwert für das Ende der Reise und der Mindestwert für den
 * Anfang der Reise.)
 * 
 * Wird ein Parameter nicht angegeben, wird der entsprechende Wert
 * nicht angepasst, sondern bleibt bestehen, wie gehabt.
 * 
 * @since	2.0
 * 
 * @param {(string|null)} [min=null]	Das früheste erlaubte Datum. Bei null bleibt das bisherige Datum bestehen.
 * 
 * @param {(string|null)} [max=null]	Das späteste erlaubte Datum. Bei null bleibt das bisherige Datum bestehen.
 */
function updateDateRange(min=null,max=null) {
	if (!(min === null)) {
		document.getElementById("journeyenddate").min = min;
		/*for (let i = 0; i < maxPos; i++) {
			document.getElementById("position"+(i+1)+"date").min = min;
		}*/
	}
	if (!(max === null)) {
		document.getElementById("journeybegindate").max = max;
		/*for (let i = 0; i < maxPos; i++) {
			document.getElementById("position"+(i+1)+"date").max = max;
		}*/
	}
}

// Funktionen zur Änderung von Werten im HTML-Formular

/**
 * Berechne den Gesamtwert aller Tagesgelder und zeige ihn an,
 * falls er größer als Null ist.
 * 
 * @since	2.0
 */
function calculateDayMoney() {
	daymoney = 0.0;
	if (days > 0 && days <= maxDates) {
		if (days == 1 && checkHours(minHours)===true) {
			daymoney = calculateSingleDay(1,dailyRateSingle);
		} else if (days > 1) {
			for (let i=1; i<=days; i++) {
				let rate = dailyRate;
				if (i==1 || i==days) {
					rate = dailyRateReduced;
				}
				daymoney += calculateSingleDay(i,rate);
			}
		}
	}
	document.getElementById("dayplural").hidden = (days==1);
	document.getElementById("mealsummary").hidden = !(Boolean(daymoney));
	document.getElementById("dayamount").innerHTML = moneyform.format(daymoney);
	calculateTotal();
}

/**
 * Berechne den Gesamtwert aller Positionen und zeige ihn an,
 * falls er größer als Null ist.
 * 
 * @since	2.0
 */
function calculatePositions() {
	positionmoney = 0.0;
	for (let i = 1; i <= maxPos; i++) {
		const amount = document.getElementById("position"+i+"amount").value;
		if (amount>0) {
			positionmoney += +amount;
		}
	}

	// Zeige Ergebnis an
	if (positionmoney) {
		document.getElementById("positiontotal").innerHTML = moneyform.format(positionmoney);
	}
	document.getElementById("positionnotes").hidden = !(!!positionmoney);
	calculateTotal();
}

/**
 * Berechne das Fahrt- und Übernachtungsgeld und zeige beide an,
 * falls sie größer als Null sind.
 * 
 * @since	2.0
 */
function calculateExtra() {
	const km = parseFloat(document.getElementById("cardistance").value);
	if (!(isNaN(km)) && (km > 0)) {
		carmoney = Math.min(km*carMoneyPerKM, carMoneyMax);
	} else {
		carmoney = 0;
	}
	if (document.getElementById("overnightcheck").checked && days > 1) {
		sleepmoney = (days-1) * moneyPerNight;
	} else {
		sleepmoney = 0;
	}

	// Zeige Ergebnis an
	if (carmoney > 0 || sleepmoney > 0) {
		let summary = "";
		if (carmoney) {
			summary = "<b>"+moneyform.format(carmoney)+"</b> an Wegstrecken&shy;entschädigung";
			if (sleepmoney) {
				summary += " und ";
			}
		}
		if (sleepmoney) {
			summary += "<b>"+moneyform.format(sleepmoney)+"</b> an Übernachtungs&shy;geld"
		}
		document.getElementById("extraamount").innerHTML = summary;
		document.getElementById("extrasummary").hidden = false;
	} else {
		document.getElementById("extrasummary").hidden = true;
	}
	calculateTotal();
}

/**
 * Rechnet alle Geldwerte zusammen und zeigt sie an,
 * falls der Gesamtwert größer als Null ist.
 */
function calculateTotal() {
	const total = daymoney + positionmoney + carmoney + sleepmoney;
	if (total > 0) {
		document.getElementById("totalamount").innerHTML = "Wir überweisen den Erstattungsbetrag von <b>"+moneyform.format(total)+"</b> auf dein Bankkonto.";
	} else {
		document.getElementById("totalamount").innerHTML = "<aside>Der Erstattungsbetrag wird hier automatisch zusammengerechnet.</aside>";
	}
}

/**
 * Leert sämtliche Eingabefelder einer einzelnen Position.
 * 
 * @since 2.4
 * 
 * @param {number} x		Die Position, die zurückgesetzt werden soll
 */
function resetPosition(x) {
	const fields = [document.getElementById("position"+x+"name"), document.getElementById("position"+x+"date"), document.getElementById("position"+x+"amount")];
	fields[0].value = "";
	fields[1].value = "";
	fields[2].value = "";
	calculatePositions();
}

/**
 * Tauscht die Inhalte der Eingabefelder von zwei Positionen.
 * 
 * @since 2.5
 * 
 * @param {int} x	Die erste zu tauschende Position
 * @param {int} y	Die zweite zu tauschende Position
 */
function swapPositions(x,y) {
	const fields1 = [document.getElementById("position"+x+"name"), document.getElementById("position"+x+"date"), document.getElementById("position"+x+"amount")];
	const fields2 = [document.getElementById("position"+y+"name"), document.getElementById("position"+y+"date"), document.getElementById("position"+y+"amount")];
	for (let i = 0; i < fields1.length; i++) {
		const carry = fields1[i].value;
		fields1[i].value = fields2[i].value;
		fields2[i].value = carry;
	}
}

// Funktionen, die anderen Funktionen Werte bereitstellen

/**
 * Berechnet das auszuzahlende Tagesgeld für einen bestimmten Tag.
 * 
 * @since	2.0
 * 
 * @param {int} day		Der Tag, dessen Tagesgeld berechnet wird
 * @param {number} rate	Der Tagessatz (ohne Abzüge) für diesen Tag
 * @returns {number}
 */
function calculateSingleDay(day,rate){
	const dayname = "day"+String(day);
	const values = [document.getElementById(dayname+"breakfast").checked,document.getElementById(dayname+"lunch").checked,document.getElementById(dayname+"dinner").checked];
	let result = rate;
	for (let i=0; i<3; i++) {
		if (values[i]) {
			result -= mealCost[i];
		}
	}
	return Math.max(result,0);
}

/**
 * Überprüft, ob eine Start- und Endzeit angegeben wurden
 * und ob diese der angegebenen Mindestlänge genügen.
 * 
 * Gibt bei fehlenden Eingaben null zurück.
 * 
 * @since	2.0
 * 
 * @param {float} threshold	Die Mindestzeit in Stunden, bei der true zurückgegeben wird
 * @returns {boolean|null}
 */
function checkHours(threshold = 0) {
	const values = [document.getElementById("journeybegintime").value,document.getElementById("journeyendtime").value];
	if (!(values[0] && values[1])) {
		return null;
	}
	const startnumbers = values[0].split(":")
	const endnumbers = values[1].split(":")
	let starttime = parseInt(startnumbers[0])*60 + parseInt(startnumbers[1]);
	let endtime = parseInt(endnumbers[0])*60 + parseInt(endnumbers[1]);
	return (endtime - starttime >= threshold * 60);
}

/**
 * Überprüft, welche Position die letzte in numerischer Reihenfolge ist,
 * in welcher ein Name, ein Datum oder ein Preis eingetragen ist.
 * 
 * @since 2.5
 * 
 * @returns {int}	Die Nummer der letzten ausgefüllten Position oder 0, falls keine Position ausgefüllt ist
 */
function lastFilledPosition() {
	for (let i = maxPos; i > 0; i--) {
		const values = [document.getElementById("position"+i+"name").value, document.getElementById("position"+i+"date").value, document.getElementById("position"+i+"amount").value];
		if (!(values[0]=="" && values[1]=="" && values[2]==0)) {
			// Ein Feld in Position i ist bereits ausgefüllt
			return i;
		}
	}
	return 0;
}

// Funktionen zur Validierung

/**
 * Überprüft ein Datumseingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
* 
 * @since	2.0
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateDate(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte gib hier ein Datum ein.');
	} else if (target.validity.rangeOverflow) {
		target.setCustomValidity('Bitte gib hier ein Datum ein, das nicht nach dem '+new Date(target.max).toLocaleDateString('de-DE',{year:'numeric',month:'long',day:'numeric'})+' liegt.');
	} else if (target.validity.rangeUnderflow) {
		target.setCustomValidity('Bitte gib hier ein Datum ein, das nicht vor dem '+new Date(target.min).toLocaleDateString('de-DE',{year:'numeric',month:'long',day:'numeric'})+' liegt.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Datumseingabefeld und gibt gegebenenfalls 
 * eine passende Fehlermeldung aus.
* 
 * @since	2.0
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateTime(target) {
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte gib hier eine Uhrzeit ein.');
	} else if (target.validity.rangeOverflow || target.validity.rangeUnderflow) {
		target.setCustomValidity('Die Anfangsuhrzeit muss vor der Enduhrzeit liegen.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Texteingabefeld und gibt gegebenenfalls
 * eine passende Fehlermeldung aus.
 * 
 * @since	2.0
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird
 */
function validateText(target) {
	target.value = target.value.trim()
	if (target.validity.valueMissing) {
		target.setCustomValidity('Bitte fülle dieses Feld aus.');
	} else {
		target.setCustomValidity('');
	}
}

/**
 * Überprüft ein Textfeld, dass für IBAN bestimmt ist,
 * auf Eingabe (falls vorausgesetzt), Länge und Prüfsumme;
 * gibt gegebenenfalls eine passende Fehlermeldung aus.
 * 
 * @since	2.0
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
 * @since	2.0
 * 
 * @param {HTMLInputElement} target	Das Eingabefeld, das überprüft wird 
 */
function validateNumber(target) {
	if (target.validity.rangeUnderflow) {
		if (target.min == 0 && (target.classList.contains('money'))) {
			target.setCustomValidity('Bitte gib hier einen Betrag ein, der nicht negativ ist.');
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
		if (target.step == 0.01 && (target.classList.contains('money'))) {
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
 * Validiert das gesamte Formular.
 * 
 * @since	2.0
 */
function validateForm() {

	// Validierung von Textfeldern
	for (let i = 0; i < fieldsText.length; i++) {
		if (fieldsText[i].classList.contains('iban')) {
			validateIban(fieldsText[i]);
		} else {
			validateText(fieldsText[i]);
		}
	}

	// Validierung von Datumsfeldern
	for (let i = 0; i < fieldsDate.length; i++) {
		validateDate(fieldsDate[i]);
	}

	// Validierung von Zeitfeldern
	for (let i = 0; i < fieldsTime.length; i++) {
		validateTime(fieldsTime[i]);
	}

	// Validierung von Zahlenfeldern
	for (let i = 0; i < fieldsNumber.length; i++) {
		validateNumber(fieldsNumber[i]);
	}

	// Gibt es unvollständig ausgefüllte Positionen?
	for (let i = 0; i < maxPos; i++) {
		validateCompletion(i+1);
	}

}

	/**
 * Überprüft, ob eine Position halb ausgefüllt ist
 * (z.B. Postion mit Namen und Wert, aber keinem Datum)
 * und gibt in diesem Fall eine Fehlermeldung aus.
 * 
 * @since	2.0
 * 
 * @param {int} position	Die ID-Nummer der zu validierenden Position
 */
function validateCompletion(position) {
	const fields = [document.getElementById("position"+position+"name"),document.getElementById("position"+position+"date"),document.getElementById("position"+position+"amount")];
	let filled = Boolean(fields[0].value || fields[1].value || fields[2].value != 0);
	if (fields[0].value == "" && filled) {
		fields[0].setCustomValidity('Bitte fülle diese Position vollständig aus.');
	}
	if (fields[1].value == "" && filled) {
		fields[1].setCustomValidity('Bitte fülle diese Position vollständig aus.');
	}
	if (fields[2].value == 0 && filled) {
		fields[2].setCustomValidity('Bitte fülle diese Position vollständig aus.');
	}
}

// Funktionen zum grundlegenden Ablauf

/**
 * Funktion zum Aufruf beim Starten dieses Scripts
 * 
 * @since	2.0
 */
function start() {
	// Setze spätestes und frühestes erlaubtes Datum
	document.getElementById("journeyenddate").max = new Date().toISOString().split("T")[0];
	document.getElementById("journeybegindate").min = earliestdate.toISOString().split("T")[0];
	for (let i = 1; i <= maxPos; i++) {
		document.getElementById("position"+(i)+"date").max = new Date().toISOString().split("T")[0];
		document.getElementById("position"+(i)+"date").min = earliestdate.toISOString().split("T")[0];
	}

	// Mache alle Elemente, die nur beim Einsatz von JavaScript sichbar sein sollen, sichtbar
	const hiddenElements = document.getElementsByClassName("jsonly");
	for (let i = 0; i < hiddenElements.length; i++) {
		hiddenElements[i].removeAttribute("hidden");
	}
	
	// Gib HTML-Elementen auslösbare Ereignisse

	// Validierung von Textfeldern
	let count = fieldsText.length;
	for (let i = 0; i < count; i++) {
		if (fieldsText[i].classList.contains('iban')) {
			fieldsText[i].addEventListener('change',function(){ validateIban(this); });
		} else {
			fieldsText[i].addEventListener('change',function(){ validateText(this); });
		}
	}

	// Validierung von Datumsfeldern
	count = fieldsDate.length;
	for (let i = 0; i < count; i++) {
		fieldsDate[i].addEventListener('change',function(){ validateDate(this); });
	}

	// Validierung von Zeitfeldern
	count = fieldsTime.length;
	for (let i = 0; i < count; i++) {
		fieldsTime[i].addEventListener('change',function(){ validateTime(this); });
	}

	// Validierung von Zahlenfeldern
	count = fieldsNumber.length;
	for (let i = 0; i < count; i++) {
		fieldsNumber[i].addEventListener('change',function(){ validateNumber(this); });
	}

	// Ereignisse für Zahlungsfelder
	document.getElementById("processuserknown").addEventListener('input',function(){ ibanLock(this.checked); });

	// Ereignisse für Datumsfelder
	document.getElementById("journeybegindate").addEventListener('change',updateMinDate);
	document.getElementById("journeybegindate").addEventListener('change',timeDisplayCheck);
	document.getElementById("journeybegindate").addEventListener('change',listDates);
	document.getElementById("journeyenddate").addEventListener('change',updateMaxDate);
	document.getElementById("journeyenddate").addEventListener('change',timeDisplayCheck);
	document.getElementById("journeyenddate").addEventListener('change',listDates);

	// Ereignisse für Uhrzeitfelder
	document.getElementById("journeybegintime").addEventListener('change',function(){ dateDisplayInitialize(1); })
	document.getElementById("journeybegintime").addEventListener('change',updateMinTime);
	document.getElementById("journeyendtime").addEventListener('change',function(){ dateDisplayInitialize(1); })
	document.getElementById("journeyendtime").addEventListener('change',updateMaxTime);

	// Ereignisse für Mahlzeiten-Checkboxen
	let fields = document.getElementById("mealdays").querySelectorAll("input[type='checkbox']");
	count = fields.length;
	for (let i = 0; i < count; i++) {
		fields[i].addEventListener('input',calculateDayMoney);
	}

	for (let i = 0; i < maxPos; i++) {
		// Ereignisse für Positionsfelder-input
		const id = "position"+(i+1);
		const displayFields = ["name","date","amount"];

		document.getElementById(id+"amount").addEventListener('input',calculatePositions);

		if (i < maxPos-1) {
			// Anzeige weiterer Positionen bei Eingabe
			for (let j = 0; j < displayFields.length; j++) {
				document.getElementById(id+displayFields[j]).addEventListener('input',function(){ positionDisplay(i+2); });
			}
		}
	}

	// Ereignisse für sonstige Eingabefelder
	document.getElementById("cardistance").addEventListener('change',calculateExtra);
	document.getElementById("overnightcheck").addEventListener('change',calculateExtra);

	// Ereignisse für Schaltflächen
	for (let i=1; i <= maxPos; i++) {
		document.getElementById("position"+i+"reset").addEventListener('click',function(){ resetPosition(i); });
	}
	document.getElementById("submit").addEventListener('click',validateForm);
	document.getElementById("reset").addEventListener('click',restart);

	// Ereignis beim Anzeigen der Seite
	window.addEventListener("pageshow", display);
}

/**
 * Setze manche Variablen und Klassen zurück.
 * 
 * Zum Aufruf durch die Reset-Schaltfläche.
 * 
 * @since	2.0
 */
function restart() {
	dateDisplayInitialize(0);
	ibanLock(false);
	positionDisplayInitialize(1);
	timeDisplay(false);
	updateDateRange(earliestdate.toISOString().split("T")[0],new Date().toISOString().split("T")[0]);

	document.getElementById("journeybegintime").max = '23:59'
	document.getElementById("journeyendtime").min = '0:00'

	document.getElementById("mealsummary").hidden = true;
	document.getElementById("positionnotes").hidden = true;
	document.getElementById("extrasummary").hidden = true;

	daymoney = 0;
	positionmoney = 0;
	carmoney = 0;
	sleepmoney = 0;
	calculateTotal();
}

/**
 * Überprüft, welche Elemente bereits ausgefüllt sind und bereite
 * Variablen und die Anzeige von Feldern entsprechend vor.
 * 
 * Zum Aufruf durch ein pageshow-Ereignis.
 * 
 * @since	2.0
 */
function display() {
	// Überprüfe, welche Felder noch leer sind, und verstecke Positionen entsprechend
	positionDisplayInitialize(lastFilledPosition()+1);

	calculatePositions();
	timeDisplayCheck();
	ibanLock(document.getElementById("processuserknown").checked);
	listDates();
	updateMinDate();
	updateMaxDate();
	calculateDayMoney();
	calculateExtra();
}

// Beim Starten dieses Scripts
start();