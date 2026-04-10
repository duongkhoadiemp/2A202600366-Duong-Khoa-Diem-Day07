# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Dương Khoa Điềm
**Nhóm:** [X1]
**Ngày:** 10/04/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)

**High cosine similarity nghĩa là gì?**

Nó biểu thị rằng hai vector có hướng rất gần nhau hoặc trùng nhau trong không gian, đồng nghĩa với việc hai văn bản mà chúng đại diện có nội dung hoặc ý nghĩa tương đồng nhau cao.

**Ví dụ HIGH similarity:**
- Sentence A: Trí tuệ nhân tạo đang làm thay đổi thế giới.
- Sentence B: AI đang cách mạng hóa toàn bộ ngành công nghiệp toàn cầu.
- Tại sao tương đồng: Cả hai câu đều mang cùng một ý nghĩa cốt lõi về tác động tích cực và to lớn của sự phát triển trí tuệ nhân tạo.

**Ví dụ LOW similarity:**
- Sentence A: Trí tuệ nhân tạo đang làm thay đổi thế giới.
- Sentence B: Công thức nấu phở truyền thống cần có hồi và quế.
- Tại sao khác: Hai câu thuộc hai lĩnh vực hoàn toàn khác nhau (công nghệ và ẩm thực), không có điểm chung nào về ngữ nghĩa.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

 Vì cosine similarity chỉ đo lường góc (hướng) giữa các vector mà không bị ảnh hưởng bởi độ dài (độ lớn) của chúng. Điều này giúp tính toán sự tương đồng ngữ nghĩa một cách chính xác ngay cả khi hai văn bản được so sánh có độ dài khác biệt nhau rất lớn.

### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap)) = ceil((10000 - 50) / (500 - 50)) = ceil(9950 / 450)
> *Đáp án:* 23 chunks

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

 Khi overlap tăng lên 100, số lượng chunk tăng lên thành: ceil((10000 - 100) / (500 - 100)) = ceil(9900 / 400) = 25 chunks. Ta muốn có overlap lớn hơn để đảm bảo các đoạn văn không bị cắt vỡ ngữ cảnh và mất mát thông tin tại khoảng giao giữa hai chunks liền nhau, hỗ trợ Retrieval lấy đúng và đủ thông tin hơn.

---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** Xanh SM FAQ (user + driver + merchant/restaurant).

**Tại sao nhóm chọn domain này?**

 Bộ FAQ có nhiều nhóm đối tượng và nhiều quy trình nghiệp vụ, rất phù hợp để kiểm tra retrieval precision, metadata filtering và grounding.

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | XanhSM - User FAQs.md | Internal dataset | 50196 | category=user, language=vi, source |
| 2 | XanhSM - electric_motor_driver FAQs.md | Internal dataset | 11662 | category=bike_driver, language=vi, source |
| 3 | XanhSM - electric_car_driver FAQs.md | Internal dataset | 3583 | category=car_driver, language=vi, source |
| 4 | XanhSM - Restaurant FAQs.md | Internal dataset | 25352 | category=restaurant, language=vi, source |
| 5 | XanhSM - FAQs.md | Internal dataset | 50196 | category=user_general, language=vi, source |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| doc_id | string | XanhSM - User FAQs | Hỗ trợ tìm kiếm hoặc delete theo tài liệu gốc |
| category | string | user / bike_driver | Hỗ trợ pre-filter theo domain đối tượng để tránh nhầm lẫn nội dung |
| language | string | vi | Tránh mix kết quả của các ngôn ngữ khác |
| source | string | data/XanhSM - User FAQs.md | Truy vết nguồn chunk và đối chiếu |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| XanhSM - User FAQs.md | FixedSizeChunker (`fixed_size`) | 258 | 194.5 | Thường cắt ngang câu. |
| XanhSM - User FAQs.md | SentenceChunker (`by_sentences`) | 312 | 160.8 | Giữ được câu, nhưng đôi khi quá ngắn. |
| XanhSM - User FAQs.md | RecursiveChunker (`recursive`) | 225 | 223.0 | Giữ vẹn toàn đoạn gốc hỏi đáp nhất. |

### Strategy Của Tôi

**Loại:** RecursiveChunker

**Mô tả cách hoạt động:**

 strategy chunk thế nào? Dựa trên dấu hiệu gì?* Thuật toán sẽ chặt đoạn văn bản lớn dần xuống, ưu tiên theo thứ tự `\n\n` cho đoạn văn, `. ` cho câu và khoảng trắng cho chữ. Trong dạng tài liệu FAQ này, cấu trúc Câu Hỏi - Trả Lời thường tách biệt nhau bởi dấu xuống dòng đôi `\n\n`. Thuật toán sẽ ưu tiên cắt được chính xác cụm trọn vẹn Hỏi - Đáp.

**Tại sao tôi chọn strategy này cho domain nhóm?**

 domain có pattern gì mà strategy khai thác?* Domain Xanh SM FAQ luôn được viết theo khuôn mẫu: [Câu hỏi] \n [Trả lời dông dài]. Việc cắt theo RecursiveChunker sẽ giúp Chunk bao bọc vừa đủ cả câu hỏi lẫn câu trả lời mà không phá vỡ tính logic của đoạn.

**Code snippet (nếu custom):**
```python
# Mặc định sử dụng class RecursiveChunker trong src/chunking.py với priority:
# DEFAULT_SEPARATORS = ["\n\n", ". ", " ", ""]
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| XanhSM - User FAQs | Baseline: FixedSizeChunker | 108 | 398.3 | Kém. Tìm kiếm từ khoá rời rạc, cắt gãy đôi câu trả lời. |
| XanhSM - User FAQs | Baseline: SentenceChunker | 132 | 281.4 | Tạm ổn. Các câu không bị đứt đoạn nhưng nội dung bị vụn. |
| XanhSM - User FAQs | **Của tôi: RecursiveChunker** | 169 | 221.3 | Rất xuất sắc. Cụm Hỏi-Đáp không bị tách rời giữa chừng, giữ Grounding tốt. |

*Phân tích thêm:* Việc chia theo `RecursiveChunker` cho chất lượng vượt trội so với các đoạn chia bị gãy vụn của Fixed hoặc Sentence Baseline. Quy trình chia cắt Đệ quy ưu tiên (Đoạn -> Câu -> Từ) cực kỳ lợi hại với các văn bản dài nhưng cấu trúc chuẩn FAQ như `XanhM - User FAQs`.

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| **Dương Khoa Điềm (Tôi)** | RecursiveChunker (~400 chars) | 7.9 | Giữ được ngữ cảnh cụm Q&A tương đối ổn. | Tuỳ biến sai sót separator khiến một số câu dài bị đứt vụn, điểm chưa cao. |
| Tuyền | Recursive (350 chars) | 8.77 | Giữ context, Q&A coherent, score cao | Số chunk nhiều (654), tốn memory |
| Thế Anh | Recursive (250 chars) | 8.752 | Giữ context, Q&A coherent, score cao | Số chunk nhiều, tốn memory |
| Võ Thanh Chung | RecursiveChunker (250 chars) | 8.0 | Giữ cấu trúc tự nhiên, chunk đều | Có thể cắt ngang câu dài |
| Nguyễn Hồ Bảo Thiên | FixedSizeChunker (chunk_size=100, overlap=20) | 8.56 | Xử lý nhanh | Dễ ngắt câu giữa chừng, gây mất ngữ nghĩa |

**Strategy nào tốt nhất cho domain này? Tại sao?**

`RecursiveChunker` là phù hợp nhất do tài liệu định rập khuôn theo Hỏi-Đáp. Tận dụng khoảng cách xuống dòng đem lại Retrieval Context xuất sắc mà các trình cơ bản không có phần hỗ trợ.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:

dùng regex gì để detect sentence? Xử lý edge case nào?* Tôi dùng biểu thức chính quy `re.split(r'[.!?]+', text)` để tách các câu dựa trên các dấu câu đặc biệt. Cách này hiệu quả hơn việc tìm kiếm khoảng trắng đơn thuần và loại bỏ các string rỗng được sinh ra khi các dấu câu đi liền nhau nhờ lệnh `strip()`.

**`RecursiveChunker.chunk` / `_split`** — approach:

 algorithm hoạt động thế nào? Base case là gì?* Chức năng này tạo vòng đệ quy để cắt list priority: `["\n\n", ". ", " ", ""]`. Thuật toán sẽ đệ quy mảng separator từ trái sang phải nếu nó tìm thấy kích cỡ chunk chưa thỏa. Base case là khi length `<= chunk_size` hoặc khi separator chỉ còn `""` (lúc này nó bị rã ra từng ký tự bằng slicing cơ bản).

### EmbeddingStore

**`add_documents` + `search`** — approach:

 lưu trữ thế nào? Tính similarity ra sao?* Do không dùng tính năng của Vector Database nên dữ liệu được dán trực tiếp trong RAM (in-memory) bằng list thuộc tính `self.data`. Kết quả search được sinh ra dựa theo Brute Force Dot Product: Tạo query vector và match chéo với tất cả tài liệu, sau đó được sort theo similarity score từ mạnh đến yếu.

**`search_with_filter` + `delete_document`** — approach:

 filter trước hay sau? Delete bằng cách nào?* Cả hai đều filter ở bước đầu tiên, `search_with_filter` thu hẹp tập subset thoả mãn metadata dictionary match toàn phần trước bằng list comprehension sau đó mới chạy Similarity check. Trong khi đó `delete_document` thay thế mảng mới trên data cũ nếu `doc.id` không khớp với file đang chọn xóa.

### KnowledgeBaseAgent

**`answer`** — approach:

 prompt structure? Cách inject context?* Gọi `self.store.search` rồi inject array dictionary theo format `Context:\n[chunk 1]\n[chunk 2]\n\nQuestion: [query]...`. Mô hình LLM sẽ được mồi Context để thực hiện format Prompt mà không được quyền suy diễn ngoài nội dung.

### Test Results

```
============================================ short test summary info ============================================= 
========================================== 42 passed in 0.23s ========================================== 
```

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Màn hình điện thoại bị vỡ có được bảo hành? | Điện thoại bị nứt kính xin hỏi cách sửa? | high | 0.86 | Yes |
| 2 | Xe máy điện Xanh SM có màu gì? | Bầu trời hôm nay thật quang đãng. | low | 0.12 | Yes |
| 3 | Giá cước đi Xanh SM là bao nhiêu? | Chi phí đi taxi điện được tính thế nào? | high | 0.89 | Yes |
| 4 | Có thể thanh toán bằng thẻ tín dụng không? | Tôi thích mua sắm bằng thẻ Visa. | low | 0.35 | Yes |
| 5 | Làm sao để đăng ký làm tài xế? | Hướng dẫn thủ tục gia nhập đối tác tài xế. | high | 0.91 | Yes |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**

Kết quả cặp số 4 gây bất ngờ nhất vì dù cùng có keyword về "thẻ", "thanh toán", và "tín dụng/Visa", điểm tương đồng vẫn rơi vào mức low. Điều này cho thấy Embeddings biểu diễn nghĩa vượt ra khỏi từ khóa (keyword) và có khả năng nắm bắt được hoàn cảnh sử dụng (đi xe và mua sắm) khác nhau nên đưa ra sự phân tách rõ ràng.

---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 | Tôi gặp tai nạn trong chuyến xe thì phải làm gì? | Gọi kiểm tra ngay CSGT tại hiện trường và liên hệ tổng đài Xanh SM 1900 2088 để được hỗ trợ và khai báo bảo hiểm. |
| 2 | Thông tin tài xế không giống trên app thì sao? | Tuyệt đối không lên xe, hãy bấm Huỷ chuyến và chọn lý do Tài xế/xe không trùng khớp để báo cho Xanh SM xử lý. |
| 3 | Làm sao để đặt xe trên ứng dụng XanhSM? | Mở ứng dụng, nhập điểm đến, chọn phương tiện phù hợp (xe máy/ô tô điện), kiểm tra giá cước và bấm Đặt xe. |
| 4 | Tôi để quên đồ trên xe thì làm sao? | Truy cập Lịch sử chuyến đi, chọn Trợ giúp và gọi cho trung tâm CSKH hoặc tài xế trong tối đa 48h để tìm lại đồ. |
| 5 | Tài xế yêu cầu đi ngoài app có nên không? | Tuyệt đối từ chối để được đảm bảo quyền lợi bảo hiểm và an toàn suốt hành trình theo quy định của nền tảng. |

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | Tôi gặp tai nạn trong chuyến xe thì phải làm gì? | (Mock chunk) Hướng dẫn giải quyết sự cố tai nạn | 0.313 | Yes | Liên hệ tổng đài CSKH bảo hiểm chuyến đi ngay lập tức. |
| 2 | Thông tin tài xế không giống trên app thì sao? | (Mock chunk) Quy định xác minh biển số xe | 0.370 | Yes | Không nên lên xe, hãy huỷ chuyến báo cáo lên Xanh SM. |
| 3 | Làm sao để đặt xe trên ứng dụng XanhSM? | (Mock chunk) Cách thức gọi xe ứng dụng | 0.321 | Yes | Tải app, nhập điểm đến và bấm gọi. |
| 4 | Tôi để quên đồ trên xe thì làm sao? | (Mock chunk) Xử lý thất lạc tài sản trên xe | 0.429 | Yes | Vào Trip History và lấy thông tin liên lạc tài xế để gọi. |
| 5 | Tài xế yêu cầu đi ngoài app có nên không? | (Mock chunk) Khuyến cáo không đi ngoài ứng dụng | 0.319 | Yes | Xanh SM cấm mọi hành vi đi ngoài ứng dụng. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**

 Tôi học được từ cách triển khai của Tuyền và Thế Anh về việc giới hạn kích thước chunk xuống mức thấp hơn (250 - 350 chars) cho `RecursiveChunker`. Cách đánh đổi này tuy tốn kém bộ nhớ hơn nhưng đã giải quyết dứt điểm rủi ro loãng Context so với việc giữ chunk khổng lồ như cách tôi từng làm.

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**

Kinh nghiệm sử dụng RegEx đặc trị cho từng đoạn biểu thức lặp lại thay vì dùng ký tự Space cơ bản. Nó là một chiến thuật trích xuất văn bản cực kỳ hiệu quả mà các document phức tạp nên áp dụng.

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**

Tôi sẽ tách riêng tính năng Câu hỏi gắn vào Metadata Query và phần Trả lời thu dọn lại thành Content. Việc đó sẽ thu gọn Embeddings và tập trung bắt dính trực tiếp các truy vấn từ người dùng với hiệu suất cao hơn.

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | 5 / 5 |
| Document selection | Nhóm | 8 / 10 |
| Chunking strategy | Nhóm | 12 / 15 |
| My approach | Cá nhân | 8 / 10 |
| Similarity predictions | Cá nhân | 4 / 5 |
| Results | Cá nhân | 8 / 10 |
| Core implementation (tests) | Cá nhân | 30 / 30 |
| Demo | Nhóm | 4 / 5 |
| **Tổng** | | **79 / 100** |
