from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

# Ensure the 'uploads' directory exists
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        files = request.files.getlist("videos")  # Expecting "videos" key from React

        if len(files) != 4:
            logging.error("Incorrect number of videos uploaded.")
            return jsonify({"error": "Please upload exactly 4 videos"}), 400

        video_paths = []
        for i, file in enumerate(files):
            if file.filename == "":
                return jsonify({"error": f"File {i+1} has no name"}), 400

            try:
                video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"video_{i}.mp4")
                file.save(video_path)
                video_paths.append(f"uploads/video_{i}.mp4")  # Returning relative path
                logging.info(f"✅ Video {i+1} saved: {video_path}")
            except Exception as e:
                logging.exception(f"Error saving video {i+1}")
                return jsonify({"error": f"Error saving video {i+1}: {str(e)}"}), 500

        # Simulated Traffic Light Optimization Result (Example Data)
        example_result = {"north": 15, "south": 20, "west": 10, "east": 25, "videos": video_paths}

        return jsonify(example_result), 200

    except Exception as e:
        logging.exception("❌ An unexpected error occurred during upload")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


@app.route("/uploads/<filename>")
def get_uploaded_video(filename):
    """Serve uploaded videos to React frontend."""
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/")
def home():
    return jsonify({"message": "Flask backend is running!"})


if __name__ == "__main__":
    app.run(debug=True)
