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
    query = request.args.get("query")
    if not query:
        return {"error": "query missing"}

    data = jiosaavn.search_for_song(query, False, True)
    song = data[0] if isinstance(data, list) else data

    img_io = generate_thumbnail(song)

    return send_file(
        img_io,
        mimetype="image/png",
        as_attachment=False,
        download_name="thumb.png"
    )


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
            song["custom_thumbnail"] = (
                request.host_url + "thumb?query=" + query
            )
            return song

        # Multiple songs
        if isinstance(data, list):
            data = [add_thumb(song) for song in data]
            return jsonify(data)

        # Single song
        if isinstance(data, dict):
            return jsonify(add_thumb(data))

        return jsonify(data)

    except Exception as e:
        print_exc()
        return jsonify({"status": False, "error": str(e)})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, threaded=True)
