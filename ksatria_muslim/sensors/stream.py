import datetime
import os.path
import traceback
from urllib.parse import urlparse

import m3u8
import requests

from moviepy.editor import VideoFileClip, concatenate_videoclips


base_path = os.path.dirname(__file__)

import requests

class RequestsClient():
    def download(self, uri, timeout=None, headers={}, verify_ssl=True):
        o = requests.get(uri, timeout=timeout, headers=headers)
        return o.text, o.url

class M3U8Stream:
    BASE_PATH = os.path.join(base_path, "streams")

    def __init__(self, timeout=60):

        # in seconds
        self.timeout = timeout

        self.playlists = []
        self.output_fname = ""

        os.makedirs(self.BASE_PATH, exist_ok=True)

    def download(self, url):
        time = datetime.datetime.now()
        tick = datetime.datetime.now()
        while True:
            if (tick - time).seconds >= self.timeout:
                print("timeout")
                break

            remote_playlists = m3u8.load(url, http_client=RequestsClient())
            print(f"downloading playlist url, got : {len(remote_playlists.files)}")

            for file_url in remote_playlists.files:

                filename = urlparse(file_url).path.rsplit("/", maxsplit=1)[1]
                print(filename)

                if filename in self.playlists:
                    print(f"file {filename} found, skip")
                    continue

                try:
                    resp = requests.get(file_url)
                    if resp.status_code == 404:
                        print("file not found, skip me")
                        continue

                    with open(os.path.join(self.BASE_PATH, filename), "wb") as f:
                        f.write(resp.content)

                    self.playlists.append(filename)

                except Exception as e:
                    print(f"exception occurred: {e}")
                    traceback.format_exc()
                    continue

            tick = datetime.datetime.now()

    def concat_playlists(self):
        def sorter_key(f):
            key = int(f.split(".")[0].rsplit("_", 1)[1])
            return int(key)

        if not self.playlists:
            print("No playlist downloaded, skip")
            return

        sorted_playlist = sorted(self.playlists, key=sorter_key)

        clips = [VideoFileClip(os.path.join(self.BASE_PATH, f)) for f in sorted_playlist]
        concatenated_clips = concatenate_videoclips(clips)

        output_fname = os.path.join(self.BASE_PATH, "output.mp4")
        concatenated_clips.write_videofile(output_fname)
        self.output_fname = output_fname

    def clean(self):
        files = [
            os.path.join(self.BASE_PATH, f) for f in self.playlists
        ] + [self.output_fname]

        for f in files:
            os.remove(f)

    @property
    def output_file(self):
        return self.output_fname

