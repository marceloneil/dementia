import os
from flask import Flask, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename
import psycopg2

UPLOAD_FOLDER = os.path.realpath("upload")
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conn = psycopg2.connect(host='localhost', dbname='dementia', user='postgres', port=5432)
conn.set_session(autocommit=True)
cur = conn.cursor()

def csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == "csv"

@app.route("/", methods=['GET', 'POST'])
def index():
    print(request)
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for("index", error="part"))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for("index", error="select"))
        if not csv(file.filename):
            return redirect(url_for("index", error="csv"))
        if file and csv(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for("index", success="true"))
        else:
            return redirect(url_for("index", error="unknown"))
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template('index.html', error=error, success=success)

@app.route("/post", methods=["POST"])
def post():
    json = request.get_json()
    print(json["EEG1"],json["EEG2"],json["EEG3"],json["EEG4"],json["EEG5"],json["AUX_LEFT"],json["AUX_RIGHT"])
    cur.execute("INSERT INTO dementia_patients VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (json["EEG1"],json["EEG2"],json["EEG3"],json["EEG4"],json["EEG5"],json["AUX_LEFT"],json["AUX_RIGHT"],"thing"))
    return "success"

if __name__ == "__main__":
    app.run()
