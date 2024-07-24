from typing import Optional
from app.db.firestore import FirestoreModel
import datetime


firestore_model = FirestoreModel('users')


class User:
    db_model = firestore_model

    @classmethod
    def get(cls, id):
        user_data = cls.db_model.get(id)
        if user_data is None:
            return None
        return User(user_data)

    def __init__(self, user_info):
        # 실제 데이터와 매칭해보기
        self.user_img = user_info.get('img') or user_info.get('picture')
        self.name = user_info['name']
        self.email = user_info['email']
        self.id = user_info.get('id') or user_info.get('sub')
        self.channel_id: Optional[str] = user_info.get('channel_id')
        self.refresh_token: Optional[str] = user_info.get('refresh_token')
        self.access_token: Optional[str] = user_info.get('access_token')
        self.last_comment_date: Optional[datetime.datetime] = user_info.get(
            'last_comment_date')

    def __repr__(self) -> str:
        return "user_{}".format(self.name)

    def to_dict(self):
        return {
            'user_img': self.user_img,
            'name': self.name,
            'email': self.email,
            'id': self.id,
            'channel_id': self.channel_id,
            'refresh_token': self.refresh_token,
            'access_token': self.access_token,
            'last_comment_date': self.last_comment_date.isoformat() if self.last_comment_date else None
        }

    def save(self):
        user_data = self.to_dict()
        if self.db_model.get(self.id) is None:
            self.db_model.create(self.id, user_data)
        else:
            self.db_model.update(self.id, user_data)
