import React, { useState, useEffect } from "react";

interface InputMethodsProps {
  youtubeLink: string;
  setYoutubeLink: (value: string) => void;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleYoutubeSubmit: () => void;
  captionsExtracted: boolean;
}

const InputMethods: React.FC<InputMethodsProps> = ({
  youtubeLink,
  setYoutubeLink,
  handleFileChange,
  handleYoutubeSubmit,
  captionsExtracted,
}) => {
  const [isExpanded, setIsExpanded] = useState(!captionsExtracted);

  useEffect(() => {
    setIsExpanded(!captionsExtracted);
  }, [captionsExtracted]);

  return (
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
          padding: "1rem 2rem",
          cursor: "pointer",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          fontWeight: "600",
          fontSize: "1.2rem",
          background: "#e9ecef",
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>📥 Input Methods</span>
        <span style={{ fontSize: "1.5rem" }}>{isExpanded ? "▼" : "▶"}</span>
      </div>

      {isExpanded && (
        <div style={{ padding: "2rem" }}>
          <div
            style={{
              display: "flex",
              gap: "2rem",
              flexWrap: "wrap",
            }}
          >
            <div
              style={{
                flex: "1",
                minWidth: "300px",
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
                flex: "1",
                minWidth: "300px",
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
                    background:
                      "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
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
          </div>
        </div>
      )}
    </div>
  );
};

export default InputMethods;
