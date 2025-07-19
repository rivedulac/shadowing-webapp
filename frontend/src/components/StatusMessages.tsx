import React from "react";

interface StatusMessagesProps {
  loading: boolean;
  error: string;
  extractionMethod: string;
  captionsLength: number;
}

const StatusMessages: React.FC<StatusMessagesProps> = ({
  loading,
  error,
  extractionMethod,
  captionsLength,
}) => {
  return (
    <>
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

        {captionsLength > 0 && (
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
              📝 Captions extracted: {captionsLength} segments
            </p>
          </div>
        )}
      </div>
    </>
  );
};

export default StatusMessages;
