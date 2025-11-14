# Timetable Application

This project provides an internal Flask web application that displays weekly timetables for teachers and classes based on EduPage / ASC Timetable HTML exports. It also includes a dedicated full-screen display mode for campus signage that loops through promotional videos and images.

## Project structure

```
timetable_app/
  app.py
  parsers.py
  data/
    Teachers.html
    Classes.html
  templates/
    base.html
    index.html
    timetable.html
    display.html
    error.html
  static/
    style.css
    logo.png
    events/
      *.mp4 / *.jpeg media files
```

## Requirements

- Python 3.8 or newer (includes `venv` module)
- Pip for installing Python packages
- Flask and BeautifulSoup4 Python packages
- EduPage timetable exports placed in `timetable_app/data`
- Event media files (`.mp4`, `.jpeg`, `.jpg`) placed in `timetable_app/static/events`

## Ubuntu Server setup and execution

1. **Install system dependencies (if not already present):**
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip
   ```
2. **Obtain the project source:**
   ```bash
   cd /opt
   git clone <repository-url> timetable
   cd timetable/timetable_app
   ```
3. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
4. **Install Python dependencies:**
   ```bash
   pip install --upgrade pip
   pip install flask beautifulsoup4
   ```
5. **Place timetable and media assets:**
   - Copy `Teachers.html` and `Classes.html` into `data/`.
   - Copy the university `logo.png` into `static/`.
   - Copy weekly event media files into `static/events/`.

6. **Run the Flask application for internal access:**
   ```bash
   export FLASK_APP=app.py
   flask run --host 0.0.0.0 --port 5000
   ```
   The application will be reachable on the internal network at `http://<server-ip>:5000/`.

7. **Optional: run in debug mode during development:**
   ```bash
   python app.py
   ```

8. **Display mode usage:**
   - Navigate to `http://<server-ip>:5000/display` from the signage PC.
   - Press `F11` in the browser for full-screen playback.

For persistent deployment you may wrap the `flask run` command in a systemd service or process supervisor suited to your environment.
