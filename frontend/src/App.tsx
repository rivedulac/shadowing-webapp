import React, { useState } from "react";
import VideoPlayer from "./components/VideoPlayer";
import { uploadVideo, transcribeYoutube } from "./api";
import "./App.css";
import YoutubePlayer from "./components/YoutubePlayer";

const App = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [captions, setCaptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [repeatCount, setRepeatCount] = useState(3);
  const [youtubeLink, setYoutubeLink] = useState("");

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

  const handleYoutubeSubmit = async () => {
    if (!youtubeLink) return;

    setLoading(true);
    try {
      const result = await transcribeYoutube(youtubeLink);
      setCaptions(result);
      setVideoUrl(youtubeLink);
    } catch (err) {
      alert("Failed to extract youtube subtitles");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>🎧 Shadowing Practice</h2>

      <div>
        <label>로컬 영상 파일 업로드:</label>
        <br />
        <input
          type="file"
          accept="video/mp4,video/webm"
          onChange={handleFileChange}
        />
      </div>

      <br />
      <hr />
      <br />

      <div>
        <label>YouTube 링크:</label>
        <br />
        <input
          type="text"
          placeholder="https://youtu.be/..."
          value={youtubeLink}
          onChange={(e) => setYoutubeLink(e.target.value)}
          style={{ width: "60%" }}
        />
        <button onClick={handleYoutubeSubmit}>Transcribe</button>
      </div>

      <br />
      <br />
      {loading && <p>⏳ Transcribing...</p>}

      {videoUrl &&
        captions.length > 0 &&
        (videoUrl.includes("youtu") ? (
          <YoutubePlayer
            youtubeUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={2.5}
          />
        ) : (
          <VideoPlayer
            videoUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={2.5}
          />
        ))}
    </div>
  );
};

export default App;
