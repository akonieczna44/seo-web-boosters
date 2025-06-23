// na razie jedna funckja - autouzupełnianie działa


function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🔍 Analiza fraz')
    .addItem('Otwórz narzędzie', 'showKeywordDialog')
    .addToUi();
}

function showKeywordDialog() {
  const html = HtmlService.createHtmlOutputFromFile('dialog')
    .setWidth(400)
    .setHeight(250);
  SpreadsheetApp.getUi().showModalDialog(html, 'Frazy – autosugestie');
}

// UTYLITKA: arkusz tworzy jeśli nie istnieje
function getOrCreateSheet(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const existing = ss.getSheets().find(s => s.getName() === sheetName);
  if (existing) return existing;
  const sheet = ss.insertSheet(sheetName);
  sheet.appendRow(['Fraza', 'Źródło', 'Klaster']);
  return sheet;
}

// GŁÓWNA FUNKCJA: autosugestie → arkusz
function getAutosuggestionsToSheet(base) {
  const sheet = getOrCreateSheet(`Frazy - ${base}`);
  const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
  const all = new Set(getSuggestionsFromGoogle(base));

  for (let i = 0; i < alphabet.length && all.size < 100; i++) {
    const query = `${base} ${alphabet[i]}`;
    const sugg = getSuggestionsFromGoogle(query);
    for (let f of sugg) {
      all.add(f);
      if (all.size >= 100) break;
    }
    Utilities.sleep(300);
  }

  const data = Array.from(all).slice(0, 100).map(f => [f, 'autosugestie', '']);
  if (data.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, data.length, 3).setValues(data);
  }

  return data.length;
}

// AUTOSUGGEST API
function getSuggestionsFromGoogle(query) {
  const url = `https://suggestqueries.google.com/complete/search?client=firefox&q=${encodeURIComponent(query)}`;
  const res = UrlFetchApp.fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const data = JSON.parse(res.getContentText());
  return data[1] || [];
}
