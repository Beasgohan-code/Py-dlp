"""Fuzzy Perceptual Media Hash and Cross-Platform Smart Deduplication Engine for Py-dlp."""

from __future__ import annotations

import json
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from pydlp.core.types import MediaInfo


class FuzzyDedupManager:
    """Detects duplicate and mirrored videos across different URLs, channels, and platforms."""

    def __init__(self, db_path: Optional[str] = None, similarity_threshold: float = 0.85):
        if db_path:
            self.db_path = Path(db_path)
        else:
            cache_dir = Path.home() / ".config" / "pydlp"
            cache_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = cache_dir / "dedup_registry.db"

        self.threshold = similarity_threshold
        self._init_db()

    def _init_db(self) -> None:
        """Initializes the SQLite deduplication fingerprint table."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS media_fingerprints (
                    media_id TEXT PRIMARY KEY,
                    extractor TEXT,
                    title TEXT,
                    clean_title TEXT,
                    duration REAL,
                    uploader TEXT,
                    filesize INTEGER,
                    webpage_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_clean_title ON media_fingerprints(clean_title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_duration ON media_fingerprints(duration)")
            conn.commit()

    @staticmethod
    def clean_text(text: Optional[str]) -> str:
        """Normalizes titles by stripping punctuation, emojis, resolution tags (1080p, 4K, HD), and extra whitespace."""
        if not text:
            return ""
        s = text.lower()
        s = re.sub(r"\[(4k|1080p|720p|hd|official video|music video|lyrics|hq)\]", "", s)
        s = re.sub(r"\((4k|1080p|720p|hd|official video|music video|lyrics|hq)\)", "", s)
        s = re.sub(r"[^\w\s]", " ", s)
        return " ".join(s.split())

    @classmethod
    def string_similarity(cls, a: str, b: str) -> float:
        """Computes word-token Jaccard / Levenshtein overlap similarity ratio between 0.0 and 1.0."""
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0

        words_a = set(a.split())
        words_b = set(b.split())
        if not words_a or not words_b:
            return 0.0

        intersection = len(words_a & words_b)
        union = len(words_a | words_b)
        jaccard = intersection / union if union > 0 else 0.0

        # Character bi-gram similarity
        def get_bigrams(s):
            return {s[i : i + 2] for i in range(len(s) - 1)}

        bi_a = get_bigrams(a)
        bi_b = get_bigrams(b)
        bi_inter = len(bi_a & bi_b)
        bi_union = len(bi_a | bi_b)
        bigram_sim = bi_inter / bi_union if bi_union > 0 else 0.0

        return 0.5 * jaccard + 0.5 * bigram_sim

    def is_duplicate(self, info: MediaInfo) -> Tuple[bool, Optional[str]]:
        """Checks if MediaInfo matches any recorded video by ID, or by fuzzy title + duration."""
        clean_curr_title = self.clean_text(info.title)
        curr_dur = float(info.duration or 0)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 1. Exact ID match
            cursor.execute("SELECT title, webpage_url FROM media_fingerprints WHERE media_id = ?", (info.id,))
            row = cursor.fetchone()
            if row:
                return True, f"Exact ID match with previously downloaded item: '{row[0]}' ({row[1]})"

            # 2. Duration + Fuzzy Title match
            if curr_dur > 5.0:  # Only for videos longer than 5 seconds
                # Find videos within ±2.5 seconds duration
                cursor.execute(
                    "SELECT media_id, title, clean_title, webpage_url FROM media_fingerprints WHERE ABS(duration - ?) <= 2.5",
                    (curr_dur,),
                )
                candidates = cursor.fetchall()
                for c_id, c_title, c_clean, c_url in candidates:
                    sim = self.string_similarity(clean_curr_title, c_clean)
                    if sim >= self.threshold:
                        return (
                            True,
                            f"Fuzzy duplicate detected ({int(sim*100)}% match) of '{c_title}' ({c_url})",
                        )

        return False, None

    def record_media(self, info: MediaInfo) -> None:
        """Stores media fingerprint in database."""
        clean_title = self.clean_text(info.title)
        filesize = (
            max([f.filesize or 0 for f in info.formats]) if info.formats else None
        )
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO media_fingerprints 
                (media_id, extractor, title, clean_title, duration, uploader, filesize, webpage_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    info.id,
                    info.extractor,
                    info.title,
                    clean_title,
                    float(info.duration or 0),
                    info.uploader,
                    filesize,
                    info.webpage_url,
                ),
            )
            conn.commit()
