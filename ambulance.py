import os
import tkinter as tk
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
    uloz_text_do_souboru()
    uloz_nepritomnosti_do_souboru()

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
        nacti_text_ze_souboru()
    except Exception as e:
        messagebox.showerror("Chyba", f"Nelze načíst poslední rozpis: {e}")

# Načtení textového rozpisu ze souboru
def nacti_text_ze_souboru():
    try:
        with open('rozpis.txt', 'r', encoding='utf-8') as file:
            text.delete('1.0', tk.END)
            text.insert(tk.END, file.read())
        nacti_nepritomnosti_ze_souboru()
    except FileNotFoundError:
        messagebox.showinfo("Info", "Žádný uložený rozpis nebyl nalezen.")

# Uložení textového rozpisu do souboru
def uloz_text_do_souboru():
    with open('rozpis.txt', 'w', encoding='utf-8') as file:
        file.write(text.get('1.0', tk.END))

# Načtení nepřítomností ze souboru
def nacti_nepritomnosti_ze_souboru():
    global absences
    absences = {}
    try:
        with open('nepritomnosti.txt', 'r', encoding='utf-8') as file:
            for line in file:
                date_str, doctor, reason = line.strip().split(',')
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
                if date not in absences:
                    absences[date] = {}
                absences[date][doctor] = reason
    except FileNotFoundError:
        pass

# Uložení nepřítomností do souboru
def uloz_nepritomnosti_do_souboru():
    with open('nepritomnosti.txt', 'w', encoding='utf-8') as file:
        for date in absences:
            for doctor in absences[date]:
                file.write(f"{date},{doctor},{absences[date][doctor]}\n")

# Uložení rozpisu do PDF
def uloz_do_pdf(data):
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
        pdf.cell(cell_width, 8, day_str, border=1)
        count_slouzi = 0
        for doctor in doctors:
            if doctor in data[date] and data[date][doctor] == "":
                count_slouzi += 1
            pdf.cell(cell_width, 8, data[date].get(doctor, ""), border=1, align='C')
        pdf.cell(cell_width, 8, str(count_slouzi), border=1, align='C')
        pdf.ln(8)
    
    pdf.output("rozpis.pdf")
    messagebox.showinfo("Info", "Rozpis byl úspěšně uložen jako rozpis.pdf")

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
    end_date = end_date_entry.get_date()
    reason = reason_var.get()
    if doctor and start_date and end_date and reason:
        current_date = start_date
        while current_date <= end_date:
            if current_date not in absences:
                absences[current_date] = {}
            absences[current_date][doctor] = reason
            current_date += datetime.timedelta(days=1)
        messagebox.showinfo("Info", f"Nepřítomnost doktora {doctor} byla přidána od {start_date} do {end_date}.")
        aktualizovat_rozpis(start_date.month)
        uloz_nepritomnosti_do_souboru()
    else:
        messagebox.showwarning("Varování", "Vyberte doktora, datum a důvod nepřítomnosti.")

# Odstranění nepřítomnosti
def odstranit_nepritomnost():
    doctor = doctor_combo.get()
    start_date = start_date_entry.get_date()
    end_date = end_date_entry.get_date()
    if doctor and start_date and end_date:
        current_date = start_date
        while current_date <= end_date:
            if current_date in absences and doctor in absences[current_date]:
                del absences[current_date][doctor]
                if not absences[current_date]:
                    del absences[current_date]
            current_date += datetime.timedelta(days=1)
        messagebox.showinfo("Info", f"Nepřítomnost doktora {doctor} byla odstraněna od {start_date} do {end_date}.")
        aktualizovat_rozpis(start_date.month)
        uloz_nepritomnosti_do_souboru()
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
    end_date_entry.configure(font=new_font)
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

def aktualizovat_rozpis(zobrazit_mesic=None):
    global rozpis_data
    # Nastavení na následující měsíc
    today = datetime.date.today()
    first_day_next_month = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
    start_date = first_day_next_month
    end_date = (start_date + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
    dates = pd.date_range(start_date, end_date).to_pydatetime()
    
    rozpis_data = {date.date(): {doctor: "" for doctor in doctors} for date in dates}
    
    for date in absences:
        if date in rozpis_data:
            for doctor in absences[date]:
                rozpis_data[date][doctor] = absences[date][doctor]
    
    # Zobrazení rozpisu
    text.delete('1.0', tk.END)
    header = "Datum".ljust(15) + "".join([center_text(d, 10) for d in doctors]) + center_text("Slouží", 10)
    text.insert(tk.END, header + "\n", "big_font")
    for date in rozpis_data:
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
                text.insert(tk.END, center_text(rozpis_data[date][doctor], 10), tag)
            text.insert(tk.END, center_text(str(count_slouzi), 10), "big_font")
            text.insert(tk.END, "\n")

# Inicializace zobrazení rozpisu při startu aplikace
text_size = 12
aktualizovat_rozpis()

# Nastavení prázdné hodnoty pro datum při startu aplikace
start_date_entry.delete(0, 'end')
end_date_entry.delete(0, 'end')

root.mainloop()
