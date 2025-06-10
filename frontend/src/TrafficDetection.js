import React, { useState } from "react";

const TrafficDetection = () => {
    const [selectedFiles, setSelectedFiles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const handleFileChange = (event) => {
        setSelectedFiles(event.target.files);
    };

    const handleUpload = async () => {
        if (selectedFiles.length !== 4) {
            alert("Please upload exactly 4 videos.");
            return;
        }

        const formData = new FormData();
        Array.from(selectedFiles).forEach((file, index) => {
            formData.append("videos", file);
        });

        setLoading(true);

        try {
            const response = await fetch("http://127.0.0.1:5000/upload", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            if (response.ok) {
                setResult(data);
            } else {
                alert(`Error: ${data.error}`);
            }
        } catch (error) {
            console.error("Error uploading videos:", error);
            alert("Failed to upload videos.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h2>Upload Traffic Videos</h2>
            <input type="file" multiple accept="video/*" onChange={handleFileChange} />
            <button onClick={handleUpload} disabled={loading}>
                {loading ? "Uploading..." : "Upload Videos"}
            </button>

            {result && (
                <div>
                    <h3>Optimization Results</h3>
                    <p>🚦 North: {result.north} seconds</p>
                    <p>🚦 South: {result.south} seconds</p>
                    <p>🚦 West: {result.west} seconds</p>
                    <p>🚦 East: {result.east} seconds</p>
                </div>
            )}
        </div>
    );
};

export default TrafficDetection;
