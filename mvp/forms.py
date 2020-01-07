from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from mvp.models import User



class RegistrationForm(FlaskForm):
    username = StringField('Firmenname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    strasse = StringField('Straßenname + Nr.',
                           validators=[DataRequired()])
    plz = StringField('Postleitzahl',
                          validators=[DataRequired()])
    ort = StringField('Stadt',
                          validators=[DataRequired()])
    ansprechpartner = StringField('Ansprechpartner',
                           validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    confirm_password = PasswordField('Passwort bestätigen',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Es existiert bereits ein Account mit diesem Firmennamen. Bitte wählen Sie einen anderen aus.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Diese E-Mailadresse ist bereits vergeben. Bitte wählen Sie eine andere aus.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember = BooleanField('An mich erinnern')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Firmenname',
                           validators=[DataRequired(), Length(min=2, max=20)])
    strasse = StringField('Straßenname + Nr.',
                          validators=[DataRequired()])
    plz = StringField('Postleitzahl',
                      validators=[DataRequired()])
    ort = StringField('Stadt',
                      validators=[DataRequired()])
    ansprechpartner = StringField('Ansprechpartner',
                                  validators=[DataRequired()])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    picture = FileField('Profilbild aktualisieren', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Aktualisieren')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Es existiert bereits ein Account mit diesem Firmennamen. Bitte wählen Sie einen anderen aus.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Diese E-Mailadresse ist bereits vergeben. Bitte wählen Sie eine andere aus.')


class PostForm(FlaskForm):
    title = StringField('Titel', validators=[DataRequired()])
    content = TextAreaField('Inhalt', validators=[DataRequired()])
    typ = SelectField('Art der Ausschreibung',coerce=int, choices=[(1, 'Bachelorarbeit'),(2,'Masterarbeit'),(3,'Nebenjob'),(4,'Praktikum'),(5,'Innovationsidee')], validators=[DataRequired()], render_kw={})
    bezahlung = StringField('Entlohnung')
    zeit = StringField ('Zeitraum')
    submit = SubmitField('Veröffentlichen')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')