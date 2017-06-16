from db import db

class UserModel(db.Model):
    __tablename__ = "user"

    #id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    #user_id = db.column(db.Integer, db.ForeignKey(user.id), primary_key = True)
    id = db.Column(db.String(64), primary_key = True)
    screenName = db.Column(db.String(200))
    name = db.Column(db.String(200))
    createdAt = db.Column(db.DateTime)
    date = db.Column(db.Date)
    year = db.Column(db.Integer)
    description = db.Column(db.String(200))
    followers = db.Column(db.Integer)
    friends = db.Column(db.Integer)
    statusCount = db.Column(db.Integer)
    favCount = db.Column(db.Integer)
    location = db.Column(db.String(100))
    isVerified = db.Column(db.Boolean, nullable = False)
    avatarUrl = db.Column(db.String(300))
    bannerUrl = db.Column(db.String(300))
    lastCheckedTime = db.Column(db.DateTime)
    lastUpdatedTime = db.Column(db.DateTime)
    lastTweetId = db.Column(db.String(64))
    webUrl = db.Column(db.String(200))
    insensitiveName = db.Column(db.String(200))
    tweets_onfile = db.Column(db.Integer)

    def __init__(self,
                tweets_onfile,
                id,
                screenName,
                name,
                createdAt,
                description,
                followers,
                friends,
                statusCount,
                #rt_count,
                favCount,
                location,
                isVerified,
                avatarUrl,
                bannerUrl,
                lastTweetId,
                lastCheckedTime,
                webUrl,
                insensitiveName,
                lastUpdatedTime):

#id,screen_name,name,created_at,description,followers,friends,status_count,rt_count,fav_count,location,is_verified,avatar_url,banner_url
        self.id = id
        self.screenName = screenName
        self.name = name
        self.createdAt = createdAt
        self.date = createdAt.date()
        self.year = createdAt.year
        self.description = description
        self.followers = followers
        self.friends = friends
        self.statusCount = statusCount
        self.favCount = favCount
        self.location = location
        self.isVerified = isVerified
        self.avatarUrl = avatarUrl
        self.bannerUrl = bannerUrl
        self.lastCheckedTime = lastCheckedTime
        self.lastTweetId = lastTweetId
        self.webUrl = webUrl
        self.insensitiveName = insensitiveName
        self.tweets_onfile = tweets_onfile
        self.lastUpdatedTime = lastUpdatedTime

    def json(self):
        if not self.lastUpdatedTime:
            value = self.lastCheckedTime.strftime("%a %b %d %H:%M:%S %z %Y")
        else:
            value = self.lastUpdatedTime.strftime("%a %b %d %H:%M:%S %z %Y")
        return {
            "id" : self.id,
            "screenName" : self.screenName,
            "name" : self.name,
            "createdAt" : self.createdAt.strftime("%a %b %d %H:%M:%S %z %Y"),
            "description" : self.description,
            "followers" : self.followers,
            "friends" : self.friends,
            "statusCount" : self.statusCount,
            "favCount" : self.favCount,
            "location" : self.location,
            "isVerified" : self.isVerified,
            "avatarUrl" : self.avatarUrl,
            "bannerUrl" : self.bannerUrl,
            "lastCheckedTime" : self.lastCheckedTime.strftime("%a %b %d %H:%M:%S %z %Y"),
            "lastUpdatedTime" : value,
            "lastTweetId" : self.lastTweetId,
            "webUrl" : self.webUrl,
            "tweets_onfile" : self.tweets_onfile
        }

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_user_id(cls, userId):
        return cls.query.filter_by(id = userId).first()

    @classmethod
    def find_by_screen_name(cls, screenName):
        return cls.query.filter_by(insensitiveName = screenName.lower()).first()

    @classmethod
    def find_by_date(cls, date):
        return cls.query.filter_by(date = date)

    @classmethod
    def find_by_year(cls, year):
        return cls.query.filter_by(year = year)


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
