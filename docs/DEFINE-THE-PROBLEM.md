# Định nghĩa bài toán — Khám phá dữ liệu đa doanh nghiệp (Multi-Business Data Discovery)

## 1. Tổng quan bài toán

- **Tên bài toán:** Khám phá dữ liệu đa doanh nghiệp (Multi-Business Data Discovery)
- **Bộ dữ liệu:** Zalo AI Challenge 2026 — DataMate, chỉ sử dụng phân vùng **`public_test`** tại [`data/public_test/`](../data/public_test) (**không sử dụng `train`**)
- **Lĩnh vực:** Trực quan hóa dữ liệu và Kể chuyện bằng dữ liệu (Data Visualization & Data Storytelling)
- **Quy mô nhóm & hình thức trình bày:** Đồ án nhóm, trình bày bằng **Jupyter Notebook (`.ipynb`)** và **Slide thuyết trình** bằng **tiếng Việt**
- **Đối tượng người xem mục tiêu:** Giảng viên môn Trực quan hóa dữ liệu (đánh giá tính trung thực, cách mã hóa thị giác, lựa chọn biểu đồ, độ sạch dữ liệu và mạch kể chuyện)

Dự án khám phá các mẫu hình vận hành, đặc trưng theo loại hình kinh doanh và biến động theo thời gian của **14 doanh nghiệp** vừa và nhỏ tại Việt Nam (`dev_001`–`dev_014`) trong tập [`data/public_test/`](../data/public_test). Tập `train` không nằm trong phạm vi phân tích và trực quan hóa.

Kết quả hướng tới là một **câu chuyện dựa trên dữ liệu (data-driven story)** theo cấu trúc **Bối cảnh → Vấn đề → Bằng chứng → Kết luận / Hành động** (Chương 1, §1.5 [`SUBJECT-CONTENT.md`](SUBJECT-CONTENT.md)): đi từ bức tranh tổng thể 14 doanh nghiệp `public_test`, đến phân tích sâu từng doanh nghiệp tiêu biểu, và đối chiếu các đặc trưng vận hành có thể so sánh giữa các ngành.

---

## 2. Bối cảnh và Động lực

Tập [`data/public_test/`](../data/public_test) chứa dữ liệu giao dịch và vận hành có cấu trúc của **14 doanh nghiệp** (`dev_001`–`dev_014`) thuộc nhiều ngành nghề khác nhau (như tạp hóa/tiện lợi, F&B, nhà thuốc, vật liệu xây dựng, sửa xe máy, cửa hàng mẹ và bé, cửa hàng điện thoại…). Các doanh nghiệp này khác nhau đáng kể về:

- **Hình thức ghi nhận dữ liệu:** từ sổ Excel ghi tay, file xuất từ phần mềm bán hàng/POS đến cơ sở dữ liệu quan hệ CSV hoặc SQLite (`pos.sqlite`), kèm các quy ước riêng như bảng `Ghi tắt` hay danh sách quy đổi đơn vị.
- **Mức độ chi tiết (granularity):** có doanh nghiệp ghi chi tiết từng dòng hàng kèm mã đơn, có doanh nghiệp chỉ có cấp hóa đơn (`dev_009`) hoặc có tách nhiều tệp theo tháng (`dev_002`, `dev_005`).
- **Khối lượng và khoảng thời gian quan sát:** dữ liệu nằm trong giai đoạn **2025–2026**, nhưng mỗi doanh nghiệp có ngày bắt đầu, ngày kết thúc (cutoff từ tháng 05/2026 đến tháng 09/2026) và mức độ liên tục khác nhau.

Chỉ đọc bảng số liệu thô khó nhận ra quy luật vận hành. Theo lý thuyết trực quan hóa, chuyển đổi dữ liệu sang các kênh thị giác phù hợp giúp:

- Nhận diện bức tranh đa dạng về ngành nghề, mức độ số hóa và độ phủ dữ liệu của toàn bộ **14 doanh nghiệp**.
- Phát hiện sản phẩm/dịch vụ chủ lực, phân bố hoạt động theo ngày/giờ/ca/cuối tuần hoặc dịp Tết (khi có dữ liệu).
- Nhận ra điểm chung và điểm đặc thù giữa các loại hình kinh doanh mà không đánh đồng các chỉ số khác bản chất.

Dự án **không** nhằm xếp hạng doanh nghiệp nào "tốt nhất" và **không** suy rộng cho toàn bộ doanh nghiệp Việt Nam; mọi nhận định chỉ giới hạn trong phạm vi 14 doanh nghiệp của `data/public_test/`.

---

## 3. Phát biểu bài toán chính

> *Làm thế nào để khám phá và truyền đạt một cách trung thực, rõ ràng các mẫu hình vận hành, đặc trưng theo ngành nghề và biến động theo thời gian trên tập dữ liệu đa doanh nghiệp không đồng nhất của `public_test` thông qua phân tích mô tả và trực quan hóa dữ liệu?*

Bài toán được tiếp cận theo **3 cấp độ gắn kết thành một câu chuyện hoàn chỉnh** (cả 3 cấp độ đều là một phần của nội dung trình bày):

1. **Khám phá cấp độ bộ dữ liệu (Dataset-Level Discovery):** Mô tả cấu thành, ngành nghề, hình thức ghi nhận, cấu trúc tệp và độ phủ thời gian của toàn bộ **14 doanh nghiệp `public_test`** — đóng vai trò mở đầu câu chuyện và làm căn cứ chọn mẫu.
2. **Khám phá từng doanh nghiệp (Individual Business Discovery):** Phân tích sâu cấu trúc hoạt động, cơ cấu hàng hóa/dịch vụ, phân phối đơn hàng/doanh thu và biến động thời gian của các doanh nghiệp đại diện được chọn.
3. **Khám phá liên doanh nghiệp (Cross-Business Discovery):** So sánh các chiều vận hành **thực sự tương đồng về ngữ nghĩa, đơn vị và khoảng thời gian** giữa các loại hình kinh doanh.

---

## 4. Nguồn dữ liệu và Nguyên tắc đọc chỉ đọc (`data/public_test/`)

### 4.1 Thành phần dữ liệu sử dụng

Dự án đọc trực tiếp ở chế độ **chỉ đọc (read-only)** từ [`data/public_test/`](../data/public_test):

- **14 thư mục doanh nghiệp:** [`data/public_test/data/`](../data/public_test/data) gồm `dev_001` đến `dev_014` (`.xlsx`, `.csv`, `.sqlite` và `README.md`).
- **Tệp tham chiếu chuẩn:**
  - [`data/public_test/rulebook.md`](../data/public_test/rulebook.md): chuẩn định nghĩa chỉ số, mốc thời gian, công nợ, nhập hàng và xếp hạng cho toàn bộ dự án.
  - [`data/public_test/calendar.csv`](../data/public_test/calendar.csv): bảng lịch dương/âm dùng để tra cứu ngày âm lịch và kỳ Tết.
- **Loại trừ nghiêm ngặt dữ liệu `train` và QA:**
  - Phân vùng `train` **không được đọc, gộp hay trực quan hóa**.
  - Tệp `data/public_test/questions.jsonl` (tồn tại trong thư mục gốc `public_test/`) **tuyệt đối không được đọc hoặc sử dụng** trong bất kỳ bước phân tích hay gợi ý câu hỏi nào.

### 4.2 Nguyên tắc xử lý dữ liệu không đồng nhất

- Giữ nguyên hoàn toàn các tệp gốc trong [`data/public_test/`](../data/public_test), không sửa, ghi đè hay ép gộp mọi doanh nghiệp vào một bảng duy nhất.
- Chỉ tạo các chiều phân tích chung khi định nghĩa chỉ số, đơn vị tính và mức độ chi tiết thực sự tương thích.
- Các phân tích đặc thù theo ngành (lô thuốc `dev_005`, lượt sửa xe `dev_012`, cửa hàng mẹ và bé `dev_013`, mã ghi tắt `dev_011`/`dev_014`…) giữ ở cấp phân tích từng doanh nghiệp.

---

## 5. Phạm vi thời gian và Giới hạn dữ liệu

Dữ liệu nằm trong khung **2025–2026**, nhưng không đảm bảo là chuỗi thời gian liên tục và mỗi doanh nghiệp có ngày kết thúc dữ liệu riêng:

- Phải kiểm tra khoảng ngày thực tế (`min_date` – `max_date`) và các khoảng trống dữ liệu của từng doanh nghiệp trước khi phân tích.
- **Thiếu dữ liệu không đồng nghĩa với bằng 0:** Cần báo cáo rõ khoảng trống hoặc tháng thiếu dữ liệu thay vì mặc định doanh thu/đơn hàng bằng 0.
- Chỉ so sánh theo thời gian (giữa các tháng, giữa năm 2025 và 2026, cuối tuần hay dịp Tết theo `calendar.csv`) khi các kỳ đối chiếu có độ phủ tương đương.
- Dùng cách diễn đạt thận trọng như *"biến động quan sát được trong giai đoạn có dữ liệu"* thay cho *"xu hướng dài hạn"* hay *"tính mùa vụ ổn định"*.

---

## 6. Phương pháp luận và Quy trình (Gắn với Nội dung môn học)

Dự án áp dụng **Quy trình 7 bước** (Chương 2, [`SUBJECT-CONTENT.md`](SUBJECT-CONTENT.md)) kết hợp chuyển giao từ **Khám phá (Exploratory)** sang **Giải thích (Explanatory)** (Chương 1 §1.2, Chương 2 §2.1):

1. **Phân tích vấn đề (§2.1):** Xuất phát từ người xem (giảng viên) và câu hỏi nghiên cứu cụ thể, đo được, có phạm vi thời gian rõ ràng.
2. **Thu thập & kiểm tra nguồn (§2.2):** Minh bạch nguồn, cỡ mẫu và giới hạn dữ liệu trên mỗi biểu đồ.
3. **Làm sạch & cấu trúc hóa (§2.3):** Không sửa dữ liệu gốc; kiểm tra giá trị thiếu (heatmap/bảng thống kê), chuẩn hóa định dạng ngày/số/đơn vị, loại trùng lặp, kiểm tra ngoại lệ bằng **quy tắc IQR** ($\text{IQR} = Q_3 - Q_1$; ngoài $[Q_1 - 1.5\times\text{IQR},\; Q_3 + 1.5\times\text{IQR}]$) để phân biệt lỗi nhập liệu với sự kiện vận hành thật, và tổ chức bảng theo chuẩn **Tidy Data** (dạng dài — mỗi biến 1 cột, mỗi quan sát 1 dòng).
4. **Chọn loại biểu đồ (§2.4):** Dựa trên kiểu dữ liệu (danh nghĩa, thứ tự, rời rạc, liên tục) và chức năng thông điệp (so sánh, thời gian, phân phối, quan hệ, thành phần).
5. **Công cụ thực hiện (§2.5 & Chương 3):** Sử dụng thống nhất hệ sinh thái **`Python`**, **`pandas`**, **`NumPy`**, **`matplotlib`** và **`seaborn`**.
6. **Chuẩn bị & biến đổi dữ liệu cho biểu đồ (§2.6):** Tổng hợp, chuẩn hóa về **tỉ lệ / phần trăm** khi so sánh nhóm khác quy mô, sắp xếp theo giá trị, gộp nhóm quá nhỏ khi cần, kiểm soát thang đo (tuyến tính vs. log khi trải nhiều bậc độ lớn).
7. **Tạo & tinh chỉnh biểu đồ (§2.7):** Tuân thủ chuẩn chất lượng trực quan ở Mục 7 dưới đây.

---

## 7. Tiêu chuẩn Thiết kế Biểu đồ và Tính trung thực

Mọi biểu đồ đưa vào `.ipynb` cuối cùng và slide thuyết trình phải đáp ứng các nguyên tắc nền tảng trong [`SUBJECT-CONTENT.md`](SUBJECT-CONTENT.md):

- **Nhận thức thị giác (Thang Cleveland–McGill, Chương 1 §1.1):** Ưu tiên mã hóa thông tin quan trọng nhất bằng **vị trí** và **độ dài**; hạn chế dùng diện tích/góc (hạn chế biểu đồ tròn, chỉ dùng tối đa ~5 lát khi cần nhấn tỉ trọng).
- **Trung thực dữ liệu (Chương 1 §1.1, §1.5; Chương 2 §2.6):**
  - Biểu đồ cột **luôn bắt đầu trục từ 0** (*zero baseline*, không cắt cụt trục).
  - **Không** dùng hiệu ứng 3D; tránh biểu đồ hai trục y (*dual axis*) gây ngộ nhận tương quan.
  - Luôn ghi rõ **đơn vị, nguồn dữ liệu và khoảng thời gian** quan sát.
- **5 Hướng dẫn thiết kế của Schwabish (Chương 2 §2.7):**
  1. **Cho thấy dữ liệu (*Show the data*):** Làm nổi bật các điểm/chuỗi phục vụ lập luận.
  2. **Giảm nhiễu (*Reduce clutter*):** Tối đa tỉ lệ *data-ink*, bỏ viền trên/phải (`despine`), bỏ lưới đậm và nền trang trí thừa.
  3. **Gắn chữ với hình (*Graphics + Text*):** Dùng **tiêu đề chủ động (*active title*)** nêu kết luận chính thay cho tiêu đề mô tả chung chung; ưu tiên **nhãn trực tiếp (*direct labeling*)** thay cho chú giải tách rời; thêm chú thích giải thích các đỉnh/đáy/ngoại lệ đáng chú ý.
  4. **Tránh biểu đồ spaghetti:** Khi có nhiều chuỗi hoặc nhiều doanh nghiệp, tách thành **small multiples** (`FacetGrid` / `subplots`) cùng thang trục và sắp xếp hợp lý.
  5. **Bắt đầu từ màu xám (*Start with gray*):** Vẽ nền dữ liệu bằng màu xám trung tính, chỉ dùng màu nhấn (tối đa 5–7 màu phân loại, chú ý tương phản/mù màu) cho đối tượng cần làm nổi bật.

---

## 8. Quy tắc Định nghĩa Chỉ số (Theo `rulebook.md`)

Trước khi tính toán bất kỳ chỉ số nào, phải đối chiếu [`data/public_test/rulebook.md`](../data/public_test/rulebook.md) và `README.md` của doanh nghiệp đó:

- **Doanh thu & Số đơn:** Chỉ tính đơn **không hủy** và **không trả hàng** (kể cả trả một phần là loại **cả đơn**); đơn đang giao vẫn tính.
- **Mốc thời gian:** Đơn thuộc kỳ theo **ngày đặt** (không theo ngày giao hay ngày thu tiền); đơn trả hàng sau kỳ vẫn bị loại khỏi doanh thu kỳ đặt.
- **Giá trị đơn:** Tính từ tổng thành tiền các dòng hàng (đã trừ giảm giá dòng); **không** trừ giảm giá toàn đơn, **không** cộng VAT, **không** gồm phí giao hàng.
- **Quy đổi đơn vị:** Quy về đơn vị cơ bản trước khi tổng hợp hoặc xếp hạng số lượng.
- **Phân biệt luồng (flow) và tồn (stock):** Không cộng dồn tồn kho theo ngày như doanh thu.
- **Không suy diễn nhân quả:** Tương quan hay đồng biến động không đồng nghĩa quan hệ nhân quả.

---

## 9. Ranh giới phạm vi (Scope Boundaries)

### Trong phạm vi (In scope)
- Kiểm kê, phân loại và trực quan hóa bức tranh tổng thể **14 doanh nghiệp** (`dev_001`–`dev_014`) trong [`data/public_test/`](../data/public_test).
- Phân tích mô tả và trực quan hóa từng doanh nghiệp tiêu biểu theo chuẩn `rulebook.md`.
- Đối chiếu liên doanh nghiệp trên các chiều và khung thời gian tương thích.
- Trình bày câu chuyện dữ liệu bằng tiếng Việt qua **Jupyter Notebook (`.ipynb`)** và **Slide thuyết trình** dùng `Python`, `pandas`, `NumPy`, `matplotlib`, `seaborn`.

### Ngoài phạm vi (Out of scope)
- Dữ liệu thuộc phân vùng **`train`** (`biz_101`–`biz_130`) và tệp QA **`questions.jsonl`** (tuyệt đối không đọc hoặc dùng trong trực quan hóa).
- Học máy / Học sâu (ML/DL), dự báo tương lai (forecasting), phân cụm (clustering) hay mô hình hóa thống kê phức tạp.
- Các kỹ thuật trực quan hóa ML trong Chương 1 §1.5 như PCA, t-SNE/UMAP, Confusion Matrix, ROC/AUC, Feature Importance.
- Thư viện bản đồ Folium và biểu đồ tương tác Plotly (giữ ngoài phạm vi ở giai đoạn này).
- Xếp hạng doanh nghiệp "tốt nhất" hoặc khái quát hóa cho toàn bộ doanh nghiệp Việt Nam.

---

## 10. Sản phẩm đầu ra dự kiến

1. **Danh mục & Đánh giá độ phủ 14 doanh nghiệp `public_test`:** Bảng tổng hợp ngành nghề, hình thức ghi nhận, mức chi tiết dữ liệu, khoảng thời gian và các khoảng trống dữ liệu.
2. **Tập câu hỏi khám phá có căn cứ:** Bộ câu hỏi cho cả 3 cấp độ (bộ dữ liệu, từng doanh nghiệp, liên doanh nghiệp) bám sát dữ liệu thực tế của `dev_001`–`dev_014`.
3. **Bộ Jupyter Notebook (`.ipynb`) phân tích & trực quan hóa bằng tiếng Việt:** Tái lập được, mã sạch, tuân thủ `rulebook.md` và chuẩn thiết kế biểu đồ Chương 2.
4. **Slide thuyết trình & Câu chuyện dữ liệu bằng tiếng Việt:** Mạch kể chuyện rõ ràng theo cấu trúc *Bối cảnh → Vấn đề → Bằng chứng → Kết luận*, kèm giới hạn và giả định minh bạch.
