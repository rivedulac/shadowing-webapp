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
  return data.captions;
}
