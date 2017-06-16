from flask import Flask, request, url_for
from flask_restful import Resource, Api
from resources.target_search import Target_Search, Update_Search
from resources.user import User
from resources.seven import Seven_Days, Seven_Days_No_Retweets, Render_Timeline, Get_Single_Tweet
from resources.tweet import Tweet

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','sqlite:///myteam.db')
application = app 
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trumpy.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
api = Api(app)


api.add_resource(Target_Search,'/target_search/<string:screen_name>')
api.add_resource(User, '/user/<string:user_id>')
api.add_resource(Seven_Days, '/seven/<string:user_id>')
api.add_resource(Seven_Days_No_Retweets, '/seven_no_rt/<string:user_id>')
api.add_resource(Render_Timeline, '/timeline/<string:user_id>')
api.add_resource(Get_Single_Tweet, '/single_html/<string:screen_name>/<string:t_id>')
api.add_resource(Update_Search, '/update_tweets')

# test endpoint

api.add_resource(Tweet, '/tweet/<string:tweet_id>')


@app.before_first_request
def create_db():
##########################
### Only for test ########
  #  db.drop_all() ########
##########################
    db.create_all()

if __name__ == '__main__' :
    from db import db
    db.init_app(app)
    app.run(host = '127.0.0.1', port = 5000, debug=True)