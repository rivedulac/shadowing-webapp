import React, { useState } from "react";

interface StatusMessagesProps {
  loading: boolean;
  error: string;
  extractionMethod: string;
  captionsLength: number;
  videoId: string | null;
}

const StatusMessages: React.FC<StatusMessagesProps> = ({
  loading,
  error,
  extractionMethod,
  captionsLength,
  videoId,
}) => {
  const [isExpanded, setIsExpanded] = useState(true);
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

      {(extractionMethod || captionsLength > 0 || videoId) && (
        <div
          style={{
            background: "#f8f9fa",
            borderRadius: "12px",
            border: "1px solid #e9ecef",
            marginBottom: "2rem",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "1rem 1.5rem",
              background: "#e9ecef",
              cursor: "pointer",
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              fontWeight: "600",
            }}
            onClick={() => setIsExpanded(!isExpanded)}
          >
            <span>📊 Video Information</span>
            <span style={{ fontSize: "1.2rem" }}>{isExpanded ? "▼" : "▶"}</span>
          </div>

          {isExpanded && (
            <div style={{ padding: "1.5rem" }}>
              <div
                style={{
                  display: "flex",
                  flexDirection: "column",
                  gap: "1rem",
                }}
              >
                {videoId && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <span style={{ color: "#6f42c1", fontWeight: "600" }}>
                      📺 Video ID:
                    </span>
                    <span>{videoId}</span>
                  </div>
                )}
                {extractionMethod && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <span style={{ color: "#2e7d32", fontWeight: "600" }}>
                      ✅ Method:
                    </span>
                    <span>
                      {extractionMethod === "youtube_captions"
                        ? "YouTube Captions (Fast)"
                        : "Whisper Transcription (Slow)"}
                    </span>
                  </div>
                )}

                {captionsLength > 0 && (
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.5rem",
                    }}
                  >
                    <span style={{ color: "#1976d2", fontWeight: "600" }}>
                      📝 Captions:
                    </span>
                    <span>{captionsLength} segments extracted</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </>
  );
};

export default StatusMessages;
