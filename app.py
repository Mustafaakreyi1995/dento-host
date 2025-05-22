
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.String(100), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    diagnosis = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=False)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    doctor = Doctor.query.filter_by(email=email).first()
    if doctor and check_password_hash(doctor.password_hash, password):
        return redirect(url_for('dashboard', doctor_id=doctor.id))
    return 'Invalid credentials'

@app.route('/dashboard/<int:doctor_id>')
def dashboard(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    patients = Patient.query.filter_by(doctor_id=doctor_id).all()
    return render_template('dashboard.html', doctor=doctor, patients=patients)

@app.route('/patient/<int:patient_id>')
def patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    records = Record.query.filter_by(patient_id=patient_id).all()
    return render_template('patient.html', patient=patient, records=records)

@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = request.form['name']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    contact_info = request.form['contact_info']
    doctor_id = request.form['doctor_id']
    new_patient = Patient(name=name, date_of_birth=date_of_birth, gender=gender, contact_info=contact_info, doctor_id=doctor_id)
    db.session.add(new_patient)
    db.session.commit()
    return redirect(url_for('dashboard', doctor_id=doctor_id))

@app.route('/add_record', methods=['POST'])
def add_record():
    patient_id = request.form['patient_id']
    doctor_id = request.form['doctor_id']
    date = request.form['date']
    symptoms = request.form['symptoms']
    diagnosis = request.form['diagnosis']
    notes = request.form['notes']
    new_record = Record(patient_id=patient_id, doctor_id=doctor_id, date=date, symptoms=symptoms, diagnosis=diagnosis, notes=notes)
    db.session.add(new_record)
    db.session.commit()
    return redirect(url_for('patient', patient_id=patient_id))

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
