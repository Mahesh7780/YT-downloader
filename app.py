from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_yt_video(url):
    ydl_opts = {
        'format': 'bestvideo[height<=1080]',
        'noplaylist': True,
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            file_path = download_yt_video(url)
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            return f"<h2>Error: {str(e)}</h2>"
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
