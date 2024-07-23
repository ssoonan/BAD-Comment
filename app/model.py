class User:
    def __init__(self, user_info):
        # 실제 데이터와 매칭해보기
        self.user_img = user_info.get('img') or user_info.get('picture')
        self.name = user_info['name']
        self.email = user_info['email']
        self.id = user_info.get('id') or user_info.get('sub')
        # self.channel_id = user_info['channel_id']
        # self.refresh_token = user_info.get('refresh_token')
        # self.access_token = user_info.get('access_token')
        # self.last_comment_date = user_info.get('last_comment_date')
    
    def __repr__(self) -> str:
        return "user_{}".format(self.name)

    # 클래스에서 바로 할지, dao나 다른 걸로 이을지는 고민 필요
    def save(self):
        pass