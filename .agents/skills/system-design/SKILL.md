---
name: system-design
description: BigTech System Design architecture knowledge base and engineering video production guide based on Alex Xu's System Design Interview (Vol 1 & 2). Covers 28 distributed systems (YouTube transcoding, Google Drive sync, Rate limiters, Chat systems, S3 storage, Payment gateways) for architecture planning and high-retention engineering shorts.
---

# System Design & BigTech Architecture Knowledge Base

Based on Alex Xu's industry-standard *System Design Interview — An Insider's Guide* (Vols 1 & 2, liquidslr notes), this skill equips the agent with concrete architectural designs, scaling trade-offs, and technical scripts for producing high-engagement engineering explainers and tech shorts.

---

## 1. The 28 Core System Design Blueprints

### Media, Streaming & Storage Systems
- **14. YouTube Architecture**:
  - **Video Transcoding DAG**: Splitting raw upload into GOP (Group of Pictures) chunks, parallel transcoding into multiple resolutions (1080p, 720p, 480p) and codecs (H.264, VP9, AV1).
  - **Adaptive Bitrate Streaming**: Dynamic switching between bitrate ladders using HLS and MPEG-DASH.
  - **Global CDN Edge Caching**: Replicating popular videos to edge points of presence (PoP).
- **15. Google Drive / Dropbox**:
  - **Block-level Chunking & Deduplication**: Splitting files into 4MB chunks, hashing with SHA-256 to avoid re-uploading duplicate blocks.
  - **Differential Synchronization**: Uploading only modified deltas/chunks rather than entire files.
  - **Metadata DB & Notification Service**: Long polling / WebSockets notifying other synchronized devices of remote edits.
- **24. S3-Like Object Storage**:
  - **Data vs Metadata Separation**: Fast key-value metadata store + immutable append-only chunk servers.
  - **Erasure Coding (e.g. 8+4 scheme)**: Providing 99.999999999% durability with much lower disk overhead than 3x replication.

### Real-Time Communications & Messaging
- **10. Distributed Notification System**:
  - Tiered push routing: APNs (iOS), FCM (Android), SMS (Twilio), Email (SendGrid).
  - Rate limiting, opt-out management, and queue deduplication using Redis.
- **12. Real-Time Chat System (Discord / Slack)**:
  - WebSocket connection managers handling millions of concurrent persistent sockets.
  - Read receipts, typing indicators, and message fan-out using message brokers.
  - Storage: NoSQL / Cassandra for horizontal message scaling partitioned by channel ID.
- **19. Distributed Message Queue (Kafka / Pulsar)**:
  - Log-structured append-only partitions, zero-copy reads via OS page cache (`sendfile`).
  - Consumer groups for horizontal load-balanced stream processing.

### Distributed Core & Scaling
- **01. Scaling 0 to Millions of Users**: Vertical vs Horizontal scaling, stateless web tier, DB read replicas, caching (Cache-Aside), CDN, DB sharding.
- **02. Back-of-the-Envelope Estimation**: QPS calculation, peak traffic headroom (2-5x), memory/storage sizing rules (1 byte, 1KB, 1MB, 1GB).
- **04. Rate Limiter**: Token Bucket, Leaky Bucket, Fixed Window, Sliding Window Log, Sliding Window Counter (Redis sorted sets).
- **05. Consistent Hashing**: Hash ring, virtual nodes (vnodes) to prevent hotspotting when nodes join or leave.
- **06. Key-Value Store**: Dynamo-style architecture, Quorum consensus ($R + W > N$), vector clocks for conflict resolution, gossip protocol for failure detection.
- **07. Unique ID Generator**: Twitter Snowflake (1 bit unused + 41 bit timestamp + 10 bit machine ID + 12 bit sequence number).
- **08. URL Shortener**: Base62 encoding ($[0-9a-zA-Z]$), collision handling, 301 (permanent) vs 302 (temporary analytics) redirects.
- **13. Search Autocomplete**: Trie data structure, frequency caching at prefix nodes, weekly offline MapReduce trie rebuilding.

### Geolocation & Maps
- **16. Proximity Service**: Geohash (base32 grid hierarchy) and Quadtree for spatial indexing.
- **17. Nearby Friends**: Redis Pub/Sub channels per user, location update throttling, background distance filtering.
- **18. Google Maps**: Road network graph partitioning, pre-computed hierarchical Dijkstra / A* route calculation, vector map tile servers.

### High-Integrity & Financial Systems
- **21. Ad Click Aggregation**: Real-time event streaming with Apache Flink, tumbling vs sliding windows, exactly-once delivery semantics.
- **22. Hotel Reservation System**: Concurrency control, Pessimistic locking (SELECT FOR UPDATE) vs Optimistic locking (versioning) to prevent double bookings.
- **26. Payment System**:
  - **Idempotency Keys**: Guaranteeing a charged transaction cannot be duplicated on network retries.
  - **Double-Entry Bookkeeping**: Recording debits and credits symmetrically to ensure money is never created or destroyed in transit.
  - **Reconciliation Engine**: Nightly batch comparison between internal ledger and payment gateway settlement files.
- **27. Digital Wallet**: Event sourcing pattern, immutable transaction logs, in-memory state projection with snapshotting.
- **28. Stock Exchange / Trading Engine**: Order book matching engine, LMAX Disruptor ring buffer, single-threaded core for zero lock contention.

---

## 2. Engineering Shorts Production Recipe

Use this knowledge to generate high-CTR 9:16 vertical shorts using OpenMontage's `EngineeringShortOverlay` and `Explainer`:

### Hook Formulas
1. *"유튜브는 전 세계에서 올라오는 수억 개의 영상을 어떻게 서버 다운 없이 처리할까?"* (14. YouTube)
2. *"구글 드라이브에 10GB 파일을 올릴 때 1초 만에 끝나는 천재적인 이유"* (15. Google Drive)
3. *"넷플릭스가 트래픽 폭발에도 렉이 전혀 없는 비결: 일관된 해싱"* (05. Consistent Hashing)
4. *"토스/카카오페이가 결제 중 인터넷이 끊겨도 돈이 두 번 빠져나가지 않는 원리"* (26. Payment Idempotency)

### Remotion Visual Composition
- **Component**: `remotion-composer/src/components/EngineeringShortOverlay.tsx`
- **Props**:
  - `topicTag`: "시스템 설계 · EP.14"
  - `dimensionLabel`: "DAG 기반 병렬 트랜스코딩 파이프라인"
  - `focalCallout`: "4MB 블록 분할 및 중복 제거율 94.2%"
  - `metricHighlight`: "QPS 1,200,000 / 가용성 99.999%"
  - `subtitle`: 한국어 나레이션 자막 연동
