# Smart File Duplicate Detector

A simple web application built with **Python Flask** that scans folders and detects duplicate files using **SHA-256 hashing**. The application helps users identify duplicate files and save storage space.

## Features

- Scan any folder
- Detect duplicate files
- SHA-256 hash comparison
- View duplicate file details
- Scan history stored in MySQL
- Responsive Bootstrap UI

## Tech Stack

### Frontend
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Bootstrap Icons
- Inter Font

### Backend
- Python
- Flask
- hashlib
- os
- pathlib

### Database
- MySQL

## Installation

1. Clone the repository

```bash
git clone https://github.com/your-username/Smart-File-Duplicate-Detector.git
```

2. Open the project folder

```bash
cd Smart-File-Duplicate-Detector
```

3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Create the MySQL database and required tables.

5. Update your database credentials in `config.py`.

6. Run the application

```bash
python app.py
```

7. Open your browser

```
http://127.0.0.1:5000
```

## Project Structure

```
Smart-File-Duplicate-Detector/
│
├── app.py
├── config.py
├── requirements.txt
├── scanner/
├── templates/
├── static/
├── database/
└── README.md
```

## Future Improvements

- Delete duplicate files
- Export scan report
- Dark mode
- Drag & Drop folder selection
- Scheduled folder scanning

## Author

**Pavan Kumar Shetty**
```