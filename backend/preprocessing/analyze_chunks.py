"""
Chunk Quality Analyzer
Analyzes the quality of text chunking and provides optimization recommendations.

Features:
1. Chunk size distribution analysis
2. Sentence boundary violation detection
3. Context loss detection
4. Optimization recommendations

Usage:
    python backend/preprocessing/analyze_chunks.py --corpus backend/database/text_corpus
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple
import statistics

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from .advanced_corpus_loader import load_corpus_advanced
except ImportError:
    from advanced_corpus_loader import load_corpus_advanced


class ChunkQualityAnalyzer:
    """Analyzes chunking quality and provides recommendations."""

    def __init__(self):
        self.metrics = {
            "total_chunks": 0,
            "size_distribution": [],
            "boundary_violations": 0,
            "incomplete_sentences": [],
            "orphan_chunks": 0,
            "header_coverage": 0,
        }

    def analyze_corpus(
        self, corpus_path: str, max_chunk_size: int = 800, inject_headers: bool = True
    ) -> Dict:
        """
        Analyze chunking quality of corpus.

        Args:
            corpus_path: Path to corpus
            max_chunk_size: Maximum chunk size used
            inject_headers: Whether headers were injected

        Returns:
            Analysis results
        """
        print("=" * 80)
        print("📊 CHUNK QUALITY ANALYSIS")
        print("=" * 80)

        # Load corpus
        print(f"\n1️⃣ Loading corpus from: {corpus_path}")
        _, chunks = load_corpus_advanced(
            corpus_path=corpus_path,
            max_chunk_size=max_chunk_size,
            inject_headers=inject_headers,
            use_vietnamese_segmentation=False,  # Analyze raw chunks
        )

        self.metrics["total_chunks"] = len(chunks)
        print(f"   Total chunks: {len(chunks)}")

        # Analyze each chunk
        print(f"\n2️⃣ Analyzing chunk quality...")
        for chunk in chunks:
            self._analyze_chunk(chunk)

        # Calculate statistics
        print(f"\n3️⃣ Calculating statistics...")
        results = self._calculate_statistics(max_chunk_size)

        # Print report
        self._print_report(results, max_chunk_size)

        return results

    def _analyze_chunk(self, chunk):
        """Analyze a single chunk."""
        text = chunk.metadata.get("original_text", chunk.page_content)

        # 1. Size distribution
        self.metrics["size_distribution"].append(len(text))

        # 2. Check for sentence boundary violations
        if self._has_boundary_violation(text):
            self.metrics["boundary_violations"] += 1
            self.metrics["incomplete_sentences"].append(
                {"text": text[:100] + "...", "size": len(text)}
            )

        # 3. Check for orphan chunks (too small)
        if len(text) < 100:
            self.metrics["orphan_chunks"] += 1

        # 4. Check header coverage
        if chunk.metadata.get("header_path"):
            self.metrics["header_coverage"] += 1

    def _has_boundary_violation(self, text: str) -> bool:
        """
        Check if chunk ends with incomplete sentence.

        Returns:
            True if chunk likely ends mid-sentence
        """
        # Check last 50 characters
        ending = text[-50:].strip()

        # Good endings (sentence boundaries)
        good_endings = [".", "!", "?", "。", "\n"]

        # Check if ends with sentence boundary
        for ending_char in good_endings:
            if ending.endswith(ending_char):
                return False

        # Check if ends mid-word (no space before last char)
        if len(ending) > 0 and not ending[-1].isspace():
            # Likely cut mid-sentence
            return True

        return False

    def _calculate_statistics(self, max_chunk_size: int) -> Dict:
        """Calculate statistical metrics."""
        sizes = self.metrics["size_distribution"]

        results = {
            "total_chunks": self.metrics["total_chunks"],
            "size_stats": {
                "mean": statistics.mean(sizes),
                "median": statistics.median(sizes),
                "stdev": statistics.stdev(sizes) if len(sizes) > 1 else 0,
                "min": min(sizes),
                "max": max(sizes),
            },
            "quality_metrics": {
                "boundary_violation_rate": self.metrics["boundary_violations"]
                / self.metrics["total_chunks"]
                * 100,
                "orphan_chunk_rate": self.metrics["orphan_chunks"]
                / self.metrics["total_chunks"]
                * 100,
                "header_coverage_rate": self.metrics["header_coverage"]
                / self.metrics["total_chunks"]
                * 100,
            },
            "size_distribution": self._get_size_distribution(sizes, max_chunk_size),
            "incomplete_samples": self.metrics["incomplete_sentences"][
                :5
            ],  # Top 5 examples
        }

        return results

    def _get_size_distribution(self, sizes: List[int], max_size: int) -> Dict:
        """Get size distribution by buckets."""
        buckets = {
            "very_small": 0,  # < 200
            "small": 0,  # 200-400
            "medium": 0,  # 400-600
            "large": 0,  # 600-800
            "very_large": 0,  # > 800
        }

        for size in sizes:
            if size < 200:
                buckets["very_small"] += 1
            elif size < 400:
                buckets["small"] += 1
            elif size < 600:
                buckets["medium"] += 1
            elif size < 800:
                buckets["large"] += 1
            else:
                buckets["very_large"] += 1

        # Convert to percentages
        total = len(sizes)
        return {k: (v / total * 100) for k, v in buckets.items()}

    def _print_report(self, results: Dict, max_chunk_size: int):
        """Print analysis report."""
        print("\n" + "=" * 80)
        print("📈 ANALYSIS RESULTS")
        print("=" * 80)

        # Size statistics
        print(f"\n📏 SIZE STATISTICS:")
        print(f"   Total chunks: {results['total_chunks']}")
        print(f"   Average size: {results['size_stats']['mean']:.0f} chars")
        print(f"   Median size: {results['size_stats']['median']:.0f} chars")
        print(f"   Std deviation: {results['size_stats']['stdev']:.0f} chars")
        print(
            f"   Range: {results['size_stats']['min']} - {results['size_stats']['max']} chars"
        )

        # Size distribution
        print(f"\n📊 SIZE DISTRIBUTION:")
        dist = results["size_distribution"]
        print(f"   Very Small (<200): {dist['very_small']:.1f}%")
        print(f"   Small (200-400): {dist['small']:.1f}%")
        print(f"   Medium (400-600): {dist['medium']:.1f}%")
        print(f"   Large (600-800): {dist['large']:.1f}%")
        print(f"   Very Large (>800): {dist['very_large']:.1f}%")

        # Quality metrics
        print(f"\n✅ QUALITY METRICS:")
        qm = results["quality_metrics"]
        print(f"   Boundary violations: {qm['boundary_violation_rate']:.1f}%")
        print(f"   Orphan chunks: {qm['orphan_chunk_rate']:.1f}%")
        print(f"   Header coverage: {qm['header_coverage_rate']:.1f}%")

        # Examples of incomplete sentences
        if results["incomplete_samples"]:
            print(f"\n⚠️  INCOMPLETE SENTENCE EXAMPLES:")
            for i, sample in enumerate(results["incomplete_samples"][:3], 1):
                print(f"   {i}. [{sample['size']} chars] {sample['text']}")

        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        self._print_recommendations(results, max_chunk_size)

        print("\n" + "=" * 80)

    def _print_recommendations(self, results: Dict, max_chunk_size: int):
        """Print optimization recommendations."""
        qm = results["quality_metrics"]
        stats = results["size_stats"]

        # Check boundary violations
        if qm["boundary_violation_rate"] > 20:
            print(
                f"   🔴 HIGH boundary violation rate ({qm['boundary_violation_rate']:.1f}%)"
            )
            print(f"      → Enable sentence boundary detection")
            print(f"      → Increase search window for sentence endings")
        elif qm["boundary_violation_rate"] > 10:
            print(
                f"   🟡 MODERATE boundary violation rate ({qm['boundary_violation_rate']:.1f}%)"
            )
            print(f"      → Fine-tune sentence boundary regex")
        else:
            print(
                f"   🟢 LOW boundary violation rate ({qm['boundary_violation_rate']:.1f}%)"
            )

        # Check size distribution
        if stats["stdev"] > 200:
            print(f"   🔴 HIGH size variance (σ={stats['stdev']:.0f})")
            print(f"      → Set stricter min/max chunk size limits")
            print(f"      → Consider adaptive chunking")
        elif stats["stdev"] > 150:
            print(f"   🟡 MODERATE size variance (σ={stats['stdev']:.0f})")
        else:
            print(f"   🟢 LOW size variance (σ={stats['stdev']:.0f})")

        # Check orphan chunks
        if qm["orphan_chunk_rate"] > 5:
            print(f"   🔴 TOO MANY orphan chunks ({qm['orphan_chunk_rate']:.1f}%)")
            print(f"      → Increase min_chunk_size to 300-400")
            print(f"      → Merge small chunks with neighbors")

        # Optimal chunk size recommendation
        optimal_size = int(stats["median"])
        print(f"\n   📐 OPTIMAL CHUNK SIZE RECOMMENDATION:")
        print(f"      Current: {max_chunk_size} chars")
        print(f"      Suggested: {optimal_size} chars (based on median)")

        if abs(optimal_size - max_chunk_size) > 100:
            print(f"      → Consider adjusting max_chunk_size to {optimal_size}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Analyze chunk quality")
    parser.add_argument(
        "--corpus",
        type=str,
        default="backend/database/text_corpus",
        help="Path to corpus directory",
    )
    parser.add_argument(
        "--chunk-size", type=int, default=800, help="Chunk size to analyze"
    )

    args = parser.parse_args()

    analyzer = ChunkQualityAnalyzer()
    results = analyzer.analyze_corpus(
        corpus_path=args.corpus, max_chunk_size=args.chunk_size
    )


if __name__ == "__main__":
    main()
