// google sheets + apps script 

// funkcja, która generuje różne alty
// na podstawie dostarczonych głównych fraz, pobocznych, liczby kombinacji i liczby fraz w kombinacji

function generujKombinacjeZFrazy() {
  const arkusz = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  const frazyGlowne = arkusz.getRange("B2").getValue().split(",").map(x => x.trim());
  const liczbaDodatkowych = parseInt(arkusz.getRange("C2").getValue());
  const liczbaKombinacji = parseInt(arkusz.getRange("E2").getValue());
  const frazyDodatkowe = arkusz.getRange("D2").getValue().split(",").map(x => x.trim());

  const kombinacje = new Set();

  while (kombinacje.size < liczbaKombinacji) {
    const shuffled = [...frazyDodatkowe].sort(() => 0.5 - Math.random());
    const wybrane = shuffled.slice(0, liczbaDodatkowych);
    const allFrazy = [...frazyGlowne, ...wybrane];
    const kombinacja = allFrazy.join(", ");

    kombinacje.add(kombinacja);
  }

  const kombinacjeArray = Array.from(kombinacje);

  for (let i = 0; i < kombinacjeArray.length; i++) {
    arkusz.getRange(2, 7 + i).setValue(kombinacjeArray[i]); // 7 = kolumna G
  }
}
function onEdit(e) {
  const zakres = e.range.getA1Notation();
  const edytowanyWiersz = e.range.getRow();

  // Jeśli edytowano coś w wierszu 2 w kolumnach B, C, D lub E – generuj kombinacje
  // żeby nie musieć włączać za każdym razem skryptu
  if (edytowanyWiersz === 2 && ["B2", "C2", "D2", "E2"].includes(zakres)) {
    generujKombinacjeZFrazy();
  }
}
