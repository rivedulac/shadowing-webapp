import React, { useState, useEffect } from "react";

interface ParametersProps {
  repeatCount: number;
  setRepeatCount: (value: number) => void;
  shadowingTime: number;
  setShadowingTime: (value: number) => void;
  qualityPreference: "fast" | "high" | "smart";
  setQualityPreference: (value: "fast" | "high" | "smart") => void;
  captionsExtracted: boolean;
}

const Parameters: React.FC<ParametersProps> = ({
  repeatCount,
  setRepeatCount,
  shadowingTime,
  setShadowingTime,
  qualityPreference,
  setQualityPreference,
  captionsExtracted,
}) => {
  const [isExpanded, setIsExpanded] = useState(!captionsExtracted);

  useEffect(() => {
    setIsExpanded(!captionsExtracted);
  }, [captionsExtracted]);

  return (
    <div
      style={{
        background: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        borderRadius: "16px",
        marginBottom: "1rem",
        boxShadow: "0 10px 30px rgba(0,0,0,0.1)",
        color: "white",
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
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span>⚙️ Practice Settings</span>
        <span style={{ fontSize: "1.5rem" }}>{isExpanded ? "▼" : "▶"}</span>
      </div>

      {isExpanded && (
        <div style={{ padding: "0 2rem 2rem 2rem" }}>
          <p
            style={{
              fontSize: "1rem",
              marginBottom: "2rem",
              textAlign: "center",
              opacity: "0.9",
              lineHeight: "1.6",
            }}
          >
            💡 <strong>Shadowing Time:</strong> Controls how long the video
            pauses after each caption for you to practice speaking. <br />
            Higher values give you more time to catch up with the audio.
          </p>

          <div
            style={{
              display: "flex",
              gap: "2rem",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                flex: "1",
                minWidth: "200px",
              }}
            >
              <label
                htmlFor="repeatCount"
                style={{
                  fontSize: "1rem",
                  fontWeight: "600",
                  whiteSpace: "nowrap",
                }}
              >
                🔄 Repeat Count
              </label>
              <input
                id="repeatCount"
                type="number"
                min="1"
                max="10"
                value={repeatCount}
                onChange={(e) => setRepeatCount(parseInt(e.target.value) || 1)}
                style={{
                  width: "80px",
                  padding: "0.5rem",
                  borderRadius: "8px",
                  border: "none",
                  fontSize: "1rem",
                  background: "rgba(255,255,255,0.9)",
                  color: "#2c3e50",
                  fontWeight: "500",
                  textAlign: "center",
                }}
              />
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                flex: "1",
                minWidth: "200px",
              }}
            >
              <label
                htmlFor="shadowingTime"
                style={{
                  fontSize: "1rem",
                  fontWeight: "600",
                  whiteSpace: "nowrap",
                }}
              >
                ⏱️ Shadowing Time
              </label>
              <input
                id="shadowingTime"
                type="number"
                min="0.5"
                max="3.0"
                step="0.1"
                value={shadowingTime}
                onChange={(e) =>
                  setShadowingTime(parseFloat(e.target.value) || 1.0)
                }
                style={{
                  width: "80px",
                  padding: "0.5rem",
                  borderRadius: "8px",
                  border: "none",
                  fontSize: "1rem",
                  background: "rgba(255,255,255,0.9)",
                  color: "#2c3e50",
                  fontWeight: "500",
                  textAlign: "center",
                }}
              />
            </div>

            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                flex: "1",
                minWidth: "250px",
              }}
            >
              <label
                htmlFor="qualityPreference"
                style={{
                  fontSize: "1rem",
                  fontWeight: "600",
                  whiteSpace: "nowrap",
                }}
              >
                🎯 Quality
              </label>
              <select
                id="qualityPreference"
                value={qualityPreference}
                onChange={(e) =>
                  setQualityPreference(
                    e.target.value as "fast" | "high" | "smart"
                  )
                }
                style={{
                  flex: "1",
                  padding: "0.5rem",
                  borderRadius: "8px",
                  border: "none",
                  fontSize: "0.9rem",
                  background: "rgba(255,255,255,0.9)",
                  color: "#2c3e50",
                  fontWeight: "500",
                  cursor: "pointer",
                }}
              >
                <option value="fast">⚡ Fast</option>
                <option value="smart">🧠 Smart</option>
                <option value="high">🎯 High Quality</option>
              </select>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Parameters;
