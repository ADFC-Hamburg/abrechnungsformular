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

// Funktionen zur Berechnung und Anzeige von Werten

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

	// Gib HTML-Elementen auslösbare Ereignisse

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
	document.getElementById("journeyendtime").addEventListener('change',function(){ dateDisplayInitialize(1); })

	for (let i = 0; i < maxDates; i++) {
		// Ereignisse für Mahlzeiten-Checkboxen
		const id = "day"+(i+1);
		const displayFields = ["breakfast","lunch","dinner"];
		for (let j = 0; j < displayFields.length; j++) {
			document.getElementById(id+displayFields[j]).addEventListener('input',calculateDayMoney);
		}
	}

	for (let i = 0; i < maxPos; i++) {
		// Ereignisse für Positionsfelder-input
		const id = "position"+(i+1);
		const displayFields = ["name","number","date","amount"];

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
	/*document.getElementById("submit").addEventListener('click',validateForm);*/
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
	for (let i = maxPos; i > 0; i--) {
		const values = [document.getElementById("position"+i+"name").value, document.getElementById("position"+i+"number").value, document.getElementById("position"+i+"date").value, document.getElementById("position"+i+"amount").value];
		if (!(values[0]=="" && values[1]=="" && values[2]=="" && values[3]==0)) {
			// Ein Feld in Position i ist bereits ausgefüllt
			positionDisplayInitialize(i+1);
			break;
		} else if (i==1) {
			positionDisplayInitialize(1);
		}
	}
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