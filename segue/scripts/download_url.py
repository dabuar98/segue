"""
Download content using the url
Parameters:
    url (string): A string representing the URL to download the audio features
    output_path (string): A string representing the path to save the downloaded content
"""
import os
import subprocess
from datetime import datetime

def download_url(url, output_path):
    # Ensure the path is a string
    output_path = str(output_path)
    print(f"[ {datetime.now():%Y-%m-%d %H:%M:%S} ][ INFO ] DownloadUrl: Downloading data from {url}...")
    # check=True throws a CalledProcessError if any error
    # -q: Do not create wget-log files
    subprocess.run(
        ["wget", "-q", url, "-O", output_path],
        check=True
    )