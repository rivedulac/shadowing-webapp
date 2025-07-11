import React from "react";
import VideoPlayer from "./components/VideoPlayer";
import sampleCaptions from "./sampleCaptions.json"; // 예시 자막 json

const App = () => {
  return (
    <div>
      <h1>Shadowing Player</h1>
      <VideoPlayer
        videoUrl="/aegukga.mp4"
        captions={sampleCaptions}
        repeatCount={3}
        minDuration={2.5}
      />
    </div>
  );
};

export default App;
