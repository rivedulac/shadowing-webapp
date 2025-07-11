import React, { useRef, useEffect, useState } from "react";

interface Caption {
  start: number;
  end: number;
  text: string;
}

interface YoutubePlayerProps {
  youtubeUrl: string;
  captions: Caption[];
  repeatCount: number;
  minDuration?: number;
}

const YoutubePlayer: React.FC<YoutubePlayerProps> = ({
  youtubeUrl,
  captions,
  repeatCount,
  minDuration = 0,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [repeatIndex, setRepeatIndex] = useState(0);
  const [filteredCaptions, setFilteredCaptions] = useState<Caption[]>([]);
  const [player, setPlayer] = useState<any>(null);
  const [isWaiting, setIsWaiting] = useState(false);

  // Extract video ID from given url
  const extractVideoId = (url: string) => {
    const match = url.match(/(?:\/|v=)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };

  useEffect(() => {
    const filtered = captions.filter((c) => c.end - c.start >= minDuration);
    setFilteredCaptions(filtered);
  }, [captions, minDuration]);

  // Load YouTube API
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(script);

    (window as any).onYouTubeIframeAPIReady = () => {
      const newPlayer = new (window as any).YT.Player("yt-player", {
        videoId: extractVideoId(youtubeUrl),
        events: {
          onReady: () => setPlayer(newPlayer),
        },
      });
    };
  }, [youtubeUrl]);

  useEffect(() => {
    if (!player || filteredCaptions.length === 0) return;

    const cap = filteredCaptions[currentIndex];

    const interval = setInterval(() => {
      const currentTime = player.getCurrentTime();

      if (!isWaiting && currentTime > cap.end) {
        setIsWaiting(true);
        player.pauseVideo();

        setTimeout(() => {
          if (repeatIndex + 1 < repeatCount) {
            player.seekTo(cap.start);
            setRepeatIndex(repeatIndex + 1);
          } else {
            const nextIndex = currentIndex + 1;
            if (nextIndex < filteredCaptions.length) {
              setCurrentIndex(nextIndex);
              setRepeatIndex(0);
              player.seekTo(filteredCaptions[nextIndex].start);
            } else {
              player.pauseVideo();
            }
          }
          setIsWaiting(false);
          player.playVideo();
        }, (cap.end - cap.start) * 1000);
      }
    }, 300);

    return () => clearInterval(interval);
  }, [
    player,
    currentIndex,
    repeatIndex,
    filteredCaptions,
    isWaiting,
    repeatCount,
  ]);

  return (
    <div>
      <div id="yt-player"></div>
      <p style={{ marginTop: "1rem" }}>
        <strong>Now Playing:</strong>{" "}
        {filteredCaptions[currentIndex]?.text || "End"}
        <br />
        <span>
          Repeat: {repeatIndex + 1} / {repeatCount}
        </span>
      </p>
    </div>
  );
};

export default YoutubePlayer;
