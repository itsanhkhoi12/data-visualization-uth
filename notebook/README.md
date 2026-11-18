# Bộ Notebook Thực hành Guided EDA — 4 Giai đoạn Khám phá Dữ liệu Đa Doanh nghiệp

- **Motivation/Background**: Dự án khám phá dữ liệu vận hành trên 14 doanh nghiệp không đồng nhất (`dev_001`–`dev_014`) thuộc phân vùng `public_test` cần được triển khai song song bởi bốn thành viên mà vẫn bảo toàn tính nhất quán phương pháp luận, chuẩn chỉ số, vị trí lưu trữ đầu ra và mạch kể chuyện 3 hồi.
- **Purpose**: Tài liệu hóa đầy đủ kiến trúc, mục tiêu, phân rã tác vụ, cấu trúc thư mục `mkdir` đầu ra cho từng phase, mô-đun tái sử dụng và hợp đồng đầu vào giữa 4 giai đoạn (4 phases) tương ứng với 4 Jupyter Notebook trong [`notebook/`](.).
- **Overview Pipeline**: Giai đoạn 1 ([`01_dataset_discovery.ipynb`](01_dataset_discovery.ipynb)) lập danh mục 14 doanh nghiệp & Hồi 1 → Giai đoạn 2 ([`02_business_eda.ipynb`](02_business_eda.ipynb)) chọn tập đại diện, làm sạch chuẩn `rulebook.md`/Tidy Data & Hồi 2 → Giai đoạn 3 ([`03_cross_business_eda.ipynb`](03_cross_business_eda.ipynb)) đối chiếu liên doanh nghiệp tương thích & Hồi 3 → Giai đoạn 4 ([`04_visualization_and_storytelling.ipynb`](04_visualization_and_storytelling.ipynb)) kiểm định biểu đồ, xuất ảnh `dpi=300` và hoàn thiện câu chuyện tiếng Việt.
- **Detailed Plan**: §1 Tổng quan 4 Giai đoạn & Cấu trúc Thư mục Notebook; §2 Cây Thư mục Đầu ra (`mkdir`) Theo Từng Giai đoạn; §3 Nguyên tắc Chung & Phạm vi Dữ liệu; §4 Chi tiết Từng Giai đoạn (Phases 1–4); §5 Cơ chế Phụ thuộc & Hợp đồng Đầu vào (Input Contract); §6 Hướng dẫn Chạy & Kiểm chứng Tái lập.
- **References**: [`plan/PROJECT_ROADMAP.md`](../plan/PROJECT_ROADMAP.md), [`plan/EDA_NOTEBOOK_PROMPT_NO_SLIDES.md`](../plan/EDA_NOTEBOOK_PROMPT_NO_SLIDES.md), [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md), [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md), [`docs/PRESENTATION_SCRIPT.md`](../docs/PRESENTATION_SCRIPT.md), [`data/public_test/rulebook.md`](../data/public_test/rulebook.md), [`data/public_test/calendar.csv`](../data/public_test/calendar.csv), [`.agents/rules/MD_CONVENTION.md`](../.agents/rules/MD_CONVENTION.md).
- **Created**: 2026-11-16T21:26:24+07:00
- **Last Updated**: 2026-11-18T01:40:00+07:00

[STATUS: ACTIVE]

---

## Mục lục

- [1. Tổng quan 4 Giai đoạn & Cấu trúc Thư mục Notebook](#1-tổng-quan-4-giai-đoạn--cấu-trúc-thư-mục-notebook)
- [2. Cây Thư mục Đầu ra (`mkdir`) Theo Từng Giai đoạn](#2-cây-thư-mục-đầu-ra-mkdir-theo-từng-giai-đoạn)
- [3. Nguyên tắc Chung & Phạm vi Dữ liệu](#3-nguyên-tắc-chung--phạm-vi-dữ-liệu)
- [4. Chi tiết Từng Giai đoạn (Phases 1–4)](#4-chi-tiết-từng-giai-đoạn-phases-14)
  - [4.1 Giai đoạn 1 — Khám phá & Kiểm kê Cấp độ Bộ dữ liệu](#41-giai-đoạn-1--khám-phá--kiểm-kê-cấp-độ-bộ-dữ-liệu)
  - [4.2 Giai đoạn 2 — Chọn Tập Đại diện & Khám phá Từng Doanh nghiệp](#42-giai-đoạn-2--chọn-tập-đại-diện--khám-phá-từng-doanh-nghiệp)
  - [4.3 Giai đoạn 3 — Đặc trưng Vận hành Liên Doanh nghiệp](#43-giai-đoạn-3--đặc-trưng-vận-hành-liên-doanh-nghiệp)
  - [4.4 Giai đoạn 4 — Kiểm định Biểu đồ, Xuất Bản & Hoàn thiện Câu chuyện](#44-giai-đoạn-4--kiểm-định-biểu-đồ-xuất-bản--hoàn-thiện-câu-chuyện)
- [5. Cơ chế Phụ thuộc & Hợp đồng Đầu vào (Input Contract)](#5-cơ-chế-phụ-thuộc--hợp-đồng-đầu-vào-input-contract)
- [6. Hướng dẫn Chạy & Kiểm chứng Tái lập](#6-hướng-dẫn-chạy--kiểm-chứng-tái-lập)

---

## 1. Tổng quan 4 Giai đoạn & Cấu trúc Thư mục Notebook

Thư mục [`notebook/`](.) (cùng cấp với gốc dự án) chứa bộ **04 Jupyter Notebook thực hành Guided EDA** bằng tiếng Việt tương ứng 1–1 với 4 giai đoạn trong [`plan/PROJECT_ROADMAP.md`](../plan/PROJECT_ROADMAP.md), cùng một notebook baseline cũ:

| Tệp Notebook | Giai đoạn | Vai trò trong Câu chuyện | Mã Tác vụ | Thư mục Đầu ra Chính (`mkdir`) |
|---|---|---|---|---|
| [`01_dataset_discovery.ipynb`](01_dataset_discovery.ipynb) | Giai đoạn 1 | Hồi 1: Bối cảnh (14 doanh nghiệp `public_test`) | `T1.0`, `T1.1a`, `T1.1b`, `T1.1c`, `T1.2a`, `T1.2b`, `T1.3a`, `T1.3b` | `artifacts/guided_eda/phase1_dataset_discovery/` |
| [`02_business_eda.ipynb`](02_business_eda.ipynb) | Giai đoạn 2 | Hồi 2: Bằng chứng vi mô (tập đại diện) | `T2.1`, `T2.2a`, `T2.2b`, `T2.2c`, `T2.3a`, `T2.3b` | `artifacts/guided_eda/phase2_business_eda/` |
| [`03_cross_business_eda.ipynb`](03_cross_business_eda.ipynb) | Giai đoạn 3 | Hồi 3: Bằng chứng đối chiếu (liên ngành) | `T3.1a`, `T3.1b`, `T3.2a`, `T3.2b`, `T3.2c` | `artifacts/guided_eda/phase3_cross_business/` |
| [`04_visualization_and_storytelling.ipynb`](04_visualization_and_storytelling.ipynb) | Giai đoạn 4 | Kết luận / Hành động & Cổng QA biểu đồ | `T4.1a`, `T4.1b`, `T4.1c` | `artifacts/guided_eda/phase4_storytelling/` |

Mỗi notebook trong bộ 4 phase đều tuân theo cấu trúc thống nhất 6 phần:

1. `00. Giới thiệu giai đoạn` (vai trò, mục tiêu, phạm vi, đầu ra và vị trí lưu trữ, giới hạn).
2. `01. Thiết lập môi trường` (tự động nhận diện `PROJECT_ROOT`, thêm [`src/`](../src) vào `sys.path`, cấu hình Matplotlib/Seaborn và bảng màu Schwabish).
3. `02. Đọc dữ liệu, Khởi tạo thư mục đầu ra & Hợp đồng đầu vào` (chỉ đọc `public_test`, tự động `mkdir` các thư mục đầu ra hợp lệ bên trong [`artifacts/`](../artifacts) qua `assert_not_in_raw` và `assert_safe_output`, kiểm tra tệp bàn giao từ các giai đoạn trước).
4. `03. Tổng quan dữ liệu cơ bản` (xem cấu trúc mẫu cơ bản để nắm API, không phân tích thay thành viên).
5. `04. Các tác vụ khám phá dữ liệu (EDA Tasks)` (từng tác vụ chia thành `Mục tiêu`, `Câu hỏi khám phá`, `Các bước thực hiện`, `Gợi ý phương pháp & Lưu ý`, `Triển khai` tách riêng 1 code cell cho mỗi `Bước`, `Trực quan hóa` khi phù hợp, và `Kết quả & Nhận định`).
6. `05. Tổng kết giai đoạn & Bàn giao` (checklist nghiệm thu và đầu ra chuyển cho giai đoạn sau).

---

## 2. Cây Thư mục Đầu ra (`mkdir`) Theo Từng Giai đoạn

Toàn bộ đầu ra do 4 thành viên sinh ra trong quá trình làm việc được tập trung dưới thư mục `artifacts/guided_eda/` (thuộc [`artifacts/`](../artifacts) ở project root, được `.gitignore` quản lý loại trừ và nằm hoàn toàn bên ngoài `data/` và `raw_data/`). Khi chạy mục `02` của mỗi notebook, các thư mục con của phase đó sẽ tự động được khởi tạo bằng `Path.mkdir(parents=True, exist_ok=True)`:

```text
artifacts/guided_eda/
├── phase1_dataset_discovery/                 # Khởi tạo bởi NB01 (01_dataset_discovery.ipynb)
│   ├── tables/                               # Biến Python: PHASE1_TABLES_DIR
│   │   ├── readme_metadata.csv               # Đầu ra T1.1a
│   │   ├── objects_inventory.csv             # Đầu ra T1.1b (chi tiết sheet/bảng)
│   │   ├── file_inventory.csv                # Đầu ra T1.1b (tổng hợp cấp doanh nghiệp)
│   │   ├── temporal_coverage.csv             # Đầu ra T1.1c
│   │   ├── industry_classification.csv       # Đầu ra T1.2a
│   │   └── catalog_14.csv                    # Đầu ra T1.2b (file bàn giao chính sang NB02 & NB03)
│   └── figures/                              # Biến Python: PHASE1_FIGURES_DIR (ảnh Hồi 1 từ T1.3a–T1.3b)
├── phase2_business_eda/                      # Khởi tạo bởi NB02 (02_business_eda.ipynb)
│   ├── tidy_data/                            # Biến Python: PHASE2_TIDY_DIR (<business_id>_tidy.csv từ T2.2a–T2.2b)
│   ├── tables/                               # Biến Python: PHASE2_TABLES_DIR
│   │   ├── representative_selection.csv      # Đầu ra T2.1
│   │   ├── quality_and_iqr_report.csv        # Đầu ra T2.2c
│   │   └── business_findings_summary.csv     # Đầu ra T2.3a
│   └── figures/                              # Biến Python: PHASE2_FIGURES_DIR (ảnh Hồi 2 từ T2.3a–T2.3b)
├── phase3_cross_business/                    # Khởi tạo bởi NB03 (03_cross_business_eda.ipynb)
│   ├── tables/                               # Biến Python: PHASE3_TABLES_DIR
│   │   ├── comparability_matrix.csv          # Đầu ra T3.1a
│   │   ├── normalized_cross_metrics.csv      # Đầu ra T3.1b
│   │   ├── operating_rhythm_summary.csv      # Đầu ra T3.2a
│   │   ├── tet_window_comparison.csv         # Đầu ra T3.2b
│   │   └── cross_business_limitations.csv    # Đầu ra T3.2c
│   └── figures/                              # Biến Python: PHASE3_FIGURES_DIR (ảnh Hồi 3 từ T3.2a–T3.2b)
└── phase4_storytelling/                      # Khởi tạo bởi NB04 (04_visualization_and_storytelling.ipynb)
    ├── tables/                               # Biến Python: PHASE4_TABLES_DIR
    │   ├── chart_audit_checklist.csv         # Đầu ra T4.1a
    │   └── storytelling_final_checklist.csv  # Đầu ra T4.1c
    └── figures_300dpi/                       # Biến Python: PHASE4_FIGURES_DIR (ảnh PNG dpi=300 từ T4.1b)
```

---

## 3. Nguyên tắc Chung & Phạm vi Dữ liệu

- **Nguồn dữ liệu cho phép:** Chỉ đọc trực tiếp ở chế độ read-only từ [`data/public_test/`](../data/public_test) (hoặc `raw_data/public_test/`, được [`load_config()`](../src/common/config.py) tự nhận diện), bao gồm 14 doanh nghiệp `dev_001`–`dev_014`, [`data/public_test/rulebook.md`](../data/public_test/rulebook.md) và [`data/public_test/calendar.csv`](../data/public_test/calendar.csv).
- **Bảo vệ đường dẫn đầu ra:** Toàn bộ thư mục `mkdir` của 4 phase đều đi qua [`assert_not_in_raw()`](../src/common/paths.py) và [`assert_safe_output()`](../src/common/paths.py) để đảm bảo không ghi đè hoặc thả tệp trung gian vào dữ liệu gốc.
- **Ranh giới loại trừ nghiêm ngặt:**
  - Tuyệt đối không đọc, gộp hoặc trực quan hóa phân vùng `train` hay tệp `questions.jsonl` (được kiểm tra qua hàm [`is_benchmark_file()`](../src/common/paths.py)).
  - Không dùng mô hình ML/DL, dự báo, phân cụm, PCA, t-SNE, UMAP, Confusion Matrix, ROC/AUC, Feature Importance, Plotly hoặc Folium.
  - Không sửa đổi dữ liệu gốc; không mặc định khoảng thời gian thiếu dữ liệu là có giá trị bằng `0`; không cộng gộp số dòng khác cấp độ chi tiết (`granularity`) thành số giao dịch.
- **Tái sử dụng có chọn lọc (`Selective Reuse`):** Các notebook chỉ import các tiện ích đọc dữ liệu, cấu hình và thống kê/chất lượng phù hợp trong [`src/`](../src), không gọi pipeline tự động trong `orchestration/` để tránh làm thay phần thực hành EDA của thành viên.
- **Lưu ý kỹ thuật về Matplotlib Backend:** Module [`figure_theme.py`](../src/visualization/figure_theme.py) ép backend `Agg` khi import, vì vậy cả 4 notebook không import module này mà cấu hình trực tiếp `sns.set_theme` và `plt.rcParams` để biểu đồ hiển thị inline bình thường trong Jupyter.

---

## 4. Chi tiết Từng Giai đoạn (Phases 1–4)

### 4.1 Giai đoạn 1 — Khám phá & Kiểm kê Cấp độ Bộ dữ liệu

- **Tệp thực thi:** [`01_dataset_discovery.ipynb`](01_dataset_discovery.ipynb)
- **Mục tiêu:** Lập bản đồ toàn cảnh 14 doanh nghiệp `dev_001`–`dev_014` trong `public_test` để hình thành Hồi 1 (*Bối cảnh*) và tạo bảng kiểm kê thống nhất (`catalog_14.csv`) làm căn cứ chọn mẫu ở Giai đoạn 2.
- **Tiện ích tái sử dụng chính:** [`common/config.py`](../src/common/config.py), [`common/paths.py`](../src/common/paths.py), [`readers/markdown_reader.py`](../src/readers/markdown_reader.py), [`readers/csv_reader.py`](../src/readers/csv_reader.py), [`readers/excel_reader.py`](../src/readers/excel_reader.py), [`readers/sqlite_reader.py`](../src/readers/sqlite_reader.py), [`inventory/file_manifest.py`](../src/inventory/file_manifest.py), [`inventory/sheet_registry.py`](../src/inventory/sheet_registry.py), [`inventory/sqlite_registry.py`](../src/inventory/sqlite_registry.py), [`temporal/date_fields.py`](../src/temporal/date_fields.py), [`temporal/coverage.py`](../src/temporal/coverage.py), [`temporal/calendar_registry.py`](../src/temporal/calendar_registry.py).
- **Thư mục `mkdir` tự động:** `PHASE1_TABLES_DIR` (`artifacts/guided_eda/phase1_dataset_discovery/tables/`) và `PHASE1_FIGURES_DIR` (`artifacts/guided_eda/phase1_dataset_discovery/figures/`).

| Mã Tác vụ | Tên Tác vụ | Số Bước | Phụ thuộc | Đường dẫn Đầu ra Dự kiến |
|---|---|---|---|---|
| `T1.0` | Xác minh cấu hình chỉ đọc `public_test` và cơ chế chặn phạm vi | 3 bước | — | Hàm kiểm tra trong bộ nhớ (xác minh nguồn & rào chắn) |
| `T1.1a` | Đọc toàn bộ 14 tệp `README.md` và tổng hợp siêu dữ liệu mô tả | 4 bước | `T1.0` | `artifacts/guided_eda/phase1_dataset_discovery/tables/readme_metadata.csv` |
| `T1.1b` | Quét toàn bộ tệp `.csv`, `.xlsx` (mọi sheet) và `.sqlite` của 14 doanh nghiệp | 5 bước | `T1.0` | `artifacts/guided_eda/phase1_dataset_discovery/tables/objects_inventory.csv`, `file_inventory.csv` |
| `T1.1c` | Trích xuất `min_date`, `max_date`, số ngày/tháng có dữ liệu và khoảng trống thời gian | 4 bước | `T1.1b` | `artifacts/guided_eda/phase1_dataset_discovery/tables/temporal_coverage.csv` |
| `T1.2a` | Suy luận và kiểm chứng `industry` (ngành nghề) cho 14 doanh nghiệp | 4 bước | `T1.1a`, `T1.1b` | `artifacts/guided_eda/phase1_dataset_discovery/tables/industry_classification.csv` |
| `T1.2b` | Gắn nhãn mức độ chi tiết (`granularity`), số hóa & khả năng so sánh | 4 bước | `T1.1b` | `artifacts/guided_eda/phase1_dataset_discovery/tables/catalog_14.csv` |
| `T1.3a` | Xây dựng biểu đồ Khám phá Hồi 1 (Exploratory) | 4 bước | `T1.1c`, `T1.2a`, `T1.2b` | `artifacts/guided_eda/phase1_dataset_discovery/figures/` (bản nháp Hồi 1) |
| `T1.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 1 (Explanatory) | 4 bước | `T1.3a` | `artifacts/guided_eda/phase1_dataset_discovery/figures/` (biểu đồ Hồi 1 hoàn chỉnh) |

---

### 4.2 Giai đoạn 2 — Chọn Tập Đại diện & Khám phá Từng Doanh nghiệp

- **Tệp thực thi:** [`02_business_eda.ipynb`](02_business_eda.ipynb)
- **Mục tiêu:** Chọn tập doanh nghiệp đại diện phủ các nhóm ngành và mức độ số hóa, xây dựng hàm tính chỉ số đúng [`data/public_test/rulebook.md`](../data/public_test/rulebook.md), chuẩn hóa Tidy Data, kiểm tra thiếu dữ liệu/trùng lặp/ngoại lệ IQR và khám phá sâu nội tại từng doanh nghiệp (Hồi 2 — *Bằng chứng vi mô*).
- **Tiện ích tái sử dụng chính:** [`rulebook/rule_registry.py`](../src/rulebook/rule_registry.py), [`readers/table_reader.py`](../src/readers/table_reader.py), [`business/unit_mapping.py`](../src/business/unit_mapping.py), [`quality/missingness.py`](../src/quality/missingness.py), [`quality/duplicates.py`](../src/quality/duplicates.py), [`eda_statistics/robust_stats.py`](../src/eda_statistics/robust_stats.py), [`schema/type_inference.py`](../src/schema/type_inference.py), [`common/provenance.py`](../src/common/provenance.py).
- **Thư mục `mkdir` tự động:** `PHASE2_TIDY_DIR` (`artifacts/guided_eda/phase2_business_eda/tidy_data/`), `PHASE2_TABLES_DIR` (`artifacts/guided_eda/phase2_business_eda/tables/`), `PHASE2_FIGURES_DIR` (`artifacts/guided_eda/phase2_business_eda/figures/`).

| Mã Tác vụ | Tên Tác vụ | Số Bước | Phụ thuộc | Đường dẫn Đầu ra Dự kiến |
|---|---|---|---|---|
| `T2.1` | Chọn tập doanh nghiệp đại diện từ 14 doanh nghiệp `public_test` | 4 bước | `T1.1c`, `T1.2a`, `T1.2b` | `artifacts/guided_eda/phase2_business_eda/tables/representative_selection.csv` |
| `T2.2a` | Viết hàm đọc dữ liệu & tính chỉ số chuẩn `rulebook.md` | 5 bước | `T2.1` | Bộ hàm chuẩn `rulebook.md` và kết quả đối chiếu mẫu đơn |
| `T2.2b` | Chuẩn hóa đặc thù theo doanh nghiệp (Quy đổi đơn vị, `Ghi tắt`, Tidy Data) | 5 bước | `T2.2a` | `artifacts/guided_eda/phase2_business_eda/tidy_data/<business_id>_tidy.csv` |
| `T2.2c` | Kiểm tra chất lượng dữ liệu tập đại diện (Thiếu dữ liệu, Trùng lặp, Ngoại lệ IQR) | 5 bước | `T2.2b` | `artifacts/guided_eda/phase2_business_eda/tables/quality_and_iqr_report.csv` |
| `T2.3a` | Phân tích Khám phá nội tại từng doanh nghiệp đại diện | 5 bước | `T2.2c` | `artifacts/guided_eda/phase2_business_eda/tables/business_findings_summary.csv`, `figures/` (nháp) |
| `T2.3b` | Tinh chỉnh biểu đồ Giải thích Hồi 2 | 4 bước | `T2.3a` | `artifacts/guided_eda/phase2_business_eda/figures/` (1–2 biểu đồ trọng tâm/doanh nghiệp) |

---

### 4.3 Giai đoạn 3 — Đặc trưng Vận hành Liên Doanh nghiệp

- **Tệp thực thi:** [`03_cross_business_eda.ipynb`](03_cross_business_eda.ipynb)
- **Mục tiêu:** Đối chiếu đặc trưng vận hành giữa các doanh nghiệp chỉ trên những chiều tương thích về ngữ nghĩa, cấp độ chi tiết và khung thời gian giao nhau (chuẩn hóa về tỉ lệ/phần trăm/index theo Chương 2 §2.6), hình thành Hồi 3 (*Bằng chứng đối chiếu*).
- **Tiện ích tái sử dụng chính:** [`temporal/calendar_registry.py`](../src/temporal/calendar_registry.py), [`temporal/coverage.py`](../src/temporal/coverage.py), [`cross_business/schema_compare.py`](../src/cross_business/schema_compare.py), cùng các reader từ [`readers/`](../src/readers).
- **Thư mục `mkdir` tự động:** `PHASE3_TABLES_DIR` (`artifacts/guided_eda/phase3_cross_business/tables/`) và `PHASE3_FIGURES_DIR` (`artifacts/guided_eda/phase3_cross_business/figures/`).

| Mã Tác vụ | Tên Tác vụ | Số Bước | Phụ thuộc | Đường dẫn Đầu ra Dự kiến |
|---|---|---|---|---|
| `T3.1a` | Lập ma trận khả năng so sánh liên doanh nghiệp | 5 bước | `T1.2b`, `T2.2c` | `artifacts/guided_eda/phase3_cross_business/tables/comparability_matrix.csv` |
| `T3.1b` | Tính các chỉ số chuẩn hóa theo tỉ lệ / phần trăm | 4 bước | `T3.1a` | `artifacts/guided_eda/phase3_cross_business/tables/normalized_cross_metrics.csv` |
| `T3.2a` | Phân tích & vẽ nhịp vận hành theo giờ / ca / ngày thường–cuối tuần giữa các ngành | 5 bước | `T3.1b` | `artifacts/guided_eda/phase3_cross_business/tables/operating_rhythm_summary.csv`, `figures/` |
| `T3.2b` | Phân tích & vẽ biến động dịp Tết / trước Tết qua `calendar.csv` | 5 bước | `T3.1b` | `artifacts/guided_eda/phase3_cross_business/tables/tet_window_comparison.csv`, `figures/` |
| `T3.2c` | Tổng hợp giới hạn đối chiếu và trường hợp không thể so sánh trực tiếp | 4 bước | `T3.2a`, `T3.2b` | `artifacts/guided_eda/phase3_cross_business/tables/cross_business_limitations.csv` |

---

### 4.4 Giai đoạn 4 — Kiểm định Biểu đồ, Xuất Bản & Hoàn thiện Câu chuyện

- **Tệp thực thi:** [`04_visualization_and_storytelling.ipynb`](04_visualization_and_storytelling.ipynb)
- **Mục tiêu:** Kiểm định toàn bộ biểu đồ từ Hồi 1–3 theo thang Cleveland–McGill và 5 hướng dẫn Schwabish, xuất bộ ảnh tĩnh độ phân giải cao (`sns.set_context("talk")`, `dpi=300`, `bbox_inches="tight"`) vào thư mục đích an toàn ngoài `data/`, và kiểm tra mạch văn tiếng Việt cùng tính tái lập của cả 4 notebook.
- **Tiện ích tái sử dụng chính:** [`common/config.py`](../src/common/config.py), [`common/paths.py`](../src/common/paths.py) (`assert_not_in_raw`, `assert_safe_output`), [`visualization/figure_export.py`](../src/visualization/figure_export.py) (`export_figure`).
- **Thư mục `mkdir` tự động:** `PHASE4_TABLES_DIR` (`artifacts/guided_eda/phase4_storytelling/tables/`) và `PHASE4_FIGURES_DIR` (`artifacts/guided_eda/phase4_storytelling/figures_300dpi/`).

| Mã Tác vụ | Tên Tác vụ | Số Bước | Phụ thuộc | Đường dẫn Đầu ra Dự kiến |
|---|---|---|---|---|
| `T4.1a` | Kiểm định toàn bộ biểu đồ Hồi 1–3 theo chuẩn Cleveland–McGill & 5 hướng dẫn Schwabish | 5 bước | `T1.3b`, `T2.3b`, `T3.2c` | `artifacts/guided_eda/phase4_storytelling/tables/chart_audit_checklist.csv` |
| `T4.1b` | Xuất bộ ảnh tĩnh độ phân giải cao (`sns.set_context('talk')`, `dpi=300`, `bbox_inches='tight'`) | 4 bước | `T4.1a` | `artifacts/guided_eda/phase4_storytelling/figures_300dpi/*.png` |
| `T4.1c` | Hoàn thiện bộ Jupyter Notebook (`.ipynb`) tiếng Việt (Mạch văn & Tính tái lập) | 5 bước | `T4.1a` | `artifacts/guided_eda/phase4_storytelling/tables/storytelling_final_checklist.csv` |

---

## 5. Cơ chế Phụ thuộc & Hợp đồng Đầu vào (Input Contract)

Bốn notebook được thiết kế **độc lập về mặt thực thi kernel** nhưng kết nối tự động qua cây thư mục chuẩn tại `artifacts/guided_eda/`:

```text
NB01 (01_dataset_discovery.ipynb)
  |--[phase1_dataset_discovery/tables/catalog_14.csv]--------> NB02 (02_business_eda.ipynb)
  |                                                             |--[phase2_business_eda/tidy_data/*.csv]--> NB03
  +------------------------------------------------------------------------------------------------------> NB03 (03_cross_business_eda.ipynb)
                                                                                                             |
NB01 + NB02 + NB03 --[phase1_*/tables, figures + phase2_*/tables, figures + phase3_*/tables, figures]-----> NB04 (04_visualization_and_storytelling.ipynb)
```

Quy ước hoạt động của khối **Hợp đồng đầu vào (Input Contract)** tại mục `02` trong Notebook 02, 03 và 04:

1. **Tự động phát hiện đường dẫn chuẩn:** Các biến mặc định (`PHASE1_CATALOG_PATH`, `PHASE2_CLEAN_DATA_DIR`, `PHASE1_SUMMARY_DIR`, `PHASE2_SUMMARY_DIR`, `PHASE3_SUMMARY_DIR`) trỏ thẳng tới đúng thư mục đầu ra mà notebook trước đã `mkdir`.
2. **Trạng thái tường minh khi chờ bàn giao:** Khi tệp/thư mục chưa có dữ liệu thực từ phase trước, hàm kiểm tra (`check_phase2_input_contract`, `check_phase3_input_contract`, `check_phase4_input_contract`) hiển thị nhãn `[CHỜ BỔ SUNG]` và không tạo dữ liệu giả. Khi tệp đã tồn tại, hệ thống tự động nạp và báo `[ĐÃ SẴN SÀNG]`.
3. **Không phụ thuộc biến kernel khác:** Mỗi notebook vẫn khởi chạy độc lập từ đầu mà không cần mở hoặc chạy chung kernel với notebook khác.

---

## 6. Hướng dẫn Chạy & Kiểm chứng Tái lập

Thiết lập môi trường theo [`README.md`](../README.md) và [`requirements.txt`](../requirements.txt), sau đó mở Jupyter Lab hoặc Notebook tại thư mục gốc repository:

```bash
source venv/bin/activate
jupyter lab notebook/
```

Để kiểm chứng khả năng chạy lại hoàn toàn từ đầu (`Kernel -> Restart & Run All`) cho từng notebook mà không ghi đè file sạch:

```bash
jupyter nbconvert --to notebook --execute --stdout notebook/01_dataset_discovery.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/02_business_eda.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/03_cross_business_eda.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/04_visualization_and_storytelling.ipynb > /dev/null
```

Trước khi hoàn tất công việc ở mỗi giai đoạn, thành viên cần kiểm tra:
- Toàn bộ ô `TODO` trong mục `04` và checklist ở mục `05` của notebook phụ trách đã được hoàn thiện.
- Các tệp đầu ra (`.csv` và `.png`) được xuất đúng vào thư mục `PHASE*_TABLES_DIR`, `PHASE2_TIDY_DIR`, `PHASE*_FIGURES_DIR` tương ứng, không lưu ra ngoài cấu trúc quy định.
- Không có dữ liệu nhạy cảm hay kết luận suy diễn ngoài phạm vi `public_test`.
