import webbrowser
import pyperclip
import requests

def get_youtube_thumbnail_url(video_id, quality="maxresdefault"):
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/{quality}.jpg"

    return thumbnail_url


def get_valid_thumbnail_url(youtube_url):
    # Extract the video ID from the YouTube URL
    if "youtu.be" in youtube_url:
        video_id = youtube_url.split('/')[-1].split('?')[0]
    else:
        video_id = youtube_url.split('v=')[-1].split('&')[0]

    maxres_url = get_youtube_thumbnail_url(video_id, "maxresdefault")
    response = requests.get(maxres_url)

    if response.status_code == 404:
        print("Max resolution thumbnail not found. Falling back to high quality.")
        hq_url = get_youtube_thumbnail_url(video_id, "hqdefault")
        return hq_url
    return maxres_url

def open_url_in_browser(url):
    webbrowser.open(url)


def copy_to_clipboard(url):
    pyperclip.copy(url)


if __name__ == "__main__":
    while True:
        youtube_url = input("Enter YouTube video URL: ")
        thumbnail_url = get_valid_thumbnail_url(youtube_url)
        print("Thumbnail URL: {} ".format(thumbnail_url))
        copy_to_clipboard(thumbnail_url)
