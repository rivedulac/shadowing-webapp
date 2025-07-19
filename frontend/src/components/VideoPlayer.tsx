import React, { useRef, useState, useEffect } from "react";

interface Caption {
  start: number; // in seconds
  end: number;
  text: string;
}

interface VideoPlayerProps {
  videoUrl: string;
  captions: Caption[];
  repeatCount: number; // ex: 3
  minDuration?: number; // ex: 2.5 (filter short utterances)
  shadowingTime?: number; // ex: 1.5 (multiplier for pause duration)
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({
  videoUrl,
  captions,
  repeatCount,
  minDuration = 0,
  shadowingTime = 1.0,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [repeatIndex, setRepeatIndex] = useState<number>(0);
  const [filteredCaptions, setFilteredCaptions] = useState<Caption[]>([]);
  const [isWaiting, setIsWaiting] = useState(false);

  const handlePlay = () => {
    videoRef.current?.play();
  };

  useEffect(() => {
    const filtered = captions.filter(
      (cap) => cap.end - cap.start >= minDuration
    );
    setFilteredCaptions(filtered);
  }, [captions, minDuration]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || filteredCaptions.length === 0) return;

    const handleTimeUpdate = () => {
      if (!video || isWaiting) return;

      const cap = filteredCaptions[currentIndex];

      if (video.currentTime > cap.end) {
        setIsWaiting(true);
        video.pause();

        setTimeout(() => {
          if (repeatIndex + 1 < repeatCount) {
            video.currentTime = cap.start;
            setRepeatIndex(repeatIndex + 1);
          } else {
            const nextIndex = currentIndex + 1;
            if (nextIndex < filteredCaptions.length) {
              setCurrentIndex(nextIndex);
              setRepeatIndex(0);
              video.currentTime = filteredCaptions[nextIndex].start;
            } else {
              video.pause();
            }
          }
          setIsWaiting(false);
          video.play();
        }, (cap.end - cap.start) * shadowingTime * 1000); // 쉐도잉용 pause 시간 = 문장 길이 * shadowingTime
      }
    };

    video.addEventListener("timeupdate", handleTimeUpdate);
    video.currentTime = filteredCaptions[currentIndex].start;

    return () => {
      video.removeEventListener("timeupdate", handleTimeUpdate);
    };
  }, [currentIndex, repeatIndex, filteredCaptions, repeatCount, shadowingTime]);

  return (
    <div>
      <video
        ref={videoRef}
        src={videoUrl}
        controls
        width="640"
        autoPlay
        muted
      />
      <div style={{ marginTop: "1rem" }}>
        <button onClick={handlePlay}>Play</button>
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
            {filteredCaptions[currentIndex]?.text || "End"}
          </div>
        </div>
        <div style={{ marginTop: "1rem", fontSize: "1rem" }}>
          <span>
            Repeat: {repeatIndex + 1} / {repeatCount} | Shadowing Time:{" "}
            {shadowingTime}x
          </span>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer;
