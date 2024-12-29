import string

from flask import Blueprint, render_template, flash, session, redirect, url_for, request, current_app
from flask_login import login_required, login_user, current_user, logout_user  # Corrected
from flask_mail import Message
from sqlalchemy.sql.functions import user
from werkzeug.security import generate_password_hash, check_password_hash
from forms import RegisterForm, LoginForm, BookingForm, OTPForm
from . import db, mail
from .models import User, Bookings
import random
from datetime import datetime

auth = Blueprint('auth', __name__)

def generate_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_email(subject, recipient, body):
    try:
        msg = Message(subject, sender=current_app.config['MAIL_DEFAULT_SENDER'], recipients=[recipient])
        msg.body = body
        mail.send(msg)
        flash(f'Email sent to {recipient}', 'success')
    except Exception as e:
        flash(f'Failed to send email: {str(e)}', 'error')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit() and request.method == 'POST':
        email = form.email.data.lower()
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        try:
            if user:
                print("User exists")
                if check_password_hash(user.password, password):
                    flash("Logged In Successfully", category='success')
                    login_user(user, remember=True)
                    return redirect(url_for('views.dashboard', role=current_user.role))  # Ensure the correct URL
                else:
                    print("Password error")
                    flash('Password mismatch', category='error')
            else:
                flash('Invalid email.', 'error')
        except Exception as e:
            flash(f"An error occurred: {e}", "error")

    return render_template('login.html', form=form , user = current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()  # Corrected logout method
    return redirect(url_for('views.home'))


@auth.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            first_name = form.first_name.data.capitalize()
            last_name = form.last_name.data.capitalize()
            phone_no = form.phone_no.data
            email = form.email.data.lower()
            password = form.password.data
            confirm_password = form.confirm_password.data

            if password != confirm_password:
                flash("Passwords do not match.", "error")
                return render_template("register.html", form=form)

            # Check if user already exists
            existing_user = User.query.filter(
                (User.email == email) | (User.phone_number == phone_no)
            ).first()
            if existing_user:
                flash("Email or phone number already registered.", "error")
                return render_template("register.html", form=form)

            hashed_password = generate_password_hash(password)
            otp = generate_otp()
            session['otp'] = otp
            session['otp_timestamp'] = datetime.now().timestamp()

            # Temporarily store user details in session
            session['temp_user_details'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'password': hashed_password,
                'role': 'user',
                'phone_number': phone_no
            }
            session['email'] = email

            # Send OTP
            send_email('OTP Verification', email, f'Your OTP for verification is {otp}. Do not share it with anyone.')

            flash('Please verify your email address using the OTP sent to your email.', 'success')
            return redirect(url_for('auth.otp'))

        except Exception as e:
            flash(f'An error occurred during registration: {str(e)}', 'error')

    return render_template("register.html", form=form)


@auth.route("/otp", methods=['GET', 'POST'])
def otp():
    form = OTPForm()
    if form.validate_on_submit():  # Ensures form validation with FlaskForm
        actual_otp = session.get('otp')
        otp_timestamp = session.get('otp_timestamp')

        # Check OTP expiration (5 minutes)
        if datetime.now().timestamp() - otp_timestamp > 300:
            flash("OTP has expired. Please request a new one.", "error")
            return redirect(url_for('auth.resend'))

        # Collect the entered OTP from the form
        entered_otp = ''.join([
            form.first.data,
            form.second.data,
            form.third.data,
            form.fourth.data,
            form.fifth.data,
            form.sixth.data
        ])

        # Validate the entered OTP
        if entered_otp == actual_otp:
            user_details = session.pop('temp_user_details', None)
            if user_details:
                new_user = User(**user_details)
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash("Registration successful!", "success")
                    login_user(new_user, remember=True)  # Log in the newly registered user
                    return redirect(url_for('auth.login'))
                except Exception as e:
                    flash(f"Error saving user to the database: {str(e)}", "error")
        else:
            flash("Invalid OTP. Please try again.", "error")

    email = session.get('email')
    return render_template("otp.html", form=form, email=email)


@auth.route("/resend", methods=['POST', 'GET'])
def resend():
    email = session.get('email')
    if not email:
        flash("No email address found in session. Please restart the process.", "error")
        return redirect(url_for('auth.register'))

    otp = generate_otp()
    session['otp'] = otp
    session['otp_timestamp'] = datetime.now().timestamp()
    send_email('OTP Verification', email, f'Your OTP for verification is {otp}. Do not share it with anyone.')
    flash("A new OTP has been sent to your email.", "success")
    return render_template('otp.html', email=email)


@auth.route('/bookings/<booking_type>/user_id=<int:user_id>', methods=['GET', 'POST'])
@login_required
def booking(booking_type, user_id):
    # Define templates for each booking type
    booking_templates = {
        'carpenter': 'formcar.html',
        'carwash': 'formcarwash.html',
        'electrician': 'formelec.html',
        'lifting-shifting': 'formlift.html',
        'tutor': 'formtut.html',
    }

    # Check if the booking type is valid
    if booking_type not in booking_templates or user_id != current_user.user_id:
        flash('Invalid booking type or user ID mismatch.', category='error')
        return redirect(url_for('views.dashboard', role=current_user.role))

    # Handle form submission
    form = BookingForm()

    if form.validate_on_submit():
        # Retrieve form data
        first_name = form.firstname.data
        last_name = form.lastname.data
        phone = form.phone.data
        address = form.address.data
        pincode = form.pincode.data
        street = form.street.data
        description = form.message.data
        date_of_booking = form.dob.data

        # Combine and format full name and address
        full_name = f"{first_name.capitalize()} {last_name.capitalize()}"
        full_address = f"{address}, {street}, {pincode}"
        booking_id = ''.join(random.choices(string.ascii_uppercase+string.digits+string.ascii_lowercase, k=20))

        # Debug print statements
        print(f"Full Address: {full_address}")
        print(f"Full Name: {full_name}")
        print(f"Phone: {phone}, Description: {description}, Date: {date_of_booking}")


        # Save booking to the database
        try:
            # Create a new booking instance
            booking = Bookings(
                booking_id=f"#{booking_id}",
                fullname=full_name,
                phone_number=phone,
                email=current_user.email,
                description=description,
                date_of_booking=date_of_booking,
                address=full_address,
                booking_type=booking_type,
                booking_status='New',
                user_id=user_id  # Added user_id
            )
            # Add the booking to the session and commit
            db.session.add(booking)
            db.session.commit()

            flash('Booking successfully created!', category='success')

            # Debugging: Check if the redirect is being hit
            print(f"Redirecting to booking_success with booking_id: {booking.booking_id}")

            # Redirect to booking success page
            return redirect(url_for('views.booking_success', booking_id=booking.booking_id))

        except Exception as e:
            # Rollback session on error and print the error
            db.session.rollback()
            print(f"Error during commit: {str(e)}")
            flash(f"An error occurred while creating the booking: {str(e)}", category='error')
            return render_template(booking_templates[booking_type], form=form, user_id=user_id)

    # Render the template for the specified booking type with the form
    return render_template(booking_templates[booking_type], form=form, user_id=user_id)
