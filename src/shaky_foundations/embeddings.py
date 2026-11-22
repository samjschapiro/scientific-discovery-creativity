"""Per-atom bge-large vectors, computed by us and cached on disk.

Embedding the plain atom `text` with BAAI/bge-large-en-v1.5 (no query prefix, unit-normalised)
reproduces the package's vectors: on 1,000 random atoms our cosine to the assigned c200000 centroid
matches the package's `sim_c200000` with r = 1.0000, mean |diff| 0.0002 (checked 2026-11-21; the
query prefix gives r = 0.77). So these vectors live in the same space as the concept centroids.

Cache layout (resumable; append-only):
    <cache_dir>/chunk_00000.npy          float16 [n, 1024]
    <cache_dir>/chunk_00000.ids.parquet  atom_id, same order
    <cache_dir>/model.txt                model name; a different model fails loudly
~290 atoms/s on Apple MPS.
"""

from pathlib import Path

import numpy as np
import polars as pl


def _cached_ids(cache_dir: Path) -> set[str]:
    ids = set()
    for p in sorted(cache_dir.glob("chunk_*.ids.parquet")):
        ids.update(pl.read_parquet(p)["atom_id"].to_list())
    return ids


def ensure_embedded(con, atom_ids: list[str], cache_dir: str, model_name: str, device: str,
                    batch_size: int = 64, chunk_size: int = 20000) -> int:
    """Embed every atom_id not yet in the cache. Returns how many were newly embedded."""
    cache = Path(cache_dir)
    cache.mkdir(parents=True, exist_ok=True)
    marker = cache / "model.txt"
    if marker.exists() and marker.read_text().strip() != model_name:
        raise ValueError(f"FATAL: cache {cache} holds {marker.read_text().strip()}, not {model_name}")
    marker.write_text(model_name)

    missing = sorted(set(atom_ids) - _cached_ids(cache))
    if not missing:
        return 0
    con.register("need_ids", pl.DataFrame({"atom_id": missing}))
    texts = con.sql("SELECT a.atom_id, a.text FROM atoms a JOIN need_ids USING (atom_id)").pl()
    if texts.height != len(missing):
        raise ValueError(f"FATAL: {len(missing) - texts.height} atom_ids not found in atoms")

    from sentence_transformers import SentenceTransformer  # heavy import; only when needed
    model = SentenceTransformer(model_name, device=device)
    next_chunk = len(list(cache.glob("chunk_*.npy")))
    for i in range(0, texts.height, chunk_size):
        part = texts.slice(i, chunk_size)
        v = model.encode(part["text"].to_list(), batch_size=batch_size, normalize_embeddings=True,
                         show_progress_bar=False).astype(np.float16)
        stem = cache / f"chunk_{next_chunk:05d}"
        np.save(f"{stem}.npy", v)
        part.select("atom_id").write_parquet(f"{stem}.ids.parquet")
        next_chunk += 1
        print(f"  embedded {min(i + chunk_size, texts.height):,}/{texts.height:,}", flush=True)
    return texts.height


def load_vectors(cache_dir: str, atom_ids: list[str]) -> tuple[dict[str, int], np.ndarray]:
    """(atom_id -> row, float16 matrix) for the requested ids; fails if any is missing."""
    want = set(atom_ids)
    ids, mats = [], []
    for p in sorted(Path(cache_dir).glob("chunk_*.ids.parquet")):
        chunk_ids = pl.read_parquet(p)["atom_id"].to_numpy()
        keep = np.fromiter((a in want for a in chunk_ids), dtype=bool, count=len(chunk_ids))
        if keep.any():
            mats.append(np.load(str(p).replace(".ids.parquet", ".npy"))[keep])
            ids.extend(chunk_ids[keep].tolist())
    index = {a: i for i, a in enumerate(ids)}
    if len(index) != len(want):
        raise ValueError(f"FATAL: {len(want) - len(index)} requested atoms are not in the cache {cache_dir}")
    return index, (np.concatenate(mats) if mats else np.empty((0, 1024), dtype=np.float16))


_MODELS: dict = {}


def embed_texts(texts: list[str], model_name: str, device: str, batch_size: int = 32) -> np.ndarray:
    """Embed free text (ideas, limitation statements) in the same space as the atoms; unit-normalised float32.
    The model is loaded once per process."""
    if model_name not in _MODELS:
        from sentence_transformers import SentenceTransformer
        _MODELS[model_name] = SentenceTransformer(model_name, device=device)
    return _MODELS[model_name].encode(texts, batch_size=batch_size, normalize_embeddings=True,
                                      show_progress_bar=False).astype(np.float32)
