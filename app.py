from flask import Flask, render_template, url_for, redirect, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_mail import Mail, Message
import random
from flask_migrate import Migrate
import os



# Initialiserer Flask-applikasjonen
app = Flask(__name__)

# Riktig konfigurasjon for database URI
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "database.db")}'
app.config['SECRET_KEY'] = 'Hemmeligpassord'

# Initialiserer databasen
db = SQLAlchemy(app)

with app.app_context():
    db.create_all()
# Flask-Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jul123456654@gmail.com'
app.config['MAIL_PASSWORD'] = 'urzg ucei kdzp ftyp'
app.config['MAIL_DEFAULT_SENDER'] = 'jul123456654@gmail.com'
mail = Mail(app)
migrate = Migrate(app, db)
verification_codes = {}

bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"



# Definer VisitCount-modellen
class VisitCount(db.Model):
    __tablename__ = 'visit_count'
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, default=0)

# Sjekk om 'visit_count'-tabellen finnes, og opprett den hvis ikke
with app.app_context():
    if 'visit_count' not in db.metadata.tables:
        db.create_all()  # Oppretter alle tabeller som ikke finnes


# Definerer en modell for bruker
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)  # E-postadresse
    password = db.Column(db.String(80), nullable=False)
    defeats = db.Column(db.Integer, default=0)


class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(
        min=6, max=120)], render_kw={"placeholder": "E-post"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Registrer")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("E-posten er allerede i bruk. Velg en annen.")

        
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(
        min=6, max=120)], render_kw={"placeholder": "E-post"})
    
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")

# Ruter for nettsider
@app.route('/Registrer', methods=['GET','POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(email=form.email.data, password=hashed_password)  # Bruk e-post her
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template("Registrer.html", form=form)

@app.route('/Logginn', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()  # Søk etter bruker med e-post
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                code = random.randint(100000, 999999)
                verification_codes[user.email] = code  # Lagre koden i ordboken
                msg = Message("Verifiseringskode", recipients=[user.email])
                msg.body = f"Din verifiseringskode er: {code}"
                mail.send(msg)
                return redirect(url_for('verify', email=user.email))  # Omadresser til verifiseringsrute
    return render_template("Logginn.html", form=form)


from datetime import datetime, timedelta

verification_codes = {}

def generate_verification_code(email):
    code = random.randint(100000, 999999)
    expiration = datetime.now() + timedelta(minutes=10)  # Koden utløper etter 10 minutter
    verification_codes[email] = {'code': code, 'expiration': expiration}
    return code

@app.route('/verifiser/<email>', methods=['GET', 'POST'])
def verify(email):
    if request.method == 'POST':
        code_entered = request.form.get('code')
        stored_data = verification_codes.get(email)
        if stored_data and datetime.now() < stored_data['expiration']:
            if int(code_entered) == stored_data['code']:
                user = User.query.filter_by(email=email).first()
                login_user(user)
                flash("Velkommen!")
                del verification_codes[email]  # Fjern koden etter vellykket verifisering
                return redirect(url_for('Loggetinnn'))
            else:
                flash("Feil verifiseringskode, prøv igjen.")
        else:
            flash("Verifiseringskoden er utløpt eller ugyldig.")
    return render_template('verifiser.html', email=email)

@app.route('/loggetinn', methods=['GET', 'POST'])
@login_required
def Loggetinnn():
    visit_count = VisitCount.query.first()
    count = visit_count.count if visit_count else 0
    top_users = User.query.order_by(User.defeats.desc()).limit(10).all()
    return render_template('Loggetinn.html', visit_count=count, top_users=top_users)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    return redirect(url_for('login'))

@app.route('/')
def H():
    return render_template("Hjem.html")


@app.route('/glemt_passord', methods=['GET', 'POST'])
def glemt_passord():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generer en tilbakestillingskode
            reset_code = random.randint(100000, 999999)
            verification_codes[email] = reset_code  # Lagrer koden midlertidig
            
            msg = Message("Tilbakestilling av passord", recipients=[user.email])
            msg.body = f"Din tilbakestillingskode er: {reset_code}. Gå til /tilbakestill_passord/{email} for å tilbakestille passordet."
            mail.send(msg)
            flash("Tilbakestillingskode sendt til e-post.")
            
            # Omdirigerer direkte til tilbakestillingskode-siden
            return redirect(url_for('tilbakestill_passord', email=email))
        else:
            flash("Ingen bruker med denne e-posten.")
    
    return render_template('glemt_passord.html')

@app.route('/tilbakestill_passord/<email>', methods=['GET', 'POST'])
def tilbakestill_passord(email):
    if request.method == 'POST':
        code_entered = request.form.get('code')
        new_password = request.form.get('new_password')

        if int(code_entered) == verification_codes.get(email):
            user = User.query.filter_by(email=email).first()
            if user:
                hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')  # Husk å dekode hashen
                user.password = hashed_password
                db.session.commit()
                flash("Passordet er tilbakestilt!")
                return redirect(url_for('login'))
            else:
                flash("Ingen bruker med denne e-posten.")
        else:
            flash("Feil tilbakestillingskode, prøv igjen.")

    return render_template('tilbakestill_passord.html', email=email)
import logging
logging.basicConfig(level=logging.DEBUG)

@app.route('/Spill')
@login_required
def spill():
    try:
        # Hent besøkstelleren
        visit_count = VisitCount.query.first()
        logging.debug(f"Retrieved visit_count: {visit_count}")

        if not visit_count:
            logging.debug("No visit count found, creating new one")
            visit_count = VisitCount(count=0)
            db.session.add(visit_count)
            db.session.commit()

        if 'has_counted' not in session:
            logging.debug("Incrementing visit count")
            visit_count.count += 1
            db.session.commit()
            session['has_counted'] = True

        return render_template('Spill.html', visit_count=visit_count.count)
    except Exception as e:
        logging.error(f"Error in spill route: {str(e)}", exc_info=True)
        return f"En feil oppstod: {str(e)}", 500

@app.route('/update_defeats', methods=['POST'])
@login_required
def update_defeats():
    try:
        if not hasattr(current_user, 'defeats'):
            print("'defeats' attribute does not exist on User model")
            return jsonify({"error": "User model does not have 'defeats' attribute"}), 500
        
        if current_user.defeats is None:
            current_user.defeats = 0
        current_user.defeats += 1
        db.session.commit()
        print(f"Defeats updated for user {current_user.email}. New value: {current_user.defeats}")
        return jsonify({"success": True, "new_defeats": current_user.defeats}), 200
    except Exception as e:
        print(f"Error updating defeats: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
from sqlalchemy import inspect

def column_exists(table, column):
    inspector = inspect(db.engine)
    return column in [c['name'] for c in inspector.get_columns(table)]

with app.app_context():
    if not column_exists('user', 'defeats'):
        print("'defeats' column does not exist in User table. Please run database migrations.")

# Legg til dette midlertidig i app.py for å oppdatere eksisterende brukere
with app.app_context():
    users = User.query.all()
    for user in users:
        if user.defeats is None:
            user.defeats = 0
    db.session.commit()  
   
if __name__ == '__main__':
    app.run(debug=True)
