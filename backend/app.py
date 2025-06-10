from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import cv2
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


def count_vehicles(video_path):
    """
    Improved vehicle counting using adaptive thresholding and filtering.
    """
    cap = cv2.VideoCapture(video_path)
    vehicle_count = 0
    frame_count = 0

    # Background Subtraction
    background_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=100, detectShadows=True)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 5 != 0:  # Process every 5th frame to reduce load
            continue

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        fg_mask = background_subtractor.apply(gray)

        # Remove noise
        fg_mask = cv2.GaussianBlur(fg_mask, (5, 5), 0)
        _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)

        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 50000:  # Ignore small and very large objects
                vehicle_count += 1

        if vehicle_count > 100:  # Prevent extreme values
            break

    cap.release()
    
    return min(vehicle_count, 100)  # Limit to 100 for scaling


@app.route("/upload", methods=["POST"])
def upload_files():
    try:
        files = request.files.getlist("videos")

        if len(files) != 4:
            return jsonify({"error": "Please upload exactly 4 videos"}), 400

        vehicle_counts = {}
        video_paths = []

        directions = ["north", "south", "west", "east"]

        for i, file in enumerate(files):
            video_path = os.path.join(app.config["UPLOAD_FOLDER"], f"video_{i}.mp4")
            file.save(video_path)
            video_paths.append(f"uploads/video_{i}.mp4")

            vehicle_counts[directions[i]] = count_vehicles(video_path)

        # 🚦 Improved Traffic Signal Calculation
        max_count = max(vehicle_counts.values()) or 1  # Avoid division by zero

        traffic_light_times = {
            dir: max(5, min(30, int((count / max_count) * 30)))  # Normalize between 5s and 30s
            for dir, count in vehicle_counts.items()
        }

        response_data = {**traffic_light_times, "videos": video_paths}

        return jsonify(response_data), 200

    except Exception as e:
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
