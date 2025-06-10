import axios from "axios";
import React, { useState } from "react";
import "./styles.css";

function App() {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    if (selectedFiles.length !== 4) {
      alert("Please upload exactly 4 videos.");
      setLoading(false);
      return;
    }

    const formData = new FormData();
    selectedFiles.forEach((file) => formData.append("videos", file)); // Matching Flask key

    try {
      const response = await axios.post("http://localhost:5000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      if (response.data.error) {
        alert(`Error: ${response.data.error}`);
        setLoading(false);
        return;
      }

      setResult(response.data);
    } catch (error) {
      console.error("Error uploading files:", error);
      alert("Failed to process videos. Try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>🚗 AI Based Traffic Management</h1>
      <hr />

      <div className="main-container">
        <section id="upload" className="upload">
          <h2>📹 Upload Your Traffic Videos</h2>
          <p>Select 4 videos showing different roads at an intersection.</p>
          <form onSubmit={handleSubmit}>
            <input type="file" multiple accept="video/*" onChange={handleFileChange} />
            <br />
            <button type="submit" disabled={loading}>{loading ? "Processing..." : "Run Model"}</button>
          </form>
        </section>

        <section id="result" className="result">
          {loading && <p className="loader">Processing videos, it may take a few minutes...</p>}
          {result && !result.error && (
            <>
              <h2>✅ Optimization Results</h2>
              <ul>
                <li>🚦 North: <span>{result.north}</span> seconds</li>
                <li>🚦 South: <span>{result.south}</span> seconds</li>
                <li>🚦 West: <span>{result.west}</span> seconds</li>
                <li>🚦 East: <span>{result.east}</span> seconds</li>
              </ul>

              <h2>📹 Uploaded Videos</h2>
              {result.videos &&
                result.videos.map((videoPath, index) => (
                  <video key={index} width="300" controls>
                    <source src={`http://localhost:5000/${videoPath}`} type="video/mp4" />
                    Your browser does not support the video tag.
                  </video>
                ))}
            </>
          )}
          {result && result.error && (
            <div>
              <h2>Error:</h2>
              <p>{result.error}</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;
