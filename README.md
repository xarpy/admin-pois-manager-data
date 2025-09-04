# Admin PoIs Manager Data

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Django Version](https://img.shields.io/badge/Django-5.2-green.svg)](https://www.djangoproject.com/)

Project in Django to import **Points of Interest (PoIs)** from **CSV/JSON/XML** files and browse the data through Django Admin.

---

## 📚 Table of Contents

- [🚀 Installation](#-installation)
- [▶️ Running the App](#️-running-the-app)
- [📦 Importing Data (CLI)](#-importing-data-cli)
- [🛠 Admin Panel](#-admin-panel)
- [🐳 Running with Docker](#-running-with-docker)
- [📄 File Specifications](#-file-specifications)
  - [CSV](#csv)
  - [JSON](#json)
  - [XML](#xml)
- [🧱 Project Structure](#-project-structure)
- [🧪 Testing](#-testing)
- [📝 Assumptions \& Improvements](#-assumptions--improvements)
  - [Assumptions](#assumptions)
  - [Possible Improvements](#possible-improvements)
- [🤝 Contributing](#-contributing)
- [🪪 License](#-license)

---

## 🚀 Installation

Clone the repository and install dependencies:

```bash
git clone git@github.com:xarpy/django-admin-manager-data.git
cd django-admin-manager-data
python -m venv .venv && source .venv/bin/activate
pip install -r requirements/base.txt
```

Run database migrations and create an admin user:

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

## ▶️ Running the App

```bash
python manage.py runserver
```

- Admin: `http://127.0.0.1:8000/admin/`

---

## 📦 Importing Data (CLI)

Use the management command `import_poi_file` to import one or more files. **Globs** are supported.

```bash
# Single file
python manage.py import_poi_file data/pois.csv

# Multiple files and globs
python manage.py import_poi_file data/pois.csv data/london.json data/*.xml
```

- The command detects the type by the **suffix** (`.csv`, `.json`, `.xml`).
- **Duplication**: a PoI is identified by `external_id`. Repeated entries are **updated** (upsert).
- `ratings` accepts several formats:
  - JSON array: `“[4, 5, 3.5]”`
  - separated string: `“4|3;5, 4.5”`
  - single number: `“4.0”`

---

## 🛠 Admin Panel

Go to `http://127.0.0.1:8000/admin/` and log in with your superuser.

**List of PoIs fields displayed:**

- **PoI internal ID** (database id)
- **PoI name**
- **PoI external ID** (poi id)
- **PoI category**
- **Avg. rating** (calculated from `ratings`)

**Search filter:**

- By **Internal ID** (digit a uuid to exact search).
- By **external_id** (digit a integer to exact search).

**Field filter:**

- By **category** (text) and for **category** (text).

---

## 🐳 Running with Docker

> Adjust the service name in the command below if your `docker-compose.yml` uses something other than `backend`..

Build the containers:

```bash
docker compose up --build
```

Import the data **inside** to the container:

```bash
docker-compose exec backend python manage.py import_poi_file data/pois.csv
docker-compose exec backend python manage.py import_poi_file data/london.json
docker-compose exec backend python manage.py import_poi_file "data/*.xml"
```

Acess:

- Admin (local): `http://localhost/admin/` (We are using nginx as proxy)

Stop containers:

```bash
docker-compose down
```

---

## 📄 File Specifications

The PoIs files follow the structure below:

### CSV

```csv
poi_id, poi_name, poi_latitude, poi_longitude, poi_category, poi_ratings
```

### JSON

```json
[
    {
        "id": "6166590368",
        "name": "unser Laden, Familie Lackinger",
        "category": "convenience-store",
        "description": "dzpdfeldblkzqcxltrn",
        "coordinates": {
            "latitude": 48.008273899935716,
            "longitude": 16.2454885
        },
        "ratings": [
            2,
            2,
            3,
            3,
            4,
            5,
            2,
            2,
            4,
            1
        ]
    }
]
```

### XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<RECORDS>
  <DATA_RECORD>
    <pid>146612179</pid>
    <pname>Дзіцячы сад №34</pname>
    <pcategory>kindergarten</pcategory>
    <platitude>55.5390834275</platitude>
    <plongitude>28.6235719789</plongitude>
    <pratings>1,1,3,1,4,1,5,3,1,2</pratings>
  </DATA_RECORD>
</RECORDS>
```

---

## 🧱 Project Structure

```
In construction...
```

---

## 🧪 Testing

To run the tests:

```bash
pytest
```

---

## 📝 Assumptions & Improvements

### Assumptions

- `coordinates` in JSON can be a **list** `[lat, lon]` or an **object** `{latitude, longitude}`.
- `ratings` accepts JSON array, single number, or string separated by `, ; |`. Invalid values are ignored.
- Lat/Lon stored as `FloatField`. We do not use GeoDjango to keep the setup simple.

### Possible Improvements

- All improvements are listed on this [board](https://trello.com/invite/b/68b79efc18b4c5b5f55ec0ef/ATTI0a769da9e60344a9e82c429fe9f2a0c2963B6985/th-searchsmartly).
- Feel free to open an issue on this repo, to add, request or report a bug.

---

## 🤝 Contributing

To create a Pull Request, we asking to follow the best for it, in this case we recommend to follow the git convention and Angular recommendations for it:

- [Git commit conventions](https://www.conventionalcommits.org/en/v1.0.0/);
- [Angular recommendations](https://nitayneeman.com/blog/understanding-semantic-commit-messages-using-git-and-angular/);

Based on that, feel free to open issues or PRs:

```bash
git checkout -b feature/your-feature
git commit -m "feat: add your feature"
git push origin feature/your-feature
```

Open a Pull Request.

---

## 🪪 License

MIT License. Take a look on the file `LICENSE`.
