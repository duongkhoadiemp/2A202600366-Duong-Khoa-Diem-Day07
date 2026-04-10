import os
from pathlib import Path
from src.models import Document
from src.store import EmbeddingStore
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker
from src.embeddings import _mock_embed

# ============= 1. TỰ ĐỘNG LOAD DATA =============
def load_docs():
    data_dir = Path("./data")
    # Lấy tất cả file .md trong thư mục data
    files = list(data_dir.glob("*.md"))
    docs = []
    for f in files:
        if f.name == "chunking_experiment_report.md": continue
        content = f.read_text(encoding="utf-8")
        docs.append(Document(id=f.stem, content=content, metadata={"source": f.name}))
    return docs

# ============= 2. BỘ CÂU HỎI KIỂM THỬ =============
QUERIES = [
    "Tôi gặp tai nạn trong chuyến xe thì phải làm gì?",
    "Thông tin tài xế không giống trên app thì xử lý thế nào?",
    "Làm sao để đặt xe trên ứng dụng XanhSM?",
    "Tôi để quên đồ trên xe thì phải làm sao?",
    "Tài xế yêu cầu đi ngoài app có nên không?"
]

# ============= 3. CHẠY SO SÁNH =============
def run():
    docs = load_docs()
    if not docs:
        print("❌ Không tìm thấy file .md nào trong thư mục data!")
        return

    strategies = {
        "Fixed-Size": FixedSizeChunker(chunk_size=400, overlap=50),
        "Sentence": SentenceChunker(max_sentences_per_chunk=3),
        "Recursive": RecursiveChunker(chunk_size=400)
    }

    print(f"✅ Đã tải {len(docs)} tài liệu từ folder data.\n")
    print(f"{'Query':<35} | {'Fixed':<8} | {'Sentence':<8} | {'Recursive':<8}")
    print("-" * 75)

    # Lưu kết quả để so sánh điểm số
    for q in QUERIES:
        scores = []
        for name, chunker in strategies.items():
            store = EmbeddingStore(embedding_fn=_mock_embed)
            for d in docs:
                chunks = chunker.chunk(d.content)
                chunk_docs = [Document(id=f"{d.id}_{i}", content=c, metadata=d.metadata) for i, c in enumerate(chunks)]
                store.add_documents(chunk_docs)
            
            res = store.search(q, top_k=1)
            scores.append(f"{res[0]['score']:.3f}" if res else "0.000")
        
        print(f"{q[:35]:<35} | {scores[0]:<8} | {scores[1]:<8} | {scores[2]:<8}")

if __name__ == "__main__":
    run()