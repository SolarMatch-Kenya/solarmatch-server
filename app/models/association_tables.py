from ..extensions import db

user_favorites = db.Table(
    'user_favorites',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('installer_id', db.Integer, db.ForeignKey('installers.id'), primary_key=True),
)
