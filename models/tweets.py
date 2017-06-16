from db import db
from datetime import timedelta
from pytz import timezone
from sqlalchemy import func

class TweetModel(db.Model):
    __tablename__ = "tweets"

    #id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #user_id = db.column(db.Integer, db.ForeignKey(user.id), primary_key = True)
    id = db.Column(db.String(64), primary_key = True)
    created_at = db.Column(db.DateTime)
    user_id = db.Column(db.String(64), db.ForeignKey("user.id"))
    user_screen_name = db.Column(db.String(32))
    full_text = db.Column(db.String(250))
    is_quote_status = db.Column(db.Boolean)
    is_retweeted = db.Column(db.Boolean)
    rt_count = db.Column(db.Integer)
    fv_count = db.Column(db.Integer)
    retweeted_statsus_id = db.Column(db.String(64))
    # TODO hashtag = db.Column(db.String(140))
    # TODO mentions
    # TODO WEEKDAY

    def __init__(self, id, created_at, user_id, full_text, is_quote_status, is_retweeted, rt_count, fv_count, retweeted_statsus_id, user_screen_name):
        #print(created_at)
        self.id = id
        self.created_at = timezone('UTC').localize(created_at).astimezone(tz = timezone("US/Eastern"))
        self.user_id = user_id
        self.full_text = full_text
        self.is_quote_status = is_quote_status
        self.is_retweeted = is_retweeted
        self.retweeted_statsus_id = retweeted_statsus_id
        self.rt_count = rt_count
        self.fv_count = fv_count
        self.user_screen_name = user_screen_name

    def json(self):
        return {
            "id" : self.id,
            "created_at" : self.created_at.strftime("%a %b %d %H:%M:%S %z %Y"),
            "user_id" : self.user_id,
            "full_text" : self.full_text,
            "is_quote_status" : self.is_quote_status,
            "is_retweeted" : self.is_retweeted,
            "rt_count" : self.rt_count,
            "fv_count" : self.fv_count,
            "retweeted_statsus_id" : self.retweeted_statsus_id,
            "user_screen_name" : self.user_screen_name,
        }

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_tweet_id(cls, id):
        return cls.query.filter_by(id = id).first()

    @classmethod
    def find_by_user_id(cls, userId):
        return cls.query.filter_by(user_id = userId)

    @classmethod
    def find_recent_week(cls, user_id, today_date):
        return cls.query.filter_by(user_id = user_id).filter(func.Date(cls.created_at) >= today_date - timedelta(days = 6)).order_by(cls.created_at)

    @classmethod
    def find_recent_week_no_rt(cls, user_id, today_date):
        return cls.query.filter_by(user_id = user_id).filter(cls.created_at >= today_date - timedelta(days = 6)).filter_by(is_retweeted = False).order_by(cls.created_at)

    @classmethod
    def find_recent_week_only_rt(cls, user_id, today_date):
        return cls.query.filter_by(user_id = user_id).filter(cls.created_at >= today_date - timedelta(days = 6)).filter_by(is_retweeted = True).order_by(cls.created_at)

    @classmethod
    def find_by_date(cls, date):
        return cls.query.filter_by(created_at = date)

    @classmethod
    def find_tweets_before(cls, user_id, since_id):
        return cls.query.filter_by(user_id = user_id).filter(cls.id > since_id)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
