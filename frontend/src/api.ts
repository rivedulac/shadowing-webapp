export async function uploadVideo(file: File) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch("http://localhost:8000/transcribe", {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Failed to upload and transcribe video");
  }

  const data = await res.json();
  return data.captions; // 배열 형태
}

export async function transcribeYoutube(url: string) {
  const res = await fetch("http://localhost:8000/transcribe-youtube", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    throw new Error("Failed to transcribe YouTube video");
  }

  const data = await res.json();
  return { captions: data.captions, method: data.method };
}

export async function extractYoutubeCaptionsOnly(url: string) {
  const res = await fetch("http://localhost:8000/extract-youtube-captions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });

  if (!res.ok) {
    throw new Error("Failed to extract YouTube captions");
  }

  const data = await res.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return { captions: data.captions, method: data.method };
}

export async function extractYoutubeCaptionsWithDuration(
  url: string,
  minDuration: number
) {
  const res = await fetch(
    "http://localhost:8000/extract-youtube-captions-with-duration",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, min_duration: minDuration }),
    }
  );

  if (!res.ok) {
    throw new Error("Failed to extract YouTube captions");
  }

  const data = await res.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return { captions: data.captions, method: data.method };
}

export async function smartExtractCaptions(url: string, minDuration: number) {
  const res = await fetch("http://localhost:8000/smart-extract-captions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url, min_duration: minDuration }),
  });

  if (!res.ok) {
    throw new Error("Failed to extract captions");
  }

  const data = await res.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return {
    captions: data.captions,
    method: data.method,
    quality_assessment: data.quality_assessment,
  };
}
