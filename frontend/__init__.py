import os
from flask import Flask, url_for, redirect, request, abort
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_security import Security, SQLAlchemyUserDatastore, signals, \
                           current_user
import flask_admin
from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers
from flask_wtf.csrf import CSRFProtect
from celery import Celery

# -----------------------------------------------------------------------------
# SETUP APP AND BASIC COMPONENTS
# -----------------------------------------------------------------------------

appdir = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.abspath(os.path.join(appdir, os.pardir))
user_data_folder = os.path.join(ROOTDIR, 'userData')

app = Flask(__name__, instance_path=user_data_folder)

app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

mail = Mail(app)

csrf = CSRFProtect(app)

def create_celery_app():
    celery = Celery(__name__, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    celery.app = app
    return celery

# Late import so modules can import their dependencies properly
# The order of the three is important as well!
from frontend import forms, views, models

# -----------------------------------------------------------------------------
# SETUP LOGIN, SECURITY, ADD CUSTOM COUNTRY AND UNI FIELDS TO USER
# -----------------------------------------------------------------------------

from .models import User, Role, load_user
from .forms import ExtendedRegisterForm

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.user_loader(load_user)
login_manager.login_view = "/login"

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore,
                    register_form=ExtendedRegisterForm,
                    confirm_register_form=ExtendedRegisterForm)

# after registration extract uni and country from uni db and add to user
# we also set the default role of the user
from .forms import uni_loaded, uni_data, load_uni_address_data
@signals.user_confirmed.connect_via(app)
def user_confirmed_sighandler(app, user):
    default_role = user_datastore.find_role("user")
    user_datastore.add_role_to_user(user, default_role)
    if not uni_loaded:
        load_uni_address_data()
    user.country = uni_data[user.email.split("@")[1]][0]
    user.uni = uni_data[user.email.split("@")[1]][1]
    return

# -----------------------------------------------------------------------------
# SETUP FLASK ADMIN TO INTEGRATE WITH FLASK SECURITY
# -----------------------------------------------------------------------------

class MyModelView(sqla.ModelView):

    # This allows us to display primary keys, which are hidden by default
    def __init__(self, model, session, name=None, category=None, endpoint=None,
                 url=None, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

        super(MyModelView, self).__init__(model, session, name=name,
                                          category=category, endpoint=endpoint,
                                          url=url)

    # this function connects Flask-Admin to the roles of Flask-Security
    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True
        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is
        not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))

# Create admin
admin = flask_admin.Admin(
    app,
    'Admin panel',
    base_template='admin_base.html',
    template_mode='bootstrap3',
)

# Add model views to the admin panel, these will all get a CRUD interface
from .models import Studies, Analyses
admin.add_view(MyModelView(Role, db.session))
# this way we get to see all the id's and foreign keys as well
cols = [c for c in User.__table__.columns]
admin.add_view(MyModelView(User, db.session, column_list=cols))
cols = [c for c in Studies.__table__.columns]
admin.add_view(MyModelView(Studies, db.session, column_list=cols))
cols = [c for c in Analyses.__table__.columns]
admin.add_view(MyModelView(Analyses, db.session, column_list=cols))

# define a context processor for merging flask-admin's template context
# into the flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )

# -----------------------------------------------------------------------------
# SETUP ERROR SENDING TO ADMIN VIA MAIL AND LOG FILE
# -----------------------------------------------------------------------------

if not app.debug:
    import logging
    from .config import ADMINS, MAIL_SERVER, \
        MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER
    from logging.handlers import SMTPHandler, RotatingFileHandler

    # send bugs to admin(s)
    credentials = (MAIL_USERNAME, MAIL_PASSWORD)
    server = (MAIL_SERVER, MAIL_PORT)
    mail_handler = SMTPHandler(mailhost=server, fromaddr=MAIL_DEFAULT_SENDER,
                               toaddrs=ADMINS, subject='Science Flask error',
                               credentials=credentials, secure=())
    mail_handler.setLevel(logging.ERROR)
    mail_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: '
                              '%(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.addHandler(mail_handler)

    # write log file to server
    log_path = os.path.join(app.config['ROOTDIR'], 'logs', 'ScienceFlask.log')
    file_handler = RotatingFileHandler(log_path, 'a', 1 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: '
                                    '%(message)s [in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.WARNING)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
    app.logger.info('Science Flask started')
