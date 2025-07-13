import React, { useState } from "react";
import VideoPlayer from "./components/VideoPlayer";
import {
  uploadVideo,
  transcribeYoutube,
  extractYoutubeCaptionsWithDuration,
  smartExtractCaptions,
} from "./api";
import "./App.css";
import YoutubePlayer from "./components/YoutubePlayer";

const App = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [captions, setCaptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [repeatCount, setRepeatCount] = useState(3);
  const [minDuration, setMinDuration] = useState(2.5);
  const [youtubeLink, setYoutubeLink] = useState("");
  const [extractionMethod, setExtractionMethod] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [qualityPreference, setQualityPreference] = useState<
    "fast" | "high" | "smart"
  >("fast");

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setError("");

    try {
      // Create a URL to play a local file on the browser
      const url = URL.createObjectURL(file);
      setVideoUrl(url);

      // Upload the video to the backend side and get subtitles
      const result = await uploadVideo(file);
      setCaptions(result);
      setExtractionMethod("whisper_transcription");
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to extract text";
      setError(errorMessage);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleYoutubeSubmit = async () => {
    if (!youtubeLink) return;

    setLoading(true);
    setError("");

    try {
      if (qualityPreference === "fast") {
        // First try to extract captions only (faster)
        const result = await extractYoutubeCaptionsWithDuration(
          youtubeLink,
          minDuration
        );
        setCaptions(result.captions);
        setExtractionMethod(result.method);
        setVideoUrl(youtubeLink);
      } else if (qualityPreference === "smart") {
        // Smart extraction: tries YouTube first, falls back to Whisper if quality is poor
        const result = await smartExtractCaptions(youtubeLink, minDuration);
        setCaptions(result.captions);
        setExtractionMethod(result.method);
        setVideoUrl(youtubeLink);

        // Show quality assessment info if available
        if (result.quality_assessment) {
          console.log("Quality assessment:", result.quality_assessment);
        }
      } else {
        // Go straight to high-quality transcription
        const result = await transcribeYoutube(youtubeLink);
        setCaptions(result.captions);
        setExtractionMethod(result.method);
        setVideoUrl(youtubeLink);
      }
    } catch (err) {
      // If caption extraction fails and we're in fast mode, fall back to transcription
      if (qualityPreference === "fast") {
        console.log("Caption extraction failed, trying full transcription...");
        try {
          const result = await transcribeYoutube(youtubeLink);
          setCaptions(result.captions);
          setExtractionMethod(result.method);
          setVideoUrl(youtubeLink);
        } catch (transcriptionErr) {
          const errorMessage =
            transcriptionErr instanceof Error
              ? transcriptionErr.message
              : "Failed to extract youtube subtitles";
          setError(errorMessage);
          console.error(transcriptionErr);
        }
      } else {
        const errorMessage =
          err instanceof Error
            ? err.message
            : "Failed to extract youtube subtitles";
        setError(errorMessage);
        console.error(err);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "2rem" }}>
      <h2>🎧 Shadowing Practice</h2>

      <div style={{ marginBottom: "2rem" }}>
        <h3>Settings</h3>
        <div style={{ display: "flex", gap: "2rem", alignItems: "center" }}>
          <div>
            <label htmlFor="repeatCount">Repeat Count: </label>
            <input
              id="repeatCount"
              type="number"
              min="1"
              max="10"
              value={repeatCount}
              onChange={(e) => setRepeatCount(parseInt(e.target.value) || 1)}
              style={{ width: "60px", marginLeft: "0.5rem" }}
            />
          </div>
          <div>
            <label htmlFor="minDuration">Minimum Duration (seconds): </label>
            <input
              id="minDuration"
              type="number"
              min="0.5"
              max="10"
              step="0.5"
              value={minDuration}
              onChange={(e) =>
                setMinDuration(parseFloat(e.target.value) || 0.5)
              }
              style={{ width: "80px", marginLeft: "0.5rem" }}
            />
          </div>
          <div>
            <label htmlFor="qualityPreference">Quality: </label>
            <select
              id="qualityPreference"
              value={qualityPreference}
              onChange={(e) =>
                setQualityPreference(
                  e.target.value as "fast" | "high" | "smart"
                )
              }
              style={{ marginLeft: "0.5rem" }}
            >
              <option value="fast">
                Fast (YouTube Captions - Lower Quality)
              </option>
              <option value="smart">
                Smart (Try YouTube, Fallback to Whisper)
              </option>
              <option value="high">
                High Quality (Whisper - Best Quality)
              </option>
            </select>
          </div>
        </div>
      </div>

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
        <button onClick={handleYoutubeSubmit}>Extract Captions</button>
      </div>

      <br />
      <br />
      {loading && <p>⏳ Extracting captions...</p>}
      {error && <p style={{ color: "red" }}>❌ Error: {error}</p>}
      {extractionMethod && (
        <p style={{ color: "green", fontSize: "0.9em" }}>
          ✅ Method:{" "}
          {extractionMethod === "youtube_captions"
            ? "YouTube Captions (Fast)"
            : "Whisper Transcription (Slow)"}
        </p>
      )}
      {captions.length > 0 && (
        <p style={{ color: "blue", fontSize: "0.9em" }}>
          📝 Captions extracted: {captions.length} segments
        </p>
      )}

      {/* Debug information */}
      <div
        style={{
          marginTop: "1rem",
          padding: "1rem",
          backgroundColor: "#f0f0f0",
          fontSize: "0.8em",
        }}
      >
        <h4>Debug Info:</h4>
        <p>videoUrl: {videoUrl || "null"}</p>
        <p>captions.length: {captions.length}</p>
        <p>
          videoUrl.includes('youtu'):{" "}
          {videoUrl ? videoUrl.includes("youtu") : "N/A"}
        </p>
        <p>
          Should show player: {videoUrl && captions.length > 0 ? "YES" : "NO"}
        </p>
        <p>
          Should show YouTube player:{" "}
          {videoUrl && captions.length > 0 && videoUrl.includes("youtu")
            ? "YES"
            : "NO"}
        </p>
      </div>

      {videoUrl &&
        captions.length > 0 &&
        (videoUrl.includes("youtu") ? (
          <YoutubePlayer
            youtubeUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={minDuration}
          />
        ) : (
          <VideoPlayer
            videoUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={minDuration}
          />
        ))}
    </div>
  );
};

export default App;
