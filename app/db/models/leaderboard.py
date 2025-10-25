from app.db.database import db


class Leaderboard(db.Model):
    __tablename__ = "leaderboards"

    id = db.Column(db.Integer, primary_key=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    total_savings = db.Column(db.Float)
    total_co2_reduced = db.Column(db.Float)
    rank = db.Column(db.Integer)
