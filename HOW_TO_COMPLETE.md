# Hướng Dẫn Hoàn Thành Lab 7: Embedding & Vector Store

> **Mục tiêu:** Hướng dẫn từng bước để hoàn thành assignment, từ setup đến nộp bài.

---

## Phase 0: Chuẩn Bị Môi Trường (15 phút)

### Step 1: Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Kiểm Tra Tests Ban Đầu

```bash
pytest tests/ -v
```

- **Kỳ vọng:** Phần lớn tests sẽ FAIL (vì bạn chưa implement)
- **Mục tiêu:** Cuối cùng tất cả tests phải PASS

### Step 3: (Tùy Chọn) Chọn Embedding Backend

| Backend | Cài Đặt | Ưu Điểm |
|---------|---------|---------|
| **Mock** (mặc định) | Không cần cài thêm | Chạy ngay, không cần API key |
| **Local** | `pip install sentence-transformers` | Miễn phí, offline, chất lượng tốt |
| **OpenAI** | `pip install openai` + set `OPENAI_API_KEY` | Chất lượng cao nhất |

**Verify backend đã chọn:**
```bash
python -c "from src import LocalEmbedder; e = LocalEmbedder(); print(len(e('test')))"
```

---

## Phase 1: Cá Nhân - Core Implementation (3-4 giờ)

### Step 4: Warm-up Exercises (30 phút)

Mở file `report/REPORT.md` và điền **Section 1 (Warm-up)**:

| Exercise | File | Nội dung |
|----------|------|----------|
| Ex 1.1 | `report/REPORT.md` | Giải thích cosine similarity conceptually |
| Ex 1.2 | `report/REPORT.md` | Tính chunk count với công thức |

**Công thức chunk count:**
```
num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
```

Ví dụ: 10,000 chars, chunk_size=500, overlap=50
```
num_chunks = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450) = 23 chunks
```

### Step 5: Implement `src/chunking.py` (45 phút)

Mở `src/chunking.py` và implement các TODO:

#### 5.1 `SentenceChunker.chunk()`
- **Input:** text string
- **Output:** list of chunks (max_sentences_per_chunk sentences mỗi chunk)
- **Logic:** 
  - Split text on `. `, `! `, `? `, hoặc `.\n`
  - Group sentences thành chunks
  - Strip whitespace từ mỗi chunk

#### 5.2 `RecursiveChunker.chunk()` và `_split()`
- **Input:** text, separators priority list
- **Output:** list of chunks (không chunk nào vượt quá chunk_size)
- **Logic:**
  - Thử từng separator theo thứ tự
  - Nếu piece nào vẫn > chunk_size, recurse với separator tiếp theo
  - Base case: separator cuối cùng (split từng ký tự)

#### 5.3 `compute_similarity()`
- **Formula:** `dot(a, b) / (||a|| * ||b||)`
- **Guard:** Return 0.0 nếu either vector có magnitude = 0
- **Hint:** Dùng `_dot()` helper đã có

#### 5.4 `ChunkingStrategyComparator.compare()`
- **Input:** text, chunk_size
- **Output:** dict với stats cho cả 3 strategies
- **Include:** chunk count, avg length cho mỗi strategy

**Kiểm tra sau mỗi implement:**
```bash
pytest tests/test_solution.py -v -k chunking
```

### Step 6: Implement `src/store.py` (60 phút)

#### 6.1 `EmbeddingStore.__init__()` - ChromaDB initialization
- Try import chromadb
- Nếu success: init client + collection
- Nếu fail: dùng in-memory store

#### 6.2 `EmbeddingStore._make_record()`
- Build normalized dict với: id, embedding, content, metadata

#### 6.3 `EmbeddingStore._search_records()`
- Embed query
- Compute dot product với tất cả records
- Return top_k theo similarity

#### 6.4 `EmbeddingStore.add_documents()`
- Embed mỗi document
- Add vào store (ChromaDB hoặc in-memory)

#### 6.5 `EmbeddingStore.search()`
- Embed query
- Call `_search_records()` trên toàn bộ store

#### 6.6 `EmbeddingStore.get_collection_size()`
- Return số lượng records trong store

#### 6.7 `EmbeddingStore.search_with_filter()`
- Filter records theo metadata trước
- Search trong filtered subset

#### 6.8 `EmbeddingStore.delete_document()`
- Remove tất cả records có `metadata['doc_id'] == doc_id`
- Return True nếu có xóa gì, False nếu không

**Kiểm tra:**
```bash
pytest tests/test_solution.py -v -k store
```

### Step 7: Implement `src/agent.py` (30 phút)

#### 7.1 `KnowledgeBaseAgent.__init__()`
- Store reference to `store` và `llm_fn`

#### 7.2 `KnowledgeBaseAgent.answer()`
- Retrieve top_k chunks từ store
- Build prompt với context từ chunks
- Call `llm_fn(prompt)` và return answer

**Prompt structure gợi ý:**
```
Context:
[chunk 1 content]
[chunk 2 content]
...

Question: [user question]
Answer:
```

**Kiểm tra:**
```bash
pytest tests/test_solution.py -v -k agent
```

### Step 8: Verify Tất Cả Tests Pass

```bash
pytest tests/ -v
```

**Kỳ vọng:** Tất cả tests PASS

---

## Phase 2: Nhóm - Document & Strategy (2-3 giờ)

### Step 9: Chọn Domain & Thu Thập Tài Liệu (Cùng nhóm)

**Gợi ý domain:** FAQ, SOP, cooking recipes, Vietnamese law, technical docs

**Requirements:**
- 5-10 tài liệu
- Lưu vào `data/` dưới dạng `.txt` hoặc `.md`
- Mỗi tài liệu ít nhất 2 metadata fields

**Convert PDF to Markdown nếu cần:**
```bash
pip install marker-pdf
marker_single input.pdf output/
```

**Điền vào `report/REPORT.md` Section 2:**
- Domain & lý do chọn
- Data inventory table
- Metadata schema

### Step 10: Thiết Kế Chunking Strategy (Mỗi người khác nhau)

Mỗi thành viên chọn/chiến lược KHÁC NHAU:

| Thành viên | Strategy | Gợi ý tham số |
|------------|----------|---------------|
| A | FixedSizeChunker | chunk_size=300, overlap=50 |
| B | SentenceChunker | max_sentences=5 |
| C | RecursiveChunker | chunk_size=400 |
| D | Custom | By headers, Q&A pairs, etc. |

**Điền vào `report/REPORT.md` Section 3:**
- Baseline analysis (chạy `ChunkingStrategyComparator`)
- Strategy của bạn + rationale
- So sánh với baseline
- So sánh với thành viên khác

### Step 11: Chuẩn Bị 5 Benchmark Queries (Cùng nhóm)

Thống nhất 5 queries + gold answers:

| # | Query | Gold Answer | Metadata Filter Needed? |
|---|-------|-------------|------------------------|
| 1 | | | |
| ... | | | |

**Yêu cầu:**
- Queries đa dạng
- Ít nhất 1 query cần metadata filtering
- Gold answers cụ thể, verifiable

**Điền vào `report/REPORT.md` Section 6:**

### Step 12: Similarity Predictions (Cá nhân)

Chọn 5 cặp sentences, dự đoán similarity trước khi chạy:

| Pair | Sentence A | Sentence B | Dự đoán | Actual |
|------|-----------|-----------|---------|--------|
| 1 | | | high/low | |

**Điền vào `report/REPORT.md` Section 5**

---

## Phase 3: Benchmark & Report (1-2 giờ)

### Step 13: Chạy Benchmark Queries

```python
from src import EmbeddingStore, KnowledgeBaseAgent

# Setup
store = EmbeddingStore()
# ... add your documents ...
agent = KnowledgeBaseAgent(store, mock_llm)

# Run queries
for query in benchmark_queries:
    results = store.search(query, top_k=3)
    answer = agent.answer(query)
    print(f"Query: {query}")
    print(f"Top-3: {results}")
    print(f"Answer: {answer}")
```

**Điền vào `report/REPORT.md` Section 6:**
- Kết quả cho mỗi query
- Top-1 retrieved chunk
- Score
- Whether relevant
- Agent answer

### Step 14: Failure Analysis

Tìm ít nhất 1 case retrieval thất bại:
- Query nào?
- Tại sao? (chunk size, metadata thiếu, etc.)
- Đề xuất cải thiện?

**Điền vào `report/REPORT.md` Section 7**

### Step 15: Hoàn Thiện Report

Kiểm tra tất cả sections trong `report/REPORT.md`:

| Section | Nội dung | Điểm |
|---------|----------|------|
| 1 | Warm-up | 5 |
| 2 | Document Selection | 10 (nhóm) |
| 3 | Chunking Strategy | 15 (nhóm) |
| 4 | My Approach | 10 |
| 5 | Similarity Predictions | 5 |
| 6 | Results | 10 |
| 7 | What I Learned | 5 |

### Step 16: Self-Assessment

Điền bảng tự đánh giá cuối report:

```markdown
| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| ... | ... | ... |
| **Tổng** | | **/ 100** |
```

---

## Phase 4: Final Verification & Nộp Bài (30 phút)

### Step 17: Final Test Run

```bash
pytest tests/ -v
```

**Confirm:** All tests PASS

### Step 18: Code Review

Kiểm tra `src/`:
- `chunking.py` - all TODOs implemented
- `store.py` - all TODOs implemented  
- `agent.py` - all TODOs implemented

### Step 19: Report Review

Kiểm tra `report/REPORT.md`:
- [ ] Điền đầy đủ thông tin cá nhân
- [ ] All sections completed
- [ ] Tables filled
- [ ] Self-assessment done

### Step 20: Submission

**Files cần nộp:**
1. `src/` - hoàn thành tất cả TODO
2. `report/REPORT.md` - báo cáo cá nhân

---

## Quick Reference: Files Structure

```
Day-07-Lab-Data-Foundations/
├── src/
│   ├── chunking.py       ← Your implementation
│   ├── store.py          ← Your implementation
│   ├── agent.py          ← Your implementation
│   └── ...
├── report/
│   └── REPORT.md         ← Your report
├── data/                 ← Your documents
├── tests/                ← Run to verify
└── HOW_TO_COMPLETE.md    ← This file
```

## Tips Thành Công

1. **Implement từng phần nhỏ** - đừng cố làm cùng lúc
2. **Chạy tests liên tục** - sau mỗi function implement
3. **Hiểu rõ cosine similarity** - core concept của lab
4. **Thảo luận với nhóm** - về domain, queries, strategies
5. **Document your rationale** - giải thích tại sao chọn strategy này
6. **So sánh thật lòng** - strategy của ai tốt hơn? Tại sao?

## Resources

- `README.md` - Tổng quan lab
- `exercises.md` - Chi tiết exercises
- `docs/EVALUATION.md` - Metrics đánh giá
- `docs/SCORING.md` - Rubric chấm điểm
- `tests/test_solution.py` - Tests để verify

---

**Chúc bạn hoàn thành tốt! 🚀**
