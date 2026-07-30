# 1. Store the vector index as JSON files instead of a vector database

- Status: Accepted
- Date: 2026-07-30

## Context

Each uploaded PDF is split into chunks, and every chunk is embedded into a vector. These vectors need to be saved somewhere, so a document can be queried again without re-embedding it every time — embedding is the slow part, and it should run once per document.

The scale is small. A typical document produces around 1,000–1,500 chunks. Thanks to the multi-document library, the app keeps **one document's index in memory at a time**: activating a document loads its index, and a query just runs a brute-force cosine-similarity scan over that single list. The library can hold many documents on disk, but they're never all loaded at once.

The constraints: the project has to run at zero cost and stay open and self-hostable by anyone, it's built solo, and it should avoid dependencies it doesn't actually need.

## Decision

I store each document's index as a plain JSON file on disk, and load the active document's index into memory for brute-force vector search. I don't use a dedicated vector database.

## Alternatives considered

**A dedicated vector database (Chroma, Qdrant, Pinecone).** These shine when you have hundreds of thousands of vectors and a linear scan becomes too slow — that's what their ANN indexes are for. At my scale (~1,000–1,500 vectors in memory at a time), a brute-force scan already runs in milliseconds, so a vector DB would add a dependency and operational surface without solving a problem I actually have. Cost isn't the deciding factor here — Chroma runs locally for free — the point is that it's over-engineering for this scale.

**A binary format (NumPy, pickle) or SQLite with a vector extension.** A binary format would load faster and take less space than JSON. I chose JSON anyway: I know it well, it has zero dependencies (standard library), and it's human-readable — I can open an index and inspect it directly, which has already helped me debug retrieval. Picking a binary format would have meant learning a new one to save time the user never notices — effort better spent elsewhere at this scale. At a few MB loaded once per activation, the speed difference is invisible, so I optimized for simplicity and inspectability over raw performance.

## Consequences

**Positive.** No external services or dependencies to run: the whole thing works with the standard library, which keeps the project zero-cost and trivially self-hostable — anyone can clone and run it. Indexes are human-readable and easy to debug. The design stays provider-agnostic: nothing is tied to a specific vendor's API or data format.

**Negative.** Brute-force search is O(n) — it scans every vector on each query. This is fine now, but it degrades linearly as a document grows. Loading a full index into memory also caps document size at whatever fits in RAM. And keeping only one index in memory at a time means switching documents pays a reload cost, rather than querying across the whole library at once.

**When to revisit.** This decision holds while documents stay in the ~thousands-of-chunks range and are queried one at a time. If the use case shifts toward much larger documents, or searching across the entire library simultaneously, the brute-force scan becomes the bottleneck and a vector database (with ANN indexing) becomes the right call. That migration is already noted in the project backlog.