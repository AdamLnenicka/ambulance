# Ambulance

Tato aplikace umožňuje spravovat rozpis doktorů v ambulanci.


  - **Poznámka:** v případě divnýho chování jak aplikace tak souborů dej vědět, já aplikaci testoval jak se dalo, vše se zdá v normě.

    
## Obsah

### Soubor `doktoři.txt`
- Obsahuje seznam doktorů.
- **Pro přidání:** Edituj soubor přidáním nového doktora na nový řádek.
- **Pro odstranění:** Smaž odpovídající řádek.

### Nepřítomnosti
- Při zadání jednodenní nepřítomnosti je nutné zadat stejné datum do polí `Datum od` i `Datum do`.
- Nepřítomnosti se spolu s celým rozpisem uloží do souboru `rozpis.txt` pouze v okamžiku generování PDF, ne při každé změně.
  - **Poznámka:** V případě, že je aplikace ukončena bez vygenerování PDF, zadané nepřítomnosti se neuloží.

### Zobrazení posledního rozpisu
- Pomocí tlačítka `Zobrazit poslední rozpis` se do programu nahraje obsah rozpisu (ze souboru `rozpis.txt`) z okamžiku posledního generování PDF.

### Generování rozpisu
- Tlačítko `Generovat rozpis` vygeneruje soubor `rozpis.pdf` se zadanými nepřítomnostmi .
  - **Poznámka:** Název PDF souboru obsahuje datum a čas vygenerování ve formátu `den.mesic.rok_hodina-minuta-vterina`.

## Instalace

1. **Stáhni si repozitář:**
    - Klikni na zelenou ikonku `Code` -> `Download ZIP`.

2. **Extrahuj ZIP:**
    - Extrahuj tam, kde chceš program mít, třeba na plochu.
    - Ve složce `dist` je spustitelný soubor `ambulance.exe`.
    - Pokud chceš jednoduchého zástupce na ploše, stačí pravým tlačítkem kliknout na ambulance.exe (možná shif+pravé tlačítko, tak to mám já) a vytvořit ho na ploše. Pak si můžeš složku se soubory hodit kam chceš, ale závislosti musí zůstat ve složce kde jsou. Pdf se ti tam budou generovat taky.

3. **Spusť aplikaci:**
    - Otevři složku `dist` a spusť aplikaci přes soubor `ambulance.exe`, nebo přes vytvořeného zástupce.


## **Update 1**
Opravy:
1) Odstraněno informační okno při zadání/odstranění nepřítomnosti.
2) Pro zadání/odstranění jednodenní nepřítomnosti stačí zadat datum dne v poli `Datum od`.
3) Opraveno neproporcionální zvětšovaní, zmenšování textu v různých elementech programu při využití tlačítek. Aby ukázka rozpisu zůstala přehledná, je akorát potřeba si při zvětšení textu roztáhnout aplikační okno. 

Nové funkce:
1) Přidáno tlačítko `Reset datum do` pro reset datumu do (Jelikož standardní mechanismus kalendáře neumožňuje přímo nastavit datum na None pomocí interakce, musíme přidat tlačítko nebo jiný mechanismus pro explicitní resetování).
2) Přidána funkcionalita aplikace, která umožňuje automaticky generovat záznamy absencí pro každého doktora na základě specifikovaných dnů v souboru `doktoři.txt`. Formát: Soubor `doktoři.txt` má nyní řádky ve formátu jako `JménoDoktora Dny`, kde `Dny` jsou volitelné a jsou to čísla dnů v týdnu, kdy je doktor neustále nepřítomný z důvodu absence.
Např. řádek `Jára 345` znamená, že Jára bude chybět každou středu, čtvrtek a pátek v měsíci z důvodu absence.
3) Přidána nabídka pro výběr měsíce. Defaultní je aktuální měsíc. Předdefinované absence se automaticky aplikují na vybraný měsíc.
4) Přidána funkcionalita pro výběr uloženého rozpisu. Rozpisy se nyní při vygenerování ukládají se svým datem i časem a nepřepisují se.
5) Přidáno tlačítko `Uložit rozpis` pro uložení rozpracovaného rozpisu bez nutnosti generování pdf.
6) Přidáno tlačítko `Vyčistit rozpis`, které smaže všechny absence v rozpise.
7) Přidáno tlačítko `Zpět`, vrátí poslední změnu učiněnou v rozpise.