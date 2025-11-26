"""
Optimized Parent-Child Chunking Strategy
Implements research-backed best practices for Vietnamese medical text.

Key Optimizations:
1. Vietnamese-aware sentence boundary detection
2. Enriched metadata with quality metrics
3. Minimum chunk size enforcement (200 chars)
4. Enhanced header detection (questions, numbered, bold)
"""

from typing import List, Dict, Tuple, Optional
from pathlib import Path
from collections import Counter
import re


class OptimizedParentChildChunker:
    """
    Production-ready Parent-Child chunking with Vietnamese optimizations.

    Research-backed parameters:
    - Child: 400-600 chars (optimal for embedding)
    - Parent: 1000-1500 chars (optimal for context)
    - Overlap: 15-20% (balance between redundancy and coverage)
    """

    # Vietnamese stopwords for keyword extraction
    VIETNAMESE_STOPWORDS = {
        "là",
        "của",
        "và",
        "có",
        "được",
        "trong",
        "với",
        "cho",
        "từ",
        "theo",
        "này",
        "đó",
        "các",
        "những",
        "một",
        "để",
        "khi",
        "đã",
        "sẽ",
        "bị",
        "về",
        "như",
        "hay",
        "hoặc",
        "nhưng",
        "mà",
        "nếu",
        "thì",
        "vì",
        "do",
    }

    def __init__(
        self,
        parent_max_size: int = 1500,
        child_max_size: int = 500,
        child_min_size: int = 200,  # NEW: Minimum chunk size
        child_overlap: int = 100,
    ):
        """
        Initialize optimized chunker.

        Args:
            parent_max_size: Maximum size for parent chunks
            child_max_size: Maximum size for child chunks
            child_min_size: Minimum size for child chunks (quality threshold)
            child_overlap: Overlap between child chunks
        """
        self.parent_max_size = parent_max_size
        self.child_max_size = child_max_size
        self.child_min_size = child_min_size
        self.child_overlap = child_overlap

    def chunk_document(
        self, content: str, filename: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Chunk document into optimized parent-child hierarchy.

        Args:
            content: Document content
            filename: Source filename

        Returns:
            (parent_chunks, child_chunks) with enriched metadata
        """
        # Step 1: Create parent chunks
        parents = self._create_parent_chunks(content, filename)

        # Step 2: Create children from each parent
        children = []
        for parent in parents:
            parent_children = self._create_child_chunks(
                parent_text=parent["text"],
                parent_id=parent["id"],
                parent_header=parent["header"],
                parent_depth=parent["section_depth"],
                filename=filename,
            )
            children.extend(parent_children)

        return parents, children

    def _detect_header(self, line: str) -> Optional[Tuple[str, int]]:
        """
        Detect header with multiple patterns.

        Returns:
            (header_text, depth) or None
        """
        # Pattern 1: Markdown headers (# Header, ## Header)
        md = re.match(r"^(#{1,6})\s+(.+)$", line)
        if md:
            depth = len(md.group(1))
            return (md.group(2).strip(), depth)

        # Pattern 2: ALL CAPS (HEADER TEXT)
        caps = re.match(
            r"^([A-ZÀÁẠẢÃĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆÌÍỊỈĨÒÓỌỎÕÔỐỒỔỖỘƠỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸĐ\s]{10,})$",
            line,
        )
        if caps and len(line) < 100:
            return (caps.group(1).strip(), 1)

        # Pattern 3: Question headers (Nguyên nhân là gì?)
        question = re.match(
            r"^(.+\s+(là\s+gì|như\s+thế\s+nào|tại\s+sao|vì\s+sao)\??)$",
            line,
            re.IGNORECASE,
        )
        if question and 10 < len(line) < 100:
            return (question.group(1).strip(), 2)

        # Pattern 4: Numbered (1. Header, I. Header, a. Header)
        numbered = re.match(r"^([IVXivx]+\.|[\d]+\.|[a-z]\.)\s+(.+)$", line)
        if numbered and len(line) < 100:
            return (numbered.group(2).strip(), 2)

        # Pattern 5: Bold (**Header** or __Header__)
        bold = re.match(r"^[\*_]{2}(.+?)[\*_]{2}$", line)
        if bold and len(line) < 100:
            return (bold.group(1).strip(), 2)

        return None

    def _create_parent_chunks(self, content: str, filename: str) -> List[Dict]:
        """
        Create parent chunks with enhanced header detection.
        """
        parents = []
        lines = content.split("\n")

        current_section = ""
        current_header = "Introduction"
        current_depth = 1
        section_id = 0

        for line in lines:
            # Try to detect header
            header_info = self._detect_header(line)

            if header_info:
                header_text, depth = header_info

                # Save previous section
                if current_section.strip():
                    parents.append(
                        {
                            "id": f"{filename}_parent_{section_id}",
                            "text": current_section.strip(),
                            "header": current_header,
                            "section_depth": current_depth,
                            "filename": filename,
                            "type": "parent",
                            "char_count": len(current_section.strip()),
                        }
                    )
                    section_id += 1

                # Start new section
                current_header = header_text
                current_depth = depth
                current_section = ""
            else:
                current_section += line + "\n"

                # Split if too large
                if len(current_section) >= self.parent_max_size:
                    parents.append(
                        {
                            "id": f"{filename}_parent_{section_id}",
                            "text": current_section.strip(),
                            "header": current_header,
                            "section_depth": current_depth,
                            "filename": filename,
                            "type": "parent",
                            "char_count": len(current_section.strip()),
                        }
                    )
                    section_id += 1
                    current_section = ""

        # Add last section
        if current_section.strip():
            parents.append(
                {
                    "id": f"{filename}_parent_{section_id}",
                    "text": current_section.strip(),
                    "header": current_header,
                    "section_depth": current_depth,
                    "filename": filename,
                    "type": "parent",
                    "char_count": len(current_section.strip()),
                }
            )

        return parents

    def _find_sentence_boundary(self, text: str, max_pos: int) -> Tuple[int, bool]:
        """
        Find optimal sentence boundary with Vietnamese-specific rules.

        Returns:
            (position, has_complete_sentence)
        """
        min_acceptable = int(max_pos * 0.6)

        # Priority 1: Paragraph boundary (\n\n)
        para_matches = list(re.finditer(r"\n\n", text[:max_pos]))
        if para_matches:
            last_para = para_matches[-1].end()
            if last_para >= min_acceptable:
                return (last_para, True)

        # Priority 2: Sentence boundary (Vietnamese-aware)
        sentence_patterns = [
            # Period + space + capital (NOT after abbreviations)
            r"(?<![A-Z])\. [A-ZÀÁẠẢÃĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆÌÍỊỈĨÒÓỌỎÕÔỐỒỔỖỘƠỚỜỞỠỢÙÚỤỦŨƯỨỪỬỮỰỲÝỴỶỸĐ]",
            r"\.\n",  # Period + newline
            r"[!?] ",  # Exclamation/question + space
        ]

        search_start = max(min_acceptable, max_pos - 300)
        for pattern in sentence_patterns:
            matches = list(re.finditer(pattern, text[search_start:max_pos]))
            if matches:
                pos = search_start + matches[-1].end()
                return (pos, True)

        # Priority 3: Line break
        newline_pos = text[:max_pos].rfind("\n")
        if newline_pos > max_pos - 100:
            return (newline_pos, False)

        # Fallback: Hard cut
        return (max_pos, False)

    def _extract_keywords(self, text: str, top_k: int = 5) -> List[str]:
        """Extract top keywords, excluding stopwords."""
        # Remove header injection
        text = re.sub(r"^\[.+?\]\s*", "", text)

        # Tokenize and count
        words = re.findall(r"\w+", text.lower())
        word_freq = Counter(
            w for w in words if w not in self.VIETNAMESE_STOPWORDS and len(w) > 2
        )

        return [w for w, _ in word_freq.most_common(top_k)]

    def _create_child_chunks(
        self,
        parent_text: str,
        parent_id: str,
        parent_header: str,
        parent_depth: int,
        filename: str,
    ) -> List[Dict]:
        """
        Create optimized child chunks with enriched metadata.
        """
        children = []

        # If parent is small, create single child
        if len(parent_text) <= self.child_max_size:
            chunk_text = f"[{parent_header}] {parent_text}"
            children.append(
                {
                    "id": f"{parent_id}_child_0",
                    "text": chunk_text,
                    "parent_id": parent_id,
                    "header": parent_header,
                    "filename": filename,
                    "type": "child",
                    # NEW metadata
                    "chunk_index": 0,
                    "total_children": 1,
                    "char_count": len(chunk_text),
                    "has_complete_sentences": True,
                    "section_depth": parent_depth,
                    "keywords": self._extract_keywords(chunk_text),
                }
            )
            return children

        # Split into multiple children
        start = 0
        child_id = 0

        while start < len(parent_text):
            end = start + self.child_max_size

            # Find optimal boundary
            if end < len(parent_text):
                boundary, is_complete = self._find_sentence_boundary(
                    parent_text[start:], self.child_max_size
                )
                end = start + boundary
            else:
                is_complete = True

            # Extract chunk
            chunk_content = parent_text[start:end].strip()

            if chunk_content:
                chunk_text = f"[{parent_header}] {chunk_content}"
                children.append(
                    {
                        "id": f"{parent_id}_child_{child_id}",
                        "text": chunk_text,
                        "parent_id": parent_id,
                        "header": parent_header,
                        "filename": filename,
                        "type": "child",
                        # NEW metadata
                        "chunk_index": child_id,
                        "total_children": -1,  # Will update later
                        "char_count": len(chunk_text),
                        "has_complete_sentences": is_complete,
                        "section_depth": parent_depth,
                        "keywords": self._extract_keywords(chunk_text),
                    }
                )
                child_id += 1

            # Move to next with overlap
            start = end - self.child_overlap

            if start >= len(parent_text):
                break

        # Update total_children count
        total = len(children)
        for child in children:
            child["total_children"] = total

        # Merge small children
        children = self._merge_small_children(children)

        return children

    def _merge_small_children(self, children: List[Dict]) -> List[Dict]:
        """
        Merge children smaller than min_size with neighbors.
        """
        if len(children) <= 1:
            return children

        merged = []
        i = 0

        while i < len(children):
            current = children[i]

            # If too small and not last, merge with next
            if current["char_count"] < self.child_min_size and i < len(children) - 1:
                next_child = children[i + 1]

                # Merge texts
                current["text"] = current["text"] + " " + next_child["text"]
                current["char_count"] = len(current["text"])
                current["keywords"] = self._extract_keywords(current["text"])
                current["has_complete_sentences"] = next_child["has_complete_sentences"]

                i += 2  # Skip next
            else:
                merged.append(current)
                i += 1

        # Re-index
        for idx, child in enumerate(merged):
            child["chunk_index"] = idx
            child["total_children"] = len(merged)

        return merged


# Example usage
if __name__ == "__main__":
    chunker = OptimizedParentChildChunker()

    sample = """
# Bệnh Alzheimer

## Định nghĩa là gì?
Alzheimer là bệnh thoái hóa thần kinh tiến triển, ảnh hưởng đến trí nhớ.

## Triệu chứng
Các triệu chứng bao gồm quên tên người quen, lạc đường.

1. Giai đoạn sớm
Bệnh nhân thường quên tên người quen.

2. Giai đoạn muộn
Mất khả năng giao tiếp hoàn toàn.
"""

    parents, children = chunker.chunk_document(sample, "test.txt")

    print(f"Parents: {len(parents)}")
    print(f"Children: {len(children)}")

    for child in children[:2]:
        print(f"\n{child['id']}:")
        print(f"  Index: {child['chunk_index']}/{child['total_children']}")
        print(f"  Size: {child['char_count']} chars")
        print(f"  Complete: {child['has_complete_sentences']}")
        print(f"  Keywords: {child['keywords']}")
        print(f"  Text: {child['text'][:100]}...")
