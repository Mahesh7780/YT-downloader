from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# Quality ranges
QUALITY_LEVELS = {
    '360p': (360, 480),
    '720p': (720, 1080),
    '1080p': (1080, 1440),
    '2K': (1440, 2000),
    '4K': (2000, 10000),
}

@app.route('/', methods=['GET', 'POST'])
def index():
    formats = []
    url = ""

    if request.method == 'POST':
        url = request.form.get('url')
        format_id = request.form.get('format_id')

        if format_id:
            try:
                ydl_opts = {
                    'format': format_id,
                    'merge_output_format': 'mp4',
                    'outtmpl': '/tmp/%(title)s.%(ext)s',
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)

                return send_file(filename, as_attachment=True)

            except Exception as e:
                return f"<h3>Error while downloading: {str(e)}</h3>"

        else:
            try:
                ydl_opts = {
                    'quiet': True,
                    'skip_download': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    all_formats = info.get('formats', [])

                # Get audio formats
                audio_formats = [
                    f for f in all_formats
                    if f.get('vcodec') == 'none' and f.get('acodec') != 'none' and f.get('abr') is not None
                ]
                best_audio = max(audio_formats, key=lambda x: x['abr']) if audio_formats else None

                quality_formats = {}

                for f in all_formats:
                    height = f.get('height')
                    if not height or f.get('vcodec') == 'none':
                        continue

                    for label, (min_h, max_h) in QUALITY_LEVELS.items():
                        if min_h <= height < max_h:
                            # Check if this quality has not already been added
                            if label not in quality_formats:
                                # Case 1: video+audio in one format
                                if f.get('acodec') != 'none':
                                    fmt_id = f['format_id']
                                # Case 2: video-only — merge with best audio
                                elif best_audio:
                                    # Confirm both video and audio formats are available
                                    fmt_id = f"{f['format_id']}+{best_audio['format_id']}"
                                else:
                                    continue

                                size = f.get('filesize', 0)
                                size_str = f"{size // 1024 // 1024} MB" if size else "Unknown"
                                ext = f.get('ext', 'mp4')

                                quality_formats[label] = {
                                    'format_id': fmt_id,
                                    'label': f"{label} - {ext} - {size_str}"
                                }

                # Sort final dropdown list
                ordered = ['360p', '720p', '1080p', '2K', '4K']
                formats = [quality_formats[q] for q in ordered if q in quality_formats]

            except Exception as e:
                return f"<h3>Error while fetching formats: {str(e)}</h3>"

    return render_template('index.html', url=url, formats=formats)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
