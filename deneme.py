from flask import Flask, render_template
import getData

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html', location_data=getData.location_data, regedit_data=getData.regedit_data)

app.run(debug=True)
