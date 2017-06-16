from flask import url_for
from flask_restful import Resource



class Avatar(Resource):
    def get(self, user_id):
        file_name = "/avatar/{}.png".format(user_id)

        url = url_for(file_name)

        return {'url' : url}, 200


class Banner(Resource):
    def get(self, user_id):
        file_name = "{}.png".format(user_id)
        url = url_for('banner', filename=file_name)

        return {'url' : url}, 200
