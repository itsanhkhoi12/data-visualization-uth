# Lộ trình dự án — Khám phá dữ liệu đa doanh nghiệp (DataMate — `public_test`)

- **Motivation/Background**: Thiết lập kế hoạch thực hiện thống nhất cho đồ án nhóm môn Trực quan hóa dữ liệu, khám phá mẫu hình vận hành trên **14 doanh nghiệp** Việt Nam không đồng nhất từ tập `public_test` (`dev_001`–`dev_014`) của bộ dữ liệu Zalo AI Challenge 2026 — DataMate, đồng bộ với [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md) và [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md).
- **Purpose**: Thống nhất các cột mốc, giai đoạn, sản phẩm đầu ra, quy tắc tính chỉ số và cổng kiểm soát chất lượng biểu đồ trước khi triển khai mã phân tích và vẽ biểu đồ.
- **Overview Pipeline**: Dữ liệu chỉ đọc (`data/public_test/` hoặc `raw_data/public_test/`) → Kiểm kê cấp độ bộ dữ liệu (14 doanh nghiệp) → Chọn tập đại diện & Làm sạch theo `rulebook.md`/Tidy Data → Phân tích mô tả từng doanh nghiệp & liên doanh nghiệp (*Khám phá → Giải thích*) → Bộ Notebook `.ipynb` & Slide thuyết trình tiếng Việt.
- **Detailed Plan**: §1 Tổng quan dự án; §2 Các cột mốc chính; §3 Các giai đoạn triển khai; §4 Phân rã tác vụ & Phụ thuộc; §5 Rủi ro & Biện pháp giảm thiểu; §6 Theo dõi trạng thái.
- **References**: [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md), [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md), [`data/public_test/rulebook.md`](../data/public_test/rulebook.md), [`data/public_test/calendar.csv`](../data/public_test/calendar.csv), [`.agents/templates/PROJECT_ROADMAP_TEMPLATE.md`](../.agents/templates/PROJECT_ROADMAP_TEMPLATE.md).
- **Created**: 2026-11-14T00:36:45+07:00
- **Last Updated**: 2026-11-18T00:15:00+07:00

---

## Tổng quan nhanh (At a Glance)

**Tiến độ: `3 / 4` giai đoạn hoàn thành** — Giai đoạn 1 (`T1.0`–`T1.3b`), Giai đoạn 2 (`T2.1`–`T2.3b`) và Giai đoạn 3 (`T3.1a`–`T3.2c`) đã hoàn thành và **đã chạy lại từ đầu (`jupyter nbconvert --execute`) với 0 lỗi** cho cả ba notebook. Giai đoạn 4: `T4.1a`–`T4.1c` đã hoàn thành — **24 ứng viên xuất bản đạt 10/10 tiêu chí kiểm định thị giác (0 ô `CẦN KIỂM TRA`)**, bộ ảnh 300 DPI thật đã xuất, và **cả `C9` lẫn `C10` đều `ĐẠT`**. Còn nợ: `T4.2a`–`T4.2b` (dàn ý & slide thuyết trình).

```
███████████████░   3/4 (75%)     █ = hoàn thành, ░ = còn lại
```

1. **Giai đoạn 1: Khám phá & Kiểm kê cấp độ bộ dữ liệu** — Chuẩn hóa cấu hình đọc `data/public_test/` hoặc `raw_data/public_test/`, kiểm kê 14 doanh nghiệp (`dev_001`–`dev_014`) & dựng biểu đồ Hồi 1 — `[X]`
2. **Giai đoạn 2: Chọn tập đại diện & Khám phá từng doanh nghiệp** — Chuẩn bị dữ liệu theo `rulebook.md`, Tidy Data & kiểm tra IQR; khám phá mẫu hình vận hành nội tại (Hồi 2) — `[X]`
3. **Giai đoạn 3: Đặc trưng vận hành liên doanh nghiệp** — Đối chiếu các chiều tương thích theo tỉ lệ & khung thời gian chung, biến động dịp Tết (Hồi 3) — `[X]`
4. **Giai đoạn 4: Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình** — Kiểm định biểu đồ theo chuẩn Cleveland–McGill & 5 hướng dẫn Schwabish, hoàn thiện `.ipynb` và slide tiếng Việt — `[~]`

> Quy ước trạng thái: `[X]` hoàn thành · `[ ]` chưa bắt đầu · `[~]` đang thực hiện · `[!]` bị chặn  
> **Lưu ý baseline:** Tiến độ Hồi 1 được ghi nhận hoàn thành dựa trên [`notebook/01_dataset_discovery.ipynb`](../notebook/01_dataset_discovery.ipynb) (PR `#5`). Giai đoạn 2–3 bàn giao qua PR `#6` (NB02) và PR `#7` (NB03).

**Bước tiếp theo:** Triển khai `T4.2b` (dựng slide thuyết trình tiếng Việt) trong [`notebook/04_visualization_and_storytelling.ipynb`](../notebook/04_visualization_and_storytelling.ipynb), dùng bộ 24 ảnh 300 DPI đã kiểm định tại `figures_300dpi/`. **Kịch bản trình bày đã soạn sẵn** tại [`docs/PRESENTATION_SCRIPT.md`](PRESENTATION_SCRIPT.md) — 14 slide, mỗi slide có thông điệp chủ động, số liệu đã đối chiếu với artifact, công thức + cách tính cho mọi chỉ số suy ra, và gợi ý biểu đồ.

---

## 1. Tổng quan dự án

| Hạng mục | Nội dung |
|---|---|
| **Tên dự án** | Khám phá dữ liệu đa doanh nghiệp — Multi-Business Data Discovery (DataMate `public_test`) |
| **Đối tượng người xem** | Giảng viên môn Trực quan hóa dữ liệu (đánh giá tính trung thực, mã hóa thị giác, chọn biểu đồ, độ sạch dữ liệu và mạch kể chuyện) |
| **Nhóm & phạm vi** | Đồ án nhóm; phân tích mô tả, trực quan hóa và kể chuyện bằng dữ liệu (*Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*) |
| **Ngôn ngữ trình bày** | **Tiếng Việt** (notebook `.ipynb`, tiêu đề/nhãn/chú thích biểu đồ và slide thuyết trình) |
| **Sản phẩm chính** | Bộ Jupyter Notebook (`.ipynb`) + Slide thuyết trình |
| **Phạm vi dữ liệu** | Chỉ đọc từ [`data/public_test/`](../data/public_test) (hoặc `raw_data/public_test/`) gồm **14 doanh nghiệp** (`dev_001`–`dev_014`); **không sử dụng `train`** |
| **Chuẩn chỉ số & lịch** | [`data/public_test/rulebook.md`](../data/public_test/rulebook.md) áp dụng thống nhất; [`data/public_test/calendar.csv`](../data/public_test/calendar.csv) để tra cứu âm lịch / kỳ Tết |
| **Phương pháp luận** | Quy trình 7 bước Chương 2 ([`SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md)): *Khám phá → Giải thích*, Tidy Data, kiểm tra thiếu dữ liệu & ngoại lệ IQR, chuẩn hóa tỉ lệ |
| **Công cụ kỹ thuật** | `Python`, `pandas`, `NumPy`, `matplotlib`, `seaborn` |
| **Ngoài phạm vi** | Tập **`train`**, mô hình ML/DL, dự báo, phân cụm, PCA/t-SNE/UMAP/Confusion Matrix/ROC/Feature Importance, Folium, Plotly, và **tuyệt đối không sử dụng `questions.jsonl`** |

---

## 2. Các cột mốc chính (Key Milestones)

| Mã | Cột mốc | Sản phẩm kiểm chứng được (Definition of Done) | Giai đoạn |
|---|---|---|---|
| **M1** | **Danh mục 14 doanh nghiệp & Hồi 1** | Bảng kiểm kê đầy đủ + bộ biểu đồ tổng quan 14 doanh nghiệp `public_test` (ngành nghề suy luận, hình thức ghi nhận, mức chi tiết, khoảng ngày, khoảng trống) — **ĐẠT** | Giai đoạn 1 |
| **M2** | **Tập đại diện & Tầng tính chỉ số** | Danh sách doanh nghiệp đại diện kèm lý do chọn + bộ hàm Python chuẩn `rulebook.md`, Tidy Data, kiểm tra thiếu dữ liệu & IQR — **ĐẠT** | Giai đoạn 2 |
| **M3** | **Phát hiện vi mô & đối chiếu (Hồi 2–3)** | Biểu đồ và nhận định đã kiểm chứng cho từng doanh nghiệp đại diện và các so sánh liên doanh nghiệp hợp lệ — **ĐẠT** | Giai đoạn 2–3 |
| **M4** | **Sản phẩm nộp môn học** | Bộ `.ipynb` tiếng Việt chạy tái lập từ đầu đến cuối + ảnh biểu đồ nét cao (`context="talk"`, `dpi=300`) + slide thuyết trình đạt chuẩn Chương 2 §2.7 — **ĐANG LÀM** (đã có `.ipynb` tái lập 0 lỗi + 24 ảnh 300 DPI đã kiểm định 10/10 tiêu chí + `C9`/`C10` `ĐẠT`; còn slide) | Giai đoạn 4 |

---

## 3. Các giai đoạn triển khai

### Giai đoạn 1 — Khám phá & Kiểm kê cấp độ bộ dữ liệu (Hồi 1: *Bối cảnh*)
- **Mục tiêu:** Lập bản đồ toàn cảnh 14 doanh nghiệp trong `data/public_test/` (hoặc `raw_data/public_test/`) để phần Khám phá bộ dữ liệu trở thành Hồi 1 của câu chuyện và làm cơ sở chọn mẫu.
- **Đầu ra:**
  - `T1.0` `[X]`: Cấu hình đọc chỉ đọc `data/public_test/` hoặc `raw_data/public_test/` (14 doanh nghiệp `dev_001`–`dev_014`, `calendar.csv`, `rulebook.md`), bảo đảm chặn đọc `questions.jsonl`.
  - Bảng kiểm kê thống nhất: `business_id`, `industry` suy luận, `recording_format`, `granularity` (đơn+dòng hàng, chỉ đơn, chỉ mặt hàng), số tệp, số dòng, `min_date`–`max_date`, ngày cutoff và khoảng trống dữ liệu.
  - Biểu đồ tổng quan Hồi 1 bằng `matplotlib`/`seaborn` (cơ cấu ngành nghề, mức độ số hóa, dòng thời gian độ phủ dữ liệu, phân bố quy mô dòng).

### Giai đoạn 2 — Chọn tập đại diện & Khám phá từng doanh nghiệp (Hồi 2: *Bằng chứng vi mô*)
- **Mục tiêu:** Chọn các doanh nghiệp đại diện cho mỗi nhóm ngành / mức độ số hóa trong 14 doanh nghiệp `public_test` và phân tích sâu mẫu hình vận hành theo đúng [`data/public_test/rulebook.md`](../data/public_test/rulebook.md) và vệ sinh dữ liệu Chương 2 §2.3.
- **Trạng thái:** `[X]` — Hoàn thành qua [`notebook/02_business_eda.ipynb`](../notebook/02_business_eda.ipynb); 6 doanh nghiệp đại diện, 6 tệp Tidy, 7 bảng bằng chứng, 15 ảnh Hồi 2 (300 DPI).
- **Đầu ra:**
  - Bộ hàm Python dùng chung: đọc dữ liệu đa định dạng, tính chỉ số theo `rulebook.md` (loại đơn hủy/trả, quy theo ngày đặt, doanh thu dòng hàng, quy đổi đơn vị cơ bản, giải mã `Ghi tắt`), chuyển dạng Tidy Data, kiểm tra thiếu dữ liệu và ngoại lệ IQR.
  - Biểu đồ Hồi 2 cho từng doanh nghiệp: cơ cấu sản phẩm/nhóm hàng, phân phối giá trị đơn hàng, đặc trưng khách hàng/thanh toán/ca làm việc/lô hàng (nếu có).

### Giai đoạn 3 — Đặc trưng vận hành liên doanh nghiệp (Hồi 3: *Bằng chứng đối chiếu*)
- **Mục tiêu:** Chỉ so sánh các doanh nghiệp trên những chiều tương đồng về ngữ nghĩa, đơn vị và khung thời gian (chuẩn hóa về **tỉ lệ / phần trăm** theo Chương 2 §2.6 khi quy mô khác nhau).
- **Trạng thái:** `[X]` — Hoàn thành qua [`notebook/03_cross_business_eda.ipynb`](../notebook/03_cross_business_eda.ipynb); cửa sổ giao nhau chung 328 ngày, 5 bảng bằng chứng, 5 ảnh Hồi 3 (300 DPI).
- **Đầu ra:**
  - Ma trận khả năng so sánh (mức chi tiết dữ liệu, có giờ giao dịch hay không, khoảng thời gian hoạt động giao nhau).
  - Biểu đồ Hồi 3: nhịp hoạt động theo giờ/ca, ngày thường vs. cuối tuần, biến động dịp Tết / trước Tết qua [`calendar.csv`](../data/public_test/calendar.csv), và đặc trưng giỏ hàng — kèm ghi chú giới hạn rõ ràng.

### Giai đoạn 4 — Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình (*Kết luận / Hành động*)
- **Mục tiêu:** Chuyển hóa kết quả khám phá thành bộ notebook và slide giải thích hoàn chỉnh bằng tiếng Việt cho giảng viên môn Trực quan hóa dữ liệu.
- **Trạng thái:** `[~]` — `T4.1a`–`T4.1c` đã hoàn thành: **33 biểu đồ kiểm định, 24 ứng viên xuất bản đạt 10/10 tiêu chí (0 ô `CẦN KIỂM TRA`)**, 24 ảnh 300 DPI thật; `C9` **và** `C10` đều `ĐẠT`. Còn `T4.2a`–`T4.2b` (slide) chưa làm.
- **Đầu ra:**
  - Cổng kiểm định chất lượng biểu đồ (`T4.1a`) theo [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md):
    - Ưu tiên thang Cleveland–McGill; biểu đồ cột luôn bắt đầu từ 0; không dùng 3D hay hai trục y gây hiểu lầm.
    - 5 hướng dẫn Schwabish: *Cho thấy dữ liệu*, *Giảm nhiễu* (`despine`), *Gắn chữ với hình* (tiêu đề chủ động + nhãn trực tiếp + chú thích), *Small multiples* thay spaghetti, *Bắt đầu từ màu xám*.
    - Xuất ảnh cho slide (`sns.set_context("talk")`, `dpi=300`, `bbox_inches="tight"`).
  - Bộ `.ipynb` tiếng Việt hoàn chỉnh + Slide thuyết trình theo mạch *Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*.

---

## 4. Phân rã tác vụ & Phụ thuộc

### Giai đoạn 1 — Khám phá & Kiểm kê cấp độ bộ dữ liệu (Hồi 1)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T1.0` | Cấu hình đọc chỉ đọc `data/public_test/` hoặc `raw_data/public_test/` (14 doanh nghiệp) | `[X]` | — | Cấu hình nguồn dữ liệu & kiểm thử |
| `T1.1a` | Đọc toàn bộ 14 tệp `README.md` (trích xuất hình thức ghi nhận, ngày cutoff, quy ước đơn vị/ghi tắt, mô tả bảng) | `[X]` | `T1.0` | Bảng tổng hợp metadata từ `README` |
| `T1.1b` | Quét toàn bộ tệp `.csv`, `.xlsx` (mọi sheet) và `.sqlite` của 14 doanh nghiệp để lấy tên bảng/sheet, cột và số dòng | `[X]` | `T1.0` | Bảng cấu trúc tệp & số dòng |
| `T1.1c` | Trích xuất `min_date`, `max_date`, số ngày/tháng có dữ liệu và khoảng trống thời gian của từng doanh nghiệp | `[X]` | `T1.1b` | Bảng độ phủ & khoảng trống ngày |
| `T1.2a` | Suy luận và kiểm chứng `industry` (ngành nghề) cho 14 doanh nghiệp từ `README.md` + mẫu tên hàng/giao dịch | `[X]` | `T1.1a`, `T1.1b` | Nhãn ngành nghề đã kiểm chứng |
| `T1.2b` | Gắn nhãn mức độ chi tiết & khả năng so sánh (đơn+hàng vs. chỉ đơn vs. chỉ hàng; giờ, mã khách, giá vốn) | `[X]` | `T1.1b` | Danh mục 14 doanh nghiệp hoàn chỉnh |
| `T1.3a` | Xây dựng notebook Khám phá Hồi 1 (bảng tổng hợp + biểu đồ nháp về cơ cấu, mức số hóa, quy mô, độ phủ) | `[X]` | `T1.1c`, `T1.2a`, `T1.2b` | `.ipynb` khám phá Hồi 1 |
| `T1.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 1 (cơ cấu ngành, mức độ số hóa, dòng thời gian độ phủ 2025–2026) | `[X]` | `T1.3a` | Bộ biểu đồ Hồi 1 |

### Giai đoạn 2 — Chọn tập đại diện & Khám phá từng doanh nghiệp (Hồi 2)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T2.1` | Chọn tập doanh nghiệp đại diện (trong 14 doanh nghiệp `public_test`, phủ các ngành & mức số hóa) và ghi rõ tiêu chí chọn | `[X]` | `T1.2a`, `T1.2b`, `T1.1c` | Danh sách tập đại diện → `tables/representative_selection.csv` |
| `T2.2a` | Viết module đọc dữ liệu & tính chỉ số chuẩn `rulebook.md` (loại đơn hủy/trả, tính theo ngày đặt, doanh thu dòng) | `[X]` | `T2.1` | Module Python chuẩn `rulebook` |
| `T2.2b` | Chuẩn hóa đặc thù theo doanh nghiệp (quy đổi đơn vị cơ bản, giải mã `Ghi tắt`, chuyển dạng Tidy Data) | `[X]` | `T2.2a` | Bảng dữ liệu sạch dạng Tidy → `tidy_data/<business_id>_tidy.csv` (6 tệp) |
| `T2.2c` | Kiểm tra chất lượng dữ liệu tập đại diện (thống kê/heatmap giá trị thiếu, trùng lặp, kiểm tra ngoại lệ IQR với nguồn) | `[X]` | `T2.2b` | Báo cáo chất lượng dữ liệu tập mẫu → `tables/quality_and_iqr_report.csv` |
| `T2.3a` | Phân tích Khám phá nội tại từng doanh nghiệp được chọn (nhóm hàng chủ lực, phân phối đơn, khách hàng/ca/lô) | `[X]` | `T2.2c` | `.ipynb` khám phá Hồi 2 → `tables/business_findings_summary.csv` |
| `T2.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 2 (1–2 phát hiện trọng tâm mỗi doanh nghiệp, tiêu đề chủ động, nhãn trực tiếp) | `[X]` | `T2.3a` | Bộ biểu đồ Hồi 2 → `figures/t23b_dev_00{2,6,7,9}_*.png`, `t23b_dev_01{1,2}_*.png` (6 ảnh, 300 DPI) |

### Giai đoạn 3 — Đặc trưng vận hành liên doanh nghiệp (Hồi 3)

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T3.1a` | Lập ma trận khả năng so sánh (chung mức chi tiết, có mốc giờ, khung thời gian hoạt động giao nhau) | `[X]` | `T1.2b`, `T2.2c` | Ma trận khả năng so sánh → `tables/comparability_matrix.csv` |
| `T3.1b` | Tính các chỉ số chuẩn hóa theo tỉ lệ/phần trăm (tỉ trọng %, chỉ số chuẩn hóa, trung bình theo ngày hoạt động) | `[X]` | `T3.1a` | Bảng đối chiếu đã chuẩn hóa → `tables/normalized_cross_metrics.csv` (96 dòng) |
| `T3.2a` | Phân tích & vẽ nhịp vận hành theo giờ / ca / ngày thường–cuối tuần giữa các ngành (dạng small multiples) | `[X]` | `T3.1b` | Biểu đồ nhịp vận hành liên ngành → `tables/operating_rhythm_summary.csv`, `figures/t3_2a_*.png` |
| `T3.2b` | Phân tích & vẽ biến động dịp Tết / trước Tết qua `calendar.csv` (chỉ cho doanh nghiệp đủ độ phủ) | `[X]` | `T3.1b` | Biểu đồ dịp Tết & lịch → `tables/tet_window_comparison.csv`, `figures/t3_2b_*.png` |
| `T3.2c` | Tổng hợp giới hạn đối chiếu, lưu ý về độ phủ và các trường hợp không thể so sánh trực tiếp | `[X]` | `T3.2a`, `T3.2b` | Ghi chú giới hạn Hồi 3 → `tables/cross_business_limitations.csv` |

### Giai đoạn 4 — Hoàn thiện câu chuyện, `.ipynb` & Slide thuyết trình

| Mã | Tác vụ | Trạng thái | Phụ thuộc | Đầu ra |
|---|---|---|---|---|
| `T4.1a` | Kiểm định toàn bộ biểu đồ Hồi 1–3 theo chuẩn Cleveland–McGill & 5 hướng dẫn Schwabish | `[X]` | `T1.3b`, `T2.3b`, `T3.2c` | Danh sách kiểm định biểu đồ → `tables/chart_audit_checklist.csv` + `tables/chart_audit_summary.csv` (33 biểu đồ; **24 ứng viên xuất bản ĐẠT 10/10 tiêu chí, 0 ô `CẦN KIỂM TRA`**; 9 bản nháp trong `figures/drafts/` bị loại có chủ đích). Mỗi biểu đồ được ánh xạ tự động về đúng ô `savefig` vẽ nó để chấm bằng bằng chứng kiểm tra được |
| `T4.1b` | Xuất bộ ảnh tĩnh cho slide (`sns.set_context("talk")`, `dpi=300`, `bbox_inches="tight"`) | `[X]` | `T4.1a` | Bộ ảnh PNG độ phân giải cao → `figures_300dpi/` (**24 ảnh 300 DPI thật**, kiểm tra hậu kỳ: chữ ký PNG, DPI=300, chiều rộng ≥ 2.000 px, biên an toàn ≥ 4 px) |
| `T4.1c` | Hoàn thiện bộ Jupyter Notebook (`.ipynb`) tiếng Việt (mạch văn rõ ràng, chạy tái lập từ đầu đến cuối) | `[X]` | `T4.1a` | Bộ `.ipynb` hoàn chỉnh → `tables/storytelling_final_checklist.csv` (**`C9` `ĐẠT` — tái lập toàn tuyến 0 lỗi; `C10` `ĐẠT` — 24/24 ứng viên đạt 10/10 tiêu chí**, tự suy ra từ bảng kiểm định chứ không nhập tay) |
| `T4.2a` | Lập dàn ý slide thuyết trình tiếng Việt (*Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hạn chế & Hướng phát triển*) | `[X]` | `T4.1a` | Khung nội dung slide → [`docs/PRESENTATION_SCRIPT.md`](PRESENTATION_SCRIPT.md) — 14 slide theo 4 hồi, mỗi slide có thông điệp chủ động + số liệu đối chiếu artifact + **công thức & cách tính** cho mọi chỉ số suy ra + gợi ý biểu đồ; Slide 13–14 chỉ nêu kết luận / hạn chế / hướng phát triển dự kiến |
| `T4.2b` | Hoàn thiện slide thuyết trình, chèn ảnh `dpi=300`, bổ sung ghi chú thuyết trình & chú thích giới hạn | `[ ]` | `T4.1b`, `T4.2a` | Slide thuyết trình hoàn chỉnh |

---

## 5. Rủi ro & Biện pháp giảm thiểu

| Rủi ro | Tác động | Biện pháp giảm thiểu |
|---|---|---|
| **So sánh các chỉ số khác bản chất** (ví dụ: `dev_009` chỉ có cấp hóa đơn vs. doanh nghiệp có chi tiết dòng hàng) | Biểu đồ đối chiếu sai lệch | Bắt buộc phân tầng khả năng so sánh (`T1.2b`, `T3.1a`) và chuẩn hóa tỉ lệ (Chương 2 §2.6) trước khi vẽ |
| **Ngày kết thúc dữ liệu khác nhau** (tháng 05–09/2026) & dữ liệu bị đứt quãng | Sai lệch xu hướng tháng hoặc ngộ nhận mùa vụ | Vẽ dòng thời gian độ phủ ngay ở Hồi 1 (`T1.3b`); chỉ đối chiếu theo cửa sổ thời gian giao nhau và loại tháng cuối thiếu ngày |
| **Hiểu sai quy tắc `rulebook.md`** (tính nhầm đơn hủy/trả, quên quy đổi đơn vị, mã `Ghi tắt`) | Số liệu tính toán sai | Tập trung hóa logic `rulebook.md` trong module `T2.2a`–`T2.2b` và đối chiếu ngoại lệ IQR với dữ liệu gốc |
| **Biểu đồ rối hoặc gây hiểu lầm** (spaghetti nhiều đường, cột cắt trục, quá nhiều màu/chú giải) | Giảm điểm đánh giá của giảng viên | Áp dụng cổng kiểm định `T4.1a` (5 hướng dẫn Schwabish + trục cột từ 0 + `context="talk"`) |
| **Trượt phạm vi sang `train`, ML/DL hoặc thư viện ngoài phạm vi** | Sai yêu cầu dữ liệu hoặc loãng câu chuyện | Giữ chặt phạm vi: chỉ dùng `data/public_test/` (hoặc `raw_data/public_test/`), không `train`, không ML/DL, không Folium/Plotly, không dùng `questions.jsonl` |
| **Hợp đồng đầu vào giữa các notebook bị lệch schema** (đã xảy ra 1 lần: `catalog_14.csv` đổi tên cột làm `T2.1` của NB02 lỗi `KeyError`) | Notebook hậu kỳ không chạy được dù Hồi trước vẫn đúng | `catalog_14.csv` là **hợp đồng giữa NB01 → NB02/NB03**: mọi thay đổi tên cột phải cập nhật đồng thời ô đọc ở NB02 (`cols_show`, `CRITERIA`) và NB03 (`pick_col`). Luôn kiểm tra bằng chuỗi `NB01 → NB02 → NB03 → NB04` trên `artifacts/` sạch (đã xác nhận `C9` ở Giai đoạn 4) |

---

## 6. Theo dõi trạng thái

- **Trạng thái hiện tại:** `[STATUS: ACTIVE]` — Hoàn thành `3/4` giai đoạn (**Giai đoạn 1 — Hồi 1** qua [`notebook/01_dataset_discovery.ipynb`](../notebook/01_dataset_discovery.ipynb); **Giai đoạn 2 — Hồi 2** qua [`notebook/02_business_eda.ipynb`](../notebook/02_business_eda.ipynb) với 6 DN đại diện (`dev_002`, `dev_006`, `dev_007`, `dev_009`, `dev_011`, `dev_012`); **Giai đoạn 3 — Hồi 3** qua [`notebook/03_cross_business_eda.ipynb`](../notebook/03_cross_business_eda.ipynb)). **Giai đoạn 4**: `T4.1a`–`T4.1c` đã hoàn thành — `figures_300dpi/` có 24 ảnh 300 DPI thật, **24/24 ứng viên xuất bản đạt 10/10 tiêu chí kiểm định (0 ô `CẦN KIỂM TRA`)**, `C9` **và** `C10` đều `ĐẠT`. Còn `T4.2a`–`T4.2b` (slide).
   - **Kết quả kiểm chứng (chạy lại 2026-11-17, `jupyter nbconvert --to notebook --execute --inplace`):**

  | Notebook | Ô code | Lỗi | Ghi chú |
  |---|---|---|---|
  | `01_dataset_discovery.ipynb` | 43 | **0** | Sinh lại 7 bảng kiểm kê + 4 ảnh Hồi 1 (đã sửa từ `dpi=180` → **`dpi=300, bbox_inches="tight"`** + bổ sung chú thích đơn vị/nguồn/`n`/khoảng ngày) |
  | `02_business_eda.ipynb` | 37 | **0** | Sinh lại 7 bảng + 6 tệp Tidy + 15 ảnh Hồi 2 (300 DPI; bổ sung chú thích cho `t21`, `t22c` ×2, `t23a` ×3, `t23b` ×6) |
  | `03_cross_business_eda.ipynb` | 31 | **0** | Sinh lại 5 bảng + 5 ảnh Hồi 3 (300 DPI; bổ sung chú thích cho cả 5 ảnh) |
  | `04_visualization_and_storytelling.ipynb` | 20 | **0** | Sinh lại 3 bảng kiểm định (`chart_audit_checklist`, `chart_audit_summary`, `storytelling_final_checklist`) + **24 ảnh 300 DPI** |

  > Đã xác nhận `C9` (tái lập toàn tuyến): **xóa sạch `artifacts/guided_eda/`** rồi chạy lại theo chuỗi `NB01 → NB02 → NB03 → NB04` — cả 4 notebook chạy thành công, **0 lỗi**, và **15/15 artifact bàn giao** (6 bảng Hồi 1 · 7 bảng + 6 tệp Tidy Hồi 2 · 5 bảng Hồi 3) đều được tạo lại đầy đủ — kiểm tra tự động trong `T4.1c` Bước 4.
  >
  > Đã xác nhận `C10` (review thị giác): `C10` **không nhập tay** mà được **suy ra tự động** từ `chart_audit_checklist.csv` — mọi ô `CẦN KIỂM TRA` đã được thay bằng đánh giá kiểm chứng được. Cơ chế: (1) **phân tích tĩnh mã nguồn** — mỗi `chart_id` được ánh xạ tự động về đúng ô `savefig` vẽ nó trong NB01/NB02/NB03 (hỗ trợ f-string loop template & biến trung gian), rồi chấm tiêu chí cấu trúc (trục cột từ 0, `twinx`/`secondary_y`/`plot_surface`/`mplot3d`, `despine`/`spines`, `bar_label`/`ax.text`, `subplots`+`sharey`, bảng màu xám + màu nhấn, chú thích `fig.text` chứa nguồn/`n`/khoảng ngày/đơn vị); (2) **đo trực tiếp trên pixel** — DPI kết xuất thực tế, cỡ chữ nhỏ nhất quy đổi ra px, biên an toàn đỉnh/đáy, mật độ mực. Kết quả: **24/24 ứng viên xuất bản ĐẠT 10/10 tiêu chí**, 0 ô `CẦN KIỂM TRA`.
  >
  > **Bốn lỗi thật do kiểm định phát hiện — đã sửa tại gốc (NB01–NB03), không sửa trong NB04:** (1) `discover_chart_manifest` chỉ loại trừ tiền tố `draft_`/`readme_length` nên **9 bản nháp trong `figures/drafts/`** lọt vào bộ xuất bản → sửa thành loại trừ **toàn bộ** thư mục `figures/drafts/`; (2) 4 ảnh Hồi 1 bàn giao ở `dpi=180`; (3) 10 ảnh thiếu chú thích đơn vị/nguồn/`n`/khoảng ngày; (4) nhãn cứng `"Cửa sổ chung 314 ngày"` trong panel `t13b` → thay bằng f-string đọc từ `common_days`.

- **Phát hiện chính đã chốt (Hồi 2 & Hồi 3):**
  - **Tập đại diện (T2.1):** 6/14 doanh nghiệp — `dev_002` (F&B, xlsx 18 tệp theo tháng), `dev_006` (nhà thuốc, SQLite), `dev_007` (F&B, csv), `dev_009` (cấp đơn, csv), `dev_011` (điện thoại, xlsx), `dev_012` (sửa xe, xlsx). Tiêu chí 5 mục (độ giàu thuộc tính 30%, quy mô 20%, độ dài thời gian 20%, độ phức tạp cấu trúc 15%, có chi tiết dòng hàng 15%) + quy tắc phủ; phủ 5/8 nhóm ngành và cả 3 hình thức ghi nhận.
  - **Chuẩn hóa (T2.2b):** quy đổi đơn vị cơ bản (`dev_002` 60 dòng hộp→cái; `dev_006` 10.917 dòng về đơn vị cơ bản khớp 100% cột `SLQuyDoi`; `dev_007` 561 dòng thùng/két); tách 1.095 dòng topping `dev_002`; giải mã `Ghi tắt` `dev_011` (5.443 dòng → 59 tên hàng, 3 loại); tách cột `Xe` `dev_012` (100% dòng tách được).
  - **Kiểm định logic `rulebook.md` (T2.2a):** đối chiếu tự động doanh thu tính được với tổng tiền ghi trên đơn gốc — `dev_006` 37.833 đơn và `dev_007` 32.022 đơn đều **khớp 100%**; 0 dòng lỗi ngày; 0 thành tiền âm.
  - **Nghịp vận hành liên DN (T3.1b–T3.2a):** cửa sổ giao nhau chung **328 ngày** (`2025-07-01` → `2026-05-24`); tỷ trọng 7 thứ trong tuần đạt **100,00%** ở cả 6 DN (sai số làm tròn ≤ 0,0001%). Chỉ số index cuối tuần (Ngày thường = 100) trên cửa sổ này: `dev_007` **155,57** > `dev_002` **143,50** > `dev_011` **136,73** > `dev_012` **131,47** > `dev_009` **108,97** > `dev_006` **105,19**. Tính trên toàn vùng phủ riêng của từng DN, lift cuối tuần từ **+4,48%** (`dev_006`) đến **+53,28%** (`dev_007`).
  - **Dịp Tết (T3.2b):** Tết 2026 (`2026-02-10` → `2026-02-26`, 17 ngày) phủ trọn 6/6 DN; Tết 2025 chỉ **2/6** DN (`dev_002`, `dev_009`) đủ cửa sổ trước–trong–sau.
  - **Giới hạn đã ghi minh bạch (T3.2c):** loại trừ chiều theo khung giờ/ca (0/6 DN đại diện có `HH:MM` thực tế — vì vậy biểu đồ `t3_2a_hourly_shift_rhythm.png` **không được sinh ra**, không phải thiếu sót); loại trừ so sánh tổng tuyệt đối (chỉ dùng %, Index, TB/ngày); 8 DN ngoài tập đại diện chưa qua Tidy Data nên không đưa vào đối chiếu.
- **Việc còn nợ để đóng Giai đoạn 4:**
  1. `T4.2a`–`T4.2b` — dàn ý và slide thuyết trình tiếng Việt, chèn ảnh `dpi=300` từ `figures_300dpi/` (24 ảnh đã kiểm định).
  2. 9 biểu đồ `CẦN SỬA` trong Hồi 1 đều là **bản nháp khám phá** nằm trong `figures/drafts/` — đã bị loại khỏi bộ xuất bản có chủ đích, không phải lỗi.
- **Quy tắc cập nhật:** Cập nhật thanh tiến độ, bảng tác vụ và mốc `Last Updated` mỗi khi hoàn thành một cột mốc hoặc tác vụ.
