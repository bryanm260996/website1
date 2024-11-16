import os
import json
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)

# Set a secret key for session management
app.secret_key = os.urandom(24)

# Path to the folder where photos will be stored (works both locally and on Heroku)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'photos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Path to the JSON file to store data
DATA_FILE = 'data.json'

# Predetermined password for authentication
PASSWORD = os.environ.get('PASSWORD', '02100501')  # Default password for local testing

# Helper function to check if the user is authenticated
def is_authenticated():
    return session.get('authenticated', False)

# Helper function to load data from the JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            return {"countdowns": [], "photos": [], "albums": [], "dates": [], "journals": []}
    return {"countdowns": [], "photos": [], "albums": [], "dates": [], "journals": []}

# Helper function to save data to the JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/')
def home():
    # If not authenticated, ask for password
    if not is_authenticated():
        return redirect(url_for('password_prompt'))
    return render_template('home.html')

@app.route('/password', methods=['GET', 'POST'])
def password_prompt():
    if request.method == 'POST':
        password = request.form['password']
        if password == PASSWORD:
            session['authenticated'] = True
            return redirect(url_for('home'))
        else:
            # Invalid password
            return render_template('password_prompt.html', error="Invalid password")
    return render_template('password_prompt.html')

@app.route('/logout')
def logout():
    session.pop('authenticated', None)  # Log the user out
    return redirect(url_for('home'))

########################## COUNTDOWN TIMER ##########################
@app.route('/index')
def index():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))
    return render_template('index.html')

@app.route('/set_countdown', methods=['GET', 'POST'])
def set_countdown():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()

    if request.method == 'POST':
        countdown_name = request.form['name']
        countdown_date = request.form['date']
        countdown_time = request.form['time']

        # Store the countdown with a unique ID
        countdown_id = len(data["countdowns"])
        data["countdowns"].append({
            'id': countdown_id,
            'name': countdown_name,
            'date': countdown_date,
            'time': countdown_time
        })

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_countdowns'))

    return render_template('set_countdown.html')

@app.route('/view_countdowns')
def view_countdowns():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    return render_template('view_countdowns.html', countdowns=data["countdowns"])

@app.route('/view_countdown/<int:id>')
def view_countdown(id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    countdown = next((c for c in data["countdowns"] if c['id'] == id), None)
    if countdown:
        target_time = datetime.strptime(f"{countdown['date']} {countdown['time']}", '%Y-%m-%d %H:%M')
        current_time = datetime.now()
        time_remaining = target_time - current_time
        days_remaining = time_remaining.days
        seconds_remaining = time_remaining.seconds
        hours_remaining = seconds_remaining // 3600
        minutes_remaining = (seconds_remaining % 3600) // 60
        seconds_remaining = seconds_remaining % 60

        return render_template(
            'view_countdown_detail.html',
            countdown=countdown,
            days_remaining=days_remaining,
            hours_remaining=hours_remaining,
            minutes_remaining=minutes_remaining,
            seconds_remaining=seconds_remaining
        )
    else:
        return "Countdown not found", 404

@app.route('/delete_countdown/<int:id>', methods=['GET'])
def delete_countdown(id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    data["countdowns"] = [c for c in data["countdowns"] if c['id'] != id]
    save_data(data)  # Save data to JSON file
    return redirect(url_for('view_countdowns'))

####################### DATE PLANNER ############################
@app.route('/date_planner', methods=['GET'])
def date_planner():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    return render_template('date_planner.html', albums=data["albums"])

@app.route('/set_date_idea', methods=['GET', 'POST'])
def set_date_idea():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()

    if request.method == 'POST':
        set_name = request.form['name']

        # Store the date idea with a unique ID
        date_id = len(data["dates"])
        data["dates"].append({
            'id': date_id,
            'name': set_name,
            'details': '',
            'completed': False,
        })

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_date_ideas'))

    return render_template('set_date_idea.html')

@app.route('/view_date_ideas')
def view_date_ideas():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    return render_template('view_date_ideas.html', dates=data["dates"])

@app.route('/view_date_detail/<int:date_id>', methods=['GET', 'POST'])
def view_date_detail(date_id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    date_idea = next((date for date in data["dates"] if date['id'] == date_id), None)

    if not date_idea:
        return "Date idea not found", 404

    if request.method == 'POST':
        # Update date idea with the new information from the form
        date_idea['details'] = request.form['details']
        date_idea['completed'] = 'completed' in request.form  # Checkbox for completion

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_date_ideas'))

    return render_template('view_date_detail.html', date_idea=date_idea)

####################### JOURNAL ENTRIES #######################
@app.route('/shared_journal_home')
def shared_journal_home():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    return render_template('shared_journal_home.html')

@app.route('/create_journal_entry', methods=['GET', 'POST'])
def create_journal_entry():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()

    if request.method == 'POST':
        set_name = request.form['name']

        # Store journal entry with a unique ID, and placeholders for Bryan and Maro's entries
        journal_entry_id = len(data["journals"])
        data["journals"].append({
            'id': journal_entry_id,
            'name': set_name,
            'Maro': '',
            'Bryan': ''
        })

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_journals'))

    return render_template('create_journal_entry.html')

@app.route('/view_journals')
def view_journals():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    return render_template('view_journals.html', journals=data["journals"])

@app.route('/view_journal_detail/<int:journal_id>', methods=['GET', 'POST'])
def view_journal_detail(journal_id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    journal_entry = next((entry for entry in data["journals"] if entry['id'] == journal_id), None)

    if not journal_entry:
        return "Journal entry not found", 404

    if request.method == 'POST':
        # Update the journal entry with the details for Bryan and Maro
        journal_entry['Maro'] = request.form['Maro']
        journal_entry['Bryan'] = request.form['Bryan']

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_journals'))

    return render_template('view_journal_detail.html', journal_entry=journal_entry)

##################### PHOTOS ROUTES #############################
@app.route('/photos', methods=['GET'])
def photos_page():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    return render_template('photos_home.html', albums=data["albums"])

@app.route('/create_album', methods=['GET', 'POST'])
def create_album():
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()

    if request.method == 'POST':
        album_name = request.form['album_name']
        album_id = len(data["albums"])
        data["albums"].append({
            'id': album_id,
            'name': album_name,
            'photos': []  # Start with an empty list of photos
        })

        save_data(data)  # Save data to JSON file
        return redirect(url_for('view_album', album_id=album_id))

    return render_template('create_album.html')

@app.route('/view_album/<int:album_id>', methods=['GET'])
def view_album(album_id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    album = next((a for a in data["albums"] if a['id'] == album_id), None)
    if not album:
        return "Album not found", 404
    return render_template('view_album.html', album=album)

@app.route('/upload_photo/<int:album_id>', methods=['POST'])
def upload_photo(album_id):
    if not is_authenticated():
        return redirect(url_for('password_prompt'))

    data = load_data()
    album = next((a for a in data["albums"] if a['id'] == album_id), None)
    if not album:
        return "Album not found", 404

    if 'photo' not in request.files:
        return redirect(url_for('view_album', album_id=album_id))

    photo = request.files['photo']
    if photo.filename == '':
        return redirect(url_for('view_album', album_id=album_id))

    # Secure filename (to prevent directory traversal issues)
    filename = os.path.join(app.config['UPLOAD_FOLDER'], photo.filename)
    photo.save(filename)

    # Add the photo to the album
    album['photos'].append(photo.filename)

    save_data(data)  # Save data to JSON file
    return redirect(url_for('view_album', album_id=album_id))

# To run the app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the 'photos' folder if it doesn't exist

    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
