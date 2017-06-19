'''
note:
1, Query in the databse if we stored this user before
2.a, If not, we grab tweets from last 7 days as usual,
2.b, If so, we query the date of the last tweets we store.
    - if it is still within 7 days, we used it as the since_id
    - if it is beyond 7 days range, we go back to 2.a

side note:
1, Consider letting the server to grab Trump's tweets every 10 minutes
2, Front-end should by default be set to Trump's tweets


it's should be up to the front-end to decide whether to keep re-tweeted in rendering

'''

import tweepy
import urllib.request
from datetime import datetime
from datetime import date, timedelta
from pytz import timezone


class Tweetify:
    #OAuth

    #TODO use environmental variables to store tokens & secrets
    consumer_key="bYY1Bao6iZtwfUYunWsmx8BZD"
    consumer_secret="4vbM4TTSlpBRuo35vsxSWE7JAqlqbYTAm9oFsepzZO4fRBNVLs"

    access_token="733766645676670976-vvutEKaHcXYKbul2aK9iqEXDPiog2Ek"
    access_token_secret="da3m8JXpSYEwubwPwv2GKysfvZpB0OIa3R3YCcjMPi7Yf"

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)


    def __init__(self, screen_name, end_date, sid, time_now):
        '''
            end date needs to be a datetime object
        '''
        self.user = None
        self.screen_name = screen_name
        self.end_date = end_date
        self.sid = sid
        self.new_sid = sid
        self.mid = 0
        self.user_id = self.get_user_id(screen_name)

        if self.user_id == "-1":
            self.result = {"error" : "user does not exist"}
        else:
            self.result = {
                "error" : None,
                "tweets" : self.tweets_json(),
                "user" : [self.user_json(self.user, time_now)],
            }

    @classmethod
    def get_status(self, id):
        try:
            return self.api.get_status(id)
        except:
            return -1

    def get_user_id(self, screen_name):
        try:
            self.user = self.api.get_user(screen_name = screen_name)
            if self.user.status:
                self.mid = self.user.status.id
            return self.user.id_str
        except:
            return str(-1)


    def tweets_json(self):
        statuses = self.grab_tweets()
        if statuses:
            self.new_sid = statuses[0].id_str
        return statuses
        '''
        json_list = []
        for status in statuses:
            json_list.append(status._json)

        if json_list:
            self.new_sid = json_list[0]["id_str"]
        return json_list
        '''

    def user_json(self, user, time_now):
        json_dict = {}
        json_dict["id"] = user.id_str
        json_dict["screenName"] = user.screen_name
        json_dict["insensitiveName"] = json_dict["screenName"].lower()
        json_dict["name"] = user.name
        json_dict["createdAt"] = timezone('UTC').localize(user.created_at).astimezone(tz = timezone("US/Eastern"))
        json_dict["description"] = user.description
        json_dict["followers"] = user.followers_count
        json_dict["friends"] = user.friends_count
        json_dict["statusCount"] = user.statuses_count
        json_dict["favCount"] = user.favourites_count
        json_dict["location"] = user.location
        json_dict["isVerified"] = user.verified
        avatarUrl = user.profile_image_url.replace('normal', '400x400')
        #print(user.profile_image_url)
        json_dict["avatarUrl"] = avatarUrl


        try:
            json_dict["bannerUrl"] = user.profile_banner_url
            self.save_pic('banner', json_dict["id"], json_dict["bannerUrl"])
        except:
            json_dict["bannerUrl"] = None

        try:
            json_dict["webUrl"] = user.entities["url"]["urls"][0]["expanded_url"]
        except:
            try:
                json_dict["webUrl"] = user.entities["url"]["urls"][0]["url"]
            except:
                json_dict["webUrl"] = None

        self.save_pic('avatar', json_dict["id"], json_dict["avatarUrl"])
        json_dict["lastCheckedTime"] = time_now
        json_dict["lastUpdatedTime"] = time_now
        json_dict["lastTweetId"] = self.new_sid

        return json_dict

    def save_pic(self, flag, id, url):
        filename = "static/img/{}/{}.png".format(flag, id)
        f = open(filename, "wb")
        f.write(urllib.request.urlopen(url).read())
        f.close()


    def grab_tweets(self):
        status_list = []
        if not self.user.status or self.user.status == self.sid:
            return status_list
        max_id = self.mid
        while True:
                statuses = self.api.user_timeline(user_id = self.user_id, max_id = max_id, tweet_mode = "extended")
                #print(len(statuses))
                if statuses:
                    if self.judging(statuses[-1]):
                        status_list += statuses
                        max_id = status_list[-1].id - 1
                    else:
                        for s in statuses:
                            if self.judging(s):
                                status_list.append(s)
                            else:
                                break
                        break
                else:
                    break

        return status_list

    def judging(self, status):
        if self.sid == "-1":
            create_time = timezone('UTC').localize(status.created_at).astimezone(tz = timezone("US/Eastern")).date()
            return create_time >= self.end_date.date()
        else:
            return status.id > int(self.sid)

    @classmethod

    def update_list(self, user_id, since_id):
        page = 0
        tweets = []

        while True:
            current_page = self.api.user_timeline(id=user_id, since_id=since_id, page=page)
            print('ok {}'.format(len(current_page)))
            if len(current_page) == 0 :
                break
            tweets += current_page
            page += 1

        print('doki {}'.format(len(tweets)))
        tweet_info = {}

        for t in tweets:
            id = t.id_str
            tweet_info[id] = {
                "fav": t.favorite_count,
                "rt" : t.retweet_count,
                }

        return tweet_info
