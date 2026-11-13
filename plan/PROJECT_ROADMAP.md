# Lộ trình dự án — Khám phá dữ liệu đa doanh nghiệp (DataMate)

- **Motivation/Background**: Thiết lập kế hoạch thực hiện thống nhất cho đồ án nhóm môn Trực quan hóa dữ liệu, khám phá mẫu hình vận hành trên 44 doanh nghiệp Việt Nam không đồng nhất từ bộ dữ liệu Zalo AI Challenge 2026 — DataMate (`train` + `public_test`), đồng bộ với [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md) và [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md).
- **Purpose**: Thống nhất các cột mốc, giai đoạn, sản phẩm đầu ra, quy tắc tính chỉ số và cổng kiểm soát chất lượng biểu đồ trước khi triển khai mã phân tích và vẽ biểu đồ.
- **Overview Pipeline**: Dữ liệu hợp nhất (`data/merged/`) → Kiểm kê cấp độ bộ dữ liệu (44 doanh nghiệp) → Chọn tập đại diện & Làm sạch theo `rulebook.md`/Tidy Data → Phân tích mô tả từng doanh nghiệp & liên doanh nghiệp (*Khám phá → Giải thích*) → Bộ Notebook `.ipynb` & Slide thuyết trình tiếng Việt.
- **Detailed Plan**: §1 Tổng quan dự án; §2 Các cột mốc chính; §3 Các giai đoạn triển khai; §4 Phân rã tác vụ & Phụ thuộc; §5 Rủi ro & Biện pháp giảm thiểu; §6 Theo dõi trạng thái.
- **References**: [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md), [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md), [`data/merged/rulebook.md`](../data/merged/rulebook.md), [`data/merged/calendar.csv`](../data/merged/calendar.csv), [`data/merged/business_index.csv`](../data/merged/business_index.csv), [`agents/templates/PROJECT_ROADMAP_TEMPLATE.md`](../agents/templates/PROJECT_ROADMAP_TEMPLATE.md).
- **Created**: 2026-11-14T00:36:45+07:00
- **Last Updated**: 2026-11-14T02:39:10+07:00

---

## Tổng quan nhanh (At a Glance)

**Tiến độ: `0 / 4` giai đoạn hoàn thành** — Đã hợp nhất dữ liệu vào [`data/merged/`](../data/merged); đã chốt định nghĩa bài toán & nội dung môn học; sẵn sàng cho `T1.1a`.

```
█░░░░░░░░░░░░░░░   0/4 (đã xong T1.0)     █ = hoàn thành, ░ = còn lại
```

1. **Giai đoạn 1: Khám phá & Kiểm kê cấp độ bộ dữ liệu** — Đã xong hợp nhất (`T1.0` `[X]`); kiểm kê 44 doanh nghiệp (ngành nghề, hình thức ghi nhận, độ chi tiết, độ phủ thời gian, khoảng trống) & dựng biểu đồ Hồi 1 — `[~]`
2. **Giai đoạn 2: Chọn tập đại diện & Khám phá từng doanh nghiệp** — Chuẩn bị dữ liệu theo `rulebook.md`, Tidy Data & kiểm tra IQR; khám phá mẫu hình vận hành nội tại (Hồi 2) — `[ ]`
3. **Giai đoạn 3: Đặc trưng vận hành liên doanh nghiệp** — Đối chiếu các chiều tương thích theo tỉ lệ & khung thời gian chung, biến động dịp Tết (Hồi 3) — `[ ]`
4. **Giai đoạn 4: Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình** — Kiểm định biểu đồ theo chuẩn Cleveland–McGill & 5 hướng dẫn Schwabish, hoàn thiện `.ipynb` và slide tiếng Việt — `[ ]`

> Quy ước trạng thái: `[X]` hoàn thành · `[ ]` chưa bắt đầu · `[~]` đang thực hiện · `[!]` bị chặn

**Bước tiếp theo:** Thực hiện `T1.1a` (đọc và trích xuất thông tin từ toàn bộ 44 tệp `README.md` trong [`data/merged/`](../data/merged)).

---

## 1. Tổng quan dự án

| Hạng mục | Nội dung |
|---|---|
| **Tên dự án** | Khám phá dữ liệu đa doanh nghiệp — Multi-Business Data Discovery (DataMate) |
| **Đối tượng người xem** | Giảng viên môn Trực quan hóa dữ liệu (đánh giá tính trung thực, mã hóa thị giác, chọn biểu đồ, độ sạch dữ liệu và mạch kể chuyện) |
| **Nhóm & phạm vi** | Đồ án nhóm; phân tích mô tả, trực quan hóa và kể chuyện bằng dữ liệu (*Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*) |
| **Ngôn ngữ trình bày** | **Tiếng Việt** (notebook `.ipynb`, tiêu đề/nhãn/chú thích biểu đồ và slide thuyết trình) |
| **Sản phẩm chính** | Bộ Jupyter Notebook (`.ipynb`) + Slide thuyết trình |
| **Phạm vi dữ liệu** | [`data/merged/`](../data/merged) gộp `train` (`biz_101`–`biz_130`, 30) + `public_test` (`dev_001`–`dev_014`, 14) = **44 doanh nghiệp**; [`business_index.csv`](../data/merged/business_index.csv) lưu nguồn `source_split` |
| **Chuẩn chỉ số & lịch** | [`data/merged/rulebook.md`](../data/merged/rulebook.md) áp dụng thống nhất; [`data/merged/calendar.csv`](../data/merged/calendar.csv) để tra cứu âm lịch / kỳ Tết |
| **Phương pháp luận** | Quy trình 7 bước Chương 2 ([`SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md)): *Khám phá → Giải thích*, Tidy Data, kiểm tra thiếu dữ liệu & ngoại lệ IQR, chuẩn hóa tỉ lệ |
| **Công cụ kỹ thuật** | `Python`, `pandas`, `NumPy`, `matplotlib`, `seaborn` |
| **Ngoài phạm vi** | Mô hình ML/DL, dự báo, phân cụm, PCA/t-SNE/UMAP/Confusion Matrix/ROC/Feature Importance, Folium, Plotly, và **tuyệt đối không sử dụng `questions.jsonl` hay `answers.jsonl`** |

---

## 2. Các cột mốc chính (Key Milestones)

| Mã | Cột mốc | Sản phẩm kiểm chứng được (Definition of Done) | Giai đoạn |
|---|---|---|---|
| **M1** | **Danh mục 44 doanh nghiệp & Hồi 1** | Bảng kiểm kê đầy đủ + bộ biểu đồ tổng quan 44 doanh nghiệp (phân vùng, ngành nghề suy luận, hình thức ghi nhận, mức chi tiết, khoảng ngày, khoảng trống) | Giai đoạn 1 |
| **M2** | **Tập đại diện & Tầng tính chỉ số** | Danh sách doanh nghiệp đại diện kèm lý do chọn + bộ hàm Python chuẩn `rulebook.md`, Tidy Data, kiểm tra thiếu dữ liệu & IQR | Giai đoạn 2 |
| **M3** | **Phát hiện vi mô & đối chiếu (Hồi 2–3)** | Biểu đồ và nhận định đã kiểm chứng cho từng doanh nghiệp đại diện và các so sánh liên doanh nghiệp hợp lệ | Giai đoạn 2–3 |
| **M4** | **Sản phẩm nộp môn học** | Bộ `.ipynb` tiếng Việt chạy tái lập từ đầu đến cuối + ảnh biểu đồ nét cao (`context="talk"`, `dpi=300`) + slide thuyết trình đạt chuẩn Chương 2 §2.7 | Giai đoạn 4 |

---

## 3. Các giai đoạn triển khai

### Giai đoạn 1 — Khám phá & Kiểm kê cấp độ bộ dữ liệu (Hồi 1: *Bối cảnh*)
- **Mục tiêu:** Lập bản đồ toàn cảnh 44 doanh nghiệp trong [`data/merged/`](../data/merged) để phần Khám phá bộ dữ liệu trở thành Hồi 1 của câu chuyện và làm cơ sở chọn mẫu.
- **Đầu ra:**
  - `T1.0` `[X]`: Đã hợp nhất `train` + `public_test` vào [`data/merged/`](../data/merged) kèm [`business_index.csv`](../data/merged/business_index.csv), [`calendar.csv`](../data/merged/calendar.csv) và [`rulebook.md`](../data/merged/rulebook.md) (loại bỏ tệp QA).
  - Bảng kiểm kê thống nhất: `business_id`, `source_split`, `industry` suy luận, `recording_format`, `granularity` (đơn+dòng hàng, chỉ đơn, chỉ mặt hàng), số tệp, số dòng, `min_date`–`max_date`, ngày cutoff và khoảng trống dữ liệu.
  - Biểu đồ tổng quan Hồi 1 bằng `matplotlib`/`seaborn` (cơ cấu ngành nghề, mức độ số hóa, dòng thời gian độ phủ dữ liệu, phân bố quy mô dòng).

### Giai đoạn 2 — Chọn tập đại diện & Khám phá từng doanh nghiệp (Hồi 2: *Bằng chứng vi mô*)
- **Mục tiêu:** Chọn 1–2 doanh nghiệp đại diện cho mỗi nhóm ngành / mức độ số hóa và phân tích sâu mẫu hình vận hành theo đúng [`data/merged/rulebook.md`](../data/merged/rulebook.md) và vệ sinh dữ liệu Chương 2 §2.3.
- **Đầu ra:**
  - Bộ hàm Python dùng chung: đọc dữ liệu đa định dạng, tính chỉ số theo `rulebook.md` (loại đơn hủy/trả, quy theo ngày đặt, doanh thu dòng hàng, quy đổi đơn vị cơ bản, giải mã `Ghi tắt`), chuyển dạng Tidy Data, kiểm tra thiếu dữ liệu và ngoại lệ IQR.
  - Biểu đồ Hồi 2 cho từng doanh nghiệp: cơ cấu sản phẩm/nhóm hàng, phân phối giá trị đơn hàng, đặc trưng khách hàng/thanh toán/ca làm việc/lô hàng (nếu có).

### Giai đoạn 3 — Đặc trưng vận hành liên doanh nghiệp (Hồi 3: *Bằng chứng đối chiếu*)
- **Mục tiêu:** Chỉ so sánh các doanh nghiệp trên những chiều tương đồng về ngữ nghĩa, đơn vị và khung thời gian (chuẩn hóa về **tỉ lệ / phần trăm** theo Chương 2 §2.6 khi quy mô khác nhau).
- **Đầu ra:**
  - Ma trận khả năng so sánh (mức chi tiết dữ liệu, có giờ giao dịch hay không, khoảng thời gian hoạt động giao nhau).
  - Biểu đồ Hồi 3: nhịp hoạt động theo giờ/ca, ngày thường vs. cuối tuần, biến động dịp Tết / trước Tết qua [`calendar.csv`](../data/merged/calendar.csv), và đặc trưng giỏ hàng — kèm ghi chú giới hạn rõ ràng.

### Giai đoạn 4 — Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình (*Kết luận / Hành động*)
- **Mục tiêu:** Chuyển hóa kết quả khám phá thành bộ notebook và slide giải thích hoàn chỉnh bằng tiếng Việt cho giảng viên môn Trực quan hóa dữ liệu.
- **Đầu ra:**
  - Cổng kiểm định chất lượng biểu đồ (`T4.1a`) theo [`docs/DEFINE-THE-PROBLEM.md#L97-L115`](../docs/DEFINE-THE-PROBLEM.md#L97-L115):
    - Ưu tiên thang Cleveland–McGill; biểu đồ cột luôn bắt đầu từ 0; không dùng 3D hay hai trục y gây hiểu lầm.
    - 5 hướng dẫn Schwabish: *Cho thấy dữ liệu*, *Giảm nhiễu* (`despine`), *Gắn chữ với hình* (tiêu đề chủ động + nhãn trực tiếp + chú thích), *Small multiples* thay spaghetti, *Bắt đầu từ màu xám*.
    - Xuất ảnh cho slide (`sns.set_context("talk")`, `dpi=300`, `bbox_inches="tight"`).
  - Bộ `.ipynb` tiếng Việt hoàn chỉnh + Slide thuyết trình theo mạch *Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*.

---

## 4. Phân rã tác vụ & Phụ thuộc

### Giai đoạn 1 — Khám phá & Kiểm kê cấp độ bộ dữ liệu (Hồi 1)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T1.0` | Hợp nhất `train` & `public_test` vào `data/merged/` kèm `business_index.csv` | `[X]` | — | [`data/merged/`](../data/merged) |
| `T1.1a` | Đọc toàn bộ 44 tệp `README.md` (trích xuất hình thức ghi nhận, ngày cutoff, quy ước đơn vị/ghi tắt, mô tả bảng) | `[ ]` | `T1.0` | Bảng tổng hợp metadata từ `README` |
| `T1.1b` | Quét toàn bộ tệp `.csv`, `.xlsx` (mọi sheet) và `.sqlite` của 44 doanh nghiệp để lấy tên bảng/sheet, cột và số dòng | `[ ]` | `T1.0` | Bảng cấu trúc tệp & số dòng |
| `T1.1c` | Trích xuất `min_date`, `max_date`, số ngày/tháng có dữ liệu và khoảng trống thời gian của từng doanh nghiệp | `[ ]` | `T1.1b` | Bảng độ phủ & khoảng trống ngày |
| `T1.2a` | Suy luận và kiểm chứng `industry` (ngành nghề) cho 44 doanh nghiệp từ `README.md` + mẫu tên hàng/giao dịch | `[ ]` | `T1.1a`, `T1.1b` | Nhãn ngành nghề đã kiểm chứng |
| `T1.2b` | Gắn nhãn mức độ chi tiết & khả năng so sánh (đơn+hàng vs. chỉ đơn vs. chỉ hàng; giờ, mã khách, giá vốn) | `[ ]` | `T1.1b` | Danh mục 44 doanh nghiệp hoàn chỉnh |
| `T1.3a` | Xây dựng notebook Khám phá Hồi 1 (bảng tổng hợp + biểu đồ nháp về cơ cấu, mức số hóa, quy mô, độ phủ) | `[ ]` | `T1.1c`, `T1.2a`, `T1.2b` | `.ipynb` khám phá Hồi 1 |
| `T1.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 1 (cơ cấu ngành, mức độ số hóa, dòng thời gian độ phủ 2025–2026) | `[ ]` | `T1.3a` | Bộ biểu đồ Hồi 1 |

### Giai đoạn 2 — Chọn tập đại diện & Khám phá từng doanh nghiệp (Hồi 2)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T2.1` | Chọn tập doanh nghiệp đại diện (1–2 doanh nghiệp mỗi ngành & mức số hóa) và ghi rõ tiêu chí chọn | `[ ]` | `T1.2a`, `T1.2b`, `T1.1c` | Danh sách tập đại diện |
| `T2.2a` | Viết module đọc dữ liệu & tính chỉ số chuẩn `rulebook.md` (loại đơn hủy/trả, tính theo ngày đặt, doanh thu dòng) | `[ ]` | `T2.1` | Module Python chuẩn `rulebook` |
| `T2.2b` | Chuẩn hóa đặc thù theo doanh nghiệp (quy đổi đơn vị cơ bản, giải mã `Ghi tắt`, chuyển dạng Tidy Data) | `[ ]` | `T2.2a` | Bảng dữ liệu sạch dạng Tidy |
| `T2.2c` | Kiểm tra chất lượng dữ liệu tập đại diện (thống kê/heatmap giá trị thiếu, trùng lặp, kiểm tra ngoại lệ IQR với nguồn) | `[ ]` | `T2.2b` | Báo cáo chất lượng dữ liệu tập mẫu |
| `T2.3a` | Phân tích Khám phá nội tại từng doanh nghiệp được chọn (nhóm hàng chủ lực, phân phối đơn, khách hàng/ca/lô) | `[ ]` | `T2.2c` | `.ipynb` khám phá Hồi 2 |
| `T2.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 2 (1–2 phát hiện trọng tâm mỗi doanh nghiệp, tiêu đề chủ động, nhãn trực tiếp) | `[ ]` | `T2.3a` | Bộ biểu đồ Hồi 2 |

### Giai đoạn 3 — Đặc trưng vận hành liên doanh nghiệp (Hồi 3)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T3.1a` | Lập ma trận khả năng so sánh (chung mức chi tiết, có mốc giờ, khung thời gian hoạt động giao nhau) | `[ ]` | `T1.2b`, `T2.2c` | Ma trận khả năng so sánh |
| `T3.1b` | Tính các chỉ số chuẩn hóa theo tỉ lệ/phần trăm (tỉ trọng %, chỉ số chuẩn hóa, trung bình theo ngày hoạt động) | `[ ]` | `T3.1a` | Bảng đối chiếu đã chuẩn hóa |
| `T3.2a` | Phân tích & vẽ nhịp vận hành theo giờ / ca / ngày thường–cuối tuần giữa các ngành (dạng small multiples) | `[ ]` | `T3.1b` | Biểu đồ nhịp vận hành liên ngành |
| `T3.2b` | Phân tích & vẽ biến động dịp Tết / trước Tết qua `calendar.csv` (chỉ cho doanh nghiệp đủ độ phủ) | `[ ]` | `T3.1b` | Biểu đồ dịp Tết & lịch |
| `T3.2c` | Tổng hợp giới hạn đối chiếu, lưu ý về độ phủ và các trường hợp không thể so sánh trực tiếp | `[ ]` | `T3.2a`, `T3.2b` | Ghi chú giới hạn Hồi 3 |

### Giai đoạn 4 — Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T4.1a` | Kiểm định toàn bộ biểu đồ Hồi 1–3 theo chuẩn Cleveland–McGill & 5 hướng dẫn Schwabish | `[ ]` | `T1.3b`, `T2.3b`, `T3.2c` | Danh sách kiểm định biểu đồ |
| `T4.1b` | Xuất bộ ảnh tĩnh cho slide (`sns.set_context("talk")`, `dpi=300`, `bbox_inches="tight"`) | `[ ]` | `T4.1a` | Bộ ảnh PNG độ phân giải cao |
| `T4.1c` | Hoàn thiện bộ Jupyter Notebook (`.ipynb`) tiếng Việt (mạch văn rõ ràng, chạy tái lập từ đầu đến cuối) | `[ ]` | `T4.1a` | Bộ `.ipynb` hoàn chỉnh |
| `T4.2a` | Lập dàn ý slide thuyết trình tiếng Việt (*Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*) | `[ ]` | `T4.1a` | Khung nội dung slide |
| `T4.2b` | Hoàn thiện slide thuyết trình, chèn ảnh `dpi=300`, bổ sung ghi chú thuyết trình & chú thích giới hạn | `[ ]` | `T4.1b`, `T4.2a` | Slide thuyết trình hoàn chỉnh |

---

## 5. Rủi ro & Biện pháp giảm thiểu

| Rủi ro | Tác động | Biện pháp giảm thiểu |
|---|---|---|
| **So sánh các chỉ số khác bản chất** (ví dụ: tệp chỉ có mặt hàng không có `Mã đơn` vs. tệp có đơn hàng) | Biểu đồ đối chiếu sai lệch | Bắt buộc phân tầng khả năng so sánh (`T1.2b`, `T3.1a`) và chuẩn hóa tỉ lệ (Chương 2 §2.6) trước khi vẽ |
| **Ngày kết thúc dữ liệu khác nhau** (tháng 05–09/2026) & dữ liệu bị đứt quãng | Sai lệch xu hướng tháng hoặc ngộ nhận mùa vụ | Vẽ dòng thời gian độ phủ ngay ở Hồi 1 (`T1.3b`); chỉ đối chiếu theo cửa sổ thời gian giao nhau và loại tháng cuối thiếu ngày |
| **Hiểu sai quy tắc `rulebook.md`** (tính nhầm đơn hủy/trả, quên quy đổi đơn vị, mã `Ghi tắt`) | Số liệu tính toán sai | Tập trung hóa logic `rulebook.md` trong module `T2.2a`–`T2.2b` và đối chiếu ngoại lệ IQR với dữ liệu gốc |
| **Biểu đồ rối hoặc gây hiểu lầm** (spaghetti nhiều đường, cột cắt trục, quá nhiều màu/chú giải) | Giảm điểm đánh giá của giảng viên | Áp dụng cổng kiểm định `T4.1a` (5 hướng dẫn Schwabish + trục cột từ 0 + `context="talk"`) |
| **Trượt phạm vi sang ML/DL hoặc thư viện ngoài phạm vi** | Loãng câu chuyện, tốn thời gian | Giữ chặt phạm vi: không ML/DL, không Folium/Plotly, không dùng tệp QA theo [`DEFINE-THE-PROBLEM.md#L130-L143`](../docs/DEFINE-THE-PROBLEM.md#L130-L143) |

---

## 6. Theo dõi trạng thái

- **Trạng thái hiện tại:** `[STATUS: ACTIVE]` — Đã đồng bộ với [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md) và [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md); đã hoàn thành `T1.0`.
- **Quy tắc cập nhật:** Cập nhật thanh tiến độ, bảng tác vụ và mốc `Last Updated` mỗi khi hoàn thành một cột mốc hoặc tác vụ.
