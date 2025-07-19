import React, { useState } from "react";
import VideoPlayer from "./components/VideoPlayer";
import YoutubePlayer from "./components/YoutubePlayer";
import Parameters from "./components/Parameters";
import {
  uploadVideo,
  transcribeYoutube,
  extractYoutubeCaptionsWithDuration,
  smartExtractCaptions,
} from "./api";
import "./App.css";

const App = () => {
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [captions, setCaptions] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [repeatCount, setRepeatCount] = useState(3);
  const [minDuration, setMinDuration] = useState(2.5);
  const [shadowingTime, setShadowingTime] = useState(1.0);
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
    <div style={{ padding: "2rem", maxWidth: "1200px", margin: "0 auto" }}>
      <h2
        style={{
          fontSize: "2.5rem",
          fontWeight: "700",
          color: "#2c3e50",
          marginBottom: "2rem",
          textAlign: "center",
        }}
      >
        🎧 Shadowing Practice
      </h2>

      <Parameters
        repeatCount={repeatCount}
        setRepeatCount={setRepeatCount}
        shadowingTime={shadowingTime}
        setShadowingTime={setShadowingTime}
        qualityPreference={qualityPreference}
        setQualityPreference={setQualityPreference}
      />

      <div
        style={{
          background: "#f8f9fa",
          borderRadius: "12px",
          padding: "2rem",
          marginBottom: "2rem",
          border: "1px solid #e9ecef",
        }}
      >
        <h3
          style={{
            fontSize: "1.3rem",
            fontWeight: "600",
            marginBottom: "1rem",
            color: "#495057",
          }}
        >
          📁 Upload Local Video
        </h3>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
          }}
        >
          <input
            type="file"
            accept="video/mp4,video/webm"
            onChange={handleFileChange}
            style={{
              flex: "1",
              padding: "0.75rem",
              borderRadius: "8px",
              border: "2px dashed #dee2e6",
              background: "white",
              cursor: "pointer",
            }}
          />
        </div>
      </div>

      <div
        style={{
          background: "#f8f9fa",
          borderRadius: "12px",
          padding: "2rem",
          marginBottom: "2rem",
          border: "1px solid #e9ecef",
        }}
      >
        <h3
          style={{
            fontSize: "1.3rem",
            fontWeight: "600",
            marginBottom: "1rem",
            color: "#495057",
          }}
        >
          📺 YouTube Video
        </h3>
        <div
          style={{
            display: "flex",
            gap: "1rem",
            alignItems: "center",
          }}
        >
          <input
            type="text"
            placeholder="https://youtu.be/..."
            value={youtubeLink}
            onChange={(e) => setYoutubeLink(e.target.value)}
            style={{
              flex: "1",
              padding: "0.75rem",
              borderRadius: "8px",
              border: "1px solid #dee2e6",
              fontSize: "1rem",
            }}
          />
          <button
            onClick={handleYoutubeSubmit}
            style={{
              padding: "0.75rem 1.5rem",
              borderRadius: "8px",
              border: "none",
              background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
              color: "white",
              fontSize: "1rem",
              fontWeight: "600",
              cursor: "pointer",
              transition: "transform 0.2s ease",
            }}
            onMouseOver={(e) =>
              (e.currentTarget.style.transform = "translateY(-2px)")
            }
            onMouseOut={(e) =>
              (e.currentTarget.style.transform = "translateY(0)")
            }
          >
            Extract Captions
          </button>
        </div>
      </div>

      {loading && (
        <div
          style={{
            textAlign: "center",
            padding: "2rem",
            background: "#e3f2fd",
            borderRadius: "12px",
            marginBottom: "2rem",
          }}
        >
          <p style={{ fontSize: "1.1rem", color: "#1976d2", margin: "0" }}>
            ⏳ Extracting captions...
          </p>
        </div>
      )}

      {error && (
        <div
          style={{
            textAlign: "center",
            padding: "2rem",
            background: "#ffebee",
            borderRadius: "12px",
            marginBottom: "2rem",
          }}
        >
          <p style={{ fontSize: "1.1rem", color: "#d32f2f", margin: "0" }}>
            ❌ Error: {error}
          </p>
        </div>
      )}

      {extractionMethod && (
        <div
          style={{
            textAlign: "center",
            padding: "1rem 2rem",
            background: "#e8f5e8",
            borderRadius: "12px",
            marginBottom: "2rem",
          }}
        >
          <p style={{ fontSize: "1rem", color: "#2e7d32", margin: "0" }}>
            ✅ Method:{" "}
            {extractionMethod === "youtube_captions"
              ? "YouTube Captions (Fast)"
              : "Whisper Transcription (Slow)"}
          </p>
        </div>
      )}

      {captions.length > 0 && (
        <div
          style={{
            textAlign: "center",
            padding: "1rem 2rem",
            background: "#e3f2fd",
            borderRadius: "12px",
            marginBottom: "2rem",
          }}
        >
          <p style={{ fontSize: "1rem", color: "#1976d2", margin: "0" }}>
            📝 Captions extracted: {captions.length} segments
          </p>
        </div>
      )}

      {videoUrl &&
        captions.length > 0 &&
        (videoUrl.includes("youtu") ? (
          <YoutubePlayer
            youtubeUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={minDuration}
            shadowingTime={shadowingTime}
          />
        ) : (
          <VideoPlayer
            videoUrl={videoUrl}
            captions={captions}
            repeatCount={repeatCount}
            minDuration={minDuration}
            shadowingTime={shadowingTime}
          />
        ))}
    </div>
  );
};

export default App;
