from flask_restful import Resource
from models.tweets import TweetModel

'''
TODO: saving avatars to a local dir.
'''

class Tweet(Resource):
    @classmethod
    def get(self, tweet_id):

        tweet = TweetModel.find_by_tweet_id(tweet_id)


        ''' inspect module
        columns = [m.key for m in user.__table__.columns]
        print(columns)
        '''

        if tweet:
            return {"tweet" : tweet.json()}, 200
        else:
            return {"message": "User not found in the databse"}, 400
