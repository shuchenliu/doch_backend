from flask_restful import Resource
from models.tweets import TweetModel
from models.user import UserModel
from datetime import datetime
from datetime import timedelta
from pytz import timezone
import requests


def get_single_html(screen_name, t_id):
    '''
        could save one parameter, using just t_id => but that would cost
        one extra Twitter API call
    '''
    tweet_url = "https://twitter.com/{}/status/{}".format(screen_name, t_id)
    request_url = "https://publish.twitter.com/oembed?url=" + tweet_url
    r = requests.get(request_url)
    try:
        html_string = r.json()['html']
    except:
        html_string = '<h2>This tweet does not exist any longer</h2>'
        tweet = TweetModel.find_by_tweet_id(t_id)
        if tweet:
            html_string += '\n <h3>this is what we pull from the database:</h3> \n {}'.format(tweet.full_text)

    return html_string



def get_html(screen_name, tweets):

    ##render up to 200 tweets
    counter = 0
    htmls = []
    for t in tweets:
        if counter >= 5:
            break
        html_string = get_single_html(screen_name, t.id)
        htmls.append(html_string)

        counter += 1

    return {
        "body" : {
            "htmls" : htmls,
        },
        "code" : 200,
    }

def pull_up(tweets, today_date):
    count = tweets.count()
    if count == 0:
        return {
            'body' : {
                'message' : 'No recent tweets found',
            },
            'code' : 404,
        }
    res = {}
    res['tweets'] = []
    res['total_fav'] = 0
    res['total_rt'] = 0
    res['count'] = count
    #res['html_string'] = []

    days = 0
    byDay = {}
    interacts = []
    while days < 7:
        this_date = today_date - timedelta(days = days)
        datestr = this_date.isoformat()
        byDay[datestr] = 0
        interacts.append({
            'date': datestr,
            'favs': 0,
            'rts' : 0,
        });
        days +=1

    hours = 0
    hour_freq = {}
    while hours < 24:
        hour_freq[hours] = 0
        hours += 1


    max_rt = -1
    max_fv = -1
    max_rt_id = -1
    max_fv_id = -1

    datePtr = 6
    for t in tweets:
        while t.created_at.date().isoformat() != interacts[datePtr]['date']:
            datePtr -= 1

        interacts[datePtr]['favs'] += t.fv_count
        interacts[datePtr]['rts'] += t.rt_count

        if t.rt_count > max_rt:
            max_rt = t.rt_count
            max_rt_id = t.id

        if t.fv_count > max_fv:
            max_fv = t.fv_count
            max_fv_id = t.id


        max_fv = t.fv_count if t.fv_count > max_fv else max_fv
        datestr = t.created_at.date().isoformat()

        hour = t.created_at.hour
        hour_freq[hour] += 1
        this_tweet = {
            "id": t.id,
            "favs": t.fv_count,
            "rts": t.rt_count,
        }
        res['tweets'].append(this_tweet)
        res['total_fav'] += t.fv_count
        res['total_rt'] += t.rt_count
        byDay[datestr] += 1



    time_freq = {
        'early_morning': 0,
        'morning' : 0,
        'afternoon' : 0,
        'night' : 0,
    }
    for h in range(0,7):
        time_freq['early_morning'] += hour_freq[h]
    for h in range(7,12):
        time_freq['morning'] += hour_freq[h]
    for h in range(12,19):
        time_freq['afternoon'] += hour_freq[h]
    for h in range(19,24):
        time_freq['night'] += hour_freq[h]

    res['time_freq'] = time_freq
    res['hour_freq'] = hour_freq
    res['avg_rt'] = res['total_rt'] / count
    res['avg_fav'] = res['total_fav'] / count
    res['max_fv'] = {
        'count' : max_fv,
        'id' : max_fv_id,
        'text' : TweetModel.find_by_tweet_id(max_fv_id).full_text,
    }
    res['max_rt'] = {
        'count' : max_rt,
        'id' : max_rt_id,
        'text' : TweetModel.find_by_tweet_id(max_rt_id).full_text,
    }

    res['interacts'] = interacts
    res['byDay'] = byDay
    return {
        'body' : res,
        'code' : 200,
    }


class Seven_Days(Resource):
    @classmethod
    def get(self, user_id):

        today_date = datetime.now(tz = timezone("US/Eastern")).date()
        tweets = TweetModel.find_recent_week(user_id, today_date)
        res = pull_up(tweets, today_date)

        return res['body'], res['code']



class Seven_Days_No_Retweets(Resource):
    @classmethod
    def get(self, user_id):
        today_date = datetime.now(tz = timezone("US/Eastern")).date()
        tweets = TweetModel.find_recent_week_no_rt(user_id, today_date)
        #tweets.sort(key = lambda t : t.created_at)
        res = pull_up(tweets, today_date)

        return res['body'], res['code']

class Get_Single_Tweet(Resource):
    @classmethod
    def get(self, screen_name, t_id):
        html_string = get_single_html(screen_name, t_id)

        return {'html': html_string}, 200


class Render_Timeline(Resource):
    '''
    Futher thoughts:
        let the front-end to pass in ids of which associted html needs to be fecthed.
        Render 20; click next page => render another 20 => so on so forth
        Huge time optimization!
    '''
    @classmethod
    def get(self, user_id):
        today_date = datetime.now(tz = timezone("US/Eastern")).date()
        tweets = TweetModel.find_recent_week(user_id, today_date)
        user = UserModel.find_by_user_id(user_id)
        screen_name = user.screenName
        res = get_html(screen_name, tweets)
        return res['body'], res['code']
