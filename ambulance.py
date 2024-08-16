import os
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from fpdf import FPDF
import datetime
from PIL import Image, ImageTk, ImageOps

# Získání aktuálního adresáře skriptu
script_dir = os.path.dirname(os.path.abspath(__file__))

# Cesty k souborům
doctors_file = os.path.join(script_dir, 'doktoři.txt')
image_file = os.path.join(script_dir, 'grandma.png')

# Generování rozpisu
def generovat_rozpis():
    aktualizovat_rozpis()
    uloz_do_pdf(rozpis_data)
    uloz_text_do_souboru()  # Uložení textového rozpisu pouze při generování PDF

# Načítání seznamu doktorů
def nacti_doktory():
    try:
        with open(doctors_file, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        messagebox.showerror("Chyba", "Soubor 'doktoři.txt' nebyl nalezen.")
        return []

# Zobrazení posledního rozpisu
def zobrazit_posledni():
    try:
        nacti_text_ze_souboru()  # Načte poslední uložený rozpis
    except Exception as e:
        messagebox.showerror("Chyba", f"Nelze načíst poslední rozpis: {e}")

# Načtení textového rozpisu ze souboru
def nacti_text_ze_souboru():
    global absences
    try:
        with open('rozpis.txt', 'r', encoding='utf-8') as file:
            text.delete('1.0', tk.END)
            content = file.read()
            text.insert(tk.END, content)
            
            # Parsování rozpisu pro obnovení absencí
            lines = content.splitlines()
            header = lines[0].strip().split()  # První řádek s názvy doktorů a sloupce "Slouží"
            doctors_from_file = header[1:-1]  # Jména doktorů bez sloupce Datum a Slouží
            
            for line in lines[1:]:  # Přeskakujeme hlavičku
                if len(line.strip()) == 0:
                    continue  # Přeskočíme prázdné řádky

                # Rozdělení řádku na základě pevné šířky
                date_str = line[:6].strip()  # Datum je prvních 6 znaků
                try:
                    date = datetime.datetime.strptime(date_str, "%d.%m.").replace(year=datetime.date.today().year).date()
                except ValueError:
                    continue  # Pokud datum není správně naformátováno, přeskočíme tento řádek

                if date not in absences:
                    absences[date] = {}

                # Přiřazení hodnot doktorům
                for i, doctor in enumerate(doctors_from_file):
                    start_index = 15 + i * 10  # Start index pro každého doktora
                    end_index = start_index + 10  # Konec indexu pro každého doktora
                    absence_value = line[start_index:end_index].strip()
                    absences[date][doctor] = absence_value if absence_value else ""
                
                # Zpracování hodnoty sloupce "Slouží"
                slouzi_value = line[-10:].strip()
                absences[date]['Slouží'] = slouzi_value

            # Výpis obsahu proměnné absences pro kontrolu
            print("Po načtení souboru 'rozpis.txt':")
            for date, absence in absences.items():
                print(f"{date}: {absence}")
                
    except FileNotFoundError:
        messagebox.showinfo("Info", "Žádný uložený rozpis nebyl nalezen.")




# Uložení textového rozpisu do souboru
def uloz_do_pdf(data):
    # Získání aktuálního datumu a času ve formátu den.mesic.rok_hodina:minuta:vterina
    current_time = datetime.datetime.now().strftime("%d.%m.%Y_%H-%M-%S")
    
    # Vytvoření názvu souboru s datem a časem
    pdf_filename = f"rozpis_{current_time}.pdf"
    
    # Generování PDF
    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", size=8)
    
    # Nastavení šířky buněk
    margin = 10
    table_width = pdf.w - 2 * margin
    cell_width = table_width / (len(doctors) + 2)
    
    # První řada: jména doktorů
    pdf.cell(cell_width, 8, "", border=1)
    for doctor in doctors:
        pdf.cell(cell_width, 8, doctor, border=1, align='C')
    pdf.cell(cell_width, 8, "Slouží", border=1, align='C')
    pdf.ln(8)
    
    # Levý sloupec: dny v měsíci
    for date in data:
        day_str = date.strftime("%d.%m.") + " " + days[date.weekday()]
        
        # Nastavení šedého pozadí pro víkendy
        if date.weekday() >= 5:
            pdf.set_fill_color(211, 211, 211)  # Světle šedá barva pro víkendy
        else:
            pdf.set_fill_color(255, 255, 255)  # Bílá barva pro běžné dny
        
        pdf.cell(cell_width, 8, day_str, border=1, fill=True)
        
        count_slouzi = 0
        for doctor in doctors:
            # Nastavení šedého pozadí pro celý řádek o víkendech
            if date.weekday() >= 5:
                pdf.set_fill_color(211, 211, 211)  # Světle šedá barva
            elif doctor == "Jára":  # Šedá barva pro sloupec Jára
                pdf.set_fill_color(211, 211, 211)  # Světle šedá barva
            else:
                pdf.set_fill_color(255, 255, 255)  # Bílá barva
            
            if doctor in data[date] and data[date][doctor] == "":
                count_slouzi += 1
            pdf.cell(cell_width, 8, data[date].get(doctor, ""), border=1, align='C', fill=True)
        
        # Nastavení barvy zpět pro buňku "Slouží"
        pdf.set_fill_color(255, 255, 255)
        pdf.cell(cell_width, 8, str(count_slouzi), border=1, align='C', fill=True)
        pdf.ln(8)
    
    # Přidání popisku pod tabulku
    pdf.ln(5)  # Přidání menšího prázdného řádku
    pdf.set_font("DejaVu", size=8)
    popisek = "Popis symbolů absence: D - Dovolená, S - Po službě, X - Absence, B - Bronchoskopie"
    pdf.cell(0, 10, popisek, ln=True, align='C')
    
    # Uložení souboru s dynamickým názvem
    pdf.output(pdf_filename)
    messagebox.showinfo("Info", f"Rozpis byl úspěšně uložen jako {pdf_filename}")

# Načtení doktorů
doctors = nacti_doktory()

# Hlavní okno
root = tk.Tk()
root.title("Aplikace pro ambulanci")
root.geometry("1250x1000")

# Frame pro základní informace
frame_info = ttk.Frame(root, padding="10")
frame_info.grid(row=0, column=0, sticky="ew")

# Výběr doktora
doctor_label = ttk.Label(frame_info, text="Vyberte doktora:")
doctor_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
doctor_combo = ttk.Combobox(frame_info, values=doctors)
doctor_combo.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

# Datum od
start_date_label = ttk.Label(frame_info, text="Datum od:")
start_date_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
start_date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd')
start_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

def resetovat_datum_do():
    end_date_entry.delete(0, 'end')

reset_btn = ttk.Button(frame_info, text="Resetovat Datum do", command=resetovat_datum_do)
reset_btn.grid(row=2, column=2, padx=5, pady=5, sticky="ew")

# Datum do
end_date_label = ttk.Label(frame_info, text="Datum do:")
end_date_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
end_date_entry = DateEntry(frame_info, date_pattern='yyyy-mm-dd')
end_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Výběr důvodu nepřítomnosti
reason_label = ttk.Label(frame_info, text="Vyberte důvod nepřítomnosti:")
reason_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
reason_var = tk.StringVar(value="")
reasons = [("Dovolená", "D"), ("Po službě", "S"), ("Absence", "X"), ("Bronchoskopie", "B")]
for i, (text, mode) in enumerate(reasons):
    ttk.Radiobutton(frame_info, text=text, variable=reason_var, value=mode).grid(row=4+i, column=1, padx=5, pady=5, sticky="w")

# Seznam nepřítomností
absences = {}

# Přidání nepřítomnosti
def pridat_nepritomnost():
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


pridat_btn = ttk.Button(frame_info, text="Přidat nepřítomnost", command=pridat_nepritomnost)
pridat_btn.grid(row=8, column=1, padx=5, pady=10, sticky="ew")

odstranit_btn = ttk.Button(frame_info, text="Odstranit nepřítomnost", command=odstranit_nepritomnost)
odstranit_btn.grid(row=9, column=1, padx=5, pady=10, sticky="ew")

# Frame pro rozpis
frame_rozpis = ttk.Frame(root, padding="10")
frame_rozpis.grid(row=1, column=0, sticky="nsew")

# Textové pole pro zobrazení rozpisu
text = tk.Text(frame_rozpis, height=20, width=80, font=("Courier New", 12))
text.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

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
    text.configure(font=new_font)
    doctor_label.configure(font=new_font)
    doctor_combo.configure(font=new_font)
    start_date_label.configure(font=new_font)
    start_date_entry.configure(font=new_font)
    end_date_label.configure(font=new_font)
    reason_label.configure(font=new_font)
    for widget in frame_info.winfo_children():
        if isinstance(widget, ttk.Radiobutton):
            widget.configure(font=new_font)
    pridat_btn.configure(font=new_font)
    odstranit_btn.configure(font=new_font)
    generovat_btn.configure(font=new_font)
    zobrazit_btn.configure(font=new_font)
    zvetsit_btn.configure(font=new_font)
    zmensit_btn.configure(font=new_font)
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
                
                # Aktualizace proměnné absences na základě nově načteného rozpisu
                nacti_text_ze_souboru()
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


def aktualizovat_rozpis(zobrazit_mesic=None):
    global rozpis_data
    today = datetime.date.today()
    first_day_next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    start_date = first_day_next_month
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    dates = pd.date_range(start_date, end_date).to_pydatetime()

    for date in dates:
        date_only = date.date()
        if date_only not in rozpis_data:
            rozpis_data[date_only] = {}
        for doctor in doctors:
            if date_only in absences and doctor in absences[date_only]:
                rozpis_data[date_only][doctor] = absences[date_only][doctor]
            elif doctor not in rozpis_data[date_only]:
                rozpis_data[date_only][doctor] = ""

    # Výpis obsahu proměnné rozpis_data
    print("Po aktualizaci rozpisu:")
    for date, data in rozpis_data.items():
        print(f"{date}: {data}")


    # Zachováme stará data a přidáme nová
    for date in dates:
        date_only = date.date()  # Konverze datetime na date
        if date_only not in rozpis_data:
            rozpis_data[date_only] = {}
        for doctor in doctors:
            if date_only in absences and doctor in absences[date_only]:
                rozpis_data[date_only][doctor] = absences[date_only][doctor]
            elif doctor not in rozpis_data[date_only]:
                rozpis_data[date_only][doctor] = ""
    
    # Zobrazení rozpisu
    text.delete('1.0', tk.END)
    header = "Datum".ljust(15) + "".join([center_text(d, 10) for d in doctors]) + center_text("Slouží", 10)
    text.insert(tk.END, header + "\n", "big_font")
    for date in sorted(rozpis_data):
        if zobrazit_mesic is None or date.month == zobrazit_mesic:
            day_str = date.strftime("%d.%m.") + " " + days[date.weekday()]
            if date.weekday() >= 5:  # Víkendy
                text.insert(tk.END, day_str.ljust(15), ("big_font", "weekend"))
            else:
                text.insert(tk.END, day_str.ljust(15), "big_font")
            count_slouzi = 0
            for doctor in doctors:
                tag = ("big_font", "weekend", "jara") if date.weekday() >= 5 and doctor == "Jára" else \
                      ("big_font", "weekend") if date.weekday() >= 5 else \
                      ("big_font", "jara") if doctor == "Jára" else "big_font"
                if doctor in rozpis_data[date] and rozpis_data[date][doctor] == "":
                    count_slouzi += 1
                text.insert(tk.END, center_text(rozpis_data[date].get(doctor, ""), 10), tag)
            text.insert(tk.END, center_text(str(count_slouzi), 10), "big_font")
            text.insert(tk.END, "\n")

# Inicializace zobrazení rozpisu při startu aplikace
text_size = 12
aktualizovat_rozpis()

# Nastavení prázdné hodnoty pro datum při startu aplikace
start_date_entry.delete(0, 'end')
end_date_entry.delete(0, 'end')

root.mainloop()