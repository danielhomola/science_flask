#!/home/daniel/.virtualenvs/sf/bin/python
from frontend import app, db
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand

# -----------------------------------------------------------------------------
# SETUP DATABASE MIGRATION
# -----------------------------------------------------------------------------
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# -----------------------------------------------------------------------------
# SETUP DEVELOPMENT SERVER
# -----------------------------------------------------------------------------

DEBUG = True
app.debug = DEBUG
app.testing = DEBUG

manager.add_command("runserver", Server(host="0.0.0.0", port=5055))

# -----------------------------------------------------------------------------
# RUN MANAGER
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    manager.run()
