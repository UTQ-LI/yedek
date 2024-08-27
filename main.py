from flask import Flask, render_template, request
import requests, get_data, ctypes, geocoder, os, datetime

try:
    requests.get("https://www.google.com")
except requests.exceptions.ConnectionError:
    ctypes.windll.user32.MessageBoxW(0, "Check your internet connection", "Error! No internet connection", 0x10)
    exit()

now = datetime.datetime.now()

with open("logs.log", "a") as log:
    log.write(f"{'-' * 50} Program Started In This Time {now} {'-' * 50}\n\n")
get_data.Start().StartAll()

with open("logs.log", "a") as log:
    log.write(f"{'-' * 50} Program Finished Getting Data In {datetime.datetime.now()} = {datetime.datetime.now() - now} {'-' * 50}\n\n")

def controlLogFileSize():
    if os.path.getsize("logs.log") / (1024 * 1024) > 1000:
        if ctypes.windll.user32.MessageBoxW(0, "Log file size is more than 1GB. Do you want to delete the log file?", "Too big file size", 0x4) == 6:
            os.remove("logs.log")
        else:
            pass
    else:
        pass


controlLogFileSize()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/evidenceAnalysis')
def evidenceAnalysis():
    return render_template('evidenceAnalysis.html', location=get_data.Tuple.getLocationTuple, regedit=get_data.Tuple.getRegeditTuple, country=geocoder.ip(requests.get("https://api.ipify.org").text).country, ip=requests.get("https://api.ipify.org").text, ai="Şu Anda Yapay Zeka Devre Dışıdır!")

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        name = request.form['userName']
        email = request.form['email']
        message = request.form['feedback']

        send_feedback(name, email, message)

    return render_template('submit-feedback.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(400)
def bad_request(e):
    return render_template('400.html'), 400

@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('405.html'), 405

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

def send_feedback(name, email, message):
    webhook_url = "https://discord.com/api/webhooks/1197522282143305828/BdQ3v0V3YpjsPd-Are2VBfMrotFq2GVw9WqHHeJJrsrBrAfF8nro5X8fpbHGoPC7SSXS"
    messages = {
        "content": f"Name: {name}\nEmail: {email}\nMessage: {message}"
    }

    if requests.post(webhook_url, json=messages).status_code == 204:
        pass
    else:
        ctypes.windll.user32.MessageBoxW(0, "Failed to send feedback. Please try again later.", "Error!", 0x10)


app.run()
