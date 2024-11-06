from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

# List to store countdowns as dictionaries with unique IDs
countdowns = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/set_countdown', methods=['GET', 'POST'])
def set_countdown():
    if request.method == 'POST':
        # Get data from the form
        countdown_name = request.form['name']
        countdown_date = request.form['date']
        countdown_time = request.form['time']

        # Store the countdown with a unique ID and store it as a dictionary
        countdown_id = len(countdowns)  # Unique ID is based on the index of the list
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
    # Pass the list of countdowns to the template
    return render_template('view_countdowns.html', countdowns=countdowns)

@app.route('/view_countdown/<int:id>')
def view_countdown(id):
    # Find the countdown with the given ID
    countdown = next((c for c in countdowns if c['id'] == id), None)
    if countdown:
        # Calculate the time difference between now and the countdown target date and time
        target_time = datetime.strptime(f"{countdown['date']} {countdown['time']}", '%Y-%m-%d %H:%M')
        current_time = datetime.now()
        time_remaining = target_time - current_time
        days_remaining = time_remaining.days
        seconds_remaining = time_remaining.seconds
        hours_remaining = seconds_remaining // 3600
        minutes_remaining = (seconds_remaining % 3600) // 60
        seconds_remaining = seconds_remaining % 60

        # Pass the countdown data and remaining time to the template
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

@app.route('/delete_countdown/<int:id>')
def delete_countdown(id):
    global countdowns
    countdowns = [c for c in countdowns if c['id'] != id]  # Remove countdown by ID
    return redirect(url_for('view_countdowns'))  # Redirect to the view countdowns page after deletion

if __name__ == '__main__':
    app.run(debug=True)
