# Nội Dung Slide — `Presentation_Data_Visualize.pptx`

- **Motivation/Background**: Tệp [`references/Presentation_Data_Visualize.pptx`](../references/Presentation_Data_Visualize.pptx) là bản trình chiếu chính thức của nhóm, gồm 18 slide thiết kế dạng hình ảnh (toàn bộ nội dung nằm trong ảnh, không có text box). Cần một bản văn bóc tách được để tra cứu, kiểm chứng số liệu và viết lời thuyết trình.
- **Purpose**: Bóc tách toàn bộ nội dung hiển thị của 18 slide thành văn bản Markdown có cấu trúc, kèm số liệu đã đối chiếu với artifact gốc.
- **Overview Pipeline**: Trích xuất 18 ảnh nhúng từ PPTX bằng `python-pptx` → OCR bằng `RapidOCR` (tiếng Việt, dấu thanh bị mất nên được khôi phục theo ngữ cảnh) → đối chiếu mọi con số với bảng dữ liệu gốc trong [`artifacts/guided_eda/`](../artifacts/guided_eda) và [`notebook/`](../notebook).
- **Detailed Plan**: §1 Slide 01 (Bìa) → §2 Slide 02 (Mục lục) → §3 Slide 03–05 (Hồi 1 · Bối cảnh & dữ liệu) → §4 Slide 06–07 (Hồi 1 · Cấu trúc & thời gian) → §5 Slide 08 (Làm sạch) → §6 Slide 09–12 (Hồi 2 · Vi mô) → §7 Slide 13–16 (Hồi 3 · Liên doanh nghiệp) → §8 Slide 17–18 (Kết luận) → §9 Bảng đối chiếu số liệu → §10 Ghi chú giới hạn.
- **References**: [`python-pptx`](https://python-pptx.readthedocs.io/), [`RapidOCR`](https://rapidai.github.io/RapidOCRDocs/), [`artifacts/guided_eda/`](../artifacts/guided_eda), [`notebook/README.md`](../notebook/README.md), [`docs/PRESENTATION_SCRIPT.md`](PRESENTATION_SCRIPT.md).
- **Created**: 2026-11-19T18:05:00+07:00
- **Last Updated**: 2026-11-19T18:05:00+07:00

[STATUS: ACTIVE]

---

## Mục lục

- [1. Slide 01 — Bìa trình chiếu](#1-slide-01--bìa-trình-chiếu)
- [2. Slide 02 — Giới thiệu và nội dung trình bày](#2-slide-02--giới-thiệu-và-nội-dung-trình-bày)
- [3. Slide 03 — 14 doanh nghiệp: bài toán dữ liệu không đồng nhất](#3-slide-03--14-doanh-nghiệp-bài-toán-dữ-liệu-không-đồng-nhất)
- [4. Slide 04 — Dữ liệu được tổ chức khác nhau giữa Excel, CSV và SQLite](#4-slide-04--dữ-liệu-được-tổ-chức-khác-nhau-giữa-excel-csv-và-sqlite)
- [5. Slide 05 (Slide bổ sung B) — Schema thực tế và sự khác biệt về Data Grain](#5-slide-05-slide-bổ-sung-b--schema-thực-tế-và-sự-khác-biệt-về-data-grain)
- [6. Slide 06 — Cơ cấu doanh nghiệp theo ngành (Hồi 1)](#6-slide-06--cơ-cấu-doanh-nghiệp-theo-ngành-hồi-1)
- [7. Slide 07 — Độ phủ thời gian quyết định khả năng so sánh (Hồi 1)](#7-slide-07--độ-phủ-thời-gian-quyết-định-khả-năng-so-sánh-hồi-1)
- [8. Slide 08 — Data Quality & Cleaning Pipeline](#8-slide-08--data-quality--cleaning-pipeline)
- [9. Slide 09 — Sáu doanh nghiệp đại diện](#9-slide-09--sáu-doanh-nghiệp-đại-diện)
- [10. Slide 10 — Analytical Schema & Data Transformation](#10-slide-10--analytical-schema--data-transformation)
- [11. Slide 11 — Cơ cấu doanh thu theo nhóm sản phẩm của dev_011](#11-slide-11--cơ-cấu-doanh-thu-theo-nhóm-sản-phẩm-của-dev_011)
- [12. Slide 12 — Khám phá giá trị đơn hàng (Hồi 2)](#12-slide-12--khám-phá-giá-trị-đơn-hàng-hồi-2)
- [13. Slide 13 — Điều kiện khoa học để đối chiếu liên doanh nghiệp](#13-slide-13--điều-kiện-khoa-học-để-đối-chiếu-liên-doanh-nghiệp)
- [14. Slide 14 — Định nghĩa chỉ số và chuẩn hóa](#14-slide-14--định-nghĩa-chỉ-số-và-chuẩn-hóa)
- [15. Slide 15 — Chỉ số chuẩn hóa liên doanh nghiệp (Hồi 3)](#15-slide-15--chỉ-số-chuẩn-hóa-liên-doanh-nghiệp-hồi-3)
- [16. Slide 16 — Nhịp vận hành và Tết 2026 (Hồi 3)](#16-slide-16--nhịp-vận-hành-và-tết-2026-hồi-3)
- [17. Slide 17 — Kết luận](#17-slide-17--kết-luận)
- [18. Slide 18 — Thank You / Q&A](#18-slide-18--thank-you--qa)
- [19. Bảng đối chiếu số liệu với artifact gốc](#19-bảng-đối-chiếu-số-liệu-với-artifact-gốc)
- [20. Ghi chú giới hạn khi bóc tách](#20-ghi-chú-giới-hạn-khi-bóc-tách)

---

## 1. Slide 01 — Bìa trình chiếu

| Trường | Nội dung |
|---|---|
| Cơ quan | **TRƯỜNG ĐẠI HỌC GIAO THÔNG VÀ CÔNG NGHỆ TP. HỒ CHÍ MINH** |
| Tiêu đề lớn | **KHÁM PHÁ DỮ LIỆU ĐA DOANH NGHIỆP** |
| Tiêu đề phụ | **Data Visualization: DataMate Public Test** |
| Dòng mô tả | 14 doanh nghiệp · EDA · Trực quan hoá dữ liệu |
| Câu hỏi dẫn dắt | Làm thế nào khám phá và so sánh dữ liệu của những doanh nghiệp có cách ghi nhận khác nhau? |
| Tác giả | Nhóm 1 |

---

## 2. Slide 02 — Giới thiệu và nội dung trình bày

**Tiêu đề:** Giới thiệu và nội dung trình bày
**Phụ đề:** Bối cảnh, vấn đề nghiên cứu và mục tiêu của đề tài

### 2.1. Bối cảnh nghiên cứu

- Dữ liệu bán hàng từ nhiều doanh nghiệp được lưu trữ dưới các định dạng và cấu trúc khác nhau (Excel, CSV, SQLite), gây khó khăn cho việc tổng hợp và so sánh.

### 2.2. Vấn đề nghiên cứu

- Dữ liệu phân tán, không đồng nhất về schema.
- Khác biệt về mức độ chi tiết (grain) giữa các doanh nghiệp.
- Cần chuẩn hoá để phân tích và so sánh đa doanh nghiệp.

### 2.3. Mục tiêu

- Khám phá và hiểu cấu trúc nguồn dữ liệu.
- Kiểm tra chất lượng và chuẩn hoá dữ liệu.
- Xây dựng bộ chỉ số và phân tích, so sánh sau doanh nghiệp.

### 2.4. Nội dung trình bày

1. Tổng quan và dữ liệu nghiên cứu
2. Cấu trúc và schema nguồn dữ liệu
3. Quy trình kiểm tra và chuẩn hoá dữ liệu
4. Biến đổi dữ liệu và schema phân tích
5. Định nghĩa và chuẩn hoá chỉ số
6. Kết quả phân tích và so sánh sau doanh nghiệp
7. Kết luận và hướng trao đổi

---

## 3. Slide 03 — 14 doanh nghiệp: bài toán dữ liệu không đồng nhất

**Tiêu đề:** 14 doanh nghiệp — một bài toán dữ liệu không đồng nhất
**Phụ đề:** Khảo sát phạm vi dữ liệu và vấn đề so sánh

### 3.1. Các con số chính

| Chỉ số | Giá trị |
|---|---|
| Số doanh nghiệp | **14** |
| Tổng số file nghiệp vụ | **80** |
| Định dạng | XLSX, CSV, SQLite |

### 3.2. Phân rã 80 file nghiệp vụ

| Định dạng | Số file | Ghi chú |
|---|---|---|
| XLSX | 69 | Nhiều sheet trong một file |
| CSV | 10 | Phẳng, một bảng |
| SQLite | 1 | Nhiều bảng trong một CSDL |

### 3.3. Mô hình tổ chức dữ liệu

- **EDA → Khám phá dữ liệu.**
- Nguồn không đồng nhất → Cần kiểm tra cấu trúc, chất lượng và khả năng so sánh.
- Một dòng dữ liệu có thể là mặt hàng, hoá đơn hoặc giao dịch tuỳ doanh nghiệp.

> **Lưu ý:** 80 file nghiệp vụ gồm 69 XLSX, 10 CSV và 1 SQLite; không tính README, calendar, rulebook hoặc `questions.jsonl`.
> **Chuyển tiếp:** DataMate Public Test.

---

## 4. Slide 04 — Dữ liệu được tổ chức khác nhau giữa Excel, CSV và SQLite

**Tiêu đề:** Dữ liệu được tổ chức khác nhau giữa Excel, CSV và SQLite
**Phụ đề:** 80 file nghiệp vụ không đồng nghĩa với 80 bảng có cùng cấu trúc
**Phạm vi nguồn dữ liệu nghiên cứu:** 14 doanh nghiệp — `public_test`

### 4.1. Đường đi của một bản ghi, tuỳ định dạng

| Định dạng | Số lượng | Đường đi dữ liệu |
|---|---|---|
| XLSX | 69 | File → Sheet → Cột |
| CSV | 10 | File → Cột → Dòng |
| SQLite | 1 | Database → Table |

### 4.2. Schema inventory

| Chiều | Nội dung kiểm kê |
|---|---|
| Kiểu dữ liệu | Kiểu của từng cột trong mỗi sheet/bảng |
| Số dòng | Quy mô bản ghi của từng object |
| Khoá | Cột định danh / khoá chính nếu xác minh được |
| Độ chi tiết | Grain của bản ghi (mặt hàng / hoá đơn / giao dịch) |
| Quan hệ | Quan hệ giữa các bảng trong cùng nguồn |

### 4.3. Nhận xét

- Một file Excel có thể có nhiều sheet, một SQLite có thể chứa nhiều bảng, và mỗi doanh nghiệp có cách tổ chức dữ liệu khác nhau.
- Khác biệt không chỉ nằm ở định dạng lưu trữ, mà còn ở **ý nghĩa của từng dòng dữ liệu**.

> **Lưu ý:** Không suy ra tổng số bảng từ 80 file; cần phân biệt **file**, **sheet** và **table**.
> **Nguồn:** `phase1_dataset_discovery/tables/file_inventory.csv`, `objects_inventory.csv`, `catalog_14.csv`; Notebook 01.

---

## 5. Slide 05 (Slide bổ sung B) — Schema thực tế và sự khác biệt về Data Grain

**Tiêu đề:** Schema thực tế và sự khác biệt về Data Grain
**Phụ đề:** Cùng là dữ liệu bán hàng, nhưng một dòng có thể mang ý nghĩa khác nhau
**Nhãn:** Slide bổ sung B

### 5.1. Ba lớp khung nhìn

| Lớp | Nội dung |
|---|---|
| **Physical Schema** | File, sheet, table, cột, kiểu dữ liệu, khoá |
| **Logical Schema** | Thực thể và mối quan hệ giữa các thực thể |
| **Data Grain** | Một dòng dữ liệu đại diện cho đơn hàng, dòng hàng hay sự kiện nào |

### 5.2. Hai trường hợp đối chiếu

| | **Trường hợp A · Hoá đơn** | **Trường hợp B · Hoá đơn và dòng hàng** |
|---|---|---|
| Bảng ghi | Bản ghi cấp hoá đơn | Bảng hoá đơn **1:N** + Bảng dòng hàng |
| Một dòng đại diện cho | một hoá đơn | một dòng hàng A, dòng hàng B |
| Ví dụ đối chiếu | `dev_009` — chỉ có dữ liệu cấp hoá đơn, không có chi tiết mặt hàng | Hàng A, Hàng B thuộc cùng một đơn |
| Mô hình quan hệ | — | 1:N (hoá đơn → dòng hàng) |

### 5.3. Bảng schema mẫu (template)

| Field | Data Type | Vai trò |
|---|---|---|
| Tên cột thực tế số 1 | Kiểu từ source | Khoá / định danh nếu xác minh được |
| Tên cột thực tế số 2 | Kiểu từ source | Thời gian / giá trị |
| Tên cột thực tế số 3 | Kiểu từ source | Thuộc tính nghiệp vụ |

> Bảng schema mẫu (template) để minh hoạ cấu trúc, **không phải** bảng trích xuất đã xác minh.

### 5.4. Rủi ro đếm trùng

- Một hoá đơn 1 → 3 dòng hàng.
- Sau khi nối, hoá đơn có thể lặp 3 lần.
- Nếu cộng trực tiếp tiền hoá đơn trên bảng đã nối, doanh thu có thể bị **nhân lên**.

### 5.5. Yêu cầu khi đối chiếu

- Muốn tính chính xác số đơn và doanh thu, phải xác định grain và quan hệ bảng trước khi tổng hợp.
- Cần tổng hợp dòng hàng lên cấp đơn trước khi so sánh.
- Ví dụ cần đối chiếu quan hệ, tên bảng, khoá và quan hệ sẽ hiển thị sau khi đối chiếu nguồn.

> **Lưu ý:** Ví dụ này chỉ minh hoạ nguyên lý, không phải kết quả đếm thực tế của dataset.
> **Nguồn:** Nội dung bổ sung B — đối chiếu schema thực tế sau khi đọc dữ liệu nguồn.

---

## 6. Slide 06 — Cơ cấu doanh nghiệp theo ngành (Hồi 1)

**Tiêu đề:** Khám phá dữ liệu · Giai đoạn 1
**Phụ đề:** F&B chiếm 4/14 doanh nghiệp, nhưng có cấu trúc dữ liệu đa dạng

### 6.1. Cơ cấu doanh nghiệp theo ngành

| Nhóm ngành | Số doanh nghiệp |
|---|---|
| **F&B** | **4 doanh nghiệp — 4/14 (28,6%)** |
| Bán lẻ | (thuộc các nhóm còn lại) |
| Dịch vụ | (thuộc các nhóm còn lại) |
| Sản xuất | (thuộc các nhóm còn lại) |
| Khác / chưa xác định | (thuộc các nhóm còn lại) |

- Các nhóm còn lại phân tán nhiều ngành khác nhau.

### 6.2. Kết luận chính

- 28,6% doanh nghiệp thuộc nhóm F&B.
- Dữ liệu khác nhau cả về ngành và mức độ số hoá.

> **Lưu ý:** Nhóm ngành theo bảng phân loại của đồ án; chưa phải nhận ngành được xác minh độc lập.
> **Nguồn:** `phase1_dataset_discovery/tables/industry_classification.csv`, `catalog_14.csv`; Notebook 01, cell 65.
> **Chuyển tiếp:** Sau khác biệt về ngành, rủi ro lớn hơn nằm ở độ phủ thời gian.

---

## 7. Slide 07 — Độ phủ thời gian quyết định khả năng so sánh (Hồi 1)

**Tiêu đề:** Khám phá dữ liệu · Giai đoạn 1
**Phụ đề:** 14 doanh nghiệp lệch nhau 143 ngày cutoff dữ liệu
**Số liệu chính:** Độ phủ thời gian quan sát của 14 doanh nghiệp (minh hoạ)

### 7.1. Các con số

| Chỉ số | Giá trị | Diễn giải |
|---|---|---|
| Chênh lệch cutoff | **143 ngày** | Sớm nhất → muộn nhất |
| Khoảng giao chung | **314 ngày** | Cửa sổ so sánh chung của **14 doanh nghiệp** |
| Cửa sổ so sánh chung | **2025-07-01 → 2026-05-24** | 328 ngày, áp dụng cho tập 6 doanh nghiệp đại diện |

### 7.2. Biểu đồ minh hoạ

- Trục tung: DN 01 → DN 14 (14 doanh nghiệp).
- Trục ngang: Thời gian (minh hoạ), với hai mốc **Cutoff sớm nhất** và **Cutoff muộn nhất**.

### 7.3. Kết luận

- Phải chuẩn hoá khoảng thời gian trước khi đối chiếu.

> **Lưu ý:** 314 ngày áp dụng cho 14 doanh nghiệp; khác với 328 ngày của 6 doanh nghiệp đại diện dùng cho chuẩn hoá và phân tích sau.
> **Nguồn:** `phase1_dataset_discovery/tables/temporal_coverage.csv`, `catalog_14.csv`; Notebook 01, cell 66.
> **Chuyển tiếp:** Từ 14 doanh nghiệp, nhóm thu hẹp sang tập đại diện cho các slide sau.

---

## 8. Slide 08 — Data Quality & Cleaning Pipeline

**Tiêu đề:** Data Quality & Cleaning Pipeline
**Phụ đề:** Trước khi phân tích, dữ liệu phải được kiểm tra và chuẩn hoá

### 8.1. Quy trình 5 bước

| # | Bước | Nội dung |
|---|---|---|
| 1 | **Kiểm kê dữ liệu** (Raw Data Profiling) | Thống kê cột, kiểu dữ liệu, số dòng và tình trạng thiếu dữ liệu |
| 2 | **Kiểm tra schema và kiểu dữ liệu** | Xác nhận ngày tháng, số tiền, mã định danh, đơn vị và kiểu giá trị |
| 3 | **Kiểm tra trùng lặp và tính hợp lệ** | Nhận diện bản ghi trùng, trạng thái đơn không hợp lệ và các trường hợp cần loại trừ |
| 4 | **Phát hiện ngoại lệ** (IQR) | Phát hiện và gắn cờ quan sát ngoại lệ theo phương pháp IQR, **không mặc nhiên xoá** |
| 5 | **Tạo dữ liệu phân tích** | Tập dữ liệu đã xác định grain và đủ điều kiện cho từng phép tính |

### 8.2. Các chỉ số chất lượng dữ liệu (KPI)

| KPI | Sau kiểm tra |
|---|---|
| Tỷ lệ thiếu dữ liệu (Missing) | Được đo và phân loại (structural missing vs. thiếu thật) |
| Tỷ lệ bản ghi trùng (Duplicate) | Phân biệt trùng hợp lệ (nhiều dòng cùng `order_id`) và trùng cần rà soát |
| Số bản ghi hợp lệ (Sau kiểm tra) | Nền tảng cho mọi phép tính về sau |

### 8.3. Nguyên tắc

- Dữ liệu ngoại lệ không mặc nhiên là dữ liệu sai; cần kiểm tra và gắn cờ trước khi xử lý.

> **Nguồn:** Notebook 02; `missingness_report.csv`; `duplicate_report.csv`; `quality_and_iqr_report.csv`; `iqr_outlier_details.csv`.

---

## 9. Slide 09 — Sáu doanh nghiệp đại diện

**Tiêu đề:** Sáu doanh nghiệp đại diện cho nhiều cấu trúc ghi nhận
**Phụ đề:** Lựa chọn nhằm bảo phủ các trường hợp nghiệp vụ và cấu trúc khác nhau, không đơn thuần lấy sáu doanh nghiệp có điểm số cao nhất.
**Kết quả:** **6/14 doanh nghiệp** được phân tích sau.

### 9.1. Bảng lựa chọn

| Mã doanh nghiệp | Trạng thái | Lý do lựa chọn / Vai trò đại diện |
|---|---|---|
| dev_001 | Không chọn | Trùng vai trò với doanh nghiệp đã chọn |
| **dev_002** | **Được chọn** | Đại diện một cấu trúc ghi nhận khác |
| dev_003 | Không chọn | Không bổ sung trường hợp nghiệp vụ mới |
| dev_004 | Không chọn | Tương tự cấu trúc và ngành của doanh nghiệp đã chọn |
| dev_005 | Không chọn | Trùng đặc điểm chính với doanh nghiệp khác |
| **dev_006** | **Được chọn** | Đại diện kiểu ghi nhận và quy mô khác |
| **dev_007** | **Được chọn** | Đại diện một ngành và mô hình nghiệp vụ khác |
| dev_008 | Không chọn | Không tạo thêm khác biệt về cấu trúc ghi nhận |
| **dev_009** | **Được chọn** | Chỉ có dữ liệu cấp hoá đơn, không có chi tiết mặt hàng |
| dev_010 | Không chọn | Trùng vai trò đại diện với doanh nghiệp đã chọn |
| **dev_011** | **Được chọn** | Đại diện cách ghi nhận theo granularity khác |
| **dev_012** | **Được chọn** | Đại diện ngành và cấu trúc dữ liệu khác |
| dev_013 | Không chọn | Không bổ sung trường hợp mới |
| dev_014 | Không chọn | Tương đồng với doanh nghiệp đã chọn |

### 9.2. Tiêu chí bảo phủ

| Tiêu chí bảo phủ | Doanh nghiệp minh hoạ |
|---|---|
| Khác ngành | dev_006 (Nhà thuốc & Dược phẩm), dev_011 (Phụ kiện & Thiết bị số), dev_012 (Sửa chữa & Phụ tùng xe) |
| Khác kiểu ghi nhận | dev_009 (order-level, không có mặt hàng) |
| Khác granularity (cấp độ dữ liệu) | dev_002 (cap đơn), dev_009 (cap đơn) vs. các doanh nghiệp cap dòng hàng |

> **Lưu ý:** Sau doanh nghiệp này không đại diện thống kê cho toàn bộ 14 doanh nghiệp hoặc cho toàn bộ thị trường.
> **Nguồn:** `phase2_business_eda/tables/representative_selection.csv`, N2, cells 10–17.

---

## 10. Slide 10 — Analytical Schema & Data Transformation

**Tiêu đề:** Analytical Schema & Data Transformation
**Phụ đề:** Từ nhiều cấu trúc nguồn đến dữ liệu phân tích có cùng định nghĩa

### 10.1. Ba lớp xử lý

| Lớp | Nội dung |
|---|---|
| **1. Dữ liệu nguồn** (sau doanh nghiệp) | Excel · CSV · SQLite |
| **2. Ánh xạ và biến đổi dữ liệu** (Data Mapping & Transformation) | Ánh xạ ngữ nghĩa → Thống nhất ý nghĩa các cột chính → Chuẩn hoá kiểu và đơn vị (định dạng ngày, số, tiền, đơn vị) → Kiểm tra grain (xác định mức độ chi tiết: cấp đơn hoặc cấp dòng hàng) |
| **3. Phân tích cấp đơn / cấp dòng hàng** | Cấp đơn (cấp hoá đơn): đếm số đơn, giá trị đơn (doanh thu), phân tích theo ngày · Cấp dòng hàng (cấp chi tiết): nhóm sản phẩm, cơ cấu doanh thu (theo nhóm sản phẩm) |

### 10.2. Nguyên tắc

- Không nên ép mọi chỉ số vào một bảng phẳng duy nhất.
- Các phép phân tích có thể cần hai mức độ chi tiết khác nhau (ví dụ: số đơn theo ngày và cơ cấu doanh thu nhóm sản phẩm).
- Với doanh nghiệp chỉ có hoá đơn, không được tự tạo dữ liệu cấp dòng hàng.

---

## 11. Slide 11 — Cơ cấu doanh thu theo nhóm sản phẩm của dev_011

**Tiêu đề:** Một nhóm hàng đóng góp gần 74% doanh thu của `dev_011`
**Phụ đề:** Cơ cấu doanh thu theo nhóm sản phẩm của `dev_011` trong khoảng 2025-06-01 đến 2026-07-31.

### 11.1. Biểu đồ tròn — Tỷ trọng doanh thu theo nhóm sản phẩm của dev_011

| Nhóm sản phẩm | Tỷ trọng doanh thu | Số dòng hàng | Doanh thu (VND) |
|---|---|---|---|
| Máy mới | **73,85%** | 796 | 11 409 266 000 |
| Máy cũ | **20,42%** | 339 | 3 155 055 000 |
| Phụ kiện | **5,73%** | 3 327 | 884 853 500 |
| **Tổng** | **100%** | — | — |

### 11.2. Kết luận

- Doanh thu của `dev_011` tập trung vào nhóm "máy mới".

### 11.3. Lưu ý

- Tỷ trọng chỉ phản ánh cơ cấu doanh thu, không trực tiếp chứng minh lợi nhuận.

> **Ghi chú:** Ba tỷ trọng cộng xấp xỉ 100%; kết quả được tổng hợp từ dòng hàng hợp lệ theo quy tắc trong notebook.
> **Nguồn:** `phase2_business_eda/tables/business_findings_summary.csv` (dòng `dev_011`, `category_revenue`; N2, cells 50–55).

---

## 12. Slide 12 — Khám phá giá trị đơn hàng (Hồi 2)

**Tiêu đề:** Khám phá giá trị đơn hàng · Giai đoạn 2
**Phụ đề:** Giá trị đơn hàng phân tán mạnh — trung vị giúp đọc dữ liệu thẳng hơn

### 12.1. Ba phân vị giá trị đơn hàng của `dev_002`

| Phân vị | Giá trị |
|---|---|
| Q1 | 39.000 VND/đơn |
| Trung vị (median) | **55.000 VND/đơn** |
| Q3 | 93.000 VND/đơn |
| **IQR** | **39.000 – 93.000 VND/đơn** |

### 12.2. Biểu đồ hộp (minh hoạ)

- Trục ngang: **Giá trị đơn (VND)**, các mốc 20.000 · 40.000 · 60.000 · 80.000 · 100.000 · 120.000.
- Mốc tham chiếu: Q1 = 39.000, Trung vị = 55.000, Q3 = 93.000.

### 12.3. Ngoại lệ IQR

| Doanh nghiệp | Tỷ lệ đơn ngoại lệ IQR |
|---|---|
| `dev_011` | **15,67%** |

### 12.4. Nhận xét

- Trung vị giúp đọc tâm phân phối; IQR cho biết độ phân tán.
- Biểu đồ gốc dùng `log10(1 + giá trị đơn)`; khoảng cách trên trục log **không phải** chênh lệch VND tuyến tính.

> **Lưu ý:** Minh hoạ ba phân vị `dev_002` từ số liệu đã cung cấp; không thay thế boxplot gốc sau doanh nghiệp.
> **Nguồn:** `phase2_business_eda/tables/quality_and_iqr_report.csv`; `business_findings_summary.csv`; Notebook 02, cells 32–40.
> **Tiếp theo:** Kiểm tra điều kiện trước khi so sánh các doanh nghiệp.

---

## 13. Slide 13 — Điều kiện khoa học để đối chiếu liên doanh nghiệp

**Tiêu đề:** Không phải mọi doanh nghiệp đều có thể so sánh trực tiếp
**Phụ đề:** Điều kiện khoa học trước khi đối chiếu liên doanh nghiệp

> Chỉ so sánh khi **cùng định nghĩa chỉ số**, **cùng đơn vị**, **cùng grain** và **cùng cửa sổ thời gian**.

### 13.1. Ma trận khả năng so sánh (14 doanh nghiệp)

| Doanh nghiệp | Cửa sổ so sánh chung | Tết | Ghi chú |
|---|---|---|---|
| `dev_007` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_006` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_002` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_009` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_011` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_012` | 2025-07-01 → 2026-05-24 | ✓ | Đã qua bước chuẩn hoá phục vụ phân tích sau |
| `dev_001` | — | — | Đã kiểm kê cấu trúc, nhưng chưa thuộc tập chuẩn hoá cho các phép so sánh sau ở giai đoạn này |
| `dev_003` | — | — | Như trên |
| `dev_004` | — | — | Như trên |
| `dev_005` | — | — | Như trên |
| `dev_008` | — | — | Như trên |
| `dev_010` | — | — | Như trên |
| `dev_013` | — | — | Như trên |
| `dev_014` | — | — | Như trên |

### 13.2. Kết luận

- **6/14 doanh nghiệp** đã qua bước chuẩn hoá phục vụ phân tích sau.
- Cửa sổ so sánh chung của sau doanh nghiệp: **2025-07-01 → 2026-05-24** (328 ngày).
- Tám doanh nghiệp còn lại đã được kiểm kê cấu trúc, nhưng chưa thuộc tập chuẩn hoá cho các phép so sánh sau ở giai đoạn này.
- Khi điều kiện so sánh đã được xác định, phát hiện đầu tiên liên quan đến **cuối tuần**.

> **Nguồn:** `phase3_cross_business/tables/comparability_matrix.csv`; `cross_business_limitations.csv`; Notebook 03, cells 9–17.

---

## 14. Slide 14 — Định nghĩa chỉ số và chuẩn hóa

**Tiêu đề:** Định nghĩa chỉ số và chuẩn hóa
**Phụ đề:** Chuẩn hoá chỉ số giúp so sánh các mô hình vận hành khác nhau

### 14.1. Chỉ số cuối tuần

- **Ngày thường là mốc tham chiếu (100).**
- So sánh số đơn hợp lệ trung bình/ngày cuối tuần với ngày thường trên cùng cửa sổ.

**Công thức:**

\[
I_{\text{cuối tuần}} = 100 \times \frac{\text{Số đơn hợp lệ TB/ngày cuối tuần}}{\text{Số đơn hợp lệ TB/ngày thường}}
\]

| Thuộc tính | Giá trị |
|---|---|
| Phạm vi thời gian | **328 ngày chung** (01/07/2025 – 24/05/2026) |
| Đơn vị | Chỉ số (ngày thường = 100) |

### 14.2. Biến động Tết 2026

- So với giai đoạn trước Tết.
- So sánh số đơn hợp lệ trung bình/ngày của hai cửa sổ có cùng độ dài.

**Công thức:**

\[
A_{\text{ret}} = 100 \times \frac{\text{TB đơn/ngày trong Tết} - \text{TB đơn/ngày trước Tết}}{\text{TB đơn/ngày trước Tết}}
\]

| Thuộc tính | Giá trị |
|---|---|
| Cửa sổ phân tích | **Ba giai đoạn** |
| Độ dài | **17 ngày / cửa sổ** |
| Ghi nhãn | Trước Tết · Trong Tết · Sau Tết |

### 14.3. Lưu ý về phạm vi và chuẩn hóa

- Hai chỉ số có **phương pháp chuẩn hoá và phạm vi thời gian riêng**, không được trộn lẫn tính.
- Cần đối chiếu với Notebook 03: điều kiện đơn hợp lệ, cách tính trung bình/ngày và xử lý khi mẫu số bằng 0.

---

## 15. Slide 15 — Chỉ số chuẩn hóa liên doanh nghiệp (Hồi 3)

**Tiêu đề:** Chỉ số chuẩn hóa liên doanh nghiệp · Giai đoạn 3
**Phụ đề:** Cả sáu doanh nghiệp bán hơn cuối tuần, nhưng không cùng mức độ

**Biểu đồ cột:** Chỉ số cuối tuần trên cửa sổ so sánh chung (ngày thường = 100)
**Cửa sổ so sánh chung:** 328 ngày — 2025-07-01 → 2026-05-24
**Trục tung:** Index (mốc 100 = ngày thường; các mốc 100 · 120 · 140 · 160)

### 15.1. Giá trị chỉ số

| Doanh nghiệp | Chỉ số cuối tuần (ngày thường = 100) | Ngành |
|---|---|---|
| `dev_007` | **155,57** | F&B (Nhà hàng / Cà phê) |
| `dev_002` | 143,50 | F&B (Nhà hàng / Cà phê) |
| `dev_011` | 136,73 | Phụ kiện & Thiết bị số |
| `dev_012` | 131,47 | Sửa chữa & Phụ tùng xe |
| `dev_009` | 108,97 | Chưa xác định (Order-level) |
| `dev_006` | **105,19** | Nhà thuốc & Dược phẩm |

### 15.2. Nhận xét

- Chỉ số > 100 nghĩa là **cuối tuần bán hơn ngày thường**.
- `dev_007` cao hơn khoảng **55,57%**; `dev_006` cao hơn khoảng **5,19%**.
- Không tồn tại một mức tăng cuối tuần chung cho mọi doanh nghiệp.

> **Nguồn:** `phase3_cross_business/tables/normalized_cross_metrics.csv`; Notebook 03, cell 24.
> **Tiếp theo:** Chuyển sang giai đoạn đặc biệt trong năm — Tết.

---

## 16. Slide 16 — Nhịp vận hành và Tết 2026 (Hồi 3)

**Tiêu đề:** Nhịp vận hành và Tết 2026 · Giai đoạn 3
**Phụ đề:** Tết 2026: có doanh nghiệp giảm hơn 50%, có doanh nghiệp tăng hơn 140%

**Biểu đồ:** Mức thay đổi số đơn hợp lệ trung bình/ngày: Tết 2026 so với trước Tết
**Trục ngang:** Mức thay đổi (%) — các mốc −60% · −30% · 0% · 30% · 60% · 90% · 120% · 160%

### 16.1. Hai cực trị đã xác nhận

| Doanh nghiệp | Mức thay đổi TB đơn/ngày | Ngành |
|---|---|---|
| `dev_009` | **+144,22%** | Chưa xác định (Order-level) |
| `dev_007` | **−54,47%** | F&B (Nhà hàng / Cà phê) |

### 16.2. Các doanh nghiệp còn lại trong tập phân tích

`dev_011`, `dev_012`, `dev_006`, `dev_002` — giá trị chi tiết cần đối chiếu biểu đồ gốc.

| Doanh nghiệp | Mức thay đổi TB đơn/ngày | Ghi chú |
|---|---|---|
| `dev_011` | +49,31% | Trong bảng so sánh cửa sổ Tết 2026 |
| `dev_012` | +15,42% | Trong bảng so sánh cửa sổ Tết 2026 |
| `dev_002` | −45,42% | Trong bảng so sánh cửa sổ Tết 2026 |
| `dev_006` | −0,30% | **Gần như không đổi** (theo ghi chú phân tích) |

### 16.3. Kết luận

- Cùng kỳ Tết, nhịp vận hành biến động theo **hai chiều**.
- Không có một mẫu hình vận hành chung cho mọi doanh nghiệp.

> **Lưu ý:** Cửa sổ trước, trong và sau Tết: 17 ngày mỗi giai đoạn. Khác biệt quan sát được **không chứng minh quan hệ nhân quả**.
> **Nguồn tham chiếu:** `phase3_cross_business/tables/tet_window_comparison.csv`; `calendar.csv`; Notebook 03, cells 35–43.

---

## 17. Slide 17 — Kết luận

**Tiêu đề:** Kết luận
**Phụ đề:** Chuẩn hoá dữ liệu và bộ chỉ số giúp so sánh, phân tích hiệu quả sau doanh nghiệp

| Thực hiện | Kết quả nổi bật | Giá trị và ý nghĩa |
|---|---|---|
| **Làm sạch và chuẩn hoá dữ liệu** — Kiểm tra, xử lý, bảo đảm tính nhất quán | **Chỉ số cuối tuần** — cho thấy mức độ tăng/giảm số đơn vào cuối tuần so với ngày thường | So sánh công bằng giữa các mô hình vận hành khác nhau |
| **Xây dựng bộ chỉ số phân tích** — Chỉ số cuối tuần, biến động Tết, ... | **Biến động Tết 2026** — phản ánh mức thay đổi nhu cầu trong dịp Tết so với giai đoạn trước | Nhận diện rõ đặc điểm kinh doanh theo thời điểm (cuối tuần, Tết) |
| **Phân tích và so sánh** — Đánh giá theo cùng định nghĩa và phạm vi thời gian | | Làm cơ sở cho đánh giá hiệu quả và đề xuất giải pháp phù hợp |

### 17.1. Tổng kết

- Tom lại, việc chuẩn hoá dữ liệu và sử dụng bộ chỉ số thống nhất đã cung cấp một góc nhìn khách quan, có cơ sở và có khả năng so sánh giữa sau doanh nghiệp.

---

## 18. Slide 18 — Thank You / Q&A

- **THANK YOU**
- **QUESTIONS & ANSWERS**
- Data Visualization UTH : Multi-Business Data Discovery

---

## 19. Bảng đối chiếu số liệu với artifact gốc

Mọi con số trong tài liệu này đã được đối chiếu với bảng dữ liệu gốc trong [`artifacts/guided_eda/`](../artifacts/guided_eda):

| Số liệu trên slide | Nguồn gốc | Giá trị xác minh |
|---|---|---|
| 80 file nghiệp vụ: 69 XLSX, 10 CSV, 1 SQLite | `phase1_dataset_discovery/tables/file_inventory.csv` | 80 dòng; `Counter({'xlsx': 69, 'csv': 10, 'sqlite': 1})`; tổng 163 object (sheet/table) |
| 14 doanh nghiệp `public_test` | `phase1_dataset_discovery/tables/catalog_14.csv` | 14 dòng, `dev_001`–`dev_014` |
| F&B chiếm 4/14 (28,6%) | `phase1_dataset_discovery/tables/industry_classification.csv` | `dev_002`, `dev_003`, `dev_007`, `dev_008` → 4/14 = 28,6% |
| Lệch cutoff 143 ngày | `phase1_dataset_discovery/tables/temporal_coverage.csv` | cutoff sớm nhất `dev_005` 2026-05-10; muộn nhất `dev_014` 2026-09-30 → 143 ngày |
| Khoảng giao chung 314 ngày | `temporal_coverage.csv` | `2025-07-01` → `2026-05-10` = 314 ngày (14 doanh nghiệp) |
| Cửa sổ 328 ngày (6 doanh nghiệp) | `temporal_coverage.csv` + `representative_selection.csv` | `2025-07-01` → `2026-05-24` = 328 ngày |
| 6/14 doanh nghiệp đại diện | `phase2_business_eda/tables/representative_selection.csv` | `is_selected = True` cho `dev_002`, `dev_006`, `dev_007`, `dev_009`, `dev_011`, `dev_012` |
| `dev_011`: máy mới 73,85% / máy cũ 20,42% / phụ kiện 5,73% | `phase2_business_eda/tables/business_findings_summary.csv` | `share_pct` = 73,85032773 / 20,42215912 / 5,72751314 |
| `dev_002`: Q1 39.000 · median 55.000 · Q3 93.000 VND/đơn | `phase2_business_eda/tables/quality_and_iqr_report.csv` | `order_revenue`: `q1=39000`, `q3=93000`, `iqr=54000`, `n=51889` |
| `dev_011`: 15,67% đơn ngoại lệ IQR | `quality_and_iqr_report.csv` | `order_revenue` `outlier_pct = 15.673` |
| Chỉ số cuối tuần 155,57 / 105,19 | `phase3_cross_business/tables/normalized_cross_metrics.csv` | `weekend_vs_weekday_index`: `dev_007=155.57`, `dev_002=143.5`, `dev_011=136.73`, `dev_012=131.47`, `dev_009=108.97`, `dev_006=105.19` |
| Tết 2026: `dev_009` +144,22%, `dev_007` −54,47% | `phase3_cross_business/tables/tet_window_comparison.csv` | `tet_vs_pre_orders_pct` = 144.22 / −54.47 |
| `dev_006` gần như không đổi; `dev_011` +49,31%; `dev_012` +15,42%; `dev_002` −45,42% | `tet_window_comparison.csv` | `tet_vs_pre_orders_pct` = −0.3 / 49.31 / 15.42 / −45.42 |
| 6/14 đạt điều kiện so sánh liên doanh nghiệp | `phase3_cross_business/tables/comparability_matrix.csv` | `eligible_weekday = True` cho 6 doanh nghiệp đại diện |

---

## 20. Ghi chú giới hạn khi bóc tách

1. **Toàn bộ 18 slide là ảnh.** Không có text box, chart native, table native hay speaker note nào trong file `.pptx`; toàn bộ nội dung phải trích từ ảnh nhúng (1672×941 px).
2. **OCR mất dấu tiếng Việt.** Bộ nhận dạng `RapidOCR` trả về văn bản không dấu (ví dụ "Kham pha du lieu" → "Khám phá dữ liệu"). Trong tài liệu này dấu thanh đã được **khôi phục theo ngữ cảnh**; các con số, mã doanh nghiệp và tên tệp được giữ nguyên theo ảnh gốc.
3. **Slide 05 không nằm trong luồng chính** (có nhãn "Slide bổ sung B" trên ảnh) nhưng được giữ nguyên vị trí thứ 5 để phản ánh đúng file.
4. **Giá trị biểu đồ ở Slide 15** chỉ một phần được in trên ảnh (`155,57` và `105,19`); các giá trị còn lại lấy từ `normalized_cross_metrics.csv` (cùng metric `weekend_vs_weekday_index`) và được đánh dấu là **đã đối chiếu nguồn**.
5. **Slide 07 dùng biểu đồ minh hoạ** (giá trị trục ngang không phải số ngày thực); bảng số ở §7.1 lấy từ `temporal_coverage.csv`.
6. **Nhóm ngành** trên Slide 06 là nhóm phân loại của đồ án (mức tin cậy `medium`/`low` ở một số doanh nghiệp), **không** phải nhận ngành được xác minh độc lập — đúng như ghi chú trên slide.
