import datetime
from typing import List, Tuple
from flask import session, abort, jsonify, Blueprint, redirect, url_for, Response
import googleapiclient.discovery
import googleapiclient.errors
import google.oauth2.credentials
import dateparser

from app.ai import evaluate_comment
from app.auth import _credentials_to_dict

bp = Blueprint('main', __name__, )


def make_youtube_api():
    api_service_name = "youtube"
    api_version = "v3"
    credentials = session.get('credentials')
    if credentials is None:
        return abort(403)
    credentials = google.oauth2.credentials.Credentials(**credentials)
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
    session['credentials'] = _credentials_to_dict(credentials)
    return youtube


def get_comments_until_datetime(channel_id, target_datetime):
    comments = []
    page_token = None
    while True:
        each_comments, page_token = _get_comments_by_page_token(
            channel_id, target_datetime, page_token)
        comments.extend(each_comments)
        if page_token is None:
            break
    return comments


def _get_comments_by_page_token(channel_id, target_datetime, page_token=None) -> Tuple[List[dict], str]:
    params = {'allThreadsRelatedToChannelId': channel_id,
              'part': 'snippet', 'pageToken': page_token}
    youtube = make_youtube_api()
    request = youtube.commentThreads().list(**params)
    response = request.execute()
    comments = response['items']
    page_token = response['nextPageToken']
    filtered_comments = []
    for comment in comments:
        comment_datetime = _get_comment_datetime(comment)
        if comment_datetime < target_datetime:
            page_token = None
            break
        filtered_comments.append(comment)
    return filtered_comments, page_token


def _get_comment_datetime(comment):
    return dateparser.parse(comment['snippet']['topLevelComment']['snippet']['publishedAt'])


@bp.after_request
def after_api_auth(response: Response):  # 403으로 oauth 동의를 안 할 시
    if response.status_code == 403:
        return redirect(url_for("auth.authorize"))
    return response


@bp.route('/')
def index():
    return print_index_table()


@bp.route('/test')
def test():
    channel_id = 'UC1bbIVz7kQ014sWnY2UXBuQ'
    target_datetime = datetime.datetime.now(
        tz=datetime.UTC) - datetime.timedelta(days=1)

    comments = get_comments_until_datetime(channel_id, target_datetime)
    for i, comment in enumerate(comments):
        comments[i]["blocked"] = evaluate_comment(comment)
    return jsonify(comments)


def print_index_table():
    return ('<table>' +
            '<tr><td><a href="/test">Test an API request</a></td>' +
            '<td>Submit an API request and see a formatted JSON response. ' +
            '    Go through the authorization flow if there are no stored ' +
            '    credentials for the user.</td></tr>' +
            '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
            '<td>Go directly to the authorization flow. If there are stored ' +
            '    credentials, you still might not be prompted to reauthorize ' +
            '    the application.</td></tr>' +
            '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
            '<td>Revoke the access token associated with the current user ' +
            '    session. After revoking credentials, if you go to the test ' +
            '    page, you should see an <code>invalid_grant</code> error.' +
            '</td></tr>' +
            '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
            '<td>Clear the access token currently stored in the user session. ' +
            '    After clearing the token, if you <a href="/test">test the ' +
            '    API request</a> again, you should go back to the auth flow.' +
            '</td></tr></table>')
