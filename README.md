# Urban Land Record Management System

A Django-based academic project designed to integrate, standardize, and harmonize property records collected from multiple departmental data sources.

## About the Project

Urban Land Record Management System aims to provide a centralized platform for managing property-related information from different departments.

Different departments may maintain separate records for the same property. These records can contain inconsistent property names, addresses, ownership details, and other information.

This project aims to bring these records together, identify matching properties, detect conflicting information, and display consolidated property records.

The project uses dummy property data for demonstration and academic purposes.

## Project Objectives

- Integrate property records from multiple data sources.
- Standardize inconsistent names, addresses, and fields.
- Identify records belonging to the same property.
- Detect conflicting information between departments.
- Maintain consolidated property records.
- Allow manual property photo uploads.
- Display property locations and boundaries on an interactive map.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Django | Web application framework |
| SQLite | Database |
| HTML | Web page structure |
| CSS | Website styling |
| JavaScript | Frontend interactions |
| Bootstrap | UI components (planned) |
| Leaflet | Interactive property map (planned) |
| Pandas | Dataset processing (planned) |
| GeoPandas | Geospatial data processing (planned) |

## Project Modules

The project is planned to contain the following modules:

1. **Dashboard** – Overview of properties, uploaded datasets, matched records, and conflicts.
2. **User Authentication** – Simple dummy login and logout system for demonstration.
3. **Dataset Management** – Upload and manage CSV and GeoJSON datasets.
4. **Property Management** – Add, view, update, search, and manage property records and photos.
5. **Data Standardization** – Clean and normalize property information.
6. **Harmonization & Matching** – Match records from different departments.
7. **Conflict Management** – Identify and review inconsistent records.
8. **GIS / Property Map** – Display dummy property boundaries using an interactive map.

## Project Structure

```text
urban_land_management/
│
├── accounts/
│   ├── migrations/
│   ├── views.py
│   ├── urls.py
│   └── ...
│
├── dashboard/
│   ├── migrations/
│   ├── views.py
│   └── ...
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── templates/
│   ├── accounts/
│   │   └── login.html
│   ├── dashboard/
│   │   └── home.html
│   └── base.html
│
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── login.css
│   │   └── dashboard.css
│   ├── js/
│   └── images/
│
├── media/
│
├── .gitignore
├── requirements.txt
├── README.md
├── db.sqlite3
└── manage.py
```

*Note: The structure will expand as additional modules are developed. The database file and virtual environment are excluded from Git.*

## Installation and Setup

Follow these instructions to run the project on Windows.

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/urban-land-management.git
```

Replace `YOUR_USERNAME` with the GitHub account that owns the repository.

### 2. Open the project directory

```bash
cd urban-land-management
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

For Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

For Windows Command Prompt:

```cmd
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Apply database migrations

```bash
python manage.py migrate
```

### 7. Start the development server

```bash
python manage.py runserver
```

### 8. Open the website

Visit:

http://127.0.0.1:8000/

The development server should now be running.

## Current Development Status

The project is currently under development.

### Completed

- Django project setup.
- SQLite database configuration.
- Dummy login and logout functionality.
- Session-based login handling.
- Dashboard page setup.
- Separate CSS files for common styling, login, and dashboard.
- Git and GitHub repository setup.

### Planned

- Property Management.
- Dataset Upload and Management.
- Data Standardization.
- Record Harmonization and Matching.
- Conflict Detection and Management.
- Property Photo Upload.
- Interactive GIS Property Map.
- Dashboard statistics connected to actual database records.

## Database

SQLite is being used during the initial development phase to simplify setup.

The project will use fictional property records and sample datasets for demonstration.

## Important Notes

- This is an academic prototype, not an official government land-record system.
- All property records used for demonstration will be dummy data.
- The login system is intentionally kept simple for demonstration.
- The application is intended to run locally using Django's development server.
- Do not use real property ownership information.

## Contributors

Developed as an academic project.

Contributions and suggestions are welcome.

## License

This project is currently intended for academic and educational purposes.
