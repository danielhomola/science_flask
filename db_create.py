from frontend import app, db, user_datastore
import datetime
from sqlalchemy import exists
from flask_security.utils import encrypt_password

with app.app_context():
    db.create_all()

    # add roles and admin to the db, this is only done once
    from frontend.models import Role, User
    user_role_exist = db.session.query(exists().where(Role.name == "user")).scalar()
    super_role_exist = db.session.query(exists().where(Role.name == "superuser")).scalar()
    admin_exist = db.session.query(exists().where(User.first_name == app.config['ADMIN_NAME'])).scalar()

    if not user_role_exist:
        user_role = Role(name='user')
        db.session.add(user_role)
        db.session.commit()
    if not super_role_exist:
        super_user_role = Role(name='superuser')
        db.session.add(super_user_role)
        db.session.commit()

    if not admin_exist:
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        admin_user = user_datastore.create_user(
            first_name=app.config['ADMIN_NAME'],
            email=app.config['ADMIN_EMAIL'],
            password=encrypt_password(app.config['ADMIN_PASSWORD']),
            confirmed_at=datetime.datetime.now(),
            roles=[user_role, super_user_role]
        )
        db.session.commit()
