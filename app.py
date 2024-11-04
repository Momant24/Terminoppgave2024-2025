from flask import Flask, render_template, url_for, redirect, request, flash, session
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

@app.route('/verifiser/<email>', methods=['GET', 'POST'])
def verify(email):
    if request.method == 'POST':
        code_entered = request.form.get('code')
        if int(code_entered) == verification_codes.get(email):
            user = User.query.filter_by(email=email).first()
            login_user(user)  # Logg inn brukeren hvis koden er riktig
            flash("Velkommen!")
            return redirect(url_for('Loggetinnn'))
        else:
            flash("Feil verifiseringskode, prøv igjen.")
    return render_template('verifiser.html', email=email)

@app.route('/loggetinn', methods=['GET', 'POST'])
@login_required
def Loggetinnn():
    # Hent besøkstelleren fra databasen
    visit_count = VisitCount.query.first()
    
    # Hvis visit_count ikke eksisterer (f.eks. hvis databasen er ny), sett den til 0
    if visit_count:
        count = visit_count.count
    else:
        count = 0  # Hvis ikke opprettet, sett som 0 eller gjør en håndtering her

    # Returner Loggetinn.html og send med `visit_count`
    return render_template('Loggetinn.html', visit_count=count)

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
@app.route('/Spill')
@login_required
def spill():
    # Hent besøkstelleren fra databasen, eller opprett en ny rad hvis den ikke finnes
    visit_count = VisitCount.query.first()


    # Hvis ingen besøksteller finnes, opprett en
    if not visit_count:
        visit_count = VisitCount(count=0)
        db.session.add(visit_count)
        db.session.commit()

    # Sjekk om brukeren allerede har talt et besøk i denne sesjonen
    if 'has_counted' not in session:
        # Øk antall besøk og lagre det
        visit_count.count += 1
        db.session.commit()  # Commit after making changes

        # Sett sesjonsvariabel for å forhindre flere tellinger
        session['has_counted'] = True

    # Returner Spill.html og send med `visit_count`
    return render_template('Spill.html', visit_count=visit_count.count)

if __name__ == '__main__':
    app.run(debug=True)
