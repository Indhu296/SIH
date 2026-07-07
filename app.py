"""
Digital Farm Management Portal
Flask Application - Main Entry Point
Smart India Hackathon Project
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import os

# ── App Configuration ────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = 'farm_portal_secret_key_2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///farm_portal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── Database Models ───────────────────────────────────────────────────────────

class User(db.Model):
    """User model for authentication (Admin / Farmer)"""
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80),  unique=True, nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role     = db.Column(db.String(20),  nullable=False, default='farmer')  # admin / farmer
    created  = db.Column(db.DateTime,    default=datetime.utcnow)

class Livestock(db.Model):
    """Livestock records"""
    id          = db.Column(db.Integer, primary_key=True)
    tag_id      = db.Column(db.String(50),  unique=True, nullable=False)
    animal_type = db.Column(db.String(50),  nullable=False)
    breed       = db.Column(db.String(100), nullable=False)
    age_months  = db.Column(db.Integer,     nullable=False)
    weight_kg   = db.Column(db.Float,       nullable=False)
    farmer_name = db.Column(db.String(100), nullable=False)
    farm_location = db.Column(db.String(200), nullable=False)
    health_status = db.Column(db.String(50), default='Healthy')
    added_on    = db.Column(db.DateTime,    default=datetime.utcnow)

class MRLRecord(db.Model):
    """Maximum Residue Limit monitoring records"""
    id           = db.Column(db.Integer, primary_key=True)
    livestock_id = db.Column(db.Integer, db.ForeignKey('livestock.id'), nullable=False)
    substance    = db.Column(db.String(100), nullable=False)
    detected_val = db.Column(db.Float,       nullable=False)  # µg/kg
    mrl_limit    = db.Column(db.Float,       nullable=False)  # µg/kg
    status       = db.Column(db.String(20),  nullable=False)  # Safe / Warning / Exceeded
    sample_date  = db.Column(db.Date,        default=date.today)
    notes        = db.Column(db.Text,        default='')
    livestock    = db.relationship('Livestock', backref='mrl_records')

class AMURecord(db.Model):
    """Antimicrobial Usage tracking records"""
    id              = db.Column(db.Integer, primary_key=True)
    livestock_id    = db.Column(db.Integer, db.ForeignKey('livestock.id'), nullable=False)
    drug_name       = db.Column(db.String(100), nullable=False)
    drug_class      = db.Column(db.String(100), nullable=False)
    dosage_mg       = db.Column(db.Float,        nullable=False)
    route           = db.Column(db.String(50),   nullable=False)  # Oral/Injection/Topical
    start_date      = db.Column(db.Date,         nullable=False)
    end_date        = db.Column(db.Date,         nullable=False)
    withdrawal_days = db.Column(db.Integer,      nullable=False)
    prescribed_by   = db.Column(db.String(100),  nullable=False)
    reason          = db.Column(db.Text,         default='')
    livestock       = db.relationship('Livestock', backref='amu_records')

# ── Helper: login required decorator ─────────────────────────────────────────
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login to access this page.', 'warning')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def compute_mrl_status(detected, limit):
    """Compute MRL status based on detected vs limit value."""
    ratio = detected / limit if limit > 0 else 0
    if ratio <= 0.7:
        return 'Safe'
    elif ratio <= 1.0:
        return 'Warning'
    else:
        return 'Exceeded'

# ── Routes: Public ────────────────────────────────────────────────────────────

@app.route('/')
def home():
    total_livestock = Livestock.query.count()
    exceeded_mrl    = MRLRecord.query.filter_by(status='Exceeded').count()
    active_amu      = AMURecord.query.filter(AMURecord.end_date >= date.today()).count()
    return render_template('home.html',
                           total_livestock=total_livestock,
                           exceeded_mrl=exceeded_mrl,
                           active_amu=active_amu)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        flash('Thank you! Your message has been received. We will get back to you shortly.', 'success')
        return redirect(url_for('contact'))
    return render_template('contact.html')

# ── Routes: Auth ──────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id']  = user.id
            session['username'] = user.username
            session['role']     = user.role
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('home'))

# ── Routes: Dashboard ─────────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    total_livestock = Livestock.query.count()
    safe_mrl        = MRLRecord.query.filter_by(status='Safe').count()
    warning_mrl     = MRLRecord.query.filter_by(status='Warning').count()
    exceeded_mrl    = MRLRecord.query.filter_by(status='Exceeded').count()
    active_amu      = AMURecord.query.filter(AMURecord.end_date >= date.today()).count()
    total_mrl       = MRLRecord.query.count()
    total_amu       = AMURecord.query.count()

    # Recent exceeded MRL alerts
    alerts = (MRLRecord.query
              .filter_by(status='Exceeded')
              .order_by(MRLRecord.sample_date.desc())
              .limit(5).all())

    # Animal type distribution for chart
    animal_types = db.session.query(
        Livestock.animal_type,
        db.func.count(Livestock.id)
    ).group_by(Livestock.animal_type).all()

    return render_template('dashboard.html',
                           total_livestock=total_livestock,
                           safe_mrl=safe_mrl, warning_mrl=warning_mrl,
                           exceeded_mrl=exceeded_mrl, active_amu=active_amu,
                           total_mrl=total_mrl, total_amu=total_amu,
                           alerts=alerts, animal_types=animal_types)

# ── Routes: Livestock ─────────────────────────────────────────────────────────

@app.route('/livestock')
@login_required
def livestock():
    search = request.args.get('search', '').strip()
    filter_type = request.args.get('type', '')
    query = Livestock.query
    if search:
        query = query.filter(
            (Livestock.tag_id.ilike(f'%{search}%')) |
            (Livestock.farmer_name.ilike(f'%{search}%')) |
            (Livestock.breed.ilike(f'%{search}%'))
        )
    if filter_type:
        query = query.filter_by(animal_type=filter_type)
    records = query.order_by(Livestock.added_on.desc()).all()
    animal_types = db.session.query(Livestock.animal_type).distinct().all()
    return render_template('livestock.html', records=records,
                           animal_types=[t[0] for t in animal_types],
                           search=search, filter_type=filter_type)

@app.route('/livestock/add', methods=['GET', 'POST'])
@login_required
def add_livestock():
    if request.method == 'POST':
        new = Livestock(
            tag_id        = request.form['tag_id'].strip(),
            animal_type   = request.form['animal_type'],
            breed         = request.form['breed'].strip(),
            age_months    = int(request.form['age_months']),
            weight_kg     = float(request.form['weight_kg']),
            farmer_name   = request.form['farmer_name'].strip(),
            farm_location = request.form['farm_location'].strip(),
            health_status = request.form['health_status']
        )
        db.session.add(new)
        db.session.commit()
        flash('Livestock record added successfully!', 'success')
        return redirect(url_for('livestock'))
    return render_template('livestock_form.html', action='Add', record=None)

@app.route('/livestock/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_livestock(id):
    record = Livestock.query.get_or_404(id)
    if request.method == 'POST':
        record.tag_id        = request.form['tag_id'].strip()
        record.animal_type   = request.form['animal_type']
        record.breed         = request.form['breed'].strip()
        record.age_months    = int(request.form['age_months'])
        record.weight_kg     = float(request.form['weight_kg'])
        record.farmer_name   = request.form['farmer_name'].strip()
        record.farm_location = request.form['farm_location'].strip()
        record.health_status = request.form['health_status']
        db.session.commit()
        flash('Livestock record updated successfully!', 'success')
        return redirect(url_for('livestock'))
    return render_template('livestock_form.html', action='Edit', record=record)

@app.route('/livestock/delete/<int:id>', methods=['POST'])
@login_required
def delete_livestock(id):
    record = Livestock.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Livestock record deleted.', 'info')
    return redirect(url_for('livestock'))

# ── Routes: MRL Monitoring ────────────────────────────────────────────────────

@app.route('/mrl')
@login_required
def mrl():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '')
    query = MRLRecord.query
    if search:
        query = query.join(Livestock).filter(
            (Livestock.tag_id.ilike(f'%{search}%')) |
            (MRLRecord.substance.ilike(f'%{search}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    records = query.order_by(MRLRecord.sample_date.desc()).all()
    livestock_list = Livestock.query.all()
    return render_template('mrl.html', records=records,
                           livestock_list=livestock_list,
                           search=search, status_filter=status_filter)

@app.route('/mrl/add', methods=['GET', 'POST'])
@login_required
def add_mrl():
    if request.method == 'POST':
        detected = float(request.form['detected_val'])
        limit    = float(request.form['mrl_limit'])
        status   = compute_mrl_status(detected, limit)
        new = MRLRecord(
            livestock_id = int(request.form['livestock_id']),
            substance    = request.form['substance'].strip(),
            detected_val = detected,
            mrl_limit    = limit,
            status       = status,
            sample_date  = datetime.strptime(request.form['sample_date'], '%Y-%m-%d').date(),
            notes        = request.form.get('notes', '').strip()
        )
        db.session.add(new)
        db.session.commit()
        if status == 'Exceeded':
            flash(f'⚠️ ALERT: MRL Exceeded for {new.substance}! Immediate action required.', 'danger')
        else:
            flash('MRL record added successfully!', 'success')
        return redirect(url_for('mrl'))
    livestock_list = Livestock.query.all()
    return render_template('mrl_form.html', action='Add', record=None, livestock_list=livestock_list)

@app.route('/mrl/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_mrl(id):
    record = MRLRecord.query.get_or_404(id)
    if request.method == 'POST':
        record.livestock_id = int(request.form['livestock_id'])
        record.substance    = request.form['substance'].strip()
        record.detected_val = float(request.form['detected_val'])
        record.mrl_limit    = float(request.form['mrl_limit'])
        record.status       = compute_mrl_status(record.detected_val, record.mrl_limit)
        record.sample_date  = datetime.strptime(request.form['sample_date'], '%Y-%m-%d').date()
        record.notes        = request.form.get('notes', '').strip()
        db.session.commit()
        flash('MRL record updated!', 'success')
        return redirect(url_for('mrl'))
    livestock_list = Livestock.query.all()
    return render_template('mrl_form.html', action='Edit', record=record, livestock_list=livestock_list)

@app.route('/mrl/delete/<int:id>', methods=['POST'])
@login_required
def delete_mrl(id):
    record = MRLRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('MRL record deleted.', 'info')
    return redirect(url_for('mrl'))

# ── Routes: AMU Tracking ──────────────────────────────────────────────────────

@app.route('/amu')
@login_required
def amu():
    search = request.args.get('search', '').strip()
    route_filter = request.args.get('route', '')
    query = AMURecord.query
    if search:
        query = query.join(Livestock).filter(
            (Livestock.tag_id.ilike(f'%{search}%')) |
            (AMURecord.drug_name.ilike(f'%{search}%')) |
            (AMURecord.prescribed_by.ilike(f'%{search}%'))
        )
    if route_filter:
        query = query.filter_by(route=route_filter)
    records = query.order_by(AMURecord.start_date.desc()).all()
    today = date.today()
    livestock_list = Livestock.query.all()
    return render_template('amu.html', records=records,
                           livestock_list=livestock_list,
                           search=search, route_filter=route_filter, today=today)

@app.route('/amu/add', methods=['GET', 'POST'])
@login_required
def add_amu():
    if request.method == 'POST':
        new = AMURecord(
            livestock_id    = int(request.form['livestock_id']),
            drug_name       = request.form['drug_name'].strip(),
            drug_class      = request.form['drug_class'].strip(),
            dosage_mg       = float(request.form['dosage_mg']),
            route           = request.form['route'],
            start_date      = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date(),
            end_date        = datetime.strptime(request.form['end_date'],   '%Y-%m-%d').date(),
            withdrawal_days = int(request.form['withdrawal_days']),
            prescribed_by   = request.form['prescribed_by'].strip(),
            reason          = request.form.get('reason', '').strip()
        )
        db.session.add(new)
        db.session.commit()
        flash('AMU record added successfully!', 'success')
        return redirect(url_for('amu'))
    livestock_list = Livestock.query.all()
    return render_template('amu_form.html', action='Add', record=None, livestock_list=livestock_list)

@app.route('/amu/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_amu(id):
    record = AMURecord.query.get_or_404(id)
    if request.method == 'POST':
        record.livestock_id    = int(request.form['livestock_id'])
        record.drug_name       = request.form['drug_name'].strip()
        record.drug_class      = request.form['drug_class'].strip()
        record.dosage_mg       = float(request.form['dosage_mg'])
        record.route           = request.form['route']
        record.start_date      = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        record.end_date        = datetime.strptime(request.form['end_date'],   '%Y-%m-%d').date()
        record.withdrawal_days = int(request.form['withdrawal_days'])
        record.prescribed_by   = request.form['prescribed_by'].strip()
        record.reason          = request.form.get('reason', '').strip()
        db.session.commit()
        flash('AMU record updated!', 'success')
        return redirect(url_for('amu'))
    livestock_list = Livestock.query.all()
    return render_template('amu_form.html', action='Edit', record=record, livestock_list=livestock_list)

@app.route('/amu/delete/<int:id>', methods=['POST'])
@login_required
def delete_amu(id):
    record = AMURecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('AMU record deleted.', 'info')
    return redirect(url_for('amu'))

# ── Routes: Reports ───────────────────────────────────────────────────────────

@app.route('/reports')
@login_required
def reports():
    mrl_summary = db.session.query(
        MRLRecord.status, db.func.count(MRLRecord.id)
    ).group_by(MRLRecord.status).all()

    drug_usage = db.session.query(
        AMURecord.drug_class, db.func.count(AMURecord.id)
    ).group_by(AMURecord.drug_class).all()

    animal_mrl = db.session.query(
        Livestock.animal_type, MRLRecord.status, db.func.count(MRLRecord.id)
    ).join(MRLRecord, Livestock.id == MRLRecord.livestock_id)\
     .group_by(Livestock.animal_type, MRLRecord.status).all()

    recent_exceeded = (MRLRecord.query
                       .filter_by(status='Exceeded')
                       .order_by(MRLRecord.sample_date.desc())
                       .limit(10).all())

    return render_template('reports.html',
                           mrl_summary=mrl_summary,
                           drug_usage=drug_usage,
                           animal_mrl=animal_mrl,
                           recent_exceeded=recent_exceeded)

# ── API: Chart data ───────────────────────────────────────────────────────────

@app.route('/api/chart/mrl_status')
@login_required
def api_mrl_status():
    data = db.session.query(
        MRLRecord.status, db.func.count(MRLRecord.id)
    ).group_by(MRLRecord.status).all()
    return jsonify({'labels': [r[0] for r in data], 'values': [r[1] for r in data]})

@app.route('/api/chart/animal_types')
@login_required
def api_animal_types():
    data = db.session.query(
        Livestock.animal_type, db.func.count(Livestock.id)
    ).group_by(Livestock.animal_type).all()
    return jsonify({'labels': [r[0] for r in data], 'values': [r[1] for r in data]})

# ── Database Seeding ──────────────────────────────────────────────────────────

def seed_database():
    """Populate sample data for demonstration."""
    if User.query.count() > 0:
        return  # Already seeded

    # Users
    users = [
        User(username='admin',  email='admin@farmportal.com',
             password=generate_password_hash('admin123'),  role='admin'),
        User(username='farmer1', email='farmer1@farmportal.com',
             password=generate_password_hash('farmer123'), role='farmer'),
        User(username='farmer2', email='farmer2@farmportal.com',
             password=generate_password_hash('farmer123'), role='farmer'),
    ]
    db.session.add_all(users)

    # Livestock
    livestock_data = [
        Livestock(tag_id='LV-001', animal_type='Cattle',   breed='Holstein Friesian',
                  age_months=36, weight_kg=480.0, farmer_name='Rajan Kumar',
                  farm_location='Village Adarsh, Haryana', health_status='Healthy'),
        Livestock(tag_id='LV-002', animal_type='Cattle',   breed='Gir',
                  age_months=48, weight_kg=520.0, farmer_name='Rajan Kumar',
                  farm_location='Village Adarsh, Haryana', health_status='Healthy'),
        Livestock(tag_id='LV-003', animal_type='Poultry',  breed='Broiler',
                  age_months=3,  weight_kg=2.5,   farmer_name='Meena Devi',
                  farm_location='Poultry Farm, Punjab', health_status='Healthy'),
        Livestock(tag_id='LV-004', animal_type='Poultry',  breed='Layer',
                  age_months=12, weight_kg=1.8,   farmer_name='Meena Devi',
                  farm_location='Poultry Farm, Punjab', health_status='Under Treatment'),
        Livestock(tag_id='LV-005', animal_type='Pig',      breed='Yorkshire',
                  age_months=8,  weight_kg=85.0,  farmer_name='Suresh Patel',
                  farm_location='Pig Farm, Gujarat', health_status='Healthy'),
        Livestock(tag_id='LV-006', animal_type='Sheep',    breed='Merino',
                  age_months=18, weight_kg=45.0,  farmer_name='Anjali Singh',
                  farm_location='Sheep Farm, Rajasthan', health_status='Healthy'),
        Livestock(tag_id='LV-007', animal_type='Goat',     breed='Beetal',
                  age_months=14, weight_kg=32.0,  farmer_name='Anjali Singh',
                  farm_location='Sheep Farm, Rajasthan', health_status='Healthy'),
        Livestock(tag_id='LV-008', animal_type='Cattle',   breed='Sahiwal',
                  age_months=60, weight_kg=430.0, farmer_name='Vikram Rao',
                  farm_location='Dairy Farm, Karnataka', health_status='Healthy'),
    ]
    db.session.add_all(livestock_data)
    db.session.flush()

    # MRL Records
    mrl_data = [
        MRLRecord(livestock_id=1, substance='Oxytetracycline', detected_val=50.0,  mrl_limit=100.0, status='Safe',     sample_date=date(2024, 5, 10)),
        MRLRecord(livestock_id=2, substance='Amoxicillin',     detected_val=85.0,  mrl_limit=100.0, status='Warning',  sample_date=date(2024, 5, 12)),
        MRLRecord(livestock_id=3, substance='Enrofloxacin',    detected_val=160.0, mrl_limit=100.0, status='Exceeded', sample_date=date(2024, 5, 15)),
        MRLRecord(livestock_id=4, substance='Doxycycline',     detected_val=30.0,  mrl_limit=100.0, status='Safe',     sample_date=date(2024, 5, 18)),
        MRLRecord(livestock_id=5, substance='Chloramphenicol', detected_val=120.0, mrl_limit=100.0, status='Exceeded', sample_date=date(2024, 5, 20)),
        MRLRecord(livestock_id=6, substance='Penicillin G',    detected_val=10.0,  mrl_limit=50.0,  status='Safe',     sample_date=date(2024, 5, 22)),
        MRLRecord(livestock_id=7, substance='Streptomycin',    detected_val=45.0,  mrl_limit=50.0,  status='Warning',  sample_date=date(2024, 5, 25)),
        MRLRecord(livestock_id=8, substance='Tylosin',         detected_val=200.0, mrl_limit=100.0, status='Exceeded', sample_date=date(2024, 5, 28)),
    ]
    db.session.add_all(mrl_data)

    # AMU Records
    amu_data = [
        AMURecord(livestock_id=1, drug_name='Oxytetracycline', drug_class='Tetracyclines',
                  dosage_mg=500.0, route='Injection', start_date=date(2024, 4, 1),
                  end_date=date(2024, 4, 7), withdrawal_days=21, prescribed_by='Dr. Sharma',
                  reason='Respiratory infection'),
        AMURecord(livestock_id=2, drug_name='Amoxicillin', drug_class='Penicillins',
                  dosage_mg=250.0, route='Oral', start_date=date(2024, 4, 10),
                  end_date=date(2024, 4, 17), withdrawal_days=14, prescribed_by='Dr. Sharma',
                  reason='Mastitis prevention'),
        AMURecord(livestock_id=3, drug_name='Enrofloxacin', drug_class='Fluoroquinolones',
                  dosage_mg=100.0, route='Oral', start_date=date(2024, 4, 20),
                  end_date=date(2024, 4, 25), withdrawal_days=10, prescribed_by='Dr. Nair',
                  reason='Bacterial enteritis'),
        AMURecord(livestock_id=4, drug_name='Doxycycline', drug_class='Tetracyclines',
                  dosage_mg=200.0, route='Oral', start_date=date(2024, 5, 1),
                  end_date=date(2024, 5, 7), withdrawal_days=7,  prescribed_by='Dr. Nair',
                  reason='Mycoplasma infection'),
        AMURecord(livestock_id=5, drug_name='Chloramphenicol', drug_class='Amphenicols',
                  dosage_mg=300.0, route='Injection', start_date=date(2024, 5, 5),
                  end_date=date(2024, 5, 12), withdrawal_days=28, prescribed_by='Dr. Gupta',
                  reason='Salmonellosis'),
        AMURecord(livestock_id=6, drug_name='Penicillin G', drug_class='Penicillins',
                  dosage_mg=150.0, route='Injection', start_date=date(2024, 5, 10),
                  end_date=date(2024, 5, 14), withdrawal_days=10, prescribed_by='Dr. Verma',
                  reason='Foot rot'),
    ]
    db.session.add_all(amu_data)
    db.session.commit()
    print('✅ Database seeded with sample data.')

# ── Entry Point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
