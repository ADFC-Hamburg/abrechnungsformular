const daylength = 86400000 // Millisekunden pro Tag
const maxDates = 10; // Maximale Anzahl an Tagen für Angabe der Mahlzeiten im HTML-Dokument
const maxPos = 12; // Maximale Anzahl an Positionen im HTML-Dokument
const earliestdate = new Date ("1989-11-27");

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
 * Zeige Auswahlfelder für die ersten x Tage und verstecke den Rest.
 * 
 * @since	2.0
 * 
 * @param {number} x	Die letzte anzuzeigende Position
 */
function dateDisplayInitialize(x) {
	for (let i = 1; i <= maxDates; i++) {
		if (i<=x) {
			dateDisplay(i);
		} else {
			dateDisplay(i,false);
		}
	}
}

/**
 * Berechne die Dauer der Reise in Tagen und zeige die entsprechende
 * Anzahl an Auswahlfeldern an.
 * 
 * @since	2.0
 */
function listDates() {
	const values = [document.getElementById("journeybegindate").value,document.getElementById("journeyenddate").value];
	if (values[0] && values[1]) {
		const start = new Date(values[0]);
		const end = new Date(values[1]);
		const days = Math.min(Math.round((end.getTime() - start.getTime()) / daylength) + 1, maxDates);
		dateDisplayInitialize(Math.min(days,maxDates));
		for (let i = 1; i <= Math.min(days,maxDates); i++) {
			const labeldate = new Date(start.getTime()+(i-1)*daylength);
			const labeltext = labeldate.toLocaleDateString('de-DE',{weekday:'long',month:'long',day:'numeric'});
			document.getElementById("day"+i).innerHTML = labeltext+':';
		}
	} else {
		dateDisplayInitialize(0);
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
 * zeige oder verstecke die Angebefelder zur Uhrzeit entscprechend.
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

// Funktionen zum grundlegenden Ablauf

/**
 * Funktion zum Aufruf beim Starten dieses Scripts
 * 
 * @since	2.0
 */
function start() {
	// Gib HTML-Elementen auslösbare Ereignisse

	// Ereignisse für Datumsfelder
	document.getElementById("journeybegindate").addEventListener('change',timeDisplayCheck);
	document.getElementById("journeybegindate").addEventListener('change',listDates);
	document.getElementById("journeyenddate").addEventListener('change',timeDisplayCheck);
	document.getElementById("journeyenddate").addEventListener('change',listDates);

	for (let i = 0; i < maxPos; i++) {
		// Ereignisse für Positionsfelder-input
		const id = "position"+(i+1);
		const displayFields = ["name","number","date","amount"];

		if (i < maxPos-1) {
			// Anzeige weiterer Positionen bei Eingabe
			for (let j = 0; j < displayFields.length; j++) {
				document.getElementById(id+displayFields[j]).addEventListener('input',function(){ positionDisplay(i+2); });
			}
		}
	}

	// Ereignis beim Anzeigen der Seite
	window.addEventListener("pageshow", display);
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
	listDates();
}

// Beim Starten dieses Scripts
start();