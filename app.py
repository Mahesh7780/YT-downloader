from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    try:
        ydl_opts = {
            'cookies': 'cookies.txt',  # 👈 tell yt-dlp to use your YouTube cookies
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"<h3>Error: {str(e)}</h3><p>Make sure your cookies.txt is up to date.</p>"

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    app.run(host='0.0.0.0', port=5000,debug=True)
    

