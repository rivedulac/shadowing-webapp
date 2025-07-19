import React, { useRef, useEffect, useState } from "react";
import CaptionControls from "./CaptionControls";

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
  shadowingTime?: number; // ex: 1.5 (multiplier for pause duration)
  setShadowingTime?: (value: number) => void; // Function to update shadowing time
}

const YoutubePlayer: React.FC<YoutubePlayerProps> = ({
  youtubeUrl,
  captions,
  repeatCount,
  minDuration = 0,
  shadowingTime = 1.0,
  setShadowingTime,
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [repeatIndex, setRepeatIndex] = useState(0);
  const [filteredCaptions, setFilteredCaptions] = useState<Caption[]>([]);
  const [player, setPlayer] = useState<any>(null);
  const [isWaiting, setIsWaiting] = useState(false);
  const [playerError, setPlayerError] = useState<string>("");
  const [videoId, setVideoId] = useState<string | null>(null);

  // Extract video ID from given url
  const extractVideoId = (url: string) => {
    const match = url.match(/(?:\/|v=)([a-zA-Z0-9_-]{11})/);
    return match ? match[1] : null;
  };

  useEffect(() => {
    const filtered = captions.filter((c) => c.end - c.start >= minDuration);
    setFilteredCaptions(filtered);
  }, [captions, minDuration]);

  // Extract video ID when URL changes
  useEffect(() => {
    const id = extractVideoId(youtubeUrl);
    setVideoId(id);
    if (!id) {
      setPlayerError("Invalid YouTube URL");
    } else {
      setPlayerError("");
    }
  }, [youtubeUrl]);

  // Load YouTube API
  useEffect(() => {
    if (!videoId) return;

    // Check if YouTube API is already loaded
    if ((window as any).YT && (window as any).YT.Player) {
      createPlayer();
      return;
    }

    // Check if script is already being loaded
    if ((window as any).onYouTubeIframeAPIReady) {
      return;
    }

    const script = document.createElement("script");
    script.src = "https://www.youtube.com/iframe_api";
    script.onerror = () => setPlayerError("Failed to load YouTube API");
    document.body.appendChild(script);

    (window as any).onYouTubeIframeAPIReady = () => {
      createPlayer();
    };
  }, [videoId]);

  const createPlayer = () => {
    if (!videoId) return;

    try {
      const newPlayer = new (window as any).YT.Player("yt-player", {
        height: "360",
        width: "640",
        videoId: videoId,
        playerVars: {
          autoplay: 0,
          controls: 1,
        },
        events: {
          onReady: (event: any) => {
            console.log("YouTube player ready");
            setPlayer(event.target);
            setPlayerError("");
          },
          onError: (event: any) => {
            console.error("YouTube player error:", event.data);
            setPlayerError(`YouTube player error: ${event.data}`);
          },
          onStateChange: (event: any) => {
            console.log("YouTube player state changed:", event.data);
          },
        },
      });
    } catch (error) {
      console.error("Error creating YouTube player:", error);
      setPlayerError(`Error creating player: ${error}`);
    }
  };

  useEffect(() => {
    if (!player || filteredCaptions.length === 0) return;

    const cap = filteredCaptions[currentIndex];

    const interval = setInterval(() => {
      try {
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
          }, (cap.end - cap.start) * shadowingTime * 1000);
        }
      } catch (error) {
        console.error("Error in player control loop:", error);
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
    shadowingTime,
  ]);

  return (
    <div>
      <div id="yt-player"></div>
      {playerError && (
        <p style={{ color: "red", marginTop: "1rem" }}>❌ {playerError}</p>
      )}

      <CaptionControls
        currentCaption={filteredCaptions[currentIndex]}
        currentIndex={currentIndex}
        repeatIndex={repeatIndex}
        repeatCount={repeatCount}
        shadowingTime={shadowingTime}
        setShadowingTime={setShadowingTime}
        isEnd={currentIndex >= filteredCaptions.length}
      />
    </div>
  );
};

export default YoutubePlayer;
