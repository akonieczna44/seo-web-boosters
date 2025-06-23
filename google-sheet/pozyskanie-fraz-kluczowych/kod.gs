// autouzupełnianie przycisk i usuwanie duplikatów

// PARAMETR: Maksymalna liczba sugestii
const AUTOSUGGEST_LIMIT = 100;

function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('🔍 Analiza fraz')
    .addItem('Autosugestie Google', 'showKeywordDialog')
    .addItem('Usuń duplikaty', 'removeDuplicates')
    .addToUi();
}

// Dialog do wpisania frazy
function showKeywordDialog() {
  const html = HtmlService.createHtmlOutputFromFile('dialog')
    .setWidth(400)
    .setHeight(250);
  SpreadsheetApp.getUi().showModalDialog(html, 'Autosugestie Google');
}

// Pobieranie autosugestii
function getSuggestionsFromGoogle(query) {
  const url = `https://suggestqueries.google.com/complete/search?client=firefox&q=${encodeURIComponent(query)}`;
  const response = UrlFetchApp.fetch(url, {
    headers: { 'User-Agent': 'Mozilla/5.0' }
  });
  const json = JSON.parse(response.getContentText());
  return json[1] || [];
}

// Główna funkcja do autosugestii
function fetchSuggestions(base) {
  const alphabet = 'abcdefghijklmnopqrstuvwxyz'.split('');
  const all = new Set();

  // bazowa fraza
  const baseSuggestions = getSuggestionsFromGoogle(base);
  baseSuggestions.forEach(f => all.add(f));

  // frazy z literami
  for (let i = 0; i < alphabet.length && all.size < AUTOSUGGEST_LIMIT; i++) {
    const query = `${base} ${alphabet[i]}`;
    const suggestions = getSuggestionsFromGoogle(query);
    suggestions.forEach(f => {
      if (all.size < AUTOSUGGEST_LIMIT) all.add(f);
    });
    Utilities.sleep(200); // opóźnienie między żądaniami
  }

  const sheetName = `Frazy - ${base}`;
  let sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName(sheetName);
  if (!sheet) {
    sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet(sheetName);
    sheet.getRange(1, 1, 1, 3).setValues([['Fraza', 'Źródło', 'Klaster']]);
  }

  const existing = sheet.getDataRange().getValues().slice(1).map(row => row[0]);
  const newData = Array.from(all)
    .filter(f => !existing.includes(f))
    .map(f => [f, 'autosugestie', '']);

  if (newData.length > 0) {
    sheet.getRange(sheet.getLastRow() + 1, 1, newData.length, 3).setValues(newData);
  }

  return newData.length;
}

// Usuwanie duplikatów z aktywnego arkusza
function removeDuplicates() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();

  if (data.length <= 1) return;

  const seen = new Set();
  const output = [data[0]];

  for (let i = 1; i < data.length; i++) {
    const val = data[i][0]?.toString().trim().toLowerCase();
    if (!seen.has(val)) {
      seen.add(val);
      output.push(data[i]);
    }
  }

  sheet.clearContents();
  sheet.getRange(1, 1, output.length, output[0].length).setValues(output);
}
