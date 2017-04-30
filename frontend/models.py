from . import db
from datetime import datetime
from flask_security import UserMixin, RoleMixin

# -----------------------------------------------------------------------------
# CLASSES FOR SECURITY
# -----------------------------------------------------------------------------

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

# -----------------------------------------------------------------------------
# USER CLASS
# -----------------------------------------------------------------------------

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    country = db.Column(db.String(120))
    uni = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    created = db.Column(db.DateTime, default=datetime.now)
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)
    num_studies = db.Column(db.Integer, default=0)
    num_analyses = db.Column(db.Integer, default=0)
    profile_intro = db.Column(db.Integer, default=0)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    studies = db.relationship('Studies', backref='author', lazy='dynamic')
    analyses = db.relationship('Analyses', backref='author', lazy='dynamic')

    @property
    def cn(self):
        if not self.first_name:
            return self.email
        return u"{}".format(self.first_name)

    @property
    def gravatar(self):
        email = self.email.strip()
        email = email.encode("utf-8")
        import hashlib
        encoded = hashlib.md5(email).hexdigest()
        return "https://secure.gravatar.com/avatar/%s.png" % encoded

def load_user(user_id):
    return User.query.get(user_id)

# -----------------------------------------------------------------------------
# STUDIES AND ANALYSES
# -----------------------------------------------------------------------------

class Studies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    study_name = db.Column(db.String(30))
    dataset1 = db.Column(db.String(255))
    dataset1_type = db.Column(db.String(30))
    autocorr = db.Column(db.Boolean())
    dataset2 = db.Column(db.String(255))
    dataset2_type = db.Column(db.String(30))
    timestamp = db.Column(db.DateTime)
    analyses = db.relationship('Analyses', backref='study', lazy='dynamic')


class Analyses(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    study_id = db.Column(db.Integer, db.ForeignKey('studies.id'))
    analysis_name = db.Column(db.String(30))
    status = db.Column(db.Integer)
    feat_num = db.Column(db.Integer)
    multi_corr_method = db.Column(db.String(30))
    alpha_val = db.Column(db.Float())
    timestamp_start = db.Column(db.DateTime)
    timestamp_finish = db.Column(db.DateTime)