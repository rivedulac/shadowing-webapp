import unittest
from src.assess_quality import (
    count_overlapping_text,
    count_short_segments,
    count_no_punctuation,
    count_unique_texts,
    assess_caption_quality
)


class TestCountOverlappingText(unittest.TestCase):
    """Test cases for count_overlapping_text function"""

    def test_no_overlapping_text(self):
        """Test with no overlapping text"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "How are you", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = count_overlapping_text(captions)
        self.assertEqual(result, 0)

    def test_with_overlapping_text(self):
        """Test with overlapping text"""
        captions = [
            {"text": "Hello world this is a test", "start": 0, "end": 2},
            {"text": "Hello world this is a test and more", "start": 2, "end": 4},
            {"text": "Something different", "start": 4, "end": 6}
        ]
        result = count_overlapping_text(captions)
        self.assertEqual(result, 1)

    def test_multiple_overlapping_texts(self):
        """Test with multiple overlapping texts"""
        captions = [
            {"text": "Hello world this is a test", "start": 0, "end": 2},
            {"text": "Hello world this is a test and more", "start": 2, "end": 4},
            {"text": "Hello world this is a test and more content", "start": 4, "end": 6}
        ]
        result = count_overlapping_text(captions)
        self.assertEqual(result, 2)

    def test_short_overlapping_text_ignored(self):
        """Test that short overlapping text (<=10 chars) is ignored"""
        captions = [
            {"text": "Hi", "start": 0, "end": 2},
            {"text": "Hi there", "start": 2, "end": 4}
        ]
        result = count_overlapping_text(captions)
        self.assertEqual(result, 0)

    def test_empty_captions(self):
        """Test with empty captions list"""
        captions = []
        result = count_overlapping_text(captions)
        self.assertEqual(result, 0)

    def test_single_caption(self):
        """Test with single caption"""
        captions = [{"text": "Hello world", "start": 0, "end": 2}]
        result = count_overlapping_text(captions)
        self.assertEqual(result, 0)


class TestCountShortSegments(unittest.TestCase):
    """Test cases for count_short_segments function"""

    def test_no_short_segments(self):
        """Test with no short segments"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2.5},
            {"text": "How are you", "start": 2.5, "end": 5.0},
            {"text": "I am fine", "start": 5.0, "end": 7.5}
        ]
        result = count_short_segments(captions)
        self.assertEqual(result, 0)

    def test_with_short_segments(self):
        """Test with short segments"""
        captions = [
            {"text": "Hello", "start": 0, "end": 0.5},
            {"text": "How are you", "start": 0.5, "end": 3.0},
            {"text": "I am", "start": 3.0, "end": 3.8}
        ]
        result = count_short_segments(captions)
        self.assertEqual(result, 2)

    def test_all_short_segments(self):
        """Test with all short segments"""
        captions = [
            {"text": "Hi", "start": 0, "end": 0.5},
            {"text": "Hello", "start": 0.5, "end": 0.8},
            {"text": "Hey", "start": 0.8, "end": 0.9}
        ]
        result = count_short_segments(captions)
        self.assertEqual(result, 3)

    def test_exactly_one_second_segments(self):
        """Test with segments exactly 1 second long (should not be counted as short)"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 1.0},
            {"text": "How are you", "start": 1.0, "end": 2.0}
        ]
        result = count_short_segments(captions)
        self.assertEqual(result, 0)

    def test_empty_captions(self):
        """Test with empty captions list"""
        captions = []
        result = count_short_segments(captions)
        self.assertEqual(result, 0)


class TestCountNoPunctuation(unittest.TestCase):
    """Test cases for count_no_punctuation function"""

    def test_all_with_punctuation(self):
        """Test with all segments having punctuation"""
        captions = [
            {"text": "Hello world.", "start": 0, "end": 2},
            {"text": "How are you?", "start": 2, "end": 4},
            {"text": "I am fine!", "start": 4, "end": 6}
        ]
        result = count_no_punctuation(captions)
        self.assertEqual(result, 0)

    def test_some_without_punctuation(self):
        """Test with some segments without punctuation"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "How are you?", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = count_no_punctuation(captions)
        self.assertEqual(result, 2)

    def test_all_without_punctuation(self):
        """Test with all segments without punctuation"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "How are you", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = count_no_punctuation(captions)
        self.assertEqual(result, 3)

    def test_empty_text_segments(self):
        """Test with empty text segments"""
        captions = [
            {"text": "", "start": 0, "end": 2},
            {"text": "Hello world", "start": 2, "end": 4},
            {"text": "   ", "start": 4, "end": 6}
        ]
        result = count_no_punctuation(captions)
        self.assertEqual(result, 1)  # Only "Hello world" has text but no punctuation

    def test_mixed_punctuation_types(self):
        """Test with different types of punctuation"""
        captions = [
            {"text": "Hello world.", "start": 0, "end": 2},
            {"text": "How are you?", "start": 2, "end": 4},
            {"text": "I am fine!", "start": 4, "end": 6},
            {"text": "That's great", "start": 6, "end": 8}
        ]
        result = count_no_punctuation(captions)
        self.assertEqual(result, 1)

    def test_empty_captions(self):
        """Test with empty captions list"""
        captions = []
        result = count_no_punctuation(captions)
        self.assertEqual(result, 0)


class TestCountUniqueTexts(unittest.TestCase):
    """Test cases for count_unique_texts function"""

    def test_all_unique_texts(self):
        """Test with all unique texts"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "How are you", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 3)

    def test_some_duplicate_texts(self):
        """Test with some duplicate texts"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "Hello world", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 2)

    def test_case_insensitive_duplicates(self):
        """Test that duplicates are case-insensitive"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "HELLO WORLD", "start": 2, "end": 4},
            {"text": "hello world", "start": 4, "end": 6}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 1)

    def test_short_texts_ignored(self):
        """Test that short texts (<=5 chars) are ignored"""
        captions = [
            {"text": "Hi", "start": 0, "end": 2},
            {"text": "Hello world", "start": 2, "end": 4},
            {"text": "Hey", "start": 4, "end": 6}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 1)

    def test_exactly_five_char_texts(self):
        """Test with texts exactly 5 characters long"""
        captions = [
            {"text": "Hello", "start": 0, "end": 2},
            {"text": "World", "start": 2, "end": 4}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 0)  # 5 chars is not > 5

    def test_empty_and_whitespace_texts(self):
        """Test with empty and whitespace texts"""
        captions = [
            {"text": "", "start": 0, "end": 2},
            {"text": "   ", "start": 2, "end": 4},
            {"text": "Hello world", "start": 4, "end": 6}
        ]
        result = count_unique_texts(captions)
        self.assertEqual(result, 1)

    def test_empty_captions(self):
        """Test with empty captions list"""
        captions = []
        result = count_unique_texts(captions)
        self.assertEqual(result, 0)


class TestAssessCaptionQuality(unittest.TestCase):
    """Test cases for assess_caption_quality function"""

    def test_empty_captions(self):
        """Test with empty captions list"""
        captions = []
        result = assess_caption_quality(captions)
        expected = {
            "quality_score": 0,
            "issues": ["No captions found"],
            "recommend_whisper": True,
        }
        self.assertEqual(result, expected)

    def test_high_quality_captions(self):
        """Test with high quality captions"""
        captions = [
            {"text": "Hello world. How are you today?", "start": 0, "end": 3},
            {"text": "I am doing great, thank you!", "start": 3, "end": 6},
            {"text": "That's wonderful to hear.", "start": 6, "end": 9}
        ]
        result = assess_caption_quality(captions)
        
        self.assertEqual(result["quality_score"], 100)
        self.assertEqual(result["issues"], [])
        self.assertFalse(result["recommend_whisper"])
        self.assertEqual(result["segment_count"], 3)
        self.assertEqual(result["overlapping_count"], 0)
        self.assertEqual(result["short_segments"], 0)
        self.assertEqual(result["no_punctuation_count"], 0)

    def test_overlapping_text_penalty(self):
        """Test quality assessment with overlapping text"""
        captions = [
            {"text": "Hello world this is a test", "start": 0, "end": 2},
            {"text": "Hello world this is a test and more", "start": 2, "end": 4},
            {"text": "Something different", "start": 4, "end": 6}
        ]
        result = assess_caption_quality(captions)
        
        self.assertEqual(result["quality_score"], 55)  # 100 - 20 (overlap) - 25 (no punctuation)
        self.assertIn("Found 1 overlapping segments", result["issues"])
        self.assertIn("Many segments lack punctuation: 3/3", result["issues"])
        self.assertFalse(result["recommend_whisper"])
        self.assertEqual(result["overlapping_count"], 1)

    def test_short_segments_penalty(self):
        """Test quality assessment with too many short segments"""
        captions = [
            {"text": "Hi", "start": 0, "end": 0.5},
            {"text": "Hello", "start": 0.5, "end": 0.8},
            {"text": "Hey", "start": 0.8, "end": 0.9},
            {"text": "How are you?", "start": 1.0, "end": 3.0}
        ]
        result = assess_caption_quality(captions)
        
        self.assertEqual(result["quality_score"], 25)  # 100 - 30 (short segments) - 25 (no punctuation) - 20 (repetitive)
        self.assertIn("Too many short segments: 3/4", result["issues"])
        self.assertTrue(result["recommend_whisper"])  # Score < 50
        self.assertEqual(result["short_segments"], 3)

    def test_no_punctuation_penalty(self):
        """Test quality assessment with missing punctuation"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "How are you", "start": 2, "end": 4},
            {"text": "I am fine", "start": 4, "end": 6}
        ]
        result = assess_caption_quality(captions)
        
        self.assertEqual(result["quality_score"], 75)  # 100 - 25
        self.assertIn("Many segments lack punctuation: 3/3", result["issues"])
        self.assertFalse(result["recommend_whisper"])
        self.assertEqual(result["no_punctuation_count"], 3)

    def test_repetitive_text_penalty(self):
        """Test quality assessment with repetitive text"""
        captions = [
            {"text": "Hello world", "start": 0, "end": 2},
            {"text": "Hello world", "start": 2, "end": 4},
            {"text": "Hello world", "start": 4, "end": 6},
            {"text": "Something different", "start": 6, "end": 8}
        ]
        result = assess_caption_quality(captions)
        
        self.assertEqual(result["quality_score"], 15)  # 100 - 40 (overlap) - 25 (no punctuation) - 20 (repetitive)
        self.assertIn("Too much repetitive text: 2 unique out of 4 segments", result["issues"])
        self.assertTrue(result["recommend_whisper"])  # Score < 50
        self.assertEqual(result["unique_texts"], 2)

    def test_multiple_issues_recommend_whisper(self):
        """Test that multiple issues trigger Whisper recommendation"""
        captions = [
            {"text": "Hi", "start": 0, "end": 0.5},
            {"text": "Hi there", "start": 0.5, "end": 0.8},
            {"text": "Hello world", "start": 0.8, "end": 1.0},
            {"text": "Hello world and more", "start": 1.0, "end": 2.0}
        ]
        result = assess_caption_quality(captions)
        
        # Should have multiple issues: short segments, overlapping text
        self.assertLess(result["quality_score"], 50)
        self.assertTrue(result["recommend_whisper"])
        self.assertGreater(len(result["issues"]), 2)

    def test_low_quality_score_recommend_whisper(self):
        """Test that low quality score triggers Whisper recommendation"""
        captions = [
            {"text": "Hi", "start": 0, "end": 0.5},
            {"text": "Hello", "start": 0.5, "end": 0.8},
            {"text": "Hey", "start": 0.8, "end": 0.9},
            {"text": "Hi there", "start": 1.0, "end": 1.2},
            {"text": "Hello world", "start": 1.2, "end": 1.5},
            {"text": "Hello world and more", "start": 1.5, "end": 2.0}
        ]
        result = assess_caption_quality(captions)
        
        # Multiple overlapping texts should reduce score significantly
        self.assertLess(result["quality_score"], 50)
        self.assertTrue(result["recommend_whisper"])

    def test_quality_score_never_negative(self):
        """Test that quality score never goes below 0"""
        captions = [
            {"text": "Hi", "start": 0, "end": 0.5},
            {"text": "Hi there", "start": 0.5, "end": 0.8},
            {"text": "Hi there and more", "start": 0.8, "end": 0.9},
            {"text": "Hi there and more content", "start": 0.9, "end": 1.0}
        ]
        result = assess_caption_quality(captions)
        
        self.assertGreaterEqual(result["quality_score"], 0)


if __name__ == '__main__':
    unittest.main()
