## Dokumentace pro Aplikační Rozpis Dostupnosti Doktorů

### Obsah

1. [Úvod](#úvod)
2. [Instalace](#instalace)
3. [Architektura](#architektura)
4. [Front-end](#front-end)
    - [Komponenty](#komponenty)
5. [Back-end](#back-end)
    - [API Endpoints](#api-endpoints)
6. [Databáze](#databáze)
7. [PDF Generování](#pdf-generování)
8. [Testování](#testování)
9. [Nasazení](#nasazení)

### Úvod

Tato aplikace slouží k správě dostupnosti doktorů v ambulanci, umožňuje zadávání jejich nepřítomnosti, generování měsíčních rozpisů a ukládání těchto rozpisů ve formátu PDF. Aplikace také umožňuje přístup k historickým rozpisům.

### Instalace

#### Předpoklady

- Node.js a npm
- Python a pip
- MongoDB nebo PostgreSQL

#### Krok za krokem

1. **Klonování repozitáře:**
    ```bash
    git clone https://github.com/your-repo/ambulance-schedule-app.git
    cd ambulance-schedule-app
    ```

2. **Instalace závislostí pro front-end:**
    ```bash
    cd frontend
    npm install
    ```

3. **Instalace závislostí pro back-end:**
    ```bash
    cd ../backend
    npm install
    ```

4. **Instalace závislostí pro PDF generátor:**
    ```bash
    cd ../pdf-generator
    pip install -r requirements.txt
    ```

5. **Nastavení databáze:**
   - Konfigurujte připojení k databázi v `backend/config.js`.

6. **Spuštění aplikace:**
    - Front-end:
      ```bash
      cd frontend
      npm start
      ```
    - Back-end:
      ```bash
      cd ../backend
      npm start
      ```
    - PDF generátor je volán back-endem při generování PDF.

### Architektura

Aplikace je rozdělena do tří hlavních částí:
1. **Front-end:** React.js aplikace, která poskytuje uživatelské rozhraní.
2. **Back-end:** Node.js server s Express.js, který spravuje API a komunikaci s databází.
3. **PDF Generátor:** Python skript, který generuje PDF soubory s rozpisy.

### Front-end

Front-end je postaven na React.js a obsahuje následující klíčové komponenty:

#### Komponenty

1. **AvailabilityForm:** Formulář pro zadávání dostupnosti doktorů.
    ```jsx
    import React, { useState } from 'react';

    function AvailabilityForm({ onSubmit }) {
      const [doctor, setDoctor] = useState('');
      const [date, setDate] = useState('');
      const [time, setTime] = useState('');

      const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit({ doctor, date, time });
      };

      return (
        <form onSubmit={handleSubmit}>
          <select value={doctor} onChange={(e) => setDoctor(e.target.value)}>
            <option value="">Select Doctor</option>
            <option value="Doctor A">Doctor A</option>
            <option value="Doctor B">Doctor B</option>
          </select>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          <input type="time" value={time} onChange={(e) => setTime(e.target.value)} />
          <button type="submit">Submit</button>
        </form>
      );
    }

    export default AvailabilityForm;
    ```

2. **CalendarView:** Komponenta pro zobrazení kalendáře a dostupnosti doktorů.
    ```jsx
    import React from 'react';

    function CalendarView({ schedule }) {
      return (
        <div>
          <h2>Monthly Schedule</h2>
          {/* Implement calendar view with the schedule data */}
        </div>
      );
    }

    export default CalendarView;
    ```

### Back-end

Back-end je postaven na Node.js a Express.js a obsahuje následující API endpointy:

#### API Endpoints

1. **Přidání dostupnosti:**
    ```http
    POST /availability
    Content-Type: application/json

    {
      "doctor": "Doctor A",
      "date": "2024-08-10",
      "time": "08:00"
    }
    ```

2. **Generování rozpisu:**
    ```http
    GET /generate-schedule
    Content-Type: application/pdf
    ```

#### Příklad kódu pro back-end

```javascript
const express = require('express');
const bodyParser = require('body-parser');
const { generatePDF } = require('./pdfGenerator');

const app = express();
app.use(bodyParser.json());

let availability = [];

app.post('/availability', (req, res) => {
  availability.push(req.body);
  res.status(201).send('Availability added');
});

app.get('/generate-schedule', (req, res) => {
  const pdf = generatePDF(availability);
  res.contentType('application/pdf');
  res.send(pdf);
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

### Databáze

Aplikace může používat buď MongoDB nebo PostgreSQL. Konfigurace připojení k databázi je v souboru `backend/config.js`. Databáze ukládá informace o dostupnosti doktorů a historii rozpisů.

### PDF Generování

PDF generování je implementováno v Pythonu pomocí knihovny ReportLab. Funkce `generate_pdf` generuje PDF soubor s měsíčním rozpisem.

#### Příklad kódu pro PDF generátor

```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(availability):
    pdf_file = 'schedule.pdf'
    c = canvas.Canvas(pdf_file, pagesize=A4)
    width, height = A4

    y = height - 50
    for item in availability:
        c.drawString(50, y, f"Doctor: {item['doctor']}, Date: {item['date']}, Time: {item['time']}")
        y -= 20

    c.save()
    with open(pdf_file, 'rb') as f:
        return f.read()
```

### Testování

Testování aplikace zahrnuje:

1. **Jednotkové testy:** Pro testování jednotlivých funkcí a komponent.
2. **Integrační testy:** Pro ověření správné komunikace mezi front-endem, back-endem a databází.
3. **End-to-End testy:** Pro simulaci uživatelského chování a ověření funkčnosti celého systému.

### Nasazení

Aplikaci lze nasadit na hostingové platformy jako Heroku nebo Vercel. Databázi lze nasadit na cloudové služby jako MongoDB Atlas nebo AWS RDS. 

1. **Nasazení front-endu:**
    - Například pomocí Vercel:
    ```bash
    vercel --prod
    ```

2. **Nasazení back-endu:**
    - Například pomocí Heroku:
    ```bash
    heroku create
    git push heroku main
    ```

3. **Nastavení databáze:**
    - Konfigurujte připojení k databázi v produkčním prostředí.

Tímto je dokumentace pro aplikaci pro ambulanci kompletní. Pokud budete mít jakékoli dotazy nebo potřebujete další pomoc, neváhejte se na mě obrátit.