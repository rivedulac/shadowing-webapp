import React from "react";

interface Caption {
  start: number;
  end: number;
  text: string;
}

interface CaptionControlsProps {
  currentCaption: Caption | undefined;
  currentIndex: number;
  repeatIndex: number;
  repeatCount: number;
  shadowingTime: number;
  setShadowingTime?: (value: number) => void;
  onPlay?: () => void;
  isEnd?: boolean;
}

const CaptionControls: React.FC<CaptionControlsProps> = ({
  currentCaption,
  currentIndex,
  repeatIndex,
  repeatCount,
  shadowingTime,
  setShadowingTime,
  onPlay,
  isEnd = false,
}) => {
  return (
    <div style={{ marginTop: "1rem" }}>
      {onPlay && <button onClick={onPlay}>Play</button>}
      <div style={{ marginTop: "1rem" }}>
        <strong style={{ fontSize: "1.2rem" }}>Now Playing:</strong>
        <div
          style={{
            fontSize: "1.8rem",
            fontWeight: "600",
            color: "#2c3e50",
            marginTop: "0.5rem",
            padding: "1rem",
            background: "#f8f9fa",
            borderRadius: "8px",
            border: "2px solid #e9ecef",
          }}
        >
          {currentCaption?.text || (isEnd ? "End" : "Loading...")}
        </div>
      </div>
      <div style={{ marginTop: "1rem", fontSize: "1.5rem" }}>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <span>
            Repeat: {repeatIndex + 1} / {repeatCount}
          </span>
          <span>|</span>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            <span>Shadowing Time:</span>
            {setShadowingTime ? (
              <input
                type="number"
                min="0.5"
                max="3.0"
                step="0.1"
                value={shadowingTime}
                onChange={(e) =>
                  setShadowingTime(parseFloat(e.target.value) || 1.0)
                }
                style={{
                  width: "60px",
                  padding: "0.25rem",
                  borderRadius: "4px",
                  border: "1px solid #ccc",
                  fontSize: "0.9rem",
                  textAlign: "center",
                }}
              />
            ) : (
              <span>{shadowingTime}x</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CaptionControls;
