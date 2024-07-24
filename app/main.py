import datetime
from flask import render_template, jsonify, Blueprint, redirect, url_for, Response


from app.ai import evaluate_comment
from app.youtube import block_comment, get_comments_until_datetime, get_my_youtube_channel

bp = Blueprint('main', __name__, )


@bp.after_request
def after_api_auth(response: Response):  # 403으로 oauth 동의를 안 할 시
    if response.status_code == 403:
        return redirect(url_for("auth.authorize"))
    return response


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/test')
def test():
    target_datetime = datetime.datetime.now(
        tz=datetime.UTC) - datetime.timedelta(days=5)
    youtube_channel = get_my_youtube_channel()
    comments = get_comments_until_datetime(
        youtube_channel['id'], target_datetime)
    for i, comment in enumerate(comments):
        result = evaluate_comment(comment)
        if result:
            # 로깅으로 바꾸기
            print(comment['snippet'])
            # block_comment(comment)
    return jsonify(comments)
