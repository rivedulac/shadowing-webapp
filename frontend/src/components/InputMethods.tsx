import React from "react";

interface InputMethodsProps {
  youtubeLink: string;
  setYoutubeLink: (value: string) => void;
  handleFileChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleYoutubeSubmit: () => void;
}

const InputMethods: React.FC<InputMethodsProps> = ({
  youtubeLink,
  setYoutubeLink,
  handleFileChange,
  handleYoutubeSubmit,
}) => {
  return (
    <div
      style={{
        display: "flex",
        gap: "2rem",
        marginBottom: "2rem",
        flexWrap: "wrap",
      }}
    >
      <div
        style={{
          background: "#f8f9fa",
          borderRadius: "12px",
          padding: "2rem",
          border: "1px solid #e9ecef",
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
          background: "#f8f9fa",
          borderRadius: "12px",
          padding: "2rem",
          border: "1px solid #e9ecef",
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
    </div>
  );
};

export default InputMethods;
