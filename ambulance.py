import sys
import os
import glob
import re
import tkinter as tk
from babel import numbers
from tkinter import filedialog
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from fpdf import FPDF
import datetime
from PIL import Image, ImageTk, ImageOps

first_doctor = None

def get_resource_path(relative_path):
    """Získá absolutní cestu k souboru pro balenou aplikaci nebo během vývoje."""
    try:
        # Pokud je aplikace zabalena, bude cesta k souborům uložena v _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Během vývoje použijte aktuální adresář skriptu
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Cesty k souborům s použitím funkce get_resource_path
doctors_file = get_resource_path('doktoři.txt')
image_file = get_resource_path('grandma.png')

def generovat_rozpis():
    selected_month = months.index(month_combo.get()) + 1  # Získání aktuálně vybraného měsíce z comboboxu
    selected_year = int(year_combo.get())  # Explicitně načteme rok z year_combo

    aktualizovat_rozpis(zobrazit_mesic=selected_month)
    uloz_do_pdf(rozpis_data, selected_month, selected_year)  # Předání roku
    uloz_text_do_souboru(selected_month, selected_year)  # Předání roku


# Seznam nepřítomností
absences = {}

# Inicializace globální proměnné rozpis_data
rozpis_data = {}

# Funkce pro načtení doktorů a nastavení absencí na základě souboru doktoři.txt
def nacti_doktory(selected_year=None):
    global absences, rozpis_data, first_doctor
    doctors_list = []
    day_mapping = {'1': 0, '2': 1, '3': 2, '4': 3, '5': 4, '6': 5, '7': 6}  # Mapa čísel na dny v týdnu
    if not selected_year:
        selected_year = datetime.date.today().year

    first_doctor_absences = set()  # Přidáno pro sledování absencí prvního doktora

    # Seznam státních svátků
    statni_svatky = [
        datetime.date(selected_year, 1, 1),   # Nový rok
        datetime.date(selected_year, 5, 1),   # Svátek práce
        datetime.date(selected_year, 5, 8),   # Den vítězství
        datetime.date(selected_year, 7, 5),   # Den slovanských věrozvěstů Cyrila a Metoděje
        datetime.date(selected_year, 7, 6),   # Den upálení mistra Jana Husa
        datetime.date(selected_year, 9, 28),  # Den české státnosti
        datetime.date(selected_year, 10, 28), # Den vzniku samostatného československého státu
        datetime.date(selected_year, 11, 17), # Den boje za svobodu a demokracii
        datetime.date(selected_year, 12, 24), # Štědrý den
        datetime.date(selected_year, 12, 25), # 1. svátek vánoční
        datetime.date(selected_year, 12, 26), # 2. svátek vánoční
    ]

    try:
        with open(doctors_file, 'r', encoding='utf-8') as file:
            for idx, line in enumerate(file.readlines()):
                parts = line.strip().split()
                doctor = parts[0]
                doctors_list.append(doctor)
                
                if idx == 0:  # Uložení prvního doktora
                    first_doctor = doctor
                
                if len(parts) > 1:
                    days_off = parts[1]
                    for day_char in days_off:
                        if day_char in day_mapping:
                            day_num = day_mapping[day_char]
                            for month in range(1, 13):
                                first_day_of_month = datetime.date(selected_year, month, 1)
                                last_day_of_month = (first_day_of_month.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
                                current_date = first_day_of_month
                                
                                while current_date <= last_day_of_month:
                                    if current_date.weekday() == day_num or current_date in statni_svatky:
                                        if current_date not in absences:
                                            absences[current_date] = {}
                                        absences[current_date][doctor] = "X"  # Značení absence
                                        if current_date in rozpis_data:
                                            rozpis_data[current_date][doctor] = "X"
                                        else:
                                            rozpis_data[current_date] = {doctor: "X"}
                                    current_date += datetime.timedelta(days=1)
        
        # Absence pro víkendy a státní svátky pro všechny doktory
        for month in range(1, 13):
            first_day_of_month = datetime.date(selected_year, month, 1)
            last_day_of_month = (first_day_of_month.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
            current_date = first_day_of_month
            while current_date <= last_day_of_month:
                if current_date.weekday() >= 5 or current_date in statni_svatky:
                    for doctor in doctors_list:
                        if current_date not in absences:
                            absences[current_date] = {}
                        absences[current_date][doctor] = "X"
                        if current_date in rozpis_data:
                            rozpis_data[current_date][doctor] = "X"
                        else:
                            rozpis_data[current_date] = {doctor: "X"}
                current_date += datetime.timedelta(days=1)

    except FileNotFoundError:
        messagebox.showerror("Chyba", "Soubor 'doktoři.txt' nebyl nalezen.")
    
    return doctors_list


# Načtení doktorů a inicializace absencí
doctors = nacti_doktory()

# Funkce pro zobrazení posledního rozpisu
def zobrazit_posledni():
    try:
        # Najdeme všechny soubory, které odpovídají vzoru rozpis_*.txt
        soubory = glob.glob('rozpis_*.txt')
        
        if not soubory:
            messagebox.showinfo("Info", "Žádný uložený rozpis nebyl nalezen.")
            return
        
        # Extrahujeme měsíc, rok a datum editace
        rozpis_soubory = []
        for soubor in soubory:
            match = re.search(r'rozpis_(\d{2})_(\d{4})_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})', soubor)
            if match:
                mesic = int(match.group(1))
                rok = int(match.group(2))
                datum_editace = match.group(3)
                rozpis_soubory.append((datum_editace, rok, mesic, soubor))
        
        if not rozpis_soubory:
            messagebox.showinfo("Info", "Žádný platný rozpis nebyl nalezen.")
            return
        
        # Seřadíme soubory podle data a času editace (sestupně)
        rozpis_soubory.sort(reverse=True, key=lambda x: x[0])
        
        # Vybereme nejnovější soubor
        _, nejnovější_rok, nejnovější_mesic, posledni_soubor = rozpis_soubory[0]
        
        # Načteme obsah posledního souboru
        with open(posledni_soubor, 'r', encoding='utf-8') as file:
            content = file.read()
            text.config(state=tk.NORMAL)
            text.delete('1.0', tk.END)
            text.insert(tk.END, content)
            text.config(state=tk.DISABLED)
        
        # Nastavíme comboboxy
        year_combo.set(nejnovější_rok)
        month_combo.current(nejnovější_mesic - 1)
        
        # Aktualizujeme rozpis
        aktualizovat_rozpis(zobrazit_mesic=nejnovější_mesic)
    
    except Exception as e:
        messagebox.showerror("Chyba", f"Nelze načíst poslední rozpis: {e}")


# Načtení textového rozpisu ze souboru
def nacti_text_ze_souboru():
    global absences, rozpis_data
    try:
        with open('rozpis.txt', 'r', encoding='utf-8') as file:
            text.delete('1.0', tk.END)
            content = file.read()
            text.insert(tk.END, content)
            
            # Parsování rozpisu pro obnovení absencí a doktorů
            lines = content.splitlines()
            header = lines[0].strip().split()  # První řádek s názvy doktorů a sloupce "Slouží"
            doctors_from_file = header[1:-1]  # Jména doktorů bez sloupce Datum a Slouží
            
            absences.clear()  # Vymažeme staré absence
            rozpis_data.clear()  # Vymažeme starý rozpis

            for line in lines[1:]:  # Přeskakujeme hlavičku
                if len(line.strip()) == 0:
                    continue  # Přeskočíme prázdné řádky

                # Rozdělení řádku na základě pevné šířky
                date_str = line[:6].strip()  # Datum je prvních 6 znaků
                try:
                    date = datetime.datetime.strptime(date_str, "%d.%m.").replace(year=datetime.date.today().year).date()
                except ValueError:
                    continue  # Pokud datum není správně naformátováno, přeskočíme tento řádek

                absences[date] = {}
                rozpis_data[date] = {}

                # Přiřazení hodnot doktorům
                for i, doctor in enumerate(doctors_from_file):
                    start_index = 15 + i * 10  # Start index pro každého doktora
                    end_index = start_index + 10  # Konec indexu pro každého doktora
                    absence_value = line[start_index:end_index].strip()
                    absences[date][doctor] = absence_value if absence_value else ""
                    rozpis_data[date][doctor] = absence_value if absence_value else ""

                # Zpracování hodnoty sloupce "Slouží"
                slouzi_value = line[-10:].strip()
                absences[date]['Slouží'] = slouzi_value

            # Aktualizace zobrazení v GUI
            aktualizovat_rozpis()

    except FileNotFoundError:
        messagebox.showinfo("Info", "Žádný uložený rozpis nebyl nalezen.")


# Funkce pro uložení rozpisu do textového souboru
def uloz_text_do_souboru(zobrazit_mesic, selected_year):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Datum a čas uložení souboru
    
    # Správný formát názvu souboru
    text_filename = f"rozpis_{zobrazit_mesic:02d}_{selected_year}_{current_time}.txt"

    try:
        with open(text_filename, 'w', encoding='utf-8') as file:
            lines = text.get('1.0', tk.END).splitlines()
            for line in lines:
                if f".{zobrazit_mesic:02d}." in line:  # Uložíme jen řádky odpovídající zvolenému měsíci
                    file.write(line + "\n")
        messagebox.showinfo(
            "Info",
            f"Rozpis pro {months[zobrazit_mesic - 1]} {selected_year} byl úspěšně uložen jako {text_filename}"
        )
    except Exception as e:
        messagebox.showerror("Chyba", f"Nepodařilo se uložit soubor: {e}")



# Uložení textového rozpisu do souboru
# Funkce pro uložení rozpisu do PDF
def uloz_do_pdf(data, mesic, selected_year):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pdf_filename = f"rozpis_{mesic:02d}_{selected_year}_{current_time}.pdf"

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=8)

    margin = 10
    table_width = pdf.w - 2 * margin
    cell_width = table_width / (len(doctors) + 2)

    # Hlavička tabulky
    pdf.cell(cell_width, 8, "", border=1)
    for doctor in doctors:
        pdf.cell(cell_width, 8, doctor, border=1, align='C')
    pdf.cell(cell_width, 8, "Slouží", border=1, align='C')
    pdf.ln(8)

    # Řádky s daty
    for date in sorted(data.keys()):
        if date.month == mesic and date.year == selected_year:
            is_weekend = date.weekday() >= 5
            pdf.set_fill_color(211, 211, 211) if is_weekend else pdf.set_fill_color(255, 255, 255)

            day_str = date.strftime("%d.%m.") + " " + days[date.weekday()]
            pdf.cell(cell_width, 8, day_str, border=1, fill=True)

            count_slouzi = 0
            for doctor in doctors:
                absence_value = data[date].get(doctor, "")

                # Podmínka pro zašedění hlavního doktora
                if is_main_doctor.get() and doctor == first_doctor:
                    pdf.set_fill_color(211, 211, 211)  # Šedá barva pro hlavního doktora
                elif is_weekend:
                    pdf.set_fill_color(211, 211, 211)  # Šedá barva pro víkend
                else:
                    pdf.set_fill_color(255, 255, 255)  # Bílá pro běžné dny

                pdf.cell(cell_width, 8, absence_value, border=1, align='C', fill=True)
                
                if absence_value == "":
                    count_slouzi += 1

            pdf.cell(cell_width, 8, str(count_slouzi), border=1, align='C', fill=True)
            pdf.ln(8)

    # Popis symbolů
    popisek = "Popis symbolů absence: D - Dovolená, S - Po službě, X - Absence, N - Ve službě, ale ne v ambulanci"
    pdf.cell(0, 10, popisek, ln=True, align='C')

    # Uložení PDF souboru
    pdf.output(pdf_filename)
    messagebox.showinfo("Info", f"PDF pro {months[mesic - 1]} {selected_year} bylo úspěšně uloženo jako {pdf_filename}")


# Hlavní okno
root = tk.Tk()
root.title("Aplikace pro ambulanci")
root.geometry("1600x1200")

# Frame pro základní informace
frame_info = ttk.Frame(root, padding="10")
frame_info.grid(row=0, column=0, sticky="ew")

months = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"]

# Výběr roku
#year_label = ttk.Label(frame_info, text="Vyberte rok:")
#year_label.grid(row=0, column=2, padx=5, pady=5, sticky="w")


def on_year_change(event):
    selected_year = int(year_combo.get())
    global doctors
    absences.clear()
    rozpis_data.clear()
    doctors = nacti_doktory(selected_year)  # Načteme doktory pro nový rok
    selected_month = months.index(month_combo.get()) + 1
    aktualizovat_rozpis(zobrazit_mesic=selected_month)


current_year = datetime.date.today().year
year_combo = ttk.Combobox(frame_info, values=[current_year, current_year + 1])
year_combo.grid(row=0, column=2, padx=5, pady=5, sticky="ew")
year_combo.current(0)  # Přednastavíme aktuální rok
year_combo.bind("<<ComboboxSelected>>", on_year_change)

# Funkce pro zpracování změny měsíce
def on_month_change(event):
    selected_month = months.index(month_combo.get()) + 1  # Získání indexu vybraného měsíce (leden = 1)
    aktualizovat_rozpis(zobrazit_mesic=selected_month)

# Přidání comboboxu pro výběr měsíce do frame_info
month_label = ttk.Label(frame_info, text="Vyberte měsíc:")
month_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

month_combo = ttk.Combobox(frame_info, values=months)
month_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
month_combo.current(datetime.date.today().month - 1)  # Přednastavení na aktuální měsíc
month_combo.bind("<<ComboboxSelected>>", on_month_change)

# Výběr doktora
doctor_label = ttk.Label(frame_info, text="Vyberte doktora:")
doctor_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
doctor_combo = ttk.Combobox(frame_info, values=doctors)
doctor_combo.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

# Globální proměnná pro sledování stavu hlavního doktora
is_main_doctor = tk.BooleanVar(value=True)

# Checkbox pro volbu hlavního doktora
main_doctor_checkbox = ttk.Checkbutton(
    frame_info, text="Chci prvního doktora ze souboru doktoři jako hlavního", variable=is_main_doctor, command=lambda: aktualizovat_rozpis(zobrazit_mesic=months.index(month_combo.get()) + 1)
)
main_doctor_checkbox.grid(row=1, column=2, padx=5, pady=5, sticky="w")


# Datum od
start_date_label = ttk.Label(frame_info, text="Datum od:")
start_date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
start_date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd')
start_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Datum do
end_date_label = ttk.Label(frame_info, text="Datum do:")
end_date_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
end_date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd')
end_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

# Funkce pro resetování Datum do
def resetovat_datum_do():
    end_date_entry.delete(0, 'end')

# Tlačítko pro resetování Datum do
reset_btn = ttk.Button(frame_info, text="Resetovat Datum do", command=resetovat_datum_do)
reset_btn.grid(row=3, column=2, padx=5, pady=5, sticky="ew")

# Výběr důvodu nepřítomnosti
reason_label = ttk.Label(frame_info, text="Vyberte důvod nepřítomnosti:")
reason_label.grid(row=4, column=0, padx=5, pady=5, sticky="w")

reason_var = tk.StringVar(value="")

reasons = [("Dovolená", "D"), ("Po službě", "S"), ("Absence", "X"), ("Ve službě, ale ne na ambulanci", "N")]
# Umístění prvního rádiového tlačítka na stejný řádek jako popisek
ttk.Radiobutton(frame_info, text=reasons[0][0], variable=reason_var, value=reasons[0][1]).grid(row=4, column=1, padx=5, pady=5, sticky="w")

# Umístění zbývajících rádiových tlačítek na další řádky
for i, (text, mode) in enumerate(reasons[1:]):  # začínáme od druhého prvku seznamu
    ttk.Radiobutton(frame_info, text=text, variable=reason_var, value=mode).grid(row=5+i, column=1, padx=5, pady=5, sticky="w")


# Seznam nepřítomností
absences = {}

# Přidání nepřítomnosti
def pridat_nepritomnost():
    ulozit_do_historie()
    doctor = doctor_combo.get()
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date() if end_date_entry.get() else start_date
    reason = reason_var.get()
    if doctor and start_date and reason:
        current_date = start_date
        while current_date <= end_date:
            if current_date not in absences:
                absences[current_date] = {}
            absences[current_date][doctor] = reason
            
            if current_date in rozpis_data:
                rozpis_data[current_date][doctor] = reason
            else:
                rozpis_data[current_date] = {doctor: reason}
                
            current_date += datetime.timedelta(days=1)
        aktualizovat_rozpis(start_date.month)
    else:
        messagebox.showwarning("Varování", "Vyberte doktora, datum a důvod nepřítomnosti.")



def odstranit_nepritomnost():
    ulozit_do_historie()
    doctor = doctor_combo.get()
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date() if end_date_entry.get() else start_date  # Pokud je pole prázdné, použije se start_date

    if doctor and start_date and end_date:
        current_date = start_date
        while current_date <= end_date:
            # Odstranění z absences
            if current_date in absences and doctor in absences[current_date]:
                del absences[current_date][doctor]
                if not absences[current_date]:
                    del absences[current_date]
            
            # Odstranění z rozpis_data
            if current_date in rozpis_data and doctor in rozpis_data[current_date]:
                del rozpis_data[current_date][doctor]
                if not rozpis_data[current_date]:
                    del rozpis_data[current_date]

            current_date += datetime.timedelta(days=1)
        
        # Aktualizace zobrazení rozpisu po odstranění
        aktualizovat_rozpis(start_date.month)
    else:
        messagebox.showwarning("Varování", "Vyberte doktora a datum.")


# Tlačítka pro přidání a odstranění nepřítomnosti
pridat_btn = ttk.Button(frame_info, text="Přidat nepřítomnost", command=pridat_nepritomnost)
pridat_btn.grid(row=8, column=1, padx=5, pady=5, sticky="ew")

odstranit_btn = ttk.Button(frame_info, text="Odstranit nepřítomnost", command=odstranit_nepritomnost)
odstranit_btn.grid(row=9, column=1, padx=5, pady=5, sticky="ew")

# Frame pro rozpis
frame_rozpis = ttk.Frame(root, padding="10")
frame_rozpis.grid(row=1, column=0, sticky="nsew")

# Textové pole pro zobrazení rozpisu
text = tk.Text(frame_rozpis, height=20, width=80, font=("Courier New", 12))
text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

# Nastavení textového widgetu jako pouze pro čtení
text.config(state=tk.DISABLED)

# Nastavení pozadí pro víkendy
text.tag_configure("weekend", background="#D3D3D3")
# Nastavení pozadí pro sloupec "Jára"
text.tag_configure("jara", background="#D3D3D3")

# Funkce pro zvětšení a zmenšení textu
def zvetsit_text():
    global text_size
    text_size += 2
    aktualizovat_velikost_textu()

def zmensit_text():
    global text_size
    if text_size > 6:
        text_size -= 2
        aktualizovat_velikost_textu()

def aktualizovat_velikost_textu():
    new_font = ("Courier New", text_size)
    
    # Nastavení stylu pro tlačítka
    style = ttk.Style()
    style.configure("TButton", font=new_font)
    style.configure("TLabel", font=new_font)
    style.configure("TCombobox", font=new_font)
    style.configure("TRadiobutton", font=new_font)
    
    # Aktualizace fontu pro textové pole
    text.configure(font=new_font)
    
    # Aktualizace fontu pro všechny labely, combobox a entry
    doctor_label.configure(font=new_font)
    doctor_combo.configure(font=new_font)
    start_date_label.configure(font=new_font)
    start_date_entry.configure(font=new_font)
    end_date_label.configure(font=new_font)
    end_date_entry.configure(font=new_font)
    reason_label.configure(font=new_font)
    month_label.configure(font=new_font)
    month_combo.configure(font=new_font)
    
    # Aktualizace rozpisu
    aktualizovat_rozpis()



# Frame pro ovládací tlačítka
frame_controls = ttk.Frame(root, padding="10")
frame_controls.grid(row=0, column=1, sticky="ne")

# Tlačítka pro zvětšení a zmenšení textu
zvetsit_btn = ttk.Button(frame_controls, text="Zvětšit text", command=zvetsit_text)
zvetsit_btn.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
zmensit_btn = ttk.Button(frame_controls, text="Zmenšit text", command=zmensit_text)
zmensit_btn.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

# Načtení obrázku a jeho zobrazení
try:
    image = Image.open(image_file)  # Změňte na správnou cestu k obrázku, pokud je potřeba
    image = image.resize((200, 200), Image.LANCZOS)
    
    # Vytvoření barevného pozadí odpovídajícího barvě okna
    bg_color = 'white'  # Explicitně nastavíme bílou barvu
    background = Image.new('RGBA', image.size, bg_color)
    
    # Kombinace obrázku s pozadím
    image = Image.alpha_composite(background, image.convert('RGBA'))
    
    photo = ImageTk.PhotoImage(image)
    image_label = tk.Label(frame_controls, image=photo, bg=bg_color)
    image_label.image = photo  # Udržujte referenci, aby nedošlo ke garbage collection
    image_label.grid(row=2, column=0, padx=5, pady=5, sticky="ew")
except Exception as e:
    messagebox.showerror("Chyba", f"Nelze načíst obrázek: {e}")

# Zajištění, že frame_rozpis se nebude roztahovat s oknem
frame_rozpis.columnconfigure(0, weight=1)
frame_rozpis.rowconfigure(0, weight=1)

# Funkce pro uložení rozpracovaného rozpisu
def ulozit_rozpis():
    selected_month = months.index(month_combo.get()) + 1  # Získání aktuálně vybraného měsíce z comboboxu
    selected_year = int(year_combo.get())  # Explicitně načteme rok z year_combo
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # Datum a čas uložení souboru
    
    # Správný formát názvu souboru
    text_filename = f"rozpis_{selected_month:02d}_{selected_year}_{current_time}.txt"

    try:
        with open(text_filename, 'w', encoding='utf-8') as file:
            lines = text.get('1.0', tk.END).splitlines()
            for line in lines:
                if f".{selected_month:02d}." in line:  # Uložíme jen řádky odpovídající zvolenému měsíci
                    file.write(line + "\n")
        messagebox.showinfo(
            "Info",
            f"Rozpis pro {months[selected_month - 1]} {selected_year} byl úspěšně uložen jako {text_filename}"
        )
    except Exception as e:
        messagebox.showerror("Chyba", f"Nepodařilo se uložit soubor: {e}")


# Přidání tlačítka pro uložení rozpracovaného rozpisu
ulozit_btn = ttk.Button(frame_rozpis, text="Uložit rozpis", command=ulozit_rozpis)
ulozit_btn.grid(row=4, column=0, pady=5)

# Funkce pro vyčištění rozpisu
def vycistit_rozpis():
    ulozit_do_historie()
    selected_month = months.index(month_combo.get()) + 1  # Získání aktuálně vybraného měsíce z comboboxu
    
    # Projdeme všechny dny v rozpis_data pro zvolený měsíc a smažeme absence
    for date in list(rozpis_data.keys()):
        if date.month == selected_month:
            for doctor in doctors:
                rozpis_data[date][doctor] = ""  # Vymažeme hodnotu absence

    # Aktualizace GUI po vyčištění rozpisu
    aktualizovat_rozpis(zobrazit_mesic=selected_month)

# Přidání tlačítka pro vyčištění rozpisu
vycistit_btn = ttk.Button(frame_controls, text="Vyčistit rozpis", command=vycistit_rozpis)
vycistit_btn.grid(row=3, column=0, padx=5, pady=5, sticky="ew")

# Seznam pro uchovávání historie rozpisů
history = []

# Funkce pro uložení aktuálního stavu do historie
def ulozit_do_historie():
    global history
    # Uložíme hlubokou kopii rozpisu, abychom zachovali předchozí stav
    history.append({date: data.copy() for date, data in rozpis_data.items()})

# Funkce pro návrat zpět k předchozímu stavu rozpisu
def zpet_rozpis():
    global history, rozpis_data
    if len(history) > 0:
        # Obnovíme poslední stav z historie
        rozpis_data = history.pop()
        aktualizovat_rozpis(zobrazit_mesic=months.index(month_combo.get()) + 1)
    else:
        messagebox.showinfo("Info", "Žádné změny k vrácení zpět.")

# Přidání tlačítka pro návrat zpět
zpet_btn = ttk.Button(frame_controls, text="Zpět", command=zpet_rozpis)
zpet_btn.grid(row=4, column=0, padx=5, pady=5, sticky="ew")

# Tlačítko pro generování rozpisu
generovat_btn = ttk.Button(frame_rozpis, text="Generovat rozpis", command=generovat_rozpis)
generovat_btn.grid(row=1, column=0, pady=5)

# Tlačítko pro zobrazení posledního rozpisu
zobrazit_btn = ttk.Button(frame_rozpis, text="Zobrazit poslední rozpis", command=zobrazit_posledni)
zobrazit_btn.grid(row=2, column=0, pady=5)

def vybrat_a_nacist_rozpis():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                text.delete('1.0', tk.END)
                text.insert(tk.END, content)
                
                # Parsování rozpisu pro obnovení absencí a doktorů
                lines = content.splitlines()
                header = lines[0].strip().split()  # První řádek s názvy doktorů a sloupce "Slouží"
                
                absences.clear()  # Vymažeme staré absence
                rozpis_data.clear()  # Vymažeme starý rozpis

                for line in lines:
                    if len(line.strip()) == 0:
                        continue  # Přeskočíme prázdné řádky

                    # Rozdělení řádku na základě pevné šířky
                    date_str = line[:6].strip()  # Datum je prvních 6 znaků
                    try:
                        date = datetime.datetime.strptime(date_str, "%d.%m.").replace(year=datetime.date.today().year).date()
                    except ValueError:
                        continue  # Pokud datum není správně naformátováno, přeskočíme tento řádek

                    absences[date] = {}
                    rozpis_data[date] = {}

                    # Přiřazení hodnot doktorům na základě pevné pozice ve sloupci
                    for i, doctor in enumerate(doctors):
                        start_index = 15 + i * 10  # Start index pro každého doktora
                        end_index = start_index + 10  # Konec indexu pro každého doktora
                        absence_value = line[start_index:end_index].strip()
                        absences[date][doctor] = absence_value if absence_value else ""
                        rozpis_data[date][doctor] = absence_value if absence_value else ""

                    # Zpracování hodnoty sloupce "Slouží"
                    slouzi_value = line[-5:].strip()
                    rozpis_data[date]['Slouží'] = slouzi_value

                # Nastavení měsíce v comboboxu na základě načtených dat
                mesice = {date.month for date in rozpis_data.keys()}
                if len(mesice) == 1:
                    zvoleny_mesic = mesice.pop()
                else:
                    zvoleny_mesic = min(mesice)
                month_combo.current(zvoleny_mesic - 1)

                # Aktualizace zobrazení v GUI
                aktualizovat_rozpis(zobrazit_mesic=zvoleny_mesic)

        except Exception as e:
            messagebox.showerror("Chyba", f"Nelze načíst soubor: {e}")


#tlacitko pro vybrat rozpis
vybrat_btn = ttk.Button(frame_rozpis, text="Vybrat rozpis", command=vybrat_a_nacist_rozpis)
vybrat_btn.grid(row=3, column=0, pady=5)


# Zajištění, že hlavní okno se nebude roztahovat s oknem
root.columnconfigure(0, weight=1)
root.rowconfigure(1, weight=1)
frame_info.columnconfigure(1, weight=0)
frame_rozpis.columnconfigure(0, weight=1)
frame_rozpis.rowconfigure(0, weight=1)

# Funkce pro aktualizaci rozpisu
days = ["Po", "Út", "St", "Čt", "Pá", "So", "Ne"]

def center_text(text, width):
    if len(text) < width:
        padding = (width - len(text)) // 2
        return " " * padding + text + " " * (width - len(text) - padding)
    return text


# Inicializace globální proměnné rozpis_data
rozpis_data = {}


# Funkce pro aktualizaci rozpisu
def aktualizovat_rozpis(zobrazit_mesic=None):
    global rozpis_data
    selected_year = int(year_combo.get())  # Získáme vybraný rok
    today = datetime.date.today()

    if zobrazit_mesic is None:
        zobrazit_mesic = today.month

    # Vytvoření rozsahu pro zobrazení zvoleného měsíce a roku
    start_date = datetime.date(selected_year, zobrazit_mesic, 1)
    end_date = (start_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) - datetime.timedelta(days=1)
    dates = pd.date_range(start_date, end_date).to_pydatetime()

    # Inicializace dat pro všechny doktory v zvoleném roce a měsíci
    for date in dates:
        date_only = date.date()
        if date_only not in rozpis_data:
            rozpis_data[date_only] = {}
        for doctor in doctors:
            if doctor not in rozpis_data[date_only]:
                rozpis_data[date_only][doctor] = ""

    # Kontrola a aktualizace hlavního doktora
    if is_main_doctor.get():
        for date in dates:
            date_only = date.date()
            if first_doctor not in rozpis_data[date_only] or not rozpis_data[date_only][first_doctor]:
                rozpis_data[date_only][first_doctor] = "N"
    else:
        for date in dates:
            date_only = date.date()
            if first_doctor in rozpis_data[date_only] and rozpis_data[date_only][first_doctor] == "N":
                rozpis_data[date_only][first_doctor] = ""

    # Aktualizace zobrazení rozpisu v GUI
    text.config(state=tk.NORMAL)  # Povolit editaci
    text.delete('1.0', tk.END)
    header = "Datum".ljust(15) + "".join([center_text(d, 10) for d in doctors]) + center_text("Slouží", 10)
    text.insert(tk.END, header + "\n", "big_font")
    for date in sorted(rozpis_data):
        if date.month == zobrazit_mesic and date.year == selected_year:
            day_str = date.strftime("%d.%m.") + " " + days[date.weekday()]
            if date.weekday() >= 5:  # Víkendy
                text.insert(tk.END, day_str.ljust(15), ("big_font", "weekend"))
            else:
                text.insert(tk.END, day_str.ljust(15), "big_font")
            count_slouzi = 0
            for doctor in doctors:
                is_main = doctor == first_doctor and is_main_doctor.get()
                tag = ("big_font", "weekend", "jara") if date.weekday() >= 5 and is_main else \
                      ("big_font", "weekend") if date.weekday() >= 5 else \
                      ("big_font", "jara") if is_main else "big_font"
                if rozpis_data[date][doctor] == "":
                    count_slouzi += 1
                text.insert(tk.END, center_text(rozpis_data[date].get(doctor, ""), 10), tag)
            text.insert(tk.END, center_text(str(count_slouzi), 10), "big_font")
            text.insert(tk.END, "\n")
    text.config(state=tk.DISABLED)  # Znovu zakázat editaci



# Inicializace zobrazení rozpisu při startu aplikace
text_size = 12

# Získání aktuálního data
today = datetime.date.today()

# Určení následujícího měsíce a roku
if today.month == 12:
    # Pokud je prosinec, posuneme se na leden následujícího roku
    default_month = 1  # Leden
    default_year = today.year + 1  # Následující rok
else:
    # Jinak jen posuneme měsíc a rok zůstane stejný
    default_month = today.month + 1
    default_year = today.year

# Nastavení roku v ComboBoxu
year_combo.set(default_year)  # Nastavení na následující rok, pokud je prosinec
year_combo.event_generate("<<ComboboxSelected>>")  # Vygenerování události pro aktualizaci roku

# Načtení doktorů pro vybraný rok
doctors = nacti_doktory(selected_year=default_year)

# Nastavení měsíce v ComboBoxu
month_combo.current(default_month - 1)  # Nastavení následujícího měsíce (indexace od 0)

# Aktualizace rozpisu pro následující měsíc a rok
aktualizovat_rozpis(zobrazit_mesic=default_month)

# Nastavení prázdné hodnoty pro datum při startu aplikace
start_date_entry.delete(0, 'end')
end_date_entry.delete(0, 'end')

root.mainloop()
