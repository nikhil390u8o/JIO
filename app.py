from flask import Flask, request, redirect, jsonify, send_from_directory
import jiosaavn
import os
from traceback import print_exc
from flask_cors import CORS
from thumbnail import generate_thumbnail

app = Flask(__name__, static_folder="static")
CORS(app)

# Ensure static/thumbs folder exists
os.makedirs("static/thumbs", exist_ok=True)


@app.route('/')
def home():
    return redirect("https://cyberboysumanjay.github.io/JioSaavnAPI/")


@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

from io import BytesIO

@app.route("/thumb/")
def thumb():
    query = request.args.get("query")
    if not query:
        return {"error": "query missing"}

    data = jiosaavn.search_for_song(query, False, True)

    # first result lo
    song = data[0] if isinstance(data, list) else data

    img_io = generate_thumbnail(song)

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=False,
        download_name="thumb.png"
    )


# ---------------- RESULT WITH CUSTOM THUMBNAIL ---------------- #

@app.route('/result/')
def result():
    lyrics = False
    query = request.args.get('query')
    lyrics_ = request.args.get('lyrics')

    if lyrics_ and lyrics_.lower() != 'false':
        lyrics = True

    if not query:
        return jsonify({"status": False, "error": "Query missing"})

    try:
        data = jiosaavn.search_for_song(query, lyrics, True)

        # ---------- MULTIPLE SONGS ----------
        if isinstance(data, list) and len(data) > 0:
            for song in data:
                thumb_filename = generate_thumbnail(song)
                song["custom_thumbnail"] = (
                    request.host_url + "static/thumbs/" + thumb_filename
                )
            return jsonify(data)

        # ---------- SINGLE SONG ----------
        if isinstance(data, dict):
            thumb_filename = generate_thumbnail(data)
            data["custom_thumbnail"] = (
                request.host_url + "static/thumbs/" + thumb_filename
            )
            return jsonify(data)

        return jsonify(data)

    except Exception as e:
        print_exc()
        return jsonify({"status": False, "error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, threaded=True)
