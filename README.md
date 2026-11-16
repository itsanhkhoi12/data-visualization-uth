# Khám phá dữ liệu đa doanh nghiệp — Zalo AI Challenge 2026 (DataMate — `public_test`)

Đồ án nhóm môn **Trực quan hóa dữ liệu** nhằm khám phá mẫu hình vận hành, đặc trưng theo ngành nghề và biến động thời gian trên bộ dữ liệu gồm **14 doanh nghiệp** Việt Nam (`dev_001`–`dev_014`, giai đoạn **2025–2026**) từ phân vùng **`public_test`** của Zalo AI Challenge 2026 — DataMate.

> **Tài liệu định hướng cốt lõi:**
> - Định nghĩa bài toán: [`docs/DEFINE-THE-PROBLEM.md`](docs/DEFINE-THE-PROBLEM.md)
> - Nội dung môn học: [`docs/SUBJECT-CONTENT.md`](docs/SUBJECT-CONTENT.md)
> - Lộ trình dự án: [`plan/PROJECT_ROADMAP.md`](plan/PROJECT_ROADMAP.md)
> - Hướng dẫn 4 giai đoạn Guided EDA & thư mục đầu ra: [`notebook/README.md`](notebook/README.md)
> - Hồ sơ refactor pipeline về `public_test`: [`docs/REFACTOR_PUBLIC_TEST_ONLY.md`](docs/REFACTOR_PUBLIC_TEST_ONLY.md)

---

## Mục lục

- [1. Nguyên tắc thiết kế & Phạm vi](#1-nguyên-tắc-thiết-kế--phạm-vi)
- [2. Cấu trúc thư mục](#2-cấu-trúc-thư-mục)
- [3. Cài đặt môi trường](#3-cài-đặt-môi-trường)
- [4. Cách sử dụng & Chạy kiểm thử](#4-cách-sử-dụng--chạy-kiểm-thử)
- [5. Chuẩn trực quan hóa & Lưu ý Git](#5-chuẩn-trực-quan-hóa--lưu-ý-git)

---

## 1. Nguyên tắc thiết kế & Phạm vi

- **Đối tượng người xem & Hình thức nộp:** Giảng viên môn Trực quan hóa dữ liệu; trình bày bằng **Jupyter Notebook (`.ipynb`)** và **Slide thuyết trình** hoàn toàn bằng **tiếng Việt**.
- **Triển khai song song 4 giai đoạn (Guided EDA) & Tái sử dụng có chọn lọc:** Quá trình phân tích được chia thành **4 notebook độc lập về kernel** trong [`notebook/`](notebook) tương ứng với mạch kể chuyện 3 hồi và cổng kiểm định Giai đoạn 4, tái sử dụng có chọn lọc các module hạ tầng/tiện ích từ [`src/`](src) (giữ [`notebook/eda.ipynb`](notebook/eda.ipynb) làm legacy baseline).
- **Công cụ sử dụng:** `Python`, `pandas`, `NumPy`, `matplotlib`, `seaborn` (cùng `openpyxl`, `scipy`, `jupyter`, `pytest` — xem [`requirements.txt`](requirements.txt)).
- **Chuẩn chỉ số & Lịch:** Áp dụng [`data/public_test/rulebook.md`](data/public_test/rulebook.md) và [`data/public_test/calendar.csv`](data/public_test/calendar.csv) cho âm lịch / kỳ Tết.
- **Ngoài phạm vi:** Không sử dụng dữ liệu `train`; không đọc hoặc dùng `questions.jsonl`; không triển khai mô hình ML/DL, dự báo, phân cụm, PCA/t-SNE/UMAP, Folium hay Plotly.

---

## 2. Cấu trúc thư mục

```text
data-visualization-uth/
├── data/ (hoặc raw_data/) /public_test/     # Dữ liệu cục bộ (được .gitignore bỏ qua); load_config() tự nhận cả hai
│
├── docs/
│   ├── DEFINE-THE-PROBLEM.md                # Định nghĩa bài toán & tiêu chuẩn đánh giá (tiếng Việt)
│   ├── SUBJECT-CONTENT.md                   # Tổng hợp 3 chương bài giảng từ references/
│   └── REFACTOR_PUBLIC_TEST_ONLY.md         # Tài liệu thu hẹp pipeline EDA về split public_test
├── plan/
│   ├── PROJECT_ROADMAP.md                   # Lộ trình 4 giai đoạn & tác vụ (T1.0–T4.2b)
│   ├── EDA_NOTEBOOK_PROMPT_NO_SLIDES.md     # Đặc tả xây dựng 4 Guided EDA Notebooks
│   └── plan_detail/                         # Tài liệu kế hoạch chi tiết trước đây
│
├── src/                                     # Các package mã nguồn xử lý dữ liệu, thống kê, trực quan hóa & QA
├── notebook/
│   ├── README.md                            # Tài liệu hướng dẫn 4 giai đoạn & đầu ra Guided EDA
│   ├── 01_dataset_discovery.ipynb           # Giai đoạn 1 (Hồi 1): Kiểm kê 14 doanh nghiệp (T1.0–T1.3b)
│   ├── 02_business_eda.ipynb                # Giai đoạn 2 (Hồi 2): Tập đại diện & Tidy Data (T2.1–T2.3b)
│   ├── 03_cross_business_eda.ipynb          # Giai đoạn 3 (Hồi 3): Đối chiếu liên ngành (T3.1a–T3.2c)
│   ├── 04_visualization_and_storytelling.ipynb # Giai đoạn 4: Kiểm định biểu đồ & xuất 300 dpi (T4.1a–T4.1c)
│   └── eda.ipynb                            # Notebook legacy baseline theo 17 mục
├── artifacts/                               # Đầu ra bảng/ảnh/báo cáo (gồm guided_eda/ theo 4 phase)
├── tests/                                   # Bộ kiểm thử đơn vị và tích hợp
├── scripts/
│   ├── run_full.py                          # Script chạy toàn bộ pipeline EDA legacy trên split public_test
│   └── probe_charts.py                      # Script khảo sát biểu đồ trong quá trình phát triển
├── total_labs/                              # Các bài thực hành trên lớp (practice01–05.ipynb)
├── .agents/                                 # Quy tắc, mẫu tài liệu và kỹ năng (skills)
│
└── requirements.txt                         # Danh sách thư viện Python của đồ án
```

### Bộ 4 Notebook Guided EDA theo Giai đoạn

Chi tiết từng bước thực hiện và hợp đồng bàn giao xem tại [`notebook/README.md`](notebook/README.md). Mỗi notebook tự động khởi tạo (`mkdir`) thư mục đầu ra riêng bên dưới `artifacts/guided_eda/`:

| Giai đoạn | Notebook | Mã Tác vụ | Thư mục Đầu ra (`mkdir`) |
| --- | --- | --- | --- |
| Giai đoạn 1 (Hồi 1) | [`01_dataset_discovery.ipynb`](notebook/01_dataset_discovery.ipynb) | `T1.0`–`T1.3b` | `artifacts/guided_eda/phase1_dataset_discovery/{tables,figures}/` |
| Giai đoạn 2 (Hồi 2) | [`02_business_eda.ipynb`](notebook/02_business_eda.ipynb) | `T2.1`–`T2.3b` | `artifacts/guided_eda/phase2_business_eda/{tidy_data,tables,figures}/` |
| Giai đoạn 3 (Hồi 3) | [`03_cross_business_eda.ipynb`](notebook/03_cross_business_eda.ipynb) | `T3.1a`–`T3.2c` | `artifacts/guided_eda/phase3_cross_business/{tables,figures}/` |
| Giai đoạn 4 (Hoàn thiện) | [`04_visualization_and_storytelling.ipynb`](notebook/04_visualization_and_storytelling.ipynb) | `T4.1a`–`T4.1c` | `artifacts/guided_eda/phase4_storytelling/{tables,figures_300dpi}/` |

### Các nhóm mã nguồn chính trong `src/`

| Thư mục | Vai trò |
| --- | --- |
| `common/` | Cấu hình, đường dẫn, kiểu dữ liệu chung, provenance và quy tắc an toàn đầu ra. `config.py` tự nhận `raw_data/` hoặc `data/` và đặt thư mục artifact mặc định tại `artifacts/`. |
| `readers/` | Đọc CSV, Excel, JSONL, Markdown, SQLite, bảng và file nén. |
| `profiling/`, `schema/` | Lập hồ sơ cột/nguồn, suy luận kiểu, tìm khóa và đánh giá quan hệ giữa bảng. |
| `quality/` | Phân tích giá trị thiếu, trùng lặp, tính hợp lệ và toàn vẹn. |
| `eda_statistics/`, `statistics/`, `temporal/` | Thống kê đơn biến/đa biến/liên kết và phân tích trường ngày, lịch, độ phủ thời gian. |
| `business/`, `inventory/`, `cross_business/` | Chỉ số nghiệp vụ, tồn kho và tổng hợp giữa các đơn vị kinh doanh. |
| `rulebook/`, `questions/` | Nạp định nghĩa chỉ số, quy tắc nghiệp vụ và phân tích siêu dữ liệu câu hỏi. |
| `visualization/`, `html_tables/` | Định nghĩa, dựng và xuất biểu đồ/bảng. |
| `reporting/` | Tạo báo cáo, kết luận có dẫn chứng và đăng ký artifact. |
| `validation/` | Các cổng QA, kiểm tra thống kê, hình ảnh, hash và hồi quy. |
| `orchestration/` | Điều phối đọc dữ liệu, phân tích, trực quan hóa, báo cáo, `study_examples.py` và dựng notebook. |

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

## 4. Cách sử dụng & Chạy kiểm thử

Mở và thực hành bộ 4 Guided EDA Notebooks trong [`notebook/`](notebook):

```bash
jupyter lab notebook/
```

Kiểm chứng khả năng chạy tái lập từ đầu (`Kernel -> Restart & Run All`) cho 4 notebook Guided EDA:

```bash
jupyter nbconvert --to notebook --execute --stdout notebook/01_dataset_discovery.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/02_business_eda.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/03_cross_business_eda.ipynb > /dev/null
jupyter nbconvert --to notebook --execute --stdout notebook/04_visualization_and_storytelling.ipynb > /dev/null
```

Chạy bộ kiểm thử đơn vị và tích hợp trong [`tests/`](tests):

```bash
python -m pytest tests -q
```

Chạy pipeline legacy baseline cho split `public_test` hoặc chạy [`notebook/eda.ipynb`](notebook/eda.ipynb):

```bash
python scripts/run_full.py
jupyter nbconvert --to notebook --execute --inplace notebook/eda.ipynb
```

---

## 5. Chuẩn trực quan hóa & Lưu ý Git

- Mọi biểu đồ phục vụ báo cáo tuân thủ thang **Cleveland–McGill**, trục cột bắt đầu từ `0`, và **5 hướng dẫn thiết kế của Schwabish** (*Cho thấy dữ liệu, Giảm nhiễu/`despine`, Tiêu đề chủ động + Nhãn trực tiếp, Small multiples thay spaghetti, Bắt đầu từ màu xám*), xuất ảnh `dpi=300`.
- Không commit `raw_data/`, `public_test/`, `train/`, `.venv/`, `venv/`, `artifacts/`, file `.docx`/`.pptx`, hoặc khóa bí mật vào Git.
