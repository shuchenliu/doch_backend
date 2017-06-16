'''
note:
1, Query in the databse if we stored this user before
2.a, If not, we grab tweets from last 7 days as usual,
2.b, If so, we query the date of the last tweets we store.
    - if it is still within 7 days, we used it as the since_id
    - if it is beyond 7 days range, we go back to 2.a

side note:
1, Consider letting the server to grab Trump's tweets every 10 minutes
2, Front-end would by default set to Trump's tweets

'''



'''
Serious corner case: name changed and the database would meddle two different accounts together:
so => double check by ID
'''
import traceback
from db import db
from flask_restful import Resource, reqparse
from datetime import datetime, timedelta
from pytz import timezone


from models.user import UserModel
from models.target_search import SearchModel
from models.tweets import TweetModel

from utils.tweetify import Tweetify

class Target_Search(Resource):

    @classmethod
    def get(self, screen_name):
        # TODO check if user already in database and change endtime accordling
        time_now = datetime.now(tz = timezone("US/Eastern"))
        user = UserModel.find_by_screen_name(screen_name)
        try:
            within_a_week = timezone('US/Eastern').localize(user.lastCheckedTime).date() >= time_now.date() - timedelta(days = 6)
        except:
            within_a_week = False


        if user and within_a_week:
            end_date = user.lastCheckedTime
            since_id = user.lastTweetId
        else:
            end_date = time_now - (timedelta(days = 6))
            since_id = "-1"

        tweet_user = Tweetify(screen_name, end_date, since_id, time_now)

        data = {
            "userId" :tweet_user.user_id,
            "screenName" : screen_name,
            "timestamp" : time_now,
        }

        result = tweet_user.result;

        # Not user by this screen_name
        if result["error"]:
            data["isSuccess"] = False
            data["statusCount"] = 0
            search = SearchModel(**data)
            search.save_to_db()
            return {"search_info":search.json(),"error":result["error"]}, 404

        # Save to user db
        user_data = result["user"][0]



        if user:
            user.name = user_data["name"]
            user.insensitive_name = user_data["insensitiveName"]
            user.description = user_data["description"]
            user.followers = user_data["followers"]
            user.friends = user_data["friends"]
            user.statusCount = user_data["statusCount"]
            user.favCount = user_data["favCount"]
            user.location = user_data["location"]
            user.isVerified = user_data["isVerified"]
            user.avatarUrl = user_data["avatarUrl"]
            user.bannerUrl = user_data["bannerUrl"]
            user.lastTweetId = user_data["lastTweetId"]
            user.lastCheckedTime = user_data["lastCheckedTime"]
            user.webUrl = user_data["webUrl"]
            user.tweets_onfile += len(result["tweets"])
            user.save_to_db()

            '''
            the tweet stats updating module


            today_date = time_now.date()
            pre_tweets = TweetModel.find_recent_week_no_rt(user_data['id'], today_date)

            for t in pre_tweets:
                new_t = Tweetify.get_status(t.id)
                if new_t != -1:
                    setattr(t, "rt_count", new_t.retweet_count)
                    setattr(t, "fv_count", new_t.favorite_count)
            '''
        else:
            new_user = UserModel(tweets_onfile = len(result["tweets"]), **user_data)
            new_user.save_to_db()



        # TODO Save to tweets db
        tweets = result["tweets"]

        for t in tweets:
            tweet_data = {
                "id" : t.id_str,
                "created_at" : t.created_at,
                "user_id" : tweet_user.user_id,
                "user_screen_name" : t.author.screen_name,
                "full_text" : t.full_text,
                "is_quote_status" : t.is_quote_status,
                "rt_count" : t.retweet_count,
                "fv_count" : t.favorite_count,
            }
            try:
                tweet_data["retweeted_statsus_id"] = t.retweeted_status.id
                tweet_data["is_retweeted"] = True
                tweet_data["fv_count"] = t.retweeted_status.favorite_count
            except:
                tweet_data["is_retweeted"] = False;
                tweet_data["retweeted_statsus_id"] = None

            new_tweet = TweetModel(**tweet_data)
            new_tweet.save_to_db()


        # Save to DB & return flag to front-end
        data["isSuccess"] = True
        data["statusCount"] = len(tweets)
        search = SearchModel(**data)
        search.save_to_db()


        return {"search_info":search.json()},  200


class Update_Search(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('user_id', type=str, required=True, help="User id needed")
    parser.add_argument('since_id', type=str, required=True, help="Since id needed")

    @classmethod
    def post(self):
        data = self.parser.parse_args()
        if not data['user_id']:
                return {'message' : 'User ID cannot be blank.'}, 400

        if not data['since_id']:
                return {'message' : 'Since ID cannot be blank.'}, 400

        id = int(data['user_id'])
        since_id = int(data['since_id']) - 1
        time_now = datetime.now(tz = timezone("US/Eastern"))
        user = UserModel.find_by_user_id(id)

        within_five = not user.lastUpdatedTime or timezone('US/Eastern').localize(user.lastUpdatedTime) >= time_now - timedelta(minutes = 1)

        if within_five:
            return {'message' : 'Already updated in the last five minutes'}, 200
        else:
            user.lastUpdatedTime = time_now
            user.save_to_db()


        new_tweets = Tweetify.update_list(id, since_id)
        pre_tweets = TweetModel.find_tweets_before(id, since_id)

        try:
            #print('length is {}'.format(len(new_tweets)))
            for t in pre_tweets:

                if not new_tweets:
                    break

                t_id = t.id
                '''
                setattr(t, "rt_count", new_tweets[t_id]['rt'])
                setattr(t, "fv_count", new_tweets[t_id]['fav'])
                '''
                #print('before, {} rt is {}, fv is {}'.format(t.id, t.rt_count, t.fv_count))
                t.rt_count = new_tweets[t_id]['rt']
                t.fv_count = new_tweets[t_id]['fav']
                #print('after, {} rt is {}, fv is {}'.format(t.id, t.rt_count, t.fv_count))
                t.save_to_db()

            message = "updated {} tweets.".format(pre_tweets.count());
            return {'message': message}, 200
        except:
            traceback.print_exc()
            return {'message': 'update failed'}, 500
