import os
from flask import Flask, request, redirect, render_template, url_for, jsonify
from werkzeug.utils import secure_filename
import psycopg2

UPLOAD_FOLDER = os.path.realpath('upload')
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

conn = psycopg2.connect(host='localhost', dbname='dementia', user='postgres', port=5432)
conn.set_session(autocommit=True)
cur = conn.cursor()

def csv(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() == 'csv'

@app.route('/', methods=['GET', 'POST'])
def index():
    print(request)
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(url_for('index', error='part'))
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('index', error='select'))
        if not csv(file.filename):
            return redirect(url_for('index', error='csv'))
        if file and csv(file.filename):
            filename = secure_filename(file.filename)
            print(file)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('index', success='true'))
        else:
            return redirect(url_for('index', error='unknown'))
    error = request.args.get('error')
    success = request.args.get('success')
    return render_template('index.html', error=error, success=success)

@app.route('/data', methods=['GET', 'POST', 'DELETE'])
def data():
    if request.method == 'POST':
        j = request.get_json()
        cur.execute('INSERT INTO dementia_patients (eeg1, eeg2, eeg3, eeg4, aux1, aux2, objects) VALUES (%s,%s,%s,%s,%s,%s,%s)',
            (j['EEG1'], j['EEG2'], j['EEG3'], j['EEG4'], j['AUX_LEFT'], j['AUX_RIGHT'], 'thing'))
        return 'success'
    elif request.method == 'DELETE':
        cur.execute('TRUNCATE TABLE dementia_patients')
        cur.execute('ALTER SEQUENCE dementia_patients_id_seq RESTART WITH 1;')
        return 'success'
    cur.execute('SELECT * FROM dementia_patients')
    data = cur.fetchall()
    return jsonify({"data": data})

if __name__ == '__main__':
    app.run()
