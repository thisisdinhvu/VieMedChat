"""
Export Optimized Parent-Child Chunks
Exports both parent and child chunks with enriched metadata.

Usage:
    python backend/preprocessing/export_parent_child.py
"""

import os
import sys
from pathlib import Path
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

try:
    from .parent_child_chunker import OptimizedParentChildChunker
except ImportError:
    from parent_child_chunker import OptimizedParentChildChunker


def export_parent_child_chunks(
    corpus_path: str = "backend/database/text_corpus",
    parent_output_dir: str = "backend/database/parent_chunks_optimized",
    child_output_dir: str = "backend/database/child_chunks_optimized",
    parent_max_size: int = 1500,
    child_max_size: int = 500,
    child_overlap: int = 100,
):
    """Export optimized parent-child chunks."""
    print("=" * 80)
    print("📦 EXPORTING OPTIMIZED PARENT-CHILD CHUNKS")
    print("=" * 80)

    # Create directories
    parent_dir = Path(parent_output_dir)
    child_dir = Path(child_output_dir)
    parent_dir.mkdir(parents=True, exist_ok=True)
    child_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📁 Output directories:")
    print(f"   Parents: {parent_dir.absolute()}")
    print(f"   Children: {child_dir.absolute()}")

    # Initialize chunker
    chunker = OptimizedParentChildChunker(
        parent_max_size=parent_max_size,
        child_max_size=child_max_size,
        child_min_size=200,
        child_overlap=child_overlap,
    )

    # Process corpus
    corpus_dir = Path(corpus_path)
    all_parents = []
    all_children = []

    print(f"\n1️⃣ Processing corpus from: {corpus_path}")

    file_count = 0
    for file_path in corpus_dir.rglob("*.txt"):
        file_count += 1
        print(f"   Processing: {file_path.name}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        parents, children = chunker.chunk_document(content, file_path.name)
        all_parents.extend(parents)
        all_children.extend(children)

    print(f"\n2️⃣ Exporting chunks...")

    # Export parents
    for i, parent in enumerate(all_parents):
        filename = f"parent_{i:05d}.txt"
        file_path = parent_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# ID: {parent['id']}\n")
            f.write(f"# Header: {parent['header']}\n")
            f.write(f"# Source: {parent['filename']}\n")
            f.write(f"# Section Depth: {parent['section_depth']}\n")
            f.write(f"# Char Count: {parent['char_count']}\n")
            f.write(f"# Type: parent\n\n")
            f.write(parent["text"])

        if (i + 1) % 100 == 0:
            print(f"   Exported {i + 1}/{len(all_parents)} parents...")

    # Export children with enriched metadata
    for i, child in enumerate(all_children):
        filename = f"child_{i:05d}.txt"
        file_path = child_dir / filename

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# ID: {child['id']}\n")
            f.write(f"# Parent ID: {child['parent_id']}\n")
            f.write(f"# Header: {child['header']}\n")
            f.write(f"# Source: {child['filename']}\n")
            f.write(
                f"# Chunk Index: {child['chunk_index']}/{child['total_children']}\n"
            )
            f.write(f"# Char Count: {child['char_count']}\n")
            f.write(f"# Complete Sentences: {child['has_complete_sentences']}\n")
            f.write(f"# Section Depth: {child['section_depth']}\n")
            f.write(f"# Keywords: {', '.join(child['keywords'])}\n")
            f.write(f"# Type: child\n\n")
            f.write(child["text"])

        if (i + 1) % 100 == 0:
            print(f"   Exported {i + 1}/{len(all_children)} children...")

    # Create mapping
    mapping_file = parent_dir.parent / "parent_child_mapping_optimized.json"
    mapping = {}
    for child in all_children:
        parent_id = child["parent_id"]
        if parent_id not in mapping:
            mapping[parent_id] = []
        mapping[parent_id].append(child["id"])

    with open(mapping_file, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)

    # Statistics
    print(f"\n{'='*80}")
    print(f"✅ EXPORT COMPLETED")
    print(f"{'='*80}")
    print(f"📊 Statistics:")
    print(f"   Files processed: {file_count}")
    print(f"   Parent chunks: {len(all_parents)}")
    print(f"   Child chunks: {len(all_children)}")
    print(
        f"   Avg children per parent: {len(all_children) / max(len(all_parents), 1):.1f}"
    )

    parent_size = sum(f.stat().st_size for f in parent_dir.glob("*.txt"))
    child_size = sum(f.stat().st_size for f in child_dir.glob("*.txt"))

    print(f"   Parent chunks size: {parent_size / 1024:.2f} KB")
    print(f"   Child chunks size: {child_size / 1024:.2f} KB")

    # Quality metrics
    complete_count = sum(1 for c in all_children if c["has_complete_sentences"])
    small_count = sum(1 for c in all_children if c["char_count"] < 200)

    print(f"\n📈 Quality Metrics:")
    print(f"   Complete sentences: {complete_count / len(all_children) * 100:.1f}%")
    print(
        f"   Chunks < 200 chars: {small_count} ({small_count / len(all_children) * 100:.1f}%)"
    )

    # Sample
    if all_children:
        sample = all_children[0]
        print(f"\n📝 Sample Child Chunk:")
        print(f"   ID: {sample['id']}")
        print(f"   Index: {sample['chunk_index']}/{sample['total_children']}")
        print(f"   Size: {sample['char_count']} chars")
        print(f"   Complete: {sample['has_complete_sentences']}")
        print(f"   Keywords: {sample['keywords']}")
        print(f"   Text: {sample['text'][:100]}...")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus", default="backend/database/text_corpus")
    parser.add_argument(
        "--parent-dir", default="backend/database/parent_chunks_optimized"
    )
    parser.add_argument(
        "--child-dir", default="backend/database/child_chunks_optimized"
    )

    args = parser.parse_args()

    export_parent_child_chunks(
        corpus_path=args.corpus,
        parent_output_dir=args.parent_dir,
        child_output_dir=args.child_dir,
    )
