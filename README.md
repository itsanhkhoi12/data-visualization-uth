# Khám phá dữ liệu của 14 doanh nghiệp DataMate

Dự án khám phá dữ liệu bán hàng và vận hành của 14 doanh nghiệp, từ `dev_001` đến `dev_014` trong `public_test`. Notebook đi từ kiểm kê và độ phủ đến phân tích giá trị đơn của `dev_001` và đối chiếu nhịp bán giữa hai doanh nghiệp. Yêu cầu phân tích và thiết kế biểu đồ nằm trong [định nghĩa bài toán](docs/DEFINE-THE-PROBLEM.md).

> **Dữ liệu nguồn:** toàn bộ `raw_data/` được `.gitignore` loại khỏi Git. Thư mục này cần được tạo/copy riêng trên từng máy; clone repository không tự tải dữ liệu.

## Mục lục

- [Yêu cầu](#yêu-cầu)
- [Cấu trúc repository](#cấu-trúc-repository)
- [Cài đặt](#cài-đặt)
- [Chuẩn bị dữ liệu](#chuẩn-bị-dữ-liệu)
- [Chạy phân tích](#chạy-phân-tích)
- [Đầu ra](#đầu-ra)
- [Lưu ý dữ liệu và Git](#lưu-ý-dữ-liệu-và-git)
- [Khắc phục sự cố](#khắc-phục-sự-cố)

## Yêu cầu

- Python **3.10 trở lên**.
- Git để lấy mã nguồn (nếu làm việc từ repository).
- Dung lượng đĩa phù hợp với dữ liệu. Phân tích toàn bộ dữ liệu có thể cần nhiều RAM và thời gian.

Notebook và pipeline dùng `matplotlib`, `openpyxl`, `nbformat`, `pandas`, `seaborn`, `scipy` và `ipykernel`. Cài các thư viện trong môi trường ảo theo hướng dẫn bên dưới.

## Cấu trúc repository

```text
EDA_Data/
├── .gitignore                  # Loại dữ liệu thô, môi trường ảo, cache và file cục bộ khỏi Git
├── README.md                   # Tài liệu này
├── raw_data/                   # Dữ liệu nguồn cục bộ; bị Git bỏ qua
│   └── public_test/            # Tập dữ liệu EDA duy nhất (14 doanh nghiệp dev_001 đến dev_014)
├── raw_data_hashes.json        # Manifest hash dữ liệu được dùng cho kiểm tra hồi quy public_test
├── plan/                       # Kế hoạch và tài liệu thiết kế phân tích
├── scripts/                    # Script khởi chạy pipeline và tiện ích kiểm tra biểu đồ
│   ├── run_full.py             # Chạy pipeline trên public_test
│   └── probe_charts.py         # Khảo sát dữ liệu/biểu đồ trong quá trình phát triển
└── src/eda/
    ├── notebook/
    │   └── eda.ipynb           # Notebook EDA được pipeline tạo/cập nhật
    ├── script/                 # Mã nguồn pipeline EDA
    ├── tests/                  # Kiểm thử các thành phần và hợp đồng
    └── artifacts/              # Báo cáo, biểu đồ, manifest và kết quả theo lần chạy
```

### Các nhóm mã nguồn chính trong `src/eda/script/`

| Thư mục | Vai trò |
| --- | --- |
| `common/` | Cấu hình, đường dẫn, kiểu dữ liệu chung, provenance và quy tắc an toàn đầu ra. `config.py` xác định `raw_data/` và thư mục artifact mặc định. |
| `readers/` | Đọc CSV, Excel, JSONL, Markdown, SQLite, bảng và file nén. |
| `profiling/`, `schema/` | Lập hồ sơ cột/nguồn, suy luận kiểu, tìm khóa và đánh giá quan hệ giữa bảng. |
| `quality/` | Phân tích giá trị thiếu, trùng lặp, tính hợp lệ và toàn vẹn. |
| `eda_statistics/`, `temporal/` | Thống kê đơn biến/đa biến/liên kết và phân tích trường ngày, lịch, độ phủ thời gian. |
| `business/`, `inventory/`, `cross_business/` | Chỉ số nghiệp vụ, tồn kho và tổng hợp giữa các đơn vị kinh doanh. |
| `rulebook/` | Nạp định nghĩa chỉ số và quy tắc nghiệp vụ. |
| `visualization/`, `html_tables/` | Định nghĩa, dựng và xuất biểu đồ/bảng. |
| `reporting/` | Tạo báo cáo, kết luận có dẫn chứng và đăng ký artifact. |
| `validation/` | Các cổng QA, kiểm tra thống kê, hình ảnh, hash và hồi quy. |
| `orchestration/` | Điều phối đọc dữ liệu, phân tích, trực quan hóa, báo cáo và notebook. |

Các file điều phối quan trọng:

- `common/config.py`: tìm gốc workspace, xác định đầu vào và đầu ra mặc định.
- `orchestration/pipeline.py`: điều phối một lần chạy EDA.
- `orchestration/analysis.py`: phân tích từng tập dữ liệu.
- `orchestration/visualization_pipeline.py`: chuẩn bị dữ liệu và chạy quy trình biểu đồ.
- `orchestration/notebook_builder.py`: xây dựng notebook theo cùng hợp đồng pipeline.

## Cài đặt

Mở terminal tại thư mục gốc repository (thư mục có `README.md`). Chọn nhóm lệnh phù hợp với hệ điều hành. Tạo môi trường ảo trước khi cài thư viện để không ảnh hưởng Python toàn hệ thống.

### Linux

Trên Ubuntu/Debian, nếu chưa có Python và `venv`:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip git
```

Tạo và kích hoạt môi trường:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install matplotlib openpyxl nbformat pandas seaborn scipy ipykernel
```

### Windows (PowerShell)

Cài Python 3.10+ từ python.org hoặc Microsoft Store và bật tùy chọn thêm Python vào `PATH`. Mở PowerShell tại thư mục repository:

```powershell
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install matplotlib openpyxl nbformat pandas seaborn scipy ipykernel
```

`Set-ExecutionPolicy -Scope Process` chỉ áp dụng cho cửa sổ PowerShell hiện tại. Nếu dùng Command Prompt thay vì PowerShell, kích hoạt bằng:

```bat
.venv\Scripts\activate.bat
```

### macOS

Cài Python 3.10+ từ python.org hoặc Homebrew (nếu đã cài Homebrew):

```bash
brew install python
```

Tạo và kích hoạt môi trường:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install matplotlib openpyxl nbformat pandas seaborn scipy ipykernel
```

Sau khi kích hoạt, dấu nhắc lệnh thường hiển thị `(.venv)`. Xác nhận Python đang dùng thuộc môi trường dự án:

```bash
python --version
python -m pip --version
```

Mỗi lần mở terminal mới, cần kích hoạt lại môi trường. Lệnh hủy kích hoạt trên cả ba hệ điều hành:

```bash
deactivate
```

## Chuẩn bị dữ liệu

Pipeline mặc định tìm dữ liệu tại `raw_data/public_test` ở gốc repository. Cấu trúc thư mục chuẩn:

```text
raw_data/
└── public_test/
    ├── rulebook.md
    ├── calendar.csv
    └── data/
        ├── dev_001/
        ├── dev_002/
        └── ...
```

Đầu vào phân tích gồm `rulebook.md`, `calendar.csv` và các thư mục doanh nghiệp trong `data/`. Pipeline bỏ qua các tệp hỏi đáp của cuộc thi nếu chúng có mặt trong bản sao cục bộ.

Để thêm dữ liệu:

1. Tạo/copy dữ liệu vào đúng `raw_data/public_test/data/<id>/`.
2. Đặt các tệp tham chiếu (`rulebook.md` và `calendar.csv`) tại `raw_data/public_test/`.
3. Giữ nguyên tên file, mã hóa và cấu trúc bảng cần thiết; không sửa trực tiếp dữ liệu gốc trong quá trình EDA. Pipeline được cấu hình `read_only=True`.
4. Nếu nguồn dữ liệu có thông tin cá nhân, tài chính hoặc bí mật, chỉ lưu ở vị trí được phép và không đưa vào commit/chia sẻ.

Tạo khung thư mục rỗng:

Linux/macOS:

```bash
mkdir -p raw_data/public_test/data
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force raw_data/public_test/data
```

**Lưu ý:** `.gitignore` loại trừ toàn bộ `raw_data/`, nên Git không lưu thư mục rỗng hay dữ liệu bên trong. Clone repository không tải dữ liệu. Nếu người khác cần bộ dữ liệu, hãy phân phối qua kho dữ liệu được kiểm soát/quy trình nội bộ phù hợp, rồi đặt vào đúng cấu trúc trên. Không bỏ quy tắc ignore để commit dữ liệu thô.

## Chạy phân tích

Kích hoạt `.venv`, chuẩn bị `raw_data/public_test/`, rồi chạy từ thư mục gốc repository:

```bash
python scripts/run_full.py
```

Script chạy `run_eda` cho split `public_test`, sau đó in JSON tóm tắt gồm `run_id`, thời gian chạy, số biểu đồ, trạng thái và đường dẫn output. Pipeline mặc định đọc dữ liệu, dùng seed lấy mẫu cố định, và ghi artifact dưới `src/eda/artifacts/`.

Để xem bài phân tích của môn học, mở [eda.ipynb](src/eda/notebook/eda.ipynb) trong trình soạn thảo có hỗ trợ Jupyter, chọn kernel Python của `.venv` và chạy tất cả các ô theo thứ tự. Notebook tự chạy pipeline trên 14 doanh nghiệp, kết xuất các biểu đồ được dùng trong bài và lưu hai hình minh họa về độ phân tán và nhịp bán trong `figures/course/`. Lệnh CLI ở trên kết xuất bộ biểu đồ kỹ thuật đầy đủ nên cần nhiều thời gian hơn.

Trong mục 10, dùng bảng kiểm tra để lần theo số dòng thiếu mã, số dòng trùng và số đơn hợp lệ. Đối chiếu ngưỡng IQR với hộp Q1–Q3 trên biểu đồ. Trong mục 11, chọn một thứ và chia số đơn của thứ đó cho số ngày lịch tương ứng trong các tháng chung. Cách kiểm tra này cho phép tái lập một cột trên biểu đồ từ bảng gốc.

Bảng độ phủ đọc cả ngày và timestamp trong sổ hóa đơn của `dev_009`. Với sổ bán hàng `dev_014`, mã số ngày Excel được đổi sang ngày lịch khi tháng và năm khớp với tên sheet. Báo cáo bàn giao ghi các bước mở rộng trong chương **Hướng cải thiện**.

Để cập nhật cấu trúc hoặc lời giải thích của notebook, sửa `orchestration/notebook_builder.py` rồi chạy lại bộ dựng. Ví dụ trên PowerShell:

```powershell
$env:PYTHONPATH = 'src/eda/script'
python -m orchestration.notebook_builder
```

## Đầu ra

Mỗi lần chạy tạo một thư mục theo `run_id` trong `src/eda/artifacts/`. Tùy kết quả và các cổng kiểm tra, bên trong có thể gồm:

- `reports/`: báo cáo tổng quan, nghiệp vụ, QA và bàn giao.
- `figures/`: hình biểu đồ đã kết xuất.
- `chart_manifest/`: manifest và dữ liệu mô tả biểu đồ.
- `splits/`: kết quả phân tích theo từng split.
- Các manifest/registry: cấu hình lần chạy, hash nguồn, danh mục artifact và sổ trạng thái kiểm tra.

Artifact được sinh lại từ dữ liệu và mã nguồn. Tránh chỉnh sửa thủ công artifact; hãy cập nhật mã hoặc dữ liệu đầu vào rồi chạy lại.

## Lưu ý dữ liệu và Git

- `raw_data/` và `.venv/` đã được loại khỏi Git trong `.gitignore`.
- Không đưa `.env`, thông tin đăng nhập, khóa hoặc dữ liệu nhạy cảm vào repository.
- `raw_data_hashes.json` là manifest hiện có trong repository, dùng cho kiểm tra hash dữ liệu trong quy trình QA. Khi thay dữ liệu, xem xét cập nhật manifest theo quy trình dự án; manifest cũ không chứng minh dữ liệu hiện tại giống nguồn trước đây.
- Không commit cache, file tạm hoặc đầu ra cục bộ ngoài quy ước dự án.

## Khắc phục sự cố

| Vấn đề | Cách xử lý |
| --- | --- |
| `python` không được nhận diện trên Windows | Thử `py -3 --version`, rồi tạo môi trường bằng `py -3 -m venv .venv`. |
| Không kích hoạt được venv trên PowerShell | Chạy `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` trong cửa sổ hiện tại, sau đó chạy lại lệnh kích hoạt. |
| Báo thiếu thư viện | Kích hoạt `.venv`, rồi chạy `python -m pip install matplotlib openpyxl nbformat pandas seaborn scipy ipykernel`. |
| `raw_data root not found` | Chạy lệnh từ repository và kiểm tra `raw_data/` đã được tạo tại gốc. |
| Báo thiếu `public_test`, `rulebook.md` hoặc `calendar.csv` | Đối chiếu cấu trúc tại [Chuẩn bị dữ liệu](#chuẩn-bị-dữ-liệu), kiểm tra tên và vị trí file. |
| Chạy lâu hoặc thiếu bộ nhớ | Kiểm tra kích thước dữ liệu và tài nguyên máy; pipeline xử lý toàn bộ 14 doanh nghiệp của public_test. |
