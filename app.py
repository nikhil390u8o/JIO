from flask import Flask, request, redirect, jsonify, send_file
import jiosaavn
from flask_cors import CORS
from thumbnail import generate_thumbnail
from io import BytesIO
from traceback import print_exc

app = Flask(__name__)
CORS(app)


@app.route('/')
def home():
    return redirect("https://cyberboysumanjay.github.io/JioSaavnAPI/")


# -------- THUMBNAIL STREAM ROUTE -------- #

@app.route("/thumb/")
def thumb():
    song_id = request.args.get("id")
    if not song_id:
        return "ID missing", 400

    song_data = jiosaavn.get_song(song_id, False)
    if not song_data:
        return "Song not found", 404

    song = {
        "song": song_data.get("song", "Unknown Song"),
        "artist": song_data.get("primary_artists", "Unknown Artist"),
        "duration": song_data.get("duration", 0),
        "image": song_data.get("image", "")   # ✅ image URL add
    }

    img_io = generate_thumbnail(song)
    return send_file(img_io, mimetype="image/png", as_attachment=False, download_name="thumb.png")


# -------- RESULT WITH CUSTOM THUMB URL -------- #

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

        def add_thumb(song):
            # ✅ Query nahi, song ID use karo
            song["custom_thumbnail"] = request.host_url + "thumb?id=" + song["id"]
            return song

        results = data.get("results", [])
        data["results"] = [add_thumb(song) for song in results]
        return jsonify(data)

    except Exception as e:
        print_exc()
        return jsonify({"status": False, "error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, threaded=True)
