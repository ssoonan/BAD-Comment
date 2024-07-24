from typing import List, Tuple

from app.auth import get_and_refresh_access_token

import googleapiclient.discovery
import dateparser


def make_youtube_api():
    api_service_name = "youtube"
    api_version = "v3"
    credentials = get_and_refresh_access_token()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)
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


def get_my_youtube_channel():
    youtube = make_youtube_api()
    request = youtube.channels().list(part="id", mine=True)
    response = request.execute()
    return response['items'][0]


def block_comment(comment):
    youtube = make_youtube_api()
    request = youtube.comments().setModerationStatus(
        id=comment['id'], moderationStatus="heldForReview")
    request.execute()
