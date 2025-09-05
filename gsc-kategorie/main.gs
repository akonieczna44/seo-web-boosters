/***** KONFIG *****/
const MAIN_SHEET   = "main";
const DANE_SHEET   = "dane";
const UPDATE_SHEET = "update";
const DEBUG_SHEET  = "update_debug";

// Kolumny w "dane" (A=1):
const COL_DATE_DANE         = 2; // B - data rekordu GSC
const COL_CLICKS_DANE       = 3; // C - kliknięcia
const COL_IMPRESSIONS_DANE  = 4; // D - wyświetlenia
const COL_OUT_IMP_DANE      = 7; // G - TU wpisujemy "Wyświetlenia po update"
const COL_OUT_CLK_DANE      = 8; // H - TU wpisujemy "Kliknięcia po update"
const COL_ID_DANE           = 9; // I - ID (np. k412 lub inne śmieci)

// Kolumny w "main" (A=1):
const COL_ID_MAIN           = 2; // B - ID (np. k412)
const COL_UPDATE_DATE_MAIN  = 7; // G - data update

/***** UTILITIES *****/
function ymd(d) {
  // Zwraca "" gdy d jest puste albo nie-datą
  if (!(d instanceof Date) || isNaN(d)) return "";
  const z = n => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${z(d.getMonth() + 1)}-${z(d.getDate())}`;
}
function startOfDay(d){ const x=new Date(d); x.setHours(0,0,0,0); return x; }
function asDate(v){
  if (!v) return null;
  if (Object.prototype.toString.call(v) === "[object Date]" && !isNaN(v)) return startOfDay(v);
  if (typeof v === "number") { // serial date
    const ms = Math.round((v - 25569) * 86400 * 1000);
    const d = new Date(ms);
    return isNaN(d) ? null : startOfDay(d);
  }
  if (typeof v === "string") {
    const t = v.trim();
    if (!t) return null;
    let d = new Date(t);
    if (!isNaN(d)) return startOfDay(d);
    const m = t.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})$/);
    if (m) {
      d = new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3]));
      if (!isNaN(d)) return startOfDay(d);
    }
  }
  return null;
}
function normId(raw){
  if (raw == null) return "";
  const s = String(raw).toLowerCase();
  const m = s.match(/k\d+/); // WYCIĄGNIJ zawsze k123, nawet z „k123,coś”
  return m ? m[0] : "";
}

 /***** JEDEN PRZYCISK: wszystko naraz *****/
function uruchomWszystko() {
  const ss   = SpreadsheetApp.getActiveSpreadsheet();
  const tz   = ss.getSpreadsheetTimeZone();
  const todayStr = Utilities.formatDate(new Date(), tz, "yyyy-MM-dd");

  const main = ss.getSheetByName(MAIN_SHEET);
  const dane = ss.getSheetByName(DANE_SHEET);
  if (!main || !dane) {
    SpreadsheetApp.getUi().alert('Sprawdź nazwy zakładek: oczekuję "main" i "dane".');
    return;
  }

  const lastMain = main.getLastRow();
  const lastDane = dane.getLastRow();
  if (lastMain < 2 || lastDane < 2) {
    SpreadsheetApp.getUi().alert("Brak danych do obróbki.");
    return;
  }

  // === MAIN: najnowsza data update dla każdego ID ===
  const widthMain = Math.max(COL_UPDATE_DATE_MAIN, COL_ID_MAIN);
  const mainVals  = main.getRange(2, 1, lastMain - 1, widthMain).getValues();
  const latestUpdById = new Map(); // id -> Date (najnowsza)
  for (const row of mainVals) {
    const id = normId(row[COL_ID_MAIN - 1]);
    const d  = asDate(row[COL_UPDATE_DATE_MAIN - 1]);
    if (!id || !d) continue;
    const prev = latestUpdById.get(id);
    if (!prev || d > prev) latestUpdById.set(id, d);
  }

  // === DANE: wartości + poprzednie G/H (by policzyć "NOWE") ===
  const widthDane = Math.max(COL_ID_DANE, COL_OUT_CLK_DANE, COL_OUT_IMP_DANE, COL_IMPRESSIONS_DANE, COL_CLICKS_DANE, COL_DATE_DANE);
  const daneVals  = dane.getRange(2, 1, lastDane - 1, widthDane).getValues();
  const prevImp   = dane.getRange(2, COL_OUT_IMP_DANE, lastDane - 1, 1).getValues(); // G
  const prevClk   = dane.getRange(2, COL_OUT_CLK_DANE, lastDane - 1, 1).getValues(); // H

  const outImp = daneVals.map(_ => [""]);
  const outClk = daneVals.map(_ => [""]);

  // Sumy „NOWO dodanych” per ID:
  const addedImpById = new Map();
  const addedClkById = new Map();

  // Debug tylko dla przypadków: data rekordu < data update
  const debugRows = [["wiersz_dane","id","data_rekordu","data_update","powód"]];

  let fillImp = 0, fillClk = 0;

  for (let i = 0; i < daneVals.length; i++) {
    const row     = daneVals[i];
    const obsDate = asDate(row[COL_DATE_DANE - 1]);        // B
    const clicks  = row[COL_CLICKS_DANE - 1];              // C
    const impr    = row[COL_IMPRESSIONS_DANE - 1];         // D
    const idRaw   = row[COL_ID_DANE - 1];                  // I
    const id      = normId(idRaw);

    // Pomijamy brak ID i brak daty rekordu — nic nie logujemy
    if (!id) continue;
    if (!obsDate) continue;

    const updDate = latestUpdById.get(id);
    // Pomijamy też brak daty update w main — nic nie logujemy
    if (!updDate) continue;

    if (obsDate >= updDate) {
      // wpisujemy wartości
      outImp[i][0] = impr != null ? impr : "";
      outClk[i][0] = clicks != null ? clicks : "";
      if (outImp[i][0] !== "") fillImp++;
      if (outClk[i][0] !== "") fillClk++;

      // liczymy "nowe" (tylko gdy wcześniej było pusto)
      if (prevImp[i][0] === "" && typeof impr === "number") {
        addedImpById.set(id, (addedImpById.get(id) || 0) + impr);
      }
      if (prevClk[i][0] === "" && typeof clicks === "number") {
        addedClkById.set(id, (addedClkById.get(id) || 0) + clicks);
      }
    } else {
      // TYLKO to logujemy do debug
      debugRows.push([i+2, id, ymd(obsDate), ymd(updDate), "data rekordu < data update"]);
    }
  }

  // === Zapis do G/H ===
  if (outImp.length) dane.getRange(2, COL_OUT_IMP_DANE, outImp.length, 1).setValues(outImp);
  if (outClk.length) dane.getRange(2, COL_OUT_CLK_DANE, outClk.length, 1).setValues(outClk);

  // === Log do UPDATE: data | id | nowe_wyświetlenia | nowe_kliknięcia ===
  let upd = ss.getSheetByName(UPDATE_SHEET);
  if (!upd) {
    upd = ss.insertSheet(UPDATE_SHEET);
    upd.getRange(1,1,1,4).setValues([["data","id","nowe_wyświetlenia","nowe_kliknięcia"]]);
  }
  const toAppend = [];
  const ids = new Set([...addedImpById.keys(), ...addedClkById.keys()]);
  for (const id of ids) {
    const addImp = addedImpById.get(id) || 0;
    const addClk = addedClkById.get(id) || 0;
    if (addImp !== 0 || addClk !== 0) {
      toAppend.push([todayStr, id, addImp, addClk]);
    }
  }
  if (toAppend.length) {
    upd.getRange(upd.getLastRow()+1, 1, toAppend.length, 4).setValues(toAppend);
  }

  // === DEBUG arkusz (tylko „data rekordu < data update”) ===
  let dbg = ss.getSheetByName(DEBUG_SHEET);
  if (!dbg) dbg = ss.insertSheet(DEBUG_SHEET);
  dbg.clearContents();
  dbg.getRange(1,1,debugRows.length, debugRows[0].length).setValues(debugRows);

  SpreadsheetApp.getActive().toast(
    `Wpisano: impr=${fillImp}, clk=${fillClk}. Zalogowano ID: ${toAppend.length}. Sprawdź "${DEBUG_SHEET}" dla pominiętych.`,
    "Gotowe", 8
  );
}



/** menu z 1 przyciskiem jednak */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu("Moje funkcje")
    .addItem("Uruchom machinę!", "uruchomWszystko")
    .addToUi();
}
