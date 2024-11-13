from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)

# Path to the folder where photos will be stored (works both locally and on Heroku)
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'photos')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# List to store countdowns as dictionaries with unique IDs (in-memory storage for now)
countdowns = []
photos = []  # List to store the filenames of uploaded photos
albums = []  # List to store albums
dates = []
journals = []

@app.route('/')
def home():
    return render_template('home.html')

########################## COUNTDOWN TIMER ##########################
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/set_countdown', methods=['GET', 'POST'])
def set_countdown():
    if request.method == 'POST':
        countdown_name = request.form['name']
        countdown_date = request.form['date']
        countdown_time = request.form['time']

        # Store the countdown with a unique ID
        countdown_id = len(countdowns)
        countdowns.append({
            'id': countdown_id,
            'name': countdown_name,
            'date': countdown_date,
            'time': countdown_time
        })

        return redirect(url_for('view_countdowns'))

    return render_template('set_countdown.html')

@app.route('/view_countdowns')
def view_countdowns():
    return render_template('view_countdowns.html', countdowns=countdowns)

@app.route('/view_countdown/<int:id>')
def view_countdown(id):
    countdown = next((c for c in countdowns if c['id'] == id), None)
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
    global countdowns
    countdowns = [c for c in countdowns if c['id'] != id]
    return redirect(url_for('view_countdowns'))

####################### DATE PLANNER ############################
@app.route('/date_planner', methods=['GET'])
def date_planner():
    return render_template('date_planner.html', albums=albums)

@app.route('/set_date_idea', methods=['GET', 'POST'])
def set_date_idea():
    if request.method == 'POST':
        set_name = request.form['name']

        # Store the date idea with a unique ID
        date_id = len(dates)
        dates.append({
            'id': date_id,
            'name': set_name,
            'details': '',
            'completed': False,
        })

        return redirect(url_for('view_date_ideas'))

    return render_template('set_date_idea.html')

@app.route('/view_date_ideas')
def view_date_ideas():
    return render_template('view_date_ideas.html', dates=dates)

@app.route('/view_date_detail/<int:date_id>', methods=['GET', 'POST'])
def view_date_detail(date_id):
    # Find the date idea by ID
    date_idea = next((date for date in dates if date['id'] == date_id), None)

    if not date_idea:
        return "Date idea not found", 404

    if request.method == 'POST':
        # Update date idea with the new information from the form
        date_idea['details'] = request.form['details']
        date_idea['completed'] = 'completed' in request.form  # Checkbox for completion

        return redirect(url_for('view_date_ideas'))

    return render_template('view_date_detail.html', date_idea=date_idea)

####################### JOURNAL ENTRIES #######################
@app.route('/shared_journal_home')
def shared_journal_home():
    return render_template('shared_journal_home.html')

@app.route('/create_journal_entry', methods=['GET', 'POST'])
def create_journal_entry():
    if request.method == 'POST':
        set_name = request.form['name']

        # Store journal entry with a unique ID, and placeholders for Bryan and Maro's entries
        journal_entry_id = len(journals)
        journals.append({
            'id': journal_entry_id,
            'name': set_name,
            'Maro': '',
            'Bryan': ''
        })

        return redirect(url_for('view_journals'))

    return render_template('create_journal_entry.html')

@app.route('/view_journals')
def view_journals():
    return render_template('view_journals.html', journals=journals)

@app.route('/view_journal_detail/<int:journal_id>', methods=['GET', 'POST'])
def view_journal_detail(journal_id):
    # Find the journal entry by ID
    journal_entry = next((entry for entry in journals if entry['id'] == journal_id), None)

    if not journal_entry:
        return "Journal entry not found", 404

    if request.method == 'POST':
        # Update the journal entry with the details for Bryan and Maro
        journal_entry['Maro'] = request.form['Maro']
        journal_entry['Bryan'] = request.form['Bryan']

        return redirect(url_for('view_journals'))

    return render_template('view_journal_detail.html', journal_entry=journal_entry)

##################### PHOTOS ROUTES #############################
@app.route('/photos', methods=['GET'])
def photos_page():
    return render_template('photos_home.html', albums=albums)

@app.route('/create_album', methods=['GET', 'POST'])
def create_album():
    if request.method == 'POST':
        album_name = request.form['album_name']
        album_id = len(albums)
        albums.append({
            'id': album_id,
            'name': album_name,
            'photos': []  # Start with an empty list of photos
        })
        return redirect(url_for('view_album', album_id=album_id))

    return render_template('create_album.html')

@app.route('/view_album/<int:album_id>', methods=['GET'])
def view_album(album_id):
    album = next((a for a in albums if a['id'] == album_id), None)
    if not album:
        return "Album not found", 404
    return render_template('view_album.html', album=album)

@app.route('/upload_photo/<int:album_id>', methods=['POST'])
def upload_photo(album_id):
    album = next((a for a in albums if a['id'] == album_id), None)
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

    return redirect(url_for('view_album', album_id=album_id))


# To run the app
if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)  # Create the 'photos' folder if it doesn't exist

    # Heroku automatically uses PORT and binds to '0.0.0.0'
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
