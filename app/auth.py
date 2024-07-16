from flask import Blueprint, redirect, request, session, url_for, Response
from dotenv import load_dotenv


import google_auth_oauthlib.flow


load_dotenv()
SCOPES = ["https://www.googleapis.com/auth/youtube",
          "https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/youtube.force-ssl"]

bp = Blueprint('auth', __name__, url_prefix='/auth')


def save_credentials(credentials):
    session['credentials'] = _credentials_to_dict(credentials)


def get_credentials():
    return session.get('credentials')


def _credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes
            }


def _save_to_session(data):
    session['credentials'] = data


def save_credentials(credentials):  # 이후 db 저장까지 연결
    _save_to_session(_credentials_to_dict(credentials))


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
        'client_secret.json', scopes=SCOPES, state=state)
    flow.redirect_uri = url_for("auth.callback", _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    save_credentials(flow.credentials)
    session.permanent = True

    return redirect(url_for("main.test"))
