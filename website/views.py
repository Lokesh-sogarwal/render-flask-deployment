import random
import string
from datetime import datetime
from . import db
from flask import Blueprint, render_template, session, redirect, request, url_for, flash
from flask_login import login_required, current_user
from forms import CreateMeetingForm, JoinForm, LeaveMeetingForm, BookingForm, UpdateBookingStatusForm
from .models import Createmeeting, Active_meeting, Bookings

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html")


@views.route('/dashboard')
@login_required
def dashboard():
    role = current_user.role  # Access the role of the logged-in user
    booking = Bookings.query.first()

    if role == 'user':
        return render_template('dashboard.html')  # Redirect to user dashboard
    elif role == 'employee':
        return render_template('employeedashboard.html',booking=booking)  # Redirect to employee dashboard
    else:
        flash('You do not have permission to view this page.', 'error')
        return redirect(url_for('views.home'))  # Redirect to home page or a specific page

@views.route('/booking_success/<string:booking_id>', methods=['GET'])
def booking_success(booking_id):
    # Fetch the booking by booking_id (string-based query)
    booking = Bookings.query.filter_by(booking_id=booking_id).first_or_404()
    return render_template('success.html', booking=booking)

@views.route('/create_meeting', methods=['GET', 'POST'])
@login_required
def create_meeting():
    role = current_user.role
    if role != 'employee':
        flash('You are not authorized to create meetings.', 'error')
        return redirect(url_for('dashboard', role=role))

    form = CreateMeetingForm()
    if form.validate_on_submit():
        room_id = random.randint(10000, 99999)
        leave_id = random.randint(1000, 9999)  # Generate the leave ID
        topic = form.topic.data
        description = form.description.data
        subject = form.subject.data
        user_id = current_user.user_id  # assuming current_user has user_id

        # Create a new Createmeeting instance (corrected)
        new_meeting = Createmeeting(
            room_id=room_id,
            leave_id=leave_id,
            topic=topic,
            description=description,
            subject=subject,
            user_id=user_id,  # Adjust this as necessary
        )

        # Add the new meeting to the session and commit
        db.session.add(new_meeting)
        db.session.commit()

        # Use `room_id` in `url_for`
        return redirect(url_for('views.videoconf', room_id=room_id))

    return render_template('create_meeting.html', form=form)



@views.route('/videoconf/<room_id>')
@login_required
def videoconf(room_id):
    if not room_id:
        flash('Room ID is required.', 'error')
        return redirect(url_for('dashboard'))

    # Fetch the meeting based on room_id
    meeting = Createmeeting.query.filter_by(room_id=room_id).first()
    if not meeting:
        flash('Meeting not found.', 'error')
        return redirect(url_for('dashboard'))

    firstname = current_user.first_name
    lastname = current_user.last_name
    role = current_user.role

    if role == "user":
        print('Rendering student video conference page.')
        return render_template(
            'videoconfs.html',
            username=f"{firstname} {lastname}",
            room_id=room_id,
            role=role
        )
    elif role == 'employee':
        leave_id = meeting.leave_id  # Corrected to dot notation
        return render_template(
            'videoconft.html',
            meeting=meeting,
            room_id=room_id,
            leave_id=leave_id,
            username=f"{firstname} {lastname}"
        )
    else:
        flash('Unauthorized access.', 'error')
        return redirect(url_for('views.dashboard'))

@views.route('/join_meeting', methods=['GET', 'POST'])
@login_required
def join_meeting():
    role = current_user.role
    if role != 'user':
        flash('You are not authorized to join meetings.', 'error')
        return redirect(url_for('views.dashboard'))

    form = JoinForm()
    if form.validate_on_submit():
        entered_room_id = form.roomID.data
        username = current_user.email

        try:
            # Query the meeting with the entered room ID
            meeting = Createmeeting.query.filter_by(room_id=entered_room_id).first()
            if meeting:
                print(f"Meeting found: {meeting.room_id}")  # Debug

                # Check if the user has already joined the meeting
                active_meeting = Active_meeting.query.filter_by(room_id=entered_room_id, email=username).first()

                if active_meeting:
                    flash('You have already joined this meeting.', 'error')
                    return redirect(url_for('views.videoconf', room_id=entered_room_id))

                # If the room ID matches and the user hasn't already joined, allow the user to join
                leave_id = meeting.leave_id
                active_meeting = Active_meeting(
                    room_id=entered_room_id,
                    email=username,
                    user_id=meeting.user_id,
                    leave_id=leave_id
                )
                db.session.add(active_meeting)
                db.session.commit()
                print(f"Active meeting added for Room ID: {entered_room_id}")  # Debug
                flash('You have successfully joined the meeting.', 'success')
                return redirect(url_for('views.videoconf', room_id=entered_room_id))
            else:
                # If the room ID does not match any meeting, show an error
                print(f"No meeting found for Room ID: {entered_room_id}")  # Debug
                flash('Invalid Room ID. Please check and try again.', 'error')
                return redirect(url_for('views.join_meeting'))

        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
            print(f"Exception: {e}")  # Debug

    # Debug print to see form validation errors
    print(f"Form validation failed: {form.errors}")  # Debug

    # Print specific error messages
    for field_name, error_messages in form.errors.items():
        for message in error_messages:
            print(f"Field '{field_name}' error: {message}")  # Debug

    return render_template('join.html', form=form)




@views.route('/leave_meeting', methods=['GET', 'POST'])
@login_required
def leave_meeting():
    form = LeaveMeetingForm()
    username = current_user.email
    role = current_user.role

    if role=='user':

        if form.validate_on_submit():
            leave_id = form.room_id.data  # Form field for leave_id
            print(f"Entered Leave ID: {leave_id}")

            if not leave_id:
                flash('Leave ID is required to leave the meeting.', 'error')
                return redirect(url_for('views.leave_meeting'))

            # Query the Active_meeting table to check if the user is in the meeting
            meeting = Active_meeting.query.filter_by(leave_id=leave_id, email=username).first()

            if not meeting:
                flash('You are not currently in any meeting or invalid Leave ID.', 'error')
                print(f"No active meeting found for user: {username} with Leave ID: {leave_id}")
                return redirect(url_for('views.leave_meeting'))

            stored_leave_id = meeting.leave_id
            print(f"Stored Leave ID from database: {stored_leave_id}")

            # If the entered leave_id doesn't match the stored one, show an error
            if leave_id != stored_leave_id:
                flash("Invalid Leave ID. Please enter the correct Leave ID.", 'error')
                return redirect(url_for('views.leave_meeting'))

            # If everything is correct, remove the user from the active meeting
            try:
                if role == 'user':
                    db.session.delete(meeting)
                    db.session.commit()
                    flash('You have successfully left the meeting.', 'success')
                    print(f"User {username} successfully left the meeting with Leave ID: {leave_id}")
                    return redirect(url_for('views.dashboard'))
            except Exception as e:
                flash(f"An error occurred: {str(e)}", 'error')
                print(f"Error: {e}")
    return render_template('leave_meeting.html', form=form)


@views.route('/my_bookings', methods=['GET'])
@login_required
def my_bookings():
    # Fetch all bookings for the logged-in user
    role = current_user.role

    if role == 'user':
        # Fetch bookings for the logged-in user
        bookings = Bookings.query.filter_by(user_id=current_user.user_id).all()
        return render_template('my_bookings.html', bookings=bookings)

    if role == 'employee':
        # Fetch all bookings (or relevant bookings for employees)
        bookings = Bookings.query.all()  # Or apply a filter if needed for employees
        return render_template('booking_emp_page.html', bookings=bookings)


@views.route('/booking_status/<string:booking_id>', methods=['GET'])
@login_required
def booking_status(booking_id):
    # Fetch the booking based on booking ID and user ID
    booking = Bookings.query.filter_by(booking_id=booking_id, user_id=current_user.user_id).first()

    if booking:
        # Render the status page with the booking details
        return render_template('booking_status.html', booking=booking)
    else:
        flash('No booking found with the given ID or it does not belong to you.', category='error')
        return redirect(url_for('views.my_bookings'))



@views.route('/update_booking_status/<string:booking_id>', methods=['GET', 'POST'])
@login_required
def update_booking_status(booking_id):
    # Fetch the booking by booking_id
    booking = Bookings.query.filter_by(booking_id=booking_id).first_or_404()

    form = UpdateBookingStatusForm()

    if form.validate_on_submit():
        # Get the new status from the form
        new_status = form.booking_status.data

        try:
            # Update the booking status
            booking.booking_status = new_status
            db.session.commit()
            flash('Booking status updated successfully!', category='success')
            return redirect(url_for('views.booking_success', booking_id=booking_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating booking status: {str(e)}', category='error')

    return render_template('update_booking.html', form=form, booking=booking)

@views.route('/views/role=employee/new_bookings')
def new_bookings():
    new = Bookings.query.filter_by(booking_status="New").all()
    return render_template('new_booking.html', bookings=new)

@views.route('/booking_details/<string:booking_id>')
def booking_details(booking_id):
    # Fetch the details of the booking using the booking ID
    booking = Bookings.query.filter_by(booking_id=booking_id).first()  # Fetch a specific booking by ID
    if booking:
        return render_template('booking_details.html', booking=booking)
    else:
        return "Booking not found", 404  # Handle if no booking is found with this ID

