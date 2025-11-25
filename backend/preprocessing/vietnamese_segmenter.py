"""
Vietnamese Word Segmentation Module
Performs proper word tokenization for Vietnamese text.
Critical for BM25 keyword search accuracy.
"""

from typing import List
import re


class VietnameseSegmenter:
    """
    Vietnamese word segmentation for improved BM25 retrieval.
    Uses rule-based approach with common medical terms.
    """

    def __init__(self, use_underthesea: bool = True):
        """
        Initialize segmenter.

        Args:
            use_underthesea: Whether to use underthesea library (recommended)
        """
        self.use_underthesea = use_underthesea

        # Try to import underthesea
        if use_underthesea:
            try:
                from underthesea import word_tokenize

                self.word_tokenize = word_tokenize
                print("✅ Using Underthesea for Vietnamese segmentation")
            except ImportError:
                print("⚠️  Underthesea not found. Using fallback method.")
                print("   Install with: pip install underthesea")
                self.use_underthesea = False

        # Medical term dictionary (compound words that should stay together)
        self.medical_compounds = {
            "đau_đầu",
            "cao_huyết_áp",
            "tiểu_đường",
            "tai_biến",
            "nhồi_máu",
            "ung_thư",
            "viêm_gan",
            "viêm_phổi",
            "sốt_xuất_huyết",
            "suy_thận",
            "đột_quỵ",
            "rối_loạn_lo_âu",
            "trầm_cảm",
        }

    def segment(self, text: str) -> str:
        """
        Segment Vietnamese text into words.

        Args:
            text: Raw Vietnamese text

        Returns:
            Word-segmented text (words separated by spaces)
        """
        if self.use_underthesea:
            return self._segment_with_underthesea(text)
        else:
            return self._segment_fallback(text)

    def _segment_with_underthesea(self, text: str) -> str:
        """Use Underthesea library for segmentation."""
        try:
            # Underthesea returns list of words
            words = self.word_tokenize(text, format="text")
            return words
        except Exception as e:
            print(f"⚠️  Underthesea error: {e}. Using fallback.")
            return self._segment_fallback(text)

    def _segment_fallback(self, text: str) -> str:
        """
        Simple fallback segmentation.
        Protects common medical compound words.
        """
        # Convert compound words to underscore format
        text_lower = text.lower()
        for compound in self.medical_compounds:
            # Replace "đau đầu" with "đau_đầu"
            pattern = compound.replace("_", r"\s+")
            text_lower = re.sub(pattern, compound, text_lower)

        return text_lower

    def segment_chunks(self, chunks: List[str]) -> List[str]:
        """
        Segment multiple chunks.

        Args:
            chunks: List of text chunks

        Returns:
            List of segmented chunks
        """
        return [self.segment(chunk) for chunk in chunks]


# Example usage
if __name__ == "__main__":
    segmenter = VietnameseSegmenter()

    texts = [
        "Tôi bị đau đầu và cao huyết áp",
        "Bệnh tiểu đường type 2",
        "Triệu chứng nhồi máu cơ tim",
    ]

    print("=== Vietnamese Word Segmentation ===\n")
    for text in texts:
        segmented = segmenter.segment(text)
        print(f"Original:  {text}")
        print(f"Segmented: {segmented}\n")
