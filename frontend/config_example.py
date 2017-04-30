# coding=utf-8
import os

appdir = os.path.abspath(os.path.dirname(__file__))
ROOTDIR = os.path.abspath(os.path.join(appdir, os.pardir))

# -----------------------------------------------------------------------------
# Flask settings
# http://flask.pocoo.org/docs/config/#configuring-from-files
# -----------------------------------------------------------------------------

SECRET_KEY = "MAKE_THIS_SECURE:https://pythonadventures.wordpress.com/2015/01/01/flask-generate-a-secret-key/"
FLASH_MESSAGES = True

# If these two are true, no emails are sent
DEBUG = True
TESTING = True

# -----------------------------------------------------------------------------
# Science Flask settings
# -----------------------------------------------------------------------------

#  name of the app
APP_NAME = 'Science Flask'
# backend files
BACKEND_FOLDER = os.path.join(ROOTDIR, 'backend')
# what to use before user id as a string
USER_PREFIX = 'user'
# what to use before study id as a string
DATASET_PREFIX = 'study'
# where to upload study
UPLOAD_FOLDER = os.path.join(ROOTDIR, 'userData')
# where to copy failed analysis so we can debug them later
FAILED_FOLDER = os.path.join(ROOTDIR, 'failedAnalyses')

# max file size in upload 10 MB
MAX_CONTENT_LENGTH = 1 * 1024 * 1024
# max file size in upload as string
MAX_FILE_SIZE = '1 MB'
# maximum number of studies allowed per user at any time-point
ACTIVE_STUDY_PER_USER = 2
# maximum number of studies allowed per user altogether (delete -> re-upload)
STUDY_PER_USER = 3
# maximum number of analysis allowed per user at any time-point
ACTIVE_ANALYSIS_PER_USER = 3
# maximum number of analysis allowed per user altogether (delete -> re-upload)
ANALYSIS_PER_USER = 5

# the min number of samples that we need in both datasets and dashboard file
INTERSECTING_SAMPLES = 15
# number of maximum samples we support per dataset
MAX_SAMPLES = 100
# number of maximum features we support per dataset
MAX_FEATURES = 50
# minimum number of numeric features in a dataset
MINIMUM_FEATURES = 10

# -----------------------------------------------------------------------------
# Flask-SQLAlchemy
# http://pythonhosted.org/Flask-SQLAlchemy/config.html
# -----------------------------------------------------------------------------

SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(ROOTDIR, "science_flask.db")
SQLALCHEMY_TRACK_MODIFICATIONS = True

# If you want to have a mysql database hosted on aws instead use this line:
# SQLALCHEMY_DATABASE_URI = "mysql+pymysql://user:pass@database_name.fixed_url_of_mysql_database"
# Also check out this great tutorial: https://medium.com/@rodkey/deploying-a-flask-application-on-aws-a72daba6bb80

# -----------------------------------------------------------------------------
# Flask-Security
# http://pythonhosted.org/Flask-Security/configuration.html
# -----------------------------------------------------------------------------

SECURITY_EMAIL_SENDER = "admin@example.com"

SECURITY_POST_LOGIN_VIEW = "profile"
SECURITY_POST_REGISTER_VIEW = "profile"
SECURITY_POST_CONFIRM_VIEW = "profile"
SECURITY_POST_CHANGE_VIEW = "index"
SECURITY_POST_RESET_VIEW = "index"
SECURITY_POST_LOGOUT_VIEW = "index"

SECURITY_CONFIRMABLE = True
SECURITY_REGISTERABLE = True
SECURITY_RECOVERABLE = True
SECURITY_CHANGEABLE = True
SECURITY_TRACKABLE = True

SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_PASSWORD_SALT = SECRET_KEY
SECURITY_CONFIRM_SALT = SECRET_KEY
SECURITY_RESET_SALT = SECRET_KEY
SECURITY_LOGIN_SALT = SECRET_KEY
SECURITY_REMEMBER_SALT = SECRET_KEY
SECURITY_DEFAULT_REMEMBER_ME = True

SECURITY_MSG_INVALID_PASSWORD = ("Bad username or password", "error")
SECURITY_MSG_PASSWORD_NOT_PROVIDED = ("Bad username or password", "error")
SECURITY_MSG_USER_DOES_NOT_EXIST = ("Bad username or password", "error")
SECURITY_MSG_PASSWORD_NOT_SET = ("No password is set for this user. Sign in "
                                 "with your registered provider on the right.",
                                 "error")

# -----------------------------------------------------------------------------
# Flask-Admin credentials
# -----------------------------------------------------------------------------

ADMIN_NAME = "Admin"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "something_strong"

# -----------------------------------------------------------------------------
# Flask-Mail
# http://pythonhosted.org/Flask-Mail/
#
# if TLS = True then port needs to be 587, if SSL = True it needs to 465. With
# 465 logging SMTPhandler doesn't work. So TSL it is.
# -----------------------------------------------------------------------------

MAIL_SERVER = 'email-smtp.eu-west-1.amazonaws.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'XYZ'
MAIL_PASSWORD = 'ASD'
#MAIL_DEBUG = True
# email addresses to send errors and logs
MAIL_DEFAULT_SENDER = "admin@example.com"
# add all the emails that should be notified if there's a bug/crash/hiccup
ADMINS = ["admin@example.com"]

# -----------------------------------------------------------------------------
# Celery
# http://blog.miguelgrinberg.com/post/using-celery-with-flask
# -----------------------------------------------------------------------------

CELERY_BROKER_URL = 'amqp://'
CELERY_SEND_TASK_ERROR_EMAILS = True
SERVER_EMAIL = "admin@example.com"
EMAIL_HOST = MAIL_SERVER
EMAIL_HOST_USER = MAIL_USERNAME
EMAIL_HOST_PASSWORD = MAIL_PASSWORD
EMAIL_PORT = MAIL_PORT
EMAIL_USE_SSL = MAIL_USE_SSL
EMAIL_USE_TLS = MAIL_USE_TLS