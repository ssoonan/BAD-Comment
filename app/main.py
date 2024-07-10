from flask import session, abort, jsonify, Blueprint, redirect, url_for, Response
from typing import Dict
import requests
import googleapiclient.discovery
import googleapiclient.errors
import google.oauth2.credentials

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
    params = {
        'allThreadsRelatedToChannelId': 'UC1bbIVz7kQ014sWnY2UXBuQ', 'part': 'snippet'}
    youtube = make_youtube_api()
    request = youtube.commentThreads().list(**params)
    response = request.execute()
    return jsonify(response)


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
