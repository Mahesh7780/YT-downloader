from flask import Flask, render_template, request, send_file, redirect, url_for, session
import yt_dlp
import os

app = Flask(__name__)
app.secret_key = "replace_with_a_secure_secret_key"  # Needed for session handling

COOKIE_PATH = "cookies.txt"  # Persistent storage in app root

QUALITY_LEVELS = {
    '360p': (360, 480),
    '720p': (720, 1080),
    '1080p': (1080, 1440),
    '2K': (1440, 2000),
    '4K': (2000, 10000),
}

# Helper function for styled messages
def styled_message(title, message, back_link=True):
    back_button = '<a href="/">⬅ Back to Home</a>' if back_link else ''
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
            h1 {{ font-size: 2em; margin-bottom: 10px; }}
            p {{ font-size: 1.2em; color: #ccc; }}
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
        {back_button}
    </body>
    </html>
    """

@app.route('/', methods=['GET', 'POST'])
def index():
    formats = []
    url = request.args.get("retry_url", "")
    message = ""

    if request.method == 'POST':
        # Handle cookies upload (if manually done from main page)
        if 'cookies' in request.files:
            file = request.files['cookies']
            if file and file.filename.endswith(".txt"):
                file.save(COOKIE_PATH)
                session["cookies_uploaded"] = True
                # Retry pending URL if available
                if session.get("pending_url"):
                    return redirect(url_for("index", retry_url=session.pop("pending_url")))
                message = "✅ Cookies uploaded successfully."
                return render_template('index.html', url="", formats=[], message=message)

        # Get URL and format ID
        url = request.form.get('url', '').strip()
        format_id = request.form.get('format_id')

        # Step 1: Download
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
                if "Sign in to confirm you’re not a bot" in err_text or "This video is private" in err_text:
                    session["pending_url"] = url
                    return redirect(url_for("upload_cookies"))
                elif "Requested format is not available" in err_text:
                    return styled_message("❌ Quality Not Available", "This video is not available in the selected quality. Please choose another quality and try again.")
                else:
                    return styled_message("⚠️ Download Failed", err_text)

        # Step 2: Fetch formats
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

                # Get best audio
                audio_formats = [
                    f for f in all_formats
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('abr') is not None
                ]
                best_audio = max(audio_formats, key=lambda x: x['abr']) if audio_formats else None

                # Filter formats by quality
                quality_formats = {}
                for f in all_formats:
                    height = f.get('height')
                    if not height:
                        continue
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
                err_text = str(e)
                if "Sign in to confirm you’re not a bot" in err_text or "This video is private" in err_text:
                    session["pending_url"] = url
                    return redirect(url_for("upload_cookies"))
                else:
                    return styled_message("⚠️ Could Not Fetch Formats", err_text)

    return render_template('index.html', url=url, formats=formats, message=message)

@app.route('/upload-cookies', methods=['GET', 'POST'])
def upload_cookies():
    if request.method == 'POST':
        file = request.files.get('cookies')
        if file and file.filename.endswith(".txt"):
            file.save(COOKIE_PATH)
            session["cookies_uploaded"] = True
            if session.get("pending_url"):
                return redirect(url_for("index", retry_url=session.pop("pending_url")))
            return render_template('index.html', url="", formats=[], message="✅ Cookies uploaded successfully.")
        else:
            return styled_message("⚠️ Invalid File", "Please upload a valid cookies.txt file.")
    return styled_message("🔒 Login Required", "This video requires YouTube login to download. Please upload your cookies.txt file below.", back_link=False) + """
    <form method="POST" enctype="multipart/form-data" style="margin-top:20px; text-align:center;">
        <input type="file" name="cookies" accept=".txt" required>
        <br><br>
        <button type="submit" style="padding:10px 20px;">Upload Cookies</button>
    </form>
    """

if __name__ == '__main__':
    os.makedirs("/tmp", exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
