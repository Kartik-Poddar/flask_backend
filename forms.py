from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
import sqlite3
from flask import request
from flask_login import current_user


def connection():
    conn = None
    try:
        conn = sqlite3.connect('database.sqlite')
    except sqlite3.Error as e:
        print('Error : '+e)

    return conn


class registrationForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Confirm Password', validators=[
                                    DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        conn = connection()
        cur = conn.cursor()
        sql_query = 'SELECT USERNAME FROM USER WHERE USERNAME=?'
        cur.execute(sql_query, (str(username.data).lower(),))
        user = cur.fetchone()
        conn.close()
        if user:
            raise ValidationError('Username already exists!')

        # return super().validate(extra_validators)

    def validate_email(self, email):
        conn = connection()
        cur = conn.cursor()
        sql_query = 'SELECT EMAIL FROM USER WHERE EMAIL=?'
        cur.execute(sql_query, (str(email.data).lower(),))
        user = cur.fetchall()
        if user:
            raise ValidationError('Email already exists!')


class AccountUpdateForm(FlaskForm):
    username = StringField('Username', validators=[
                           DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    profilePic = FileField('Update Profile Picture', validators=[
                           FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Update Account')

    def validate_username(self, username):
        if username.data != current_user.username:
            conn = connection()
            cur = conn.cursor()
            sql_query = 'SELECT USERNAME FROM USER WHERE USERNAME=?'
            cur.execute(sql_query, (str(username.data).lower(),))
            user = cur.fetchone()
            conn.close()
            if user:
                raise ValidationError('Username already exists!')

        # return super().validate(extra_validators)

    def validate_email(self, email):
        if email.data != current_user.email:
            conn = connection()
            cur = conn.cursor()
            sql_query = 'SELECT EMAIL FROM USER WHERE EMAIL=?'
            cur.execute(sql_query, (str(email.data).lower(),))
            user = cur.fetchall()
            if user:
                raise ValidationError('Email already exists!')


class loginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remeber me')
    submit = SubmitField('Login')


class PostForm(FlaskForm):
    # author = current_user.username
    # date =
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField(label='Post')


class UpdatePost(FlaskForm):
    # author = current_user.username
    # date =
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Update')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset Password')

    def validate_email(self, email):
        conn = connection()
        cur = conn.cursor()
        cur.execute('SELECT EMAIL FROM USER WHERE EMAIL = (?)', [str(email.data).lower()])
        user = cur.fetchone()
        conn.close()
        if user is None:
            raise ValidationError('No account exists with this email!')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
                             DataRequired(), Length(min=8)])
    confirmPassword = PasswordField('Confirm Password', validators=[
                                    DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
