from datetime import datetime

from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)  # Primary Key
    first_name = db.Column(db.String(150), nullable=False)  # First Name
    last_name = db.Column(db.String(150), nullable=False)  # Last Name
    phone_number = db.Column(db.String(15), nullable=False)  # Phone Number as String to handle international formats
    email = db.Column(db.String(150), unique=True, nullable=False)  # User's Email
    password = db.Column(db.String(200), nullable=False)  # Hashed Password
    role = db.Column(db.String(50), nullable=False, default="user")  # User Role (e.g., student/teacher/admin)
    date_created = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Account creation date

    def get_id(self):
        return str(self.user_id)  # Return the user_id instead of id

    def __repr__(self):
        return f'<User {self.first_name} {self.last_name} - {self.email}>'

class Createmeeting(db.Model, UserMixin):
    room_id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)  # Room ID as Primary Key
    leave_id = db.Column(db.Integer, nullable=False, unique=True)  # Leave ID as Integer
    topic = db.Column(db.String(150), nullable=False)  # Topic of the meeting
    description = db.Column(db.String(300), nullable=False)  # Description of the meeting
    subject = db.Column(db.String(50), nullable=False)  # Subject of the meeting (changed to 50)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Foreign Key referencing User model's user_id
    start_time = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())  # Start time of the meeting

    def __repr__(self):
        return f'<Createmeeting {self.topic} - {self.subject}>'


class Active_meeting(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.String(100), nullable=False)  # Ensure this exists
    email = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    leave_id = db.Column(db.String(100), nullable=False)

class Bookings(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)  # Fixed typo in ForeignKey
    fullname = db.Column(db.String(50), nullable=False)
    booking_id = db.Column(db.String(255), nullable=False,unique=True)
    phone_number = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)  # Changed `Email` to `email` for naming consistency
    description = db.Column(db.String(255), nullable=False)
    mode = db.Column(db.String(50), nullable=True, default='N')
    address = db.Column(db.String(100), nullable=False)
    booking_type = db.Column(db.String(50), nullable=False)
    date_of_booking = db.Column(db.Date, nullable=False)  # Fixed type and naming
    booking_status = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


