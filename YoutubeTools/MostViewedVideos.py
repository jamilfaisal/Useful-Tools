import os
from dotenv import load_dotenv
import googleapiclient.discovery


def get_videos_from_channel(channel_id):
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    videos = []
    next_page_token = None

    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=uploads_playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            video_id = item['snippet']['resourceId']['videoId']
            title = item['snippet']['title']
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            video_data = {'title': title, 'url': video_url, 'video_id': video_id}
            videos.append(video_data)

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return videos


def filter_videos_by_views(videos, min_views=500000):
    for video in videos:
        video_id = video['video_id']
        request = youtube.videos().list(
            part="statistics",
            id=video_id
        )
        response = request.execute()
        views = int(response['items'][0]['statistics']['viewCount'])
        if views >= min_views:
            print(f"Title: {video['title']}, Views: {views}, Link: {video['url']}")


if __name__ == "__main__":
    load_dotenv()
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.getenv("YOUTUBE_API_KEY")

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

    channel_id = ""  # Channel ID
    if channel_id == "":
        print("Channel ID not entered!")
        exit(1)

    videos = get_videos_from_channel(channel_id)
    filter_videos_by_views(videos, min_views=500000)
