from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from flask import Blueprint, abort, redirect, request, session, url_for, Response
import google_auth_oauthlib.flow
import google.oauth2.credentials

from app.db.model import User


SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtube.force-ssl"]

bp = Blueprint('auth', __name__, url_prefix='/auth')


def get_credentials():
    return session.get('credentials')


def _jwt_to_user(credentials) -> User:
    user_info = id_token.verify_oauth2_token(
        credentials.id_token, Request(), credentials.client_id)
    return User(user_info)


# 순전히 access_token, refresh_token에 해당한 정보만 포함
def _credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
            }


def save_credentials(credentials):
    # 이게 403이 아니라 그냥 500이 뜨네,
    user = _jwt_to_user(credentials)
    user.access_token = credentials.token
    user.refresh_token = credentials.refresh_token
    user.save()
    session['credentials'] = _credentials_to_dict(credentials)
    session['id'] = user.id


# 1. db내 access_token 갱신 2. session내 갱신
def update_token(access_token):
    user_id = session['id']
    user = User.get(user_id)
    user.access_token = access_token
    user.save()
    session['credentials']['token'] = access_token


def get_and_refresh_access_token() -> Credentials:
    credentials = get_credentials()
    # 1. access_token X -> 인증 새로
    if credentials is None:
        return abort(403)
    # access_token이 만료되면 refresh_token으로 인해 자동 갱신
    refreshed_credentials = google.oauth2.credentials.Credentials(**credentials)
    update_token(refreshed_credentials.token)
    return refreshed_credentials


@bp.after_request
def after_api_auth(response: Response):  # 403으로 oauth 동의를 안 할 시
    if response.status_code == 403:
        return redirect(url_for("auth.authorize"))
    return response


@bp.route("/authorize", methods=['GET', 'POST'])
def authorize():
    params = {'access_type': 'offline', 'include_granted_scopes': 'true'}
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json', scopes=SCOPES)
    flow.redirect_uri = url_for("auth.callback", _external=True)
    authorization_url, state = flow.authorization_url(**params)
    session['state'] = state
    return redirect(authorization_url)


@bp.route("/callback", methods=['GET', 'POST'])
def callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'client_secret.json', scopes=None, state=state)
    flow.redirect_uri = url_for("auth.callback", _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    save_credentials(flow.credentials)
    session.permanent = True

    return redirect(url_for("main.test"))
