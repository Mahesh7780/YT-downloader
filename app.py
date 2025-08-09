from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

COOKIE_PATH = "/tmp/cookies.txt"

QUALITY_LEVELS = {
    '360p': (360, 480),
    '720p': (720, 1080),
    '1080p': (1080, 1440),
    '2K': (1440, 2000),
    '4K': (2000, 10000),
}

# Helper function for styled error messages
def styled_message(title, message):
    return f"""
    <html>
    <head>
        <style>
            body {{
                background-color: black;
                color: white;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                font-family: Arial, sans-serif;
                text-align: center;
            }}
            h1 {{
                font-size: 2em;
                margin-bottom: 10px;
            }}
            p {{
                font-size: 1.2em;
                color: #ccc;
            }}
            a {{
                color: #ffcc00;
                text-decoration: none;
                margin-top: 20px;
                display: inline-block;
                padding: 10px 20px;
                border: 1px solid #ffcc00;
                border-radius: 5px;
            }}
            a:hover {{
                background-color: #ffcc00;
                color: black;
            }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>{message}</p>
        <a href="/">⬅ Back to Home</a>
    </body>
    </html>
    """

@app.route('/', methods=['GET', 'POST'])
def index():
    formats = []
    url = ""
    message = ""

    if request.method == 'POST':
        # --- Handle cookies upload ---
        if 'cookies' in request.files:
            file = request.files['cookies']
            if file and file.filename.endswith(".txt"):
                file.save(COOKIE_PATH)
                message = "✅ Cookies uploaded successfully."
                return render_template('index.html', url="", formats=[], message=message)

        # --- Get URL and selected format ---
        url = request.form.get('url', '').strip()
        format_id = request.form.get('format_id')

        # --- Step 1: Download video ---
        if format_id:
            try:
                ydl_opts = {
                    'format': format_id,
                    'merge_output_format': 'mp4',
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                    'quiet': True
                }
                if os.path.exists(COOKIE_PATH):
                    ydl_opts['cookies'] = COOKIE_PATH

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                return send_file(filename, as_attachment=True)

            except Exception as e:
                err_text = str(e)
                if "Requested format is not available" in err_text:
                    return styled_message("❌ Quality Not Available", "This video is not available in the selected quality. Please choose another quality and try again.")
                else:
                    return styled_message("⚠️ Download Failed", err_text)

        # --- Step 2: Fetch available formats ---
        elif url:
            try:
                ydl_opts = {
                    'quiet': True,
                    'skip_download': True
                }
                if os.path.exists(COOKIE_PATH):
                    ydl_opts['cookies'] = COOKIE_PATH

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    all_formats = info.get('formats', [])

                # --- Get best audio format ---
                audio_formats = [
                    f for f in all_formats
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('abr') is not None
                ]
                best_audio = max(audio_formats, key=lambda x: x['abr']) if audio_formats else None

                # --- Filter video formats by quality ---
                quality_formats = {}
                for f in all_formats:
                    height = f.get('height')
                    if not height:
                        continue  # skip audio-only formats

                    for label, (min_h, max_h) in QUALITY_LEVELS.items():
                        if min_h <= height < max_h and label not in quality_formats:
                            if f.get('acodec') != 'none':
                                fmt_id = f['format_id']
                            elif best_audio:
                                fmt_id = f"{f['format_id']}+bestaudio"
                            else:
                                fmt_id = f['format_id']

                            size = f.get('filesize') or f.get('filesize_approx', 0)
                            size_str = f"{size // 1024 // 1024} MB" if size else "Unknown"
                            ext = f.get('ext', 'mp4')

                            quality_formats[label] = {
                                'format_id': fmt_id,
                                'label': f"{label} - {ext} - {size_str}"
                            }

                ordered = ['360p', '720p', '1080p', '2K', '4K']
                formats = [quality_formats[q] for q in ordered if q in quality_formats]

            except Exception as e:
                return styled_message("⚠️ Could Not Fetch Formats", str(e))

    return render_template('index.html', url=url, formats=formats, message=message)

if __name__ == '__main__':
    os.makedirs("/tmp", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
