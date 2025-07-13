def assess_caption_quality(captions: list) -> dict:
    """Assess the quality of YouTube captions to determine if they're suitable for shadowing"""
    if not captions:
        return {"quality_score": 0, "issues": ["No captions found"], "recommend_whisper": True}

    issues = []
    quality_score = 100

    # Check for overlapping text (same text in consecutive segments)
    overlapping_count = 0
    for i in range(1, len(captions)):
        prev_text = captions[i-1]["text"].lower().strip()
        curr_text = captions[i]["text"].lower().strip()

        # Check if current text starts with previous text (overlap)
        if curr_text.startswith(prev_text) and len(prev_text) > 10:
            overlapping_count += 1
            issues.append(f"Overlapping text detected: '{prev_text[:30]}...'")

    if overlapping_count > 0:
        quality_score -= overlapping_count * 20
        issues.append(f"Found {overlapping_count} overlapping segments")

    # Check for very short segments (likely poor segmentation)
    short_segments = 0
    for caption in captions:
        duration = caption["end"] - caption["start"]
        if duration < 1.0:
            short_segments += 1

    if short_segments > len(captions) * 0.3:  # More than 30% are very short
        quality_score -= 30
        issues.append(f"Too many short segments: {short_segments}/{len(captions)}")

    # Check for missing punctuation (indicates poor transcription)
    no_punctuation_count = 0
    for caption in captions:
        text = caption["text"].strip()
        if text and not any(p in text for p in '.!?'):
            no_punctuation_count += 1

    if no_punctuation_count > len(captions) * 0.5:  # More than 50% lack punctuation
        quality_score -= 25
        issues.append(f"Many segments lack punctuation: {no_punctuation_count}/{len(captions)}")

    # Check for repetitive text
    unique_texts = set()
    for caption in captions:
        text = caption["text"].lower().strip()
        if len(text) > 5:  # Only count meaningful text
            unique_texts.add(text)

    if len(unique_texts) < len(captions) * 0.7:  # Less than 70% unique content
        quality_score -= 20
        issues.append(f"Too much repetitive text: {len(unique_texts)} unique out of {len(captions)} segments")

    # Determine if we should recommend Whisper
    recommend_whisper = quality_score < 50 or len(issues) > 2

    return {
        "quality_score": max(0, quality_score),
        "issues": issues,
        "recommend_whisper": recommend_whisper,
        "segment_count": len(captions),
        "overlapping_count": overlapping_count,
        "short_segments": short_segments,
        "no_punctuation_count": no_punctuation_count
    }
