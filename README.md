# 🎥 YouTube Downloader Web App (Flask + yt-dlp)

This is a simple YouTube downloader web application built with **Flask** and **yt-dlp**. It allows users to input a YouTube video URL and download the video directly via a clean HTML form interface.

## 📁 Project Structure

```
├── app.py               # Main backend Flask application
├── templates/
│   └── index.html       # HTML form interface (assumed to be present)
├── downloads/           # Output folder for downloaded videos
├── cookies.txt          # YouTube authentication cookies (required)
├── requirements.txt     # Python dependencies
```

## 🚀 How It Works

### 🔧 1. `app.py`

This file contains the Flask application logic.

* **Route `/`**
  Displays the homepage with a form (via `index.html`) to input the YouTube URL.

* **Route `/download` \[POST]**
  Handles form submission. It:

  * Receives the video URL from the user.
  * Uses `yt-dlp` to download the video using options:

    * `cookies.txt`: For accessing private or age-restricted content.
    * `outtmpl`: Saves the file to the `downloads/` folder with video title and extension.
  * Sends the downloaded video file back to the user.

* **Error Handling**
  If the download fails, an HTML error message is displayed suggesting to update the `cookies.txt` file.

* **Server Startup**
  Ensures the `downloads/` folder exists, then starts the Flask server on `http://0.0.0.0:5000`.

### 🧾 2. `requirements.txt`

Specifies the Python dependencies:

```txt
Flask
yt-dlp
```

Install them via:

```bash
pip install -r requirements.txt
```

### 📎 3. `cookies.txt`

YouTube cookies file is used to authenticate the user (especially needed for age-restricted or private videos). You can export this using browser extensions like [Get cookies.txt](https://chrome.google.com/webstore/detail/get-cookiestxt/).

### 📄 4. `index.html`

An HTML template that provides a simple form to submit the video URL. (Not included here but should be present in a `templates/` folder.)

## ▶️ Running the App

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/youtube-downloader.git
   cd youtube-downloader
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Make sure you have a valid `cookies.txt` file in the project root.

4. Run the app:

   ```bash
   python app.py
   ```

5. Open `http://localhost:5000` in your browser.

## 📦 Deployment

You can deploy this app to services like **Render.com**, **Heroku**, or run it on your own server. Ensure `cookies.txt` is included, and the `downloads/` folder has appropriate write permissions.
