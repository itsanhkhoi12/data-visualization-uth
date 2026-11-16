# Khám phá dữ liệu đa doanh nghiệp — Zalo AI Challenge 2026 (DataMate)

Bài tập lớn học phần **Trực quan hóa dữ liệu** nhằm khám phá mẫu hình vận hành, đặc trưng theo ngành nghề và biến động thời gian trên bộ dữ liệu gồm **44 doanh nghiệp** Việt Nam (giai đoạn **2025–2026**) từ Zalo AI Challenge 2026 — DataMate.

> **Tài liệu định hướng cốt lõi:**
> - Định nghĩa bài toán: [`docs/DEFINE-THE-PROBLEM.md`](docs/DEFINE-THE-PROBLEM.md)
> - Nội dung môn học: [`docs/SUBJECT-CONTENT.md`](docs/SUBJECT-CONTENT.md)
> - Lộ trình dự án: [`plan/PROJECT_ROADMAP.md`](plan/PROJECT_ROADMAP.md)

---

## Mục lục

- [1. Nguyên tắc thiết kế & Phạm vi](#1-nguyên-tắc-thiết-kế--phạm-vi)
- [2. Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
- [3. Cài đặt môi trường](#3-cài-đặt-môi-trường)
- [4. Dữ liệu nguồn (`data/merged/`)](#4-dữ-liệu-nguồn-datamerged)
- [5. Cách sử dụng & Chạy kiểm thử](#5-cách-sử-dụng--chạy-kiểm-thử)
- [6. Chuẩn trực quan hóa & Lưu ý Git](#6-chuẩn-trực-quan-hóa--lưu-ý-git)

---

## 1. Nguyên tắc thiết kế & Phạm vi

- **Đối tượng người xem & Hình thức nộp:** Giảng viên môn Trực quan hóa dữ liệu; trình bày bằng **Jupyter Notebook (`.ipynb`)** và **Slide thuyết trình** hoàn toàn bằng **tiếng Việt**.
- **Tách biệt Notebook và Logic (`Thin Notebook`):** Các tệp trong [`notebooks/`](notebooks) **không cài đặt chi tiết kỹ thuật** (không viết hàm đọc tệp, làm sạch hay vẽ biểu đồ phức tạp trực tiếp trong cell); notebook chỉ trình bày mạch kể chuyện (*Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động*) và gọi các hàm sạch từ [`src/datamate_viz/`](src/datamate_viz).
- **Công cụ sử dụng:** `Python`, `pandas`, `NumPy`, `matplotlib`, `seaborn` (xem [`requirements.txt`](requirements.txt)).
- **Chuẩn chỉ số & Lịch:** Áp dụng thống nhất [`data/merged/rulebook.md`](data/merged/rulebook.md) (bản `public_test` mở rộng) và [`data/merged/calendar.csv`](data/merged/calendar.csv) cho âm lịch / kỳ Tết.
- **Ngoài phạm vi:** Không dùng `questions.jsonl` và `answers.jsonl`; không triển khai mô hình ML/DL, dự báo, phân cụm, PCA/t-SNE/UMAP, Folium hay Plotly.

---

## 2. Cấu trúc thư mục

```text
data-visualization-uth/
├── data/                            # Dữ liệu cục bộ (được .gitignore bỏ qua)
│   ├── train/                       # Dữ liệu gốc split train (30 doanh nghiệp: biz_101–biz_130)
│   ├── public_test/                 # Dữ liệu gốc split public_test (14 doanh nghiệp: dev_001–dev_014)
│   └── merged/                      # Tập làm việc hợp nhất (44 doanh nghiệp, không chứa file QA)
│       ├── business_index.csv       # Ánh xạ business_id → source_split (train / public_test)
│       ├── calendar.csv             # Lịch dương / âm phục vụ phân tích dịp Tết
│       ├── rulebook.md              # Chuẩn định nghĩa chỉ số thống nhất
│       └── data/                    # 44 thư mục doanh nghiệp (biz_101..biz_130, dev_001..dev_014)
├── docs/
│   ├── DEFINE-THE-PROBLEM.md        # Định nghĩa bài toán & tiêu chuẩn đánh giá (tiếng Việt)
│   └── SUBJECT-CONTENT.md           # Tổng hợp 3 chương bài giảng từ references/
├── plan/
│   ├── PROJECT_ROADMAP.md           # Lộ trình 4 giai đoạn & 24 tác vụ (T1.0–T4.2b)
│   └── plan_detail/                 # Tài liệu kế hoạch chi tiết trước đây
├── references/                      # Slide bài giảng gốc của môn học (.pptx)
├── labs/                            # Các bài thực hành trên lớp (practice01–05.ipynb)
├── src/
│   ├── datamate_viz/                # Package chính của đồ án Trực quan hóa dữ liệu
│   │   ├── config.py                # Đường dẫn chuẩn (data/merged/, outputs/) & bảng màu Schwabish
│   │   ├── io/                      # Đọc dữ liệu chỉ đọc (README, CSV, XLSX, SQLite, calendar)
│   │   ├── inventory/               # Giai đoạn 1: Kiểm kê 44 DN, phân ngành, granularity, độ phủ ngày
│   │   ├── metrics/                 # Giai đoạn 2: Luật rulebook.md, quy đổi đơn vị, Tidy Data & IQR
│   │   ├── analysis/                # Tổng hợp cho Hồi 1, Hồi 2 (từng DN), Hồi 3 (liên ngành)
│   │   └── charts/                  # Hàm vẽ Matplotlib/Seaborn (theme, act1, act2, act3)
│   └── eda/                         # [LEGACY] Pipeline EDA trước đây; giữ nguyên tham khảo, không chỉnh sửa
├── notebooks/                       # Notebook kể chuyện (chỉ gọi hàm từ src/datamate_viz/)
│   ├── 01_boi_canh_44_doanh_nghiep.ipynb   # Hồi 1: Bức tranh toàn cảnh 44 doanh nghiệp
│   ├── 02_kham_pha_doanh_nghiep.ipynb      # Hồi 2: Phân tích sâu từng doanh nghiệp đại diện
│   └── 03_doi_chieu_lien_nganh.ipynb       # Hồi 3: Đối chiếu liên ngành & Kết luận
├── scripts/
│   ├── build_inventory.py           # CLI chạy kiểm kê T1.1–T1.2
│   └── export_figures.py            # CLI xuất toàn bộ ảnh dpi=300 cho slide (T4.1b)
├── outputs/
│   ├── tables/                      # Bảng kiểm kê, bảng chất lượng dữ liệu (CSV/Markdown)
│   └── figures/                     # Ảnh biểu đồ tĩnh dpi=300 phục vụ slide thuyết trình
├── tests/                           # Kiểm thử đơn vị cho config, readers, metrics & kiểm chứng dữ liệu
├── agents/                          # Quy tắc và mẫu tài liệu làm việc
└── requirements.txt                 # Danh sách thư viện Python của đồ án
```

---

## 3. Cài đặt môi trường

Yêu cầu **Python 3.10 trở lên**. Tạo virtual environment tại thư mục gốc repository:

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 4. Dữ liệu nguồn (`data/merged/`)

Thư mục `data/` được loại trừ khỏi Git (xem [`.gitignore`](.gitignore)). Để chạy được mã nguồn trên máy mới:

1. Đặt hai bộ dữ liệu gốc vào `data/train/` và `data/public_test/`.
2. Hợp nhất 44 thư mục doanh nghiệp vào `data/merged/data/`, sao chép `calendar.csv` và `rulebook.md` (từ `public_test`) vào `data/merged/`, loại bỏ `questions.jsonl`/`answers.jsonl`, và tạo `data/merged/business_index.csv` lưu `business_id`, `source_split`, `relative_path`.

---

## 5. Cách sử dụng & Chạy kiểm thử

Chạy kiểm thử đơn vị để xác minh cấu hình, đường dẫn `data/merged/` và module đọc dữ liệu:

```bash
pytest tests/ -v
```

Kiểm tra nhanh CLI chuẩn bị kiểm kê và thư mục xuất ảnh:

```bash
python scripts/build_inventory.py
python scripts/export_figures.py
```

Mở và chạy các notebook trình bày trong [`notebooks/`](notebooks) theo thứ tự từ `01` đến `03`.

---

## 6. Chuẩn trực quan hóa & Lưu ý Git

- Mọi biểu đồ trong [`src/datamate_viz/charts/`](src/datamate_viz/charts) tuân thủ thang **Cleveland–McGill**, trục cột bắt đầu từ `0`, và **5 hướng dẫn thiết kế của Schwabish** (*Cho thấy dữ liệu, Giảm nhiễu/`despine`, Tiêu đề chủ động + Nhãn trực tiếp, Small multiples thay spaghetti, Bắt đầu từ màu xám*).
- Ảnh phục vụ slide xuất qua `save_figure(..., dpi=300)` với `sns.set_context("talk")`.
- Không commit `data/`, `.venv/`, file `.docx`/`.pptx`, hoặc khóa bí mật vào Git.
