"""Dependency-free checks for the UniAssist UMT corpus."""
from collections import Counter
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def validate():
    metadata = json.loads((ROOT / "metadata.json").read_text(encoding="utf-8"))
    catalogue = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
    entries = metadata["documents"]
    files = sorted((ROOT / "corpus").glob("*.txt"))
    assert len(entries) == 20 and len(files) == 20, "Expected exactly 20 corpus files and entries"
    assert {f.name for f in files} == {e["file"] for e in entries}, "Metadata filenames do not match files"
    seen = set()
    total_words = 0
    genres = Counter()
    referenced_sources = set()
    for entry in entries:
        path = ROOT / "corpus" / entry["file"]
        text = path.read_text(encoding="utf-8")
        word_count = len(text.split())
        assert 200 <= word_count <= 300, f"Wrong word count in {path.name}: {word_count}"
        assert word_count == entry["words"], f"Metadata count stale for {path.name}"
        assert text not in seen, f"Duplicate contents in {path.name}"
        assert "\ufffd" not in text, f"Replacement character detected in {path.name}"
        assert entry.get("sources") and all(url.startswith("https://umt.edu.al/") for url in entry["sources"]), f"Missing official UMT source: {path.name}"
        assert "Reference: https://umt.edu.al/" in text, f"Missing visible source attribution: {path.name}"
        referenced_sources.update(entry["sources"])
        genres[entry["genre"]] += 1
        seen.add(text)
        total_words += word_count
        print(f"{path.name:38} {word_count:3} words  {entry['genre']}")
    assert len(genres) >= 3, "Expected at least three genres"
    catalogue_urls = [source["url"] for source in catalogue["sources"]]
    assert len(catalogue_urls) == len(set(catalogue_urls)), "Duplicate URL in source catalogue"
    assert set(catalogue_urls) == referenced_sources, "Source catalogue and metadata differ"
    print(f"Source catalogue: {len(catalogue_urls)} unique official UMT URLs")
    print(f"\nPASS: {len(files)} UTF-8 documents, {total_words} words, genres={dict(genres)}")
    return metadata


if __name__ == "__main__":
    validate()
