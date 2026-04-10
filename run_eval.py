from src.chunking import compute_similarity, ChunkingStrategyComparator
import math

def eval_logic():
    print("--- 📏 TEST SIMILARITY (Mục 5 Report) ---")
    # Cặp 1: Giống nhau
    v1, v2 = [1, 0.5, 0], [1, 0.4, 0.1]
    print(f"Similarity (Giống): {compute_similarity(v1, v2):.4f}")
    
    # Cặp 2: Khác nhau hoàn toàn
    v3, v4 = [1, 0, 0], [0, 1, 0]
    print(f"Similarity (Khác): {compute_similarity(v3, v4):.4f}")

    print("\n--- 📊 TEST CHUNKING STATS (Mục 3 Report) ---")
    text = "Xanh SM là ứng dụng đặt xe điện đầu tiên tại Việt Nam. " * 50
    comp = ChunkingStrategyComparator()
    stats = comp.compare(text, chunk_size=200)
    
    for s, data in stats.items():
        print(f"{s}: {data['count']} chunks, Avg len: {data['avg_length']:.1f}")

if __name__ == "__main__":
    eval_logic()