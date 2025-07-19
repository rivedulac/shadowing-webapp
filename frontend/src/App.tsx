import React, { useState } from "react";
import VideoPlayer from "./components/VideoPlayer";
import YoutubePlayer from "./components/YoutubePlayer";
import Parameters from "./components/Parameters";
import InputMethods from "./components/InputMethods";
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

      <InputMethods
        youtubeLink={youtubeLink}
        setYoutubeLink={setYoutubeLink}
        handleFileChange={handleFileChange}
        handleYoutubeSubmit={handleYoutubeSubmit}
      />

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

      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginBottom: "2rem",
          flexWrap: "wrap",
        }}
      >
        {extractionMethod && (
          <div
            style={{
              textAlign: "center",
              padding: "1rem 2rem",
              background: "#e8f5e8",
              borderRadius: "12px",
              flex: "1",
              minWidth: "250px",
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
              flex: "1",
              minWidth: "250px",
            }}
          >
            <p style={{ fontSize: "1rem", color: "#1976d2", margin: "0" }}>
              📝 Captions extracted: {captions.length} segments
            </p>
          </div>
        )}
      </div>

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
