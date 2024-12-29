from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField,TextAreaField,DateField,TimeField,SelectField,FileField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email",validators=[DataRequired()])
    phone_no = IntegerField("Phone Number", validators=[
        DataRequired(),
        NumberRange(min=1000000000, max=9999999999, message="Phone number must be 10 digits")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message="Password must be at least 8 characters")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message="Passwords must match")
    ])
    submit = SubmitField("Register")

class CreateMeetingForm(FlaskForm):
    topic = StringField('Topic', validators=[DataRequired()])
    description = TextAreaField('Description')
    subject = StringField('Subject',validators=[DataRequired()])
    submit = SubmitField('Create Meeting')

class JoinForm(FlaskForm):
    roomID = StringField('Room ID', validators=[DataRequired()])
    submit = SubmitField('Join Class')
class LeaveMeetingForm(FlaskForm):
    room_id = StringField('Leave ID', validators=[DataRequired()])
    submit = SubmitField('Leave Meeting')
class BookingForm(FlaskForm):
    firstname = StringField('First Name')
    lastname = StringField('Last Name')
    dob = DateField('Date of Booking')
    phone = StringField('Phone Number')
    email = StringField('Email Address')
    address = StringField('Address')
    pincode = StringField('Pincode')
    street = StringField('City')
    message = TextAreaField('Description about work')

class UpdateBookingStatusForm(FlaskForm):
    booking_status = SelectField(
        'New Status',
        choices=[

                 ('Pending', 'Pending'),
                 ('Visiting','Visting'),
                 ('In Progress', 'In Progress'),
                 ('Completed', 'Completed'),
                 ('Cancelled', 'Cancelled')],
        validators=[DataRequired(message="Please select a status")]
    )

class OTPForm(FlaskForm):
    first = StringField('First', validators=[DataRequired(), Length(min=1, max=1)])
    second = StringField('Second', validators=[DataRequired(), Length(min=1, max=1)])
    third = StringField('Third', validators=[DataRequired(), Length(min=1, max=1)])
    fourth = StringField('Fourth', validators=[DataRequired(), Length(min=1, max=1)])
    fifth = StringField('Fifth', validators=[DataRequired(), Length(min=1, max=1)])
    sixth = StringField('Sixth', validators=[DataRequired(), Length(min=1, max=1)])
    submit = SubmitField('Validate')

