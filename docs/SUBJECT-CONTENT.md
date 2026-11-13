# Nội dung môn học: Trực quan hóa dữ liệu

> Tài liệu này tổng hợp toàn bộ nội dung bài giảng học phần

---

## Chương 1: Tổng quan về Trực quan hóa dữ liệu

**Mục tiêu học tập:**
- **Kiến thức:** Nắm khái niệm, vai trò, lịch sử và các nguyên tắc nền tảng của trực quan hóa dữ liệu.
- **Phân loại:** Phân biệt các loại trực quan hóa theo mục đích, hình thức, kiểu dữ liệu và thông điệp.
- **Quy trình:** Mô tả quy trình 7 bước từ thu thập đến tương tác và áp dụng cho một bài toán cụ thể.
- **Công cụ:** Biết ưu nhược điểm của Excel, Tableau, Power BI, Python, R và JavaScript để chọn đúng công cụ.
- **Thái độ & Vận dụng:** Trung thực, rõ ràng với dữ liệu; áp dụng trong Khoa học dữ liệu.

### 1.1 Giới thiệu về trực quan hóa dữ liệu
- **Khái niệm:** Biểu diễn dữ liệu và thông tin dưới dạng đồ họa (biểu đồ, bản đồ, đồ thị, dashboard) để con người dễ quan sát; chuyển dữ liệu từ số và chữ sang các kênh thị giác (vị trí, độ dài, màu sắc, kích thước, hình dạng). Hai mảng chính: *khám phá dữ liệu* và *truyền đạt thông tin*. Là cầu nối giữa dữ liệu thô, người phân tích và người ra quyết định.
- **Lịch sử phát triển:**
  - `1786`: William Playfair phát minh biểu đồ đường và biểu đồ cột để trình bày số liệu kinh tế.
  - `1854`: John Snow vẽ bản đồ các ca tả ở London, chỉ ra nguồn nước bị ô nhiễm.
  - `1869`: Charles Minard biểu diễn chiến dịch Nga của Napoléon trên một hình với nhiều biến.
  - `1977 đến nay`: Tukey đề xuất EDA; sau năm 2000 xuất hiện dữ liệu lớn, công cụ BI và dashboard tương tác.
- **Vì sao cần trực quan hóa?**
  - *Bộ tứ Anscombe:* Bốn tập dữ liệu có cùng trung bình, phương sai và hệ số tương quan nhưng hình dạng hoàn toàn khác nhau — chỉ dựa vào chỉ số thống kê dễ bỏ sót ngoại lệ hoặc quan hệ phi tuyến.
  - Giúp tóm lược dữ liệu lớn và giúp nhiều bên thống nhất nhanh hơn khi ra quyết định.
- **Cơ sở nhận thức thị giác:**
  - *Xử lý tiền chú ý:* Mắt người nhận ra màu, hướng, kích thước, vị trí trong vài trăm mili giây mà không cần tập trung.
  - *Thang Cleveland–McGill:* Độ chính xác khi đọc cao nhất với **vị trí chung**, rồi **độ dài**, **góc**, **diện tích**, và thấp nhất là **màu sắc**. Hệ quả: biểu đồ cột thường dễ đọc hơn biểu đồ tròn; dùng vị trí và độ dài cho dữ liệu quan trọng nhất.
- **Mã hóa thị giác và màu sắc:**
  - Kênh mã hóa: vị trí, độ dài, màu, kích thước, hình dạng, độ trong suốt.
  - Bảng màu: *Tuần tự* (dải màu đậm nhạt cho dữ liệu có thứ tự), *Phân kỳ* (hai màu trái ngược như teal và đỏ quanh mốc trung tâm như 0), *Phân loại* (tối đa 5–7 màu khác biệt, chú ý người mù màu).
- **Nguyên tắc thiết kế biểu đồ:**
  - *Trung thực:* Không cắt cụt trục, không bóp méo tỉ lệ; *Lie factor* (Tufte) gần 1.
  - *Tối giản:* Tối đa tỉ lệ *data-ink*, bỏ lưới dày, nền và hiệu ứng 3D không mang thông tin.
  - *Rõ ràng:* Có tiêu đề nêu kết luận, nhãn trục, đơn vị và nguồn dữ liệu.
  - *Phù hợp người xem:* Chọn mức chi tiết theo đối tượng (lãnh đạo, chuyên gia, công chúng).
- **Ứng dụng:** Kinh doanh (KPI, doanh thu, phễu bán hàng, hành vi khách hàng), Y tế (dịch tễ, xét nghiệm, điều trị), Tài chính (giá, rủi ro, giao dịch bất thường), Khoa học & Giáo dục (mô phỏng, khí hậu, thiên văn).

### 1.2 Phân loại trực quan hóa dữ liệu
- **4 tiêu chí phân loại:**
  1. *Theo mục đích:* **Khám phá (exploratory)** (chưa biết câu trả lời, vẽ nhanh nhiều biểu đồ) vs. **Giải thích (explanatory)** (đã có kết luận, ít biểu đồ nhưng tinh chỉnh kỹ, nhấn màu để thuyết phục).
  2. *Theo hình thức:* **Tĩnh** (báo cáo in, bài báo, slide; kiểm soát hoàn toàn bố cục) vs. **Tương tác** (dashboard, web; lọc, zoom, tooltip, drill-down theo nguyên tắc Shneiderman: *tổng quan trước, phóng to và lọc, rồi xem chi tiết khi cần*).
  3. *Theo kiểu dữ liệu:* Số, phân loại, thời gian, không gian, mạng, phân cấp, văn bản.
  4. *Theo thông điệp:*
     - *So sánh và xu hướng:* Cột/thanh (sắp xếp theo giá trị, trục bắt đầu từ 0), đường (xu hướng theo thời gian, có thể cắt trục nhưng ghi rõ), vùng và vùng chồng.
     - *Phân phối:* Histogram, boxplot (trung vị, tứ phân vị, ngoại lệ), violin, density.
     - *Quan hệ:* Scatter, bubble (thêm kích thước cho biến thứ 3, màu cho biến thứ 4), đường xu hướng. Cảnh báo: *tương quan không đồng nghĩa nhân quả*.
     - *Thành phần và tỉ trọng:* Tròn/vành khuyên (tối đa 5 phần, tổng 100%; tránh 3D), cột chồng, treemap.
     - *Địa lý, mạng, phân cấp, văn bản:* Choropleth, bản đồ điểm, heatmap địa lý; đồ thị nút–cạnh; cây, sunburst, dendrogram; word cloud.

### 1.3 Quy trình xử lý trực quan hóa (7 bước theo Ben Fry)
Quy trình có **tính lặp** (không tuyến tính), xuất phát từ câu hỏi và người xem:
1. **Thu thập (Acquire):** CSV, Excel, SQL, API, web scraping, dữ liệu mở; kiểm tra độ tin cậy, cập nhật, quyền sử dụng, lưu nguồn/thời điểm/phiên bản để tái lập, tuân thủ riêng tư.
2. **Cấu trúc hóa (Parse):** Biến dữ liệu thô thành bảng gọn (*tidy data*: mỗi biến 1 cột, mỗi quan sát 1 dòng, mỗi loại đơn vị 1 bảng); gán đúng kiểu, chuẩn hóa tên cột, đơn vị, ngày giờ, mã hóa ký tự.
3. **Lọc và làm sạch (Filter):** Xử lý giá trị thiếu, trùng lặp, sai định dạng, giá trị vô lý; phát hiện ngoại lệ bằng quy tắc IQR hoặc z-score và ghi chú lý do giữ/loại.
4. **Khai phá (Mine):** Thống kê mô tả (trung bình, trung vị, độ lệch chuẩn, phân vị), tương quan (Pearson tuyến tính, Spearman thứ hạng), tổng hợp/nhóm/pivot để tìm câu chuyện chính.
5. **Biểu diễn (Represent):** Từ câu hỏi → kiểu dữ liệu → kênh mã hóa → chọn loại biểu đồ, vẽ nhiều phương án thử nghiệm.
6. **Tinh chỉnh (Refine):** Tiêu đề nêu kết luận chính; giảm nhiễu (bỏ viền, lưới thừa, chú giải không cần); ghi nhãn trực tiếp; nhấn màu (đỏ cho điểm cần chú ý, teal/xám cho phần còn lại); kiểm tra lại số liệu, đơn vị, nguồn.
7. **Tương tác (Interact):** Tooltip, lọc và zoom, drill-down, liên kết giữa các biểu đồ (*brushing and linking*).

### 1.4 Công cụ, phần mềm trực quan hóa
- **Dải công cụ:** Từ không lập trình (Excel, Tableau, Power BI, Looker Studio) đến lập trình (Python, R/`ggplot2`/`tidyverse`/`Shiny`, JavaScript: D3.js, Chart.js, ECharts, Plotly.js).
- **Hệ sinh thái Python:** `pandas` (xử lý bảng), `matplotlib` (nền tảng, tùy biến sâu), `seaborn` (thống kê, cú pháp ngắn), `plotly` / `bokeh` / `altair` (tương tác web).
- **Tiêu chí lựa chọn:** Kỹ năng, quy mô/nguồn dữ liệu, nhu cầu tương tác & chia sẻ, chi phí/bản quyền.

### 1.5 Kỹ thuật trực quan hóa trong Khoa học dữ liệu
- **EDA (Khám phá dữ liệu):** Một biến (histogram, boxplot, violin), hai biến (scatter, boxplot theo nhóm, cột chồng), nhiều biến (pair plot, heatmap tương quan, parallel coordinates).
- **Tương quan & chọn đặc trưng:** Heatmap ma trận tương quan (teal dương, đỏ âm); loại biến tương quan quá cao để tránh đa cộng tuyến; cần kiến thức miền để diễn giải.
- **Dữ liệu nhiều chiều & giảm chiều:** PCA (tuyến tính, giữ phương sai lớn nhất), t-SNE & UMAP (phi tuyến, giữ cấu trúc láng giềng để thấy cụm), parallel coordinates, radar chart.
- **Đánh giá mô hình:** Confusion matrix, ROC & AUC, learning curve (phát hiện overfitting), feature importance.
- **Dashboard & kể chuyện bằng dữ liệu:** Dashboard gồm vài KPI chính, biểu đồ liên kết, bộ lọc rõ; cấu trúc kể chuyện: **Bối cảnh → Vấn đề → Bằng chứng → Hành động đề xuất**; đặt thông tin quan trọng ở góc trên trái.
- **Những sai lệch thường gặp:** Trục cắt cụt trên biểu đồ cột, biểu đồ 3D, quá nhiều màu, thiếu ngữ cảnh (nguồn, đơn vị, khoảng thời gian).

---

## Chương 2: Quy trình xử lý trực quan hóa dữ liệu

*(Tham khảo chính từ Schwabish (2021), Better Data Visualizations — tóm lược theo bài giảng.)*

**Mục tiêu học tập:** Nêu 7 bước từ phân tích vấn đề đến tạo biểu đồ; hiểu vai trò từng bước; chọn đúng biểu đồ theo tình huống; phát hiện biểu đồ gây hiểu lầm và đề xuất thiết kế lại.

### 2.1 Phân tích vấn đề
- **Bắt đầu từ người xem, không từ dữ liệu:** Xác định người xem là ai (lãnh đạo, nhà hoạch định chính sách, đồng nghiệp, công chúng), họ cần biết gì và sẽ làm gì (ra quyết định, phê duyệt, hay tìm hiểu).
- **Đặt câu hỏi nghiên cứu rõ ràng:** Cụ thể, đo được, có phạm vi thời gian và đối tượng, dẫn tới một loại so sánh; viết trước giả thuyết kỳ vọng.
- **Khung hình thức và chức năng:** Trục chức năng (*Giải thích* vs. *Khám phá*) × Trục hình thức (*Tĩnh* vs. *Tương tác*, với *Hoạt hình* ở giữa).
- **Nền tảng hiển thị:** Máy tính hay điện thoại; nguyên tắc Shneiderman (1997).
- **Case study:** Gapminder (Hans Rosling, TED 2014) — dùng scatter động về tỉ lệ sinh và tuổi thọ (1962–2003) xuất phát từ câu hỏi lớn.

### 2.2 Thu thập, tạo dữ liệu
- **Nguồn dữ liệu:** Sơ cấp (khảo sát, thí nghiệm, cảm biến, nhật ký) vs. Thứ cấp (thống kê nhà nước, tổ chức, dữ liệu doanh nghiệp, dữ liệu mở như World Bank, Gapminder, UN, Kaggle, cơ quan thống kê quốc gia).
- **Phương pháp thu thập:** Khảo sát (mẫu đại diện, câu hỏi trung lập, thang đo thống nhất), API, web scraping (chỉ khi được phép), thí nghiệm (A/B testing).
- **Tự tạo dữ liệu:** Dự án *Dear Data* (Giorgia Lupi & Stefanie Posavec), *Observe, Collect, Draw*.
- **Chất lượng & đạo đức:** Tránh sai lệch mẫu, ẩn danh hóa dữ liệu cá nhân, kiểm tra bản quyền, minh bạch nguồn, cỡ mẫu và hạn chế.
- **Case study:** Bản đồ chấm dân số Mỹ 2010 (308 triệu dân, Dustin Cable) — chỉ dùng dữ liệu vẫn hiện rõ địa hình phân bố dân cư.

### 2.3 Làm sạch dữ liệu
- **Nguyên tắc:** *"Rác vào, rác ra"*; không sửa dữ liệu gốc, làm trên bản sao và ghi lại mọi thay đổi.
- **Giá trị thiếu (missing values):** Đếm ô trống theo cột, vẽ heatmap vị trí thiếu; xóa dòng (khi thiếu ít và ngẫu nhiên) hoặc điền giá trị (trung bình/trung vị cho số, phổ biến nhất cho phân loại) và ghi chú.
- **Chuẩn hóa & trùng lặp:** Thống nhất định dạng ngày tháng, tên địa danh, số/đơn vị; xóa bản ghi trùng lặp.
- **Phát hiện ngoại lệ (outliers):** Quy tắc **IQR** ($\text{IQR} = Q_3 - Q_1$; ngoài $[Q_1 - 1.5\times\text{IQR},\; Q_3 + 1.5\times\text{IQR}]$ là nghi ngờ ngoại lệ). Dùng boxplot/scatter để phát hiện; lỗi nhập liệu thì sửa, giá trị thật hiếm thì giữ và giải thích.
- **Cấu trúc dữ liệu gọn (tidy data):** Mỗi biến một cột, mỗi quan sát một dòng; phân biệt dạng rộng (*wide*) và dạng dài (*long*), chuyển đổi bằng `pivot` / `melt` / `unpivot`.
- **Case study:** Bộ tứ Anscombe — luôn vẽ biểu đồ sơ bộ ngay sau bước làm sạch.

### 2.4 Chọn loại biểu đồ
- **Kiểu dữ liệu quyết định cách vẽ:**
  - *Định tính (categorical):* Danh nghĩa (*nominal*) và Thứ tự (*ordinal*).
  - *Định lượng:* Rời rạc (*discrete*) và Liên tục (*continuous*: *interval* không có 0 thực, *ratio* có 0 tuyệt đối).
- **8 họ biểu đồ theo chức năng (Schwabish):**
  1. *So sánh danh mục:* Biểu đồ cột (trục luôn bắt đầu từ 0, sắp xếp giảm dần trừ khi có thứ tự tự nhiên), dot plot (khi giá trị gần nhau và xa 0, hoặc nhãn dài), cột cụm (*grouped*), cột chồng (*stacked*), diverging bar (cho thang Likert).
  2. *Thời gian:* Biểu đồ đường (nhiều mốc, gắn nhãn trực tiếp, tối đa 4–5 đường), slope chart (2 mốc trước–sau), area/stacked area, sparkline, Gantt/timeline.
  3. *Phân phối:* Histogram (thử nhiều độ rộng khoảng *bin width*), boxplot, violin, ridgeline.
  4. *Quan hệ:* Scatter (trục không nhất thiết từ 0 nếu 0 không có nghĩa), bubble, ma trận tương quan (heatmap), mạng và cây.
  5. *Địa lý:* Choropleth (bảng màu tuần tự, dùng tỉ lệ thay vì số thô khi vùng khác nhau về diện tích/dân số; tránh bảng màu phân kỳ khi không có mốc giữa), cartogram, proportional symbol.
  6. *Thành phần của tổng:* Tròn/pie (chỉ hợp lý khi 2–4 lát và lát chính gần 25%, 50%, 75%), cột chồng, treemap, sunburst.
  7. *Định tính & bảng.*
- **Những lựa chọn cần tránh:** Cột 3D, biểu đồ tròn quá 5 lát, hai trục y (*dual axis* dễ gợi quan hệ giả), gradient và kẻ lưới dày.

### 2.5 Chọn công cụ
- **Tiêu chí:** Kỹ năng lập trình, quy mô dữ liệu, nhu cầu người xem (bản in, dashboard, web), chi phí.
- **Công cụ & tài nguyên:** Excel (PivotChart), Tableau (*Practical Tableau*), Power BI, R (*R for Data Science*, Healy), Python (*Python Crash Course*), D3.js (*Fullstack D3*).
- **Thư viện tra cứu & cộng đồng:** Chartmaker Directory, Data Viz Project, Graphic Continuum, FT Visual Vocabulary; Makeover Monday, Tidy Tuesday, Storytelling with Data Challenge, Observe Collect Draw.

### 2.6 Chuẩn bị dữ liệu cho biểu đồ
- **Biến đổi:** Tổng hợp (*aggregation*: cộng, đếm, trung bình), đổi sang **tỉ lệ (*rate*)** khi so sánh nhóm khác quy mô (ví dụ: ca trên 100.000 dân), đối chiếu tổng sau nhóm với tổng gốc.
- **Sắp xếp, nhóm & rút gọn:** Xếp theo giá trị; gộp các nhóm nhỏ (ví dụ < 3%) vào "Khác"; chỉ giữ chuỗi quan trọng.
- **Thang đo & đường gốc:** Biểu đồ cột luôn có gốc 0 (*zero baseline*, tránh *truncated axis*); scatter/đường có thể cắt trục nếu ghi rõ; thang log (*log scale*) dùng khi dữ liệu trải qua nhiều bậc độ lớn và phải ghi chú rõ; small multiples dùng cùng thang trục.
- **Bảng màu & tiếp cận (accessibility):** Tuần tự, phân kỳ, phân loại (5–7 màu), *start with gray*; thiết kế *style guide* (tiêu đề, trục, nhãn, nguồn, chú thích, phông chữ nhất quán); đảm bảo tương phản và thân thiện với người mù màu.

### 2.7 Tạo biểu đồ — Năm hướng dẫn cho biểu đồ tốt hơn (Schwabish)
1. **Hướng dẫn 1 — Cho thấy dữ liệu (*Show the data*):** Làm nổi các giá trị phục vụ lập luận thay vì vẽ tất cả cùng một mức (ví dụ: bản đồ chấm dân số; biểu đồ 50 nước chỉ tô màu 6 nước quan tâm, 44 nước còn lại để nền xám).
2. **Hướng dẫn 2 — Giảm nhiễu (*Reduce clutter*):** Tăng tỉ lệ *data-ink*; loại bỏ nền chuyển màu, lưới đậm, viền thừa, chiều thứ ba (ví dụ: sửa cột 3D thành cột phẳng 2D có nhãn giá trị).
3. **Hướng dẫn 3 — Gắn chữ với hình (*Integrate graphics and text*):**
   - Bỏ chú giải tách rời khi có thể, dùng **nhãn trực tiếp (*direct labeling*)** thẳng hàng và khớp màu với dữ liệu (nếu buộc dùng chú giải, giữ thứ tự khớp dữ liệu).
   - Dùng **tiêu đề chủ động (*active title*)** nêu kết luận như tít báo thay cho tiêu đề mô tả chung chung.
   - Thêm **chú thích giải thích** tại đỉnh, đáy, ngoại lệ hoặc hướng dẫn cách đọc biểu đồ phức tạp (ví dụ: Neil Richards, Los Angeles Times).
4. **Hướng dẫn 4 — Tránh biểu đồ spaghetti:** Tách thành **small multiples** (lưới ô nhỏ cùng thang, cùng trục, cùng màu). Tránh 3 cạm bẫy: sắp xếp thứ tự logic, giữ nhất quán bố cục/màu, không nhồi quá nhiều chữ trong từng ô.
5. **Hướng dẫn 5 — Bắt đầu từ màu xám (*Start with gray*):** Vẽ toàn bộ dữ liệu bằng màu xám trước, sau đó chỉ tô màu và làm dày nét cho phần cần nhấn mạnh kèm nhãn trực tiếp.
- **Quy trình 4 bước tạo biểu đồ:** (1) Vẽ bản nháp bằng dữ liệu sạch → (2) Chuyển mọi thứ sang xám → (3) Nhấn màu, gắn nhãn trực tiếp, thêm tiêu đề chủ động → (4) Kiểm tra với người xem, xuất ảnh độ phân giải cao.

---

## Chương 3: Xử lý và trực quan hóa dữ liệu với Python

**Chuẩn bị & quy ước:** `pip install pandas seaborn plotly` (xuất ảnh tĩnh Plotly cần `kaleido`). Quy ước import: `pd`, `sns`, `plt`, `px`, `go`. Dữ liệu mẫu thực hành: `tips`, `penguins`, `titanic`, `gapminder`, `iris`, `mpg`, `flights`, `diamonds`.

### 3.1 Trực quan hóa dữ liệu sử dụng Matplotlib
- **3.1.1 Cấu trúc:** `Figure` (khung chứa) → `Axes` (vùng vẽ gồm 2 trục `Axis`, dữ liệu, tiêu đề, nhãn) → `Artist` (mọi thành phần hiển thị: đường, chữ, tick, spine, grid, legend). Hai cách dùng: `pyplot` (thử nghiệm nhanh) và **hướng đối tượng** (`fig, ax = plt.subplots()`, khuyến nghị cho báo cáo và dự án).
- **3.1.2 Các loại biểu đồ (11 loại + tổng hợp):**
  - `ax.plot` (line plot, tối đa 4–5 đường), `ax.fill_between` / `ax.stackplot` (area plot), `ax.hist` (histogram), `ax.bar` / `ax.barh` + `ax.bar_label` (bar chart, gốc 0, sắp xếp theo giá trị), `ax.pie` (pie chart, tối đa ~5 phần), `ax.boxplot` (box plot), `ax.scatter` (scatter plot, `set_xscale("log")`, `alpha`), `ax.scatter(..., s=...)` (bubble plot), `PyWaffle` (`Waffle`, lưới 5×20), `wordcloud` (`WordCloud` + `ax.imshow`, tiếng Việt cần `font_path` và loại stopwords), regression plot (`np.polyfit` + $R^2$).
- **3.1.3 Bố cục & tùy chỉnh:** `plt.subplots`, `GridSpec`, `tight_layout()` / `layout="constrained"`; `ax.annotate`, `ax.axvspan`, `ax.axhline`; `set_xlim`/`set_ylim`, `set_yscale("log")`, `FuncFormatter`, `ax.twinx()` (trục kép — dùng cẩn thận); `plt.style.use(...)` và `plt.rcParams.update(...)`.
- **3.1.4 Lưu hình & backend:** `fig.savefig(..., dpi=300, bbox_inches="tight")`; PNG cho web/slide, JPG cho dung lượng nhỏ, PDF/SVG vector cho bài báo/in ấn; backend `Agg` (máy chủ), `inline` (Jupyter), `qtagg`/`tkagg`. So sánh Matplotlib (nền tảng, hình in), Seaborn (thống kê, EDA nhanh), Plotly (tương tác, dashboard).

### 3.2 Trực quan hóa dữ liệu bản đồ sử dụng Folium
- **Giới thiệu:** Tạo bản đồ tương tác dựa trên Leaflet.js, xuất tệp HTML (`m.save("ten.html")`). Lưu ý thứ tự tọa độ của `folium.Map` là `[vĩ độ, kinh độ]`; các lớp nền `tiles`: `"OpenStreetMap"`, `"CartoDB positron"`, `"CartoDB dark_matter"`.
- **3.2.1 Map with Markers:** `folium.Marker` (kèm `popup`, `tooltip`, `folium.Icon`), `folium.CircleMarker` (bán kính pixel theo độ lớn số đo), `folium.plugins.MarkerCluster` (gom cụm khi có nhiều điểm).
- **3.2.2 Choropleth Maps:** `folium.Choropleth(geo_data, data, columns, key_on, fill_color, bins, nan_fill_color, legend_name)`. Cần chuẩn bị GeoJSON, nối khóa chuẩn (như mã ISO) để tránh lệch tên, và ưu tiên dùng tỉ lệ trên đầu người.

### 3.3 Trực quan hóa dữ liệu sử dụng Seaborn
- **Giới thiệu:** Thư viện thống kê (Michael Waskom) xây trên Matplotlib, tích hợp chặt với `pandas`, hoạt động tốt nhất với dữ liệu **dạng dài (tidy)**. Hai mức API: *axes-level* (vẽ lên một `Axes`) và *figure-level* (`catplot`, `displot`, `lmplot`, `relplot` tạo `FacetGrid`).
- **3.3.1 Categorical Plots:**
  - *Hiển thị điểm:* `stripplot` (`jitter`), `swarmplot`.
  - *Phân phối:* `boxplot`, `violinplot` (`inner="quart"`), `boxenplot` (dữ liệu hàng nghìn điểm).
  - *Ước lượng & đếm:* `barplot` (trung bình + CI 95%), `pointplot`, `countplot` (đếm tần suất).
  - *Figure-level:* `catplot(..., kind=..., col=..., row=...)`.
- **3.3.2 Distribution Plots:** `histplot` (`bins`, `binwidth`, `stat`, `kde=True`, `multiple`), `kdeplot` (`bw_adjust`, `common_norm`), `ecdfplot` (không phụ thuộc bin), `rugplot`, `jointplot` (`kind="scatter"|"kde"|"hist"|"hex"|"reg"|"resid"`), `pairplot` (`vars`, `hue`, `diag_kind`, `corner=True`), `displot` (figure-level).
- **3.3.3 Regression Plots:** `regplot` (axes-level, hỗ trợ `order=2`, `robust=True`, `lowess=True`, `ci=None`), `lmplot` (figure-level theo `hue`, `col`, `row`), `residplot` (kiểm tra phần dư). Lưu ý: Seaborn chỉ vẽ, hệ số và p-value cần `statsmodels`.
- **3.3.4 Tùy chỉnh biểu đồ:** `sns.set_theme`, `style` (`darkgrid`, `whitegrid`, `dark`, `ticks`), `set_context` (`"paper"`, `"notebook"`, `"talk"`, `"poster"` + `font_scale`), `palette` (phân loại `"deep"`/`"Set2"`, tuần tự `"crest"`/`"mako"`, phân kỳ `"vlag"`/`"coolwarm"`, hoặc danh sách mã màu tùy chỉnh), `sns.despine()`, `sns.move_legend`, `FacetGrid` (`height`, `aspect`, `col_wrap`, `sharex`, `sharey`), `savefig` (DPI 300 / PDF).

### 3.4 Trực quan hóa dữ liệu sử dụng Plotly
- **3.4.1 Cấu trúc:** Chạy trên `plotly.js`; 3 mức API: `plotly.express` (`px`, vẽ nhanh từ DataFrame), `plotly.graph_objects` (`go`, tùy biến chi tiết, `make_subplots` với `secondary_y=True`), và cấu trúc `Figure` dạng JSON (`data` gồm traces, `layout`, `frames`, `config`). Template (`"plotly_white"`, `"simple_white"`, `"plotly_dark"`...), `colorway`, `write_html`, `write_image` (cần `kaleido`), `to_json`.
- **3.4.2 Các loại biểu đồ Plotly:** `px.line`, `px.bar` (`barmode="group"|"stack"`), `px.scatter` (`size`, `color`, `symbol`, `marginal_x`/`marginal_y`, `trendline="ols"`), `px.histogram` / `px.box` / `px.violin` (`points="all"`, `box=True`), `px.pie` (`hole=0.5` cho donut) / `px.treemap` / `px.sunburst` (`path`), `px.imshow` (`text_auto=True`) / `px.density_heatmap`, `px.choropleth` / `px.scatter_geo` / `density_mapbox`, `px.scatter_3d` (chỉ để khám phá, không dùng báo cáo số liệu) và `candlestick`.
- **3.4.3 Tương tác với biểu đồ:** `hover_name`, `hover_data`, `hovertemplate`; zoom, pan, `rangeslider_visible=True`, `rangeselector`; `updatemenus` (dropdown, nút bấm), `sliders`, `animation_frame`; chia sẻ qua `write_html` hoặc xây ứng dụng web tương tác với **Dash** (`layout` + `callback`).
