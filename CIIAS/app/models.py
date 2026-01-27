from datetime import datetime
from app.encryption import encryption_manager
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Organization(db.Model):
    __tablename__ = 'organizations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), unique=True) # e.g. "NUST"
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'website': self.website,
            'logo_url': self.logo_url
        }

class Campus(db.Model):
    __tablename__ = 'campuses'
    id = db.Column(db.Integer, primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(255))
    contact_email = db.Column(db.String(120))
    timezone = db.Column(db.String(50), default='UTC')
    latitude = db.Column(db.Float) # For campus centering
    longitude = db.Column(db.Float) 
    


    def to_dict(self):
        return {
            'id': self.id,
            'org_id': self.org_id,
            'name': self.name,
            'location': self.location,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone
        }

class MapPOI(db.Model):
    __tablename__ = 'map_pois'
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), default='room') # room, lab, dept, cafeteria, office, emergency
    lat = db.Column(db.Float, nullable=False)
    lng = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'campus_id': self.campus_id,
            'name': self.name,
            'type': self.type,
            'lat': self.lat,
            'lng': self.lng,
            'description': self.description,
            'is_public': self.is_public
        }

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20)) # e.g. "CS", "ME"
    type = db.Column(db.String(20), default='academic') # academic, administrative, support
    

    head_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'campus_id': self.campus_id,
            'name': self.name,
            'code': self.code,
            'type': self.type
        }

class StaffDetail(db.Model):
    __tablename__ = 'staff_details'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    cnic = db.Column(db.String(20), unique=True)
    address = db.Column(db.Text)
    designation = db.Column(db.String(100))
    salary = db.Column(db.Float)
    joining_date = db.Column(db.Date)
    qualification = db.Column(db.Text)
    licence_number = db.Column(db.String(50)) # For drivers
    emergency_contact = db.Column(db.String(20))
    


    def to_dict(self):
        return {
            'id': self.id,
            'cnic': self.cnic,
            'address': self.address,
            'designation': self.designation,
            'salary': self.salary,
            'joining_date': self.joining_date.isoformat() if self.joining_date else None,
            'licence_number': self.licence_number,
            'emergency_contact': self.emergency_contact
        }

class Program(db.Model):
    __tablename__ = 'programs'
    id = db.Column(db.Integer, primary_key=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20)) # e.g. "BS-CS", "MBA"
    total_credits = db.Column(db.Integer)
    


    def to_dict(self):
        return {
            'id': self.id,
            'dept_id': self.dept_id,
            'dept_name': self.department.name if self.department else None,
            'name': self.name,
            'code': self.code,
            'total_credits': self.total_credits
        }

class University(db.Model):
    __tablename__ = 'universities'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True) # e.g. 'kicsit'
    domain = db.Column(db.String(100), unique=True) # e.g. 'kicsit.edu.pk'
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'domain': self.domain,
            'is_active': self.is_active
        }

class UniversityConfig(db.Model):
    __tablename__ = 'university_configs'
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), primary_key=True)
    primary_color = db.Column(db.String(20), default='#007BFF')
    secondary_color = db.Column(db.String(20), default='#6C757D')
    logo_url = db.Column(db.String(256))
    enabled_modules = db.Column(db.JSON, default=lambda: ["map", "incidents", "emergency"])
    map_lat = db.Column(db.Float)
    map_lng = db.Column(db.Float)
    
    university = db.relationship('University', backref=db.backref('config', uselist=False))

    def to_dict(self):
        return {
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'logo_url': self.logo_url,
            'enabled_modules': self.enabled_modules,
            'map_center': {'lat': self.map_lat, 'lng': self.map_lng}
        }

# Association table for Parent-Child relationship
parent_child = db.Table('parent_child',
    db.Column('parent_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('child_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True) # Nullable for platform broad admins
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='student')  # student, staff, security, admin
    phone = db.Column(db.String(20))
    profile_photo = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    fcm_token = db.Column(db.String(256))  # For push notifications

    university = db.relationship('University', backref='users')
    
    # Nexus 2.0 Hierarchy
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'), nullable=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    
    # Parent Portal Relationship
    children = db.relationship(
        'User', 
        secondary=parent_child,
        primaryjoin=(parent_child.c.parent_id == id),
        secondaryjoin=(parent_child.c.child_id == id),
        backref=db.backref('parents', lazy='dynamic'),
        lazy='dynamic'
    )
    

    
    # Advanced Security Features
    totp_secret = db.Column(db.String(32))
    is_2fa_enabled = db.Column(db.Boolean, default=False)
    twofactor_method = db.Column(db.String(20), default='email') # email, totp, both
    otp_code = db.Column(db.String(6))
    otp_expiry = db.Column(db.DateTime)
    backup_codes = db.Column(db.Text) # Stored as comma-separated or JSON string

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # TOTP Helpers
    def get_totp_uri(self):
        import pyotp
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            db.session.commit()
        return pyotp.totp.TOTP(self.totp_secret).provisioning_uri(
            name=self.email, issuer_name="CIIAS Portal")

    def verify_totp(self, token):
        import pyotp
        if not self.totp_secret:
            return False
        totp = pyotp.totp.TOTP(self.totp_secret)
        return totp.verify(token)

    # OTP Helpers
    def generate_otp(self):
        import random
        from datetime import timedelta
        self.otp_code = str(random.randint(100000, 999999))
        self.otp_expiry = datetime.utcnow() + timedelta(minutes=10)
        db.session.commit()
        return self.otp_code

    def verify_otp(self, code):
        if not self.otp_code or not self.otp_expiry:
            return False
        if datetime.utcnow() > self.otp_expiry:
            return False
        return self.otp_code == code

    def to_dict(self, include_phone=True):
        data = {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'campus_id': self.campus_id,
            'dept_id': self.dept_id,
            'campus_name': self.campus.name if self.campus else None,
            'dept_name': self.department.name if self.department else None,
            'profile_photo': self.profile_photo,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_phone:
            data['phone'] = self.phone
        return data



class Incident(db.Model):
    __tablename__ = 'incidents'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # security, fire, medical, accident, infrastructure
    severity = db.Column(db.String(20), default='medium')  # low, medium, high
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved
    image_url = db.Column(db.String(256))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    ai_category = db.Column(db.String(50))
    ai_confidence = db.Column(db.Float)
    ai_labels = db.Column(db.Text)
    ai_severity = db.Column(db.String(20), index=True)
    ai_recommendation = db.Column(db.Text)
    ai_analyzed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='incidents')
    university = db.relationship('University', backref='incidents')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {'name': self.user.name} if self.user else None,
            'description': encryption_manager.decrypt(self.description),
            'category': self.category,
            'severity': self.severity,
            'status': self.status,
            'image_url': self.image_url,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'x': self.x,
            'y': self.y,
            'ai_category': self.ai_category,
            'ai_confidence': self.ai_confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class IncidentComment(db.Model):
    __tablename__ = 'incident_comments'
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incidents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    incident = db.relationship('Incident', backref='comments')
    user = db.relationship('User')

    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'Unknown',
            'comment': self.comment,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SOSAlert(db.Model):
    __tablename__ = 'sos_alerts'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50))  # medical, fire, security, accident
    message = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    user = db.relationship('User', backref='sos_alerts')
    university = db.relationship('University', backref='sos_alerts')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user': {'name': self.user.name} if self.user else None,
            'alert_type': self.alert_type,
            'message': encryption_manager.decrypt(self.message),
            'latitude': self.latitude,
            'longitude': self.longitude,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200))
    message = db.Column(db.Text)
    type = db.Column(db.String(50))  # incident, sos, booking, system
    is_read = db.Column(db.Boolean, default=False)
    data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='notifications')
    university = db.relationship('University', backref='notifications')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'data': self.data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(20))
    capacity = db.Column(db.Integer)
    has_projector = db.Column(db.Boolean, default=False)
    has_whiteboard = db.Column(db.Boolean, default=False)
    has_ac = db.Column(db.Boolean, default=False)
    image_url = db.Column(db.String(256))
    is_available = db.Column(db.Boolean, default=True)
    node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'))

    university = db.relationship('University', backref='rooms')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'building': self.building,
            'floor': self.floor,
            'capacity': self.capacity,
            'has_projector': self.has_projector,
            'has_whiteboard': self.has_whiteboard,
            'has_ac': self.has_ac,
            'image_url': self.image_url,
            'is_available': self.is_available
        }


class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    purpose = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='bookings')
    room = db.relationship('Room', backref='bookings')
    university = db.relationship('University', backref='bookings')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'room_id': self.room_id,
            'room': self.room.to_dict() if self.room else None,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.strftime('%H:%M') if self.start_time else None,
            'end_time': self.end_time.strftime('%H:%M') if self.end_time else None,
            'purpose': self.purpose,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class MapNode(db.Model):
    __tablename__ = 'map_nodes'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    node_type = db.Column(db.String(50))  # building, room, exit, parking, emergency
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    building = db.Column(db.String(100))
    floor = db.Column(db.String(20))
    description = db.Column(db.Text)
    is_accessible = db.Column(db.Boolean, default=True)
    is_emergency_exit = db.Column(db.Boolean, default=False)
    altitude = db.Column(db.Float, default=0.0) # Added for AR Navigation

    university = db.relationship('University', backref='map_nodes')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'node_type': self.node_type,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'x': self.x,
            'y': self.y,
            'building': self.building,
            'floor': self.floor,
            'description': self.description,
            'is_accessible': self.is_accessible,
            'is_emergency_exit': self.is_emergency_exit
        }


class MapEdge(db.Model):
    __tablename__ = 'map_edges'
    id = db.Column(db.Integer, primary_key=True)
    from_node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'), nullable=False)
    to_node_id = db.Column(db.Integer, db.ForeignKey('map_nodes.id'), nullable=False)
    weight = db.Column(db.Float, default=1.0)

    from_node = db.relationship('MapNode', foreign_keys=[from_node_id], backref='edges_from')
    to_node = db.relationship('MapNode', foreign_keys=[to_node_id], backref='edges_to')

    def to_dict(self):
        return {
            'id': self.id,
            'from_node_id': self.from_node_id,
            'to_node_id': self.to_node_id,
            'weight': self.weight
        }


class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(50))  # security, medical, fire, police
    is_active = db.Column(db.Boolean, default=True)

    university = db.relationship('University', backref='emergency_contacts')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'type': self.type,
            'is_active': self.is_active
        }


class SafeZone(db.Model):
    __tablename__ = 'safe_zones'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    capacity = db.Column(db.Integer)
    description = db.Column(db.Text)

    university = db.relationship('University', backref='safe_zones')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'capacity': self.capacity,
            'description': self.description
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(64))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


# ==================== NEW MODULES FOR SMART CAMPUS ====================

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # CS-101
    name = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    schedule = db.Column(db.String(100)) # e.g. "Mon,Wed 10:00-11:30"
    credit_hours = db.Column(db.Integer, default=3)
    
    instructor = db.relationship('User', backref='courses_teaching')

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'instructor': self.instructor.name if self.instructor else 'Unassigned',
            'schedule': self.schedule,
            'credit_hours': self.credit_hours
        }

class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    date = db.Column(db.Date, default=datetime.today)
    status = db.Column(db.String(20), default='Present') # Present, Absent, Late

    course = db.relationship('Course', backref='attendance_records')
    student = db.relationship('User', backref='attendance_records')

class Grade(db.Model):
    __tablename__ = 'grades'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    exam_type = db.Column(db.String(50)) # Midterm, Final, Quiz
    score = db.Column(db.Float)
    total_marks = db.Column(db.Float)
    
    course = db.relationship('Course')

class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    semester = db.Column(db.String(20), default='Fall 2023')
    grade = db.Column(db.String(5), default='In Progress') # A, B, In Progress
    
    user = db.relationship('User', backref='enrollments')
    course = db.relationship('Course', backref='enrollments')

class ExamSeat(db.Model):
    __tablename__ = 'exam_seats'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    room = db.Column(db.String(50))
    seat_number = db.Column(db.String(20))
    exam_time = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='exam_seats')
    course = db.relationship('Course')

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.DateTime, nullable=False)
    total_marks = db.Column(db.Integer, default=100)
    file_url = db.Column(db.String(256))
    
    course = db.relationship('Course', backref='assignments')

    def to_dict(self):
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'total_marks': self.total_marks
        }

class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_url = db.Column(db.String(256))
    obtained_marks = db.Column(db.Float)
    teacher_remarks = db.Column(db.Text)
    
    assignment = db.relationship('Assignment', backref='submissions')
    student = db.relationship('User', backref='assignment_submissions')

    def to_dict(self):
        return {
            'id': self.id,
            'obtained_marks': self.obtained_marks,
            'submission_date': self.submission_date.isoformat() if self.submission_date else None
        }

class TeacherFeedback(db.Model):
    __tablename__ = 'teacher_feedbacks'
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    rating = db.Column(db.Integer) # 1-5
    comments = db.Column(db.Text)
    semester = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class DateSheet(db.Model):
    __tablename__ = 'datesheets'
    id = db.Column(db.Integer, primary_key=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'))
    exam_type = db.Column(db.String(50)) # Midterm, Final, Sessional
    semester = db.Column(db.String(50))
    file_url = db.Column(db.String(256)) # PDF Link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Shuttle(db.Model):
    __tablename__ = 'shuttles'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    plate_number = db.Column(db.String(20), unique=True)
    route_name = db.Column(db.String(50)) # "Blue Line"
    status = db.Column(db.String(20), default='Offline') # Active, Offline, Maintenance
    current_lat = db.Column(db.Float)
    current_lng = db.Column(db.Float)
    heading = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime)
    
    # Nexus 2.0 Enhancements
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    capacity = db.Column(db.Integer)
    model = db.Column(db.String(50))
    
    driver = db.relationship('User', backref='shuttle_assigned')
    university = db.relationship('University', backref='shuttles')

    def to_dict(self):
        return {
            'id': self.id,
            'plate_number': self.plate_number,
            'route_name': self.route_name,
            'status': self.status,
            'current_lat': self.current_lat,
            'current_lng': self.current_lng,
            'heading': self.heading,
            'driver_name': self.driver.name if self.driver else "Unassigned",
            'capacity': self.capacity,
            'model': self.model,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    isbn = db.Column(db.String(20), unique=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100))
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Available') # Available, Issued
    cover_image_url = db.Column(db.String(256))

    university = db.relationship('University', backref='books')
    
    def to_dict(self):
        return {
            'id': self.id,
            'isbn': self.isbn,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'status': self.status,
            'cover_image_url': self.cover_image_url
        }

class Wallet(db.Model):
    __tablename__ = 'wallets'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    balance = db.Column(db.Integer, default=0) # Campus Points
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('wallet', uselist=False))


class CafeteriaItem(db.Model):
    __tablename__ = 'cafeteria_items'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(256))
    is_available = db.Column(db.Boolean, default=True)
    category = db.Column(db.String(50)) # Snacks, Drinks, Meals
    
    # Nexus 2.0 Multi-Campus Support
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id'))
    cafeteria_name = db.Column(db.String(100), default='Main Cafe')
    
    campus = db.relationship('Campus', backref='cafeteria_items')
    university = db.relationship('University', backref='cafeteria_items')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'image_url': self.image_url,
            'is_available': self.is_available,
            'category': self.category,
            'campus_id': self.campus_id,
            'cafeteria_name': self.cafeteria_name
        }


class CafeteriaOrder(db.Model):
    __tablename__ = 'cafeteria_orders'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    items = db.Column(db.JSON, nullable=False) # List of {item_id, quantity, price}
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, preparing, ready, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='cafeteria_orders')
    university = db.relationship('University', backref='cafeteria_orders')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'items': self.items,
            'total_price': self.total_price,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FeeChallan(db.Model):
    __tablename__ = 'fee_challans'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='unpaid') # paid, unpaid, overdue
    pdf_url = db.Column(db.String(256))
    semester = db.Column(db.String(50))
    generated_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='fee_challans')
    university = db.relationship('University', backref='fee_challans')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': self.amount,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'status': self.status,
            'pdf_url': self.pdf_url,
            'semester': self.semester
        }


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_messages')
    university = db.relationship('University', backref='chat_messages')

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'message': encryption_manager.decrypt(self.message),
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_read': self.is_read
        }

# ==================== Relationships (Nexus 2.0 Resilience) ====================

Campus.organization = db.relationship('Organization', backref='campuses')
Department.campus = db.relationship('Campus', backref='departments')
Program.department = db.relationship('Department', backref='programs')

User.campus = db.relationship('Campus', backref='campus_members', foreign_keys=[User.campus_id])
User.department = db.relationship('Department', backref='dept_members', foreign_keys=[User.dept_id])
User.headed_dept = db.relationship('Department', backref='hod', foreign_keys='Department.head_id', uselist=False)

StaffDetail.user = db.relationship('User', backref=db.backref('staff_record', uselist=False))

CafeteriaItem.campus = db.relationship('Campus', backref='cafeteria_items')
Shuttle.campus = db.relationship('Campus', backref='shuttles')
MapPOI.campus = db.relationship('Campus', backref='pois')


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    resource = db.Column(db.String(100))
    ip_address = db.Column(db.String(45))
    details = db.Column(db.Text)
    status = db.Column(db.String(20), default='success')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    university = db.relationship('University', backref='audit_logs')
    user = db.relationship('User', backref='audit_logs')

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.name if self.user else 'System',
            'action': self.action,
            'resource': self.resource,
            'status': self.status,
            'timestamp': self.timestamp.isoformat()
        }


class GradingPolicy(db.Model):
    __tablename__ = 'grading_policies'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False) # e.g. "Standard 4.0", "Relative Grading"
    config = db.Column(db.Text) # JSON string: {"A": 85, "B": 70}
    is_active = db.Column(db.Boolean, default=True)

    university = db.relationship('University', backref='grading_policies')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'config': self.config,
            'is_active': self.is_active
        }


class Webhook(db.Model):
    __tablename__ = 'webhooks'
    id = db.Column(db.Integer, primary_key=True)
    university_id = db.Column(db.Integer, db.ForeignKey('universities.id'), nullable=False)
    url = db.Column(db.String(256), nullable=False)
    event_type = db.Column(db.String(50), nullable=False) # payment_received, user_registered, etc.
    secret_key = db.Column(db.String(64)) # For signature verification
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    university = db.relationship('University', backref='webhooks')

    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'event_type': self.event_type,
            'is_active': self.is_active
        }
