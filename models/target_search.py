from db import db
from models.user import UserModel

class SearchModel(db.Model):
    '''
    Simply for future data science use
    '''
    __tablename__ = "target_search"

    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #user_id = db.column(db.String(64), db.ForeignKey("user.id"))
    userId = db.Column(db.String(64), db.ForeignKey("user.id"))
    screenName = db.Column(db.String(200))

    timestamp = db.Column(db.DateTime)
    date = db.Column(db.Date)
    year = db.Column(db.Integer)
    month = db.Column(db.Integer)
    day = db.Column(db.Integer)
    hour = db.Column(db.Integer)

    isSuccess = db.Column(db.Boolean)
    statusCount = db.Column(db.Integer)

    def __init__(self, userId, screenName, timestamp, isSuccess, statusCount):
        self.id = None
        self.userId = userId
        self.screenName = screenName
        self.timestamp = timestamp
        self.date = timestamp.date()
        self.year = timestamp.year
        self.month = timestamp.month
        self.day = timestamp.day
        self.hour = timestamp.hour
        self.isSuccess = isSuccess
        self.statusCount = statusCount

    def json(self):
        if self.userId == "-1":
            userInfo = []
        else:
            userInfo = [UserModel.find_by_user_id(self.userId).json()]
        return {
            "id": self.id,
            "user_id" : self.userId,
            "screen_name" : self.screenName,
            "timestamp" : self.timestamp.strftime("%a %b %d %H:%M:%S %z %Y"),
            "isSuccess" : self.isSuccess,
            "status_count" : self.statusCount,
            "user" : userInfo,
        }

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_user_id(cls, userId):
        return cls.query.filter_by(userId = userId).first()

    @classmethod
    def find_by_screen_name(cls, screenName):
        return cls.query.filter_by(screenName = screenName).first()

    @classmethod
    def find_by_result(cls, isSuccess):
        return cls.query.filter_by(isSuccess = isSuccess)

    @classmethod
    def find_by_date(cls, date):
        return cls.query.filter_by(date = date)

    @classmethod
    def find_by_year(cls, year):
        return cls.query.filter_by(year = year)

    @classmethod
    def find_by_month(cls, month):
        return cls.query.filter_by(month = month)

    @classmethod
    def find_by_day(cls, day):
        return cls.query.filter_by(day = day)

    @classmethod
    def find_by_hour(cls, hour):
        return cls.query.filter_by(hour = hour)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
