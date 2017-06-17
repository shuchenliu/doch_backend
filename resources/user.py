from flask_restful import Resource
from models.user import UserModel

'''
TODO: saving avatars to a local dir.
'''

class User(Resource):
    @classmethod
    def get(self, user_id):

        user = UserModel.find_by_user_id(user_id)
        
        if not user:
            user = UserModel.find_by_screen_name(user_id)

        if user:
            return {"user" : user.json()}, 200
        else:
            return {"message": "User not found in the databse"}, 400
