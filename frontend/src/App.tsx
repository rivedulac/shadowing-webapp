import React, { useState } from "react";
import VideoPlayer from "./components/VideoPlayer";
import { uploadVideo } from "./api";
import "./App.css";

const App = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [captions, setCaptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [repeatCount, setRepeatCount] = useState(3);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);

    try {
      // Create a URL to play a local file on the browser
      const url = URL.createObjectURL(file);
      setVideoUrl(url);

      // Upload the video to the backend side and get subtitles
      const result = await uploadVideo(file);
      setCaptions(result);
    } catch (err) {
      alert("Failed to extract text");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>🎧 Shadowing Practice</h2>
      <input
        type="file"
        accept="video/mp4,video/webm"
        onChange={handleFileChange}
      />
      <br />
      <br />
      {loading && <p>⏳ Transcribing...</p>}

      {videoUrl && captions.length > 0 && (
        <VideoPlayer
          videoUrl={videoUrl}
          captions={captions}
          repeatCount={repeatCount}
          minDuration={2.5}
        />
      )}
    </div>
  );
};

export default App;
