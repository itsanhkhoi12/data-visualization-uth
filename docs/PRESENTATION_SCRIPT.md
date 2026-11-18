# Kịch bản trình bày — Khám phá dữ liệu đa doanh nghiệp `public_test`

- **Motivation/Background**: Bốn notebook Hồi 1–4 trong [`notebook/`](../notebook) đã tạo ra một lượng lớn phát hiện, bảng số liệu và biểu đồ, nhưng chưa có một kịch bản trình bày thống nhất. Đồ án nhóm cần một tài liệu để dựng slide và biểu đồ mà không phải tự tìm lại số liệu trong từng ô notebook.
- **Purpose**: Tài liệu này dựng lại toàn bộ 4 hồi thành một câu chuyện theo cấu trúc *Bối cảnh → Vấn đề → Bằng chứng → Kết luận*, mỗi slide có sẵn thông điệp chủ động, số liệu cần đưa lên và gợi ý biểu đồ lấy từ chính các notebook đã sinh ra. Mọi chỉ số suy ra đều kèm **công thức + cách tính** để người xem tự kiểm chứng được; Slide 13–14 chỉ nêu **kết luận**, **hạn chế** và **hướng phát triển dự kiến**, không nói về quy trình/pipeline.
- **Overview Pipeline**: Nội dung được đối chiếu trực tiếp với các bảng artifact do 4 notebook sinh ra (`catalog_14.csv`, `representative_selection.csv`, `quality_and_iqr_report.csv`, `normalized_cross_metrics.csv`, `operating_rhythm_summary.csv`, `tet_window_comparison.csv`, `cross_business_limitations.csv`) và với [`chart_audit_checklist.csv`](../artifacts/guided_eda/phase4_storytelling/tables/chart_audit_checklist.csv) — mọi con số trong kịch bản đều truy được về một bảng nguồn.
- **Detailed Plan**: §1 Nguyên tắc viết kịch bản · §2 Slide 01–14 theo 4 hồi (mỗi slide có khối *Công thức / Cách tính* khi có chỉ số suy ra) · §3 Sổ ký hiệu, sổ công thức & bảng tra cứu nhanh · §4 Những gì *không* được nói.
- **References**: [`docs/DEFINE-THE-PROBLEM.md`](../docs/DEFINE-THE-PROBLEM.md), [`docs/SUBJECT-CONTENT.md`](../docs/SUBJECT-CONTENT.md), [`docs/PROJECT_ROADMAP.md`](../docs/PROJECT_ROADMAP.md), [`notebook/README.md`](../notebook/README.md), [`data/public_test/rulebook.md`](../data/public_test/rulebook.md), [`data/public_test/calendar.csv`](../data/public_test/calendar.csv)
- **Created**: 2026-11-18T00:45:00+07:00
- **Last Updated**: 2026-11-18T01:40:00+07:00

[STATUS: ACTIVE]

---

## Mục lục

- [1. Nguyên tắc viết kịch bản](#1-nguyên-tắc-viết-kịch-bản)
- [2. Kịch bản slide 01–14](#2-kịch-bản-slide-0114)
  - [Hồi 1 — Bối cảnh (Slide 01–03)](#hồi-1--bối-cảnh-slide-0103)
  - [Hồi 2 — Vấn đề & Bằng chứng vi mô (Slide 04–07)](#hồi-2--vấn-đề--bằng-chứng-vi-mô-slide-0407)
  - [Hồi 3 — Bằng chứng đối chiếu (Slide 08–11)](#hồi-3--bằng-chứng-đối-chiếu-slide-0811)
  - [Hồi 4 — Kết luận & Hạn chế/Hướng phát triển (Slide 12–14)](#hồi-4--kết-luận--hạn-chếhướng-phát-triển-slide-1214)
- [3. Sổ ký hiệu & tra cứu nhanh](#3-sổ-ký-hiệu--tra-cứu-nhanh)
- [4. Những gì không được nói trên slide](#4-những-gì-không-được-nói-trên-slide)

---

## 1. Nguyên tắc viết kịch bản

**Một slide = một thông điệp.** Tiêu đề slide viết ở dạng *kết luận* ("Cuối tuần không phải lúc nào cũng bận"), không phải dạng *chủ đề* ("Phân tích cuối tuần"). Nếu không viết được tiêu đề kết luận thì slide đó chưa có ý.

**Mọi con số trên slide đều phải trả lời được "này là gì?".** Kèm theo mỗi con số: nguồn, cỡ mẫu `n`, khoảng thời gian, đơn vị. Đây là quy ước đã kiểm định ở Hồi 4 (24/24 ảnh xuất bản đạt tiêu chí "có đơn vị – nguồn – `n` – khoảng ngày").

**Biểu đồ phải trả lời câu hỏi của slide, không phải minh hoạ cho có.** Mỗi gợi ý biểu đồ bên dưới mô tả: *dữ liệu cần*, *loại biểu đồ*, *điều cần nhấn mạnh*. Không gắn sẵn file — bạn có thể thay bằng ảnh khác nếu biểu đồ nói rõ hơn.

**Câu chuyện đi từ khái quát đến cụ thể rồi quay lại khái quát.** Hồi 1 mở rộng, Hồi 2–3 thu hẹp và tìm ra điểm gãy, Hồi 4 đóng lại bằng giới hạn và hành động.

**Giữ bỏ "cẩn thận" ở chỗ.** Người xem không cần biết mỗi bước đã kiểm tra gì; họ cần biết điều gì *không* chắc chắn. Giới hạn được nói ở slide 11–12, không rải khắp bài.

**Mọi chỉ số suy ra đều phải kèm công thức.** Nếu một con số là *tự tính* (index, lift, % thay đổi, tỷ trọng, tỷ lệ hủy, điểm chọn mẫu) thì phải ghi rõ: **công thức** → **định nghĩa từng thành phần** → **quy ước mẫu số** → **giới hạn của phép tính**. Nhờ vậy người xem kiểm chứng được, và ta không bị cáo buộc "tự ra số". Các công thức đã dùng được tổng hợp ở §3.3.

**Slide kết luận nói về *thứ đã biết*, không nói về *cách đã làm*.** Slide 13–14 chỉ nêu kết luận, hạn chế và hướng phát triển — không mô tả pipeline, không kể quy trình, không liệt kê tên file/artifact.

---

## 2. Kịch bản slide 01–14

### Hồi 1 — Bối cảnh (Slide 01–03)

---

#### Slide 01 — Mở đầu: 14 doanh nghiệp, 8 ngành, 1,3 triệu dòng dữ liệu — nhưng chúng không nói chuyện với nhau

**Thông điệp chủ động (tiêu đề slide):**
> 14 doanh nghiệp trong `public_test` lưu dữ liệu theo 4 định dạng khác nhau — không ai có cùng cửa sổ thời gian.

**Nội dung đưa lên slide:**

| Con số | Giá trị | Nguồn & ngữ cảnh |
|---|---|---|
| Doanh nghiệp trong `public_test` | 14 (`dev_001`–`dev_014`) | `catalog_14.csv`, `n = 14` |
| Tổng số dòng bản ghi vật lý | **1.327.598** | `catalog_14.csv`, tổng `total_record_rows`; đơn vị: dòng bản ghi (không đồng nhất cấp dòng/đơn) |
| Nhóm ngành | 8 (F&B 4 DN · Nhà thuốc 2 · Mẹ & Bé 2 · Phụ kiện số 2 · FMCG · Xây dựng · Sửa xe · 1 DN chưa xác định) | `catalog_14.csv` + `industry_classification.csv` |
| Định dạng lưu trữ | 9 `xlsx` · 3 `csv` · 1 `sqlite` · 1 `csv/xlsx` | `catalog_14.csv`, cột `recording_format` |
| Khoảng ngày quan sát | 2025-01-01 → 2026-09-30 | `temporal_coverage.csv`, cột `min_date`/`max_date` |

**Gợi ý biểu đồ:**
- **Sơ đồ dải "4 định dạng lưu trữ"** — 4 nhóm cột, mỗi nhóm 1 doanh nghiệp đại diện (Excel ghi tay → POS xuất file → CSV quan hệ → SQLite CSDL). Đây là diagram *minh hoạ khái niệm*, không phải biểu đồ dữ liệu — dùng để đặt vấn đề: "tại sao phải chuẩn hoá trước khi so sánh?"
- *Nếu muốn dùng biểu đồ thật:* **cột ngang đếm số doanh nghiệp theo định dạng lưu trữ** (`xlsx` 9 · `csv` 3 · `sqlite` 1), nhãn trực tiếp trên cột, bỏ chú giải, trục x là danh mục rời rạc nên không cần gốc 0.

**Ghi chú thuyết trình:**
> "Chúng ta bắt đầu từ 14 doanh nghiệp. Tổng cộng hơn 1,3 triệu dòng dữ liệu — nghe rất nhiều. Nhưng con số này là của cả 14 doanh nghiệp cộng lại, mà mỗi doanh nghiệp lại dùng một cách ghi khác nhau, và không doanh nghiệp nào có cùng khoảng thời gian. Nên câu hỏi đầu tiên không phải là 'dữ liệu nói cái gì', mà là 'dữ liệu này có so sánh được với nhau không'."

**Không nói ở slide này:** chi tiết từng doanh nghiệp; mức độ số hóa (`digitization_tier`); số dòng không parse được (để dành cho Slide 02).

---

#### Slide 02 — Vấn đề: 143 ngày lệch cutoff, 144.575 dòng không đọc được ngày

**Thông điệp chủ động:**
> Dữ liệu không thiếu — dữ liệu *dừng giữa chừng*, và ngày thì không phải lúc nào cũng ở đúng định dạng.

**Nội dung đưa lên slide:**

| Phát hiện | Con số | Chi tiết |
|---|---|---|
| Ngày kết thúc dữ liệu (`cutoff`) lệch nhau | **143 ngày** | Từ 2026-05-10 (`dev_005`) đến 2026-09-30 (`dev_014`); nguồn `readme_cutoff_date` |
| Cửa sổ chung của cả 14 DN | **314 ngày** (2025-07-01 → 2026-05-10) | Giao của 14 khoảng `min_date`–`max_date` |
| Dòng không parse được ngày ở Hồi 1 | **144.575** trên **7/14** doanh nghiệp | `temporal_coverage.csv`, cột `parse_failure_n`; đã **giải quyết triệt để ở Hồi 2** bằng cách chuẩn hoá theo từng DN → 0 dòng thiếu ngày trong 6 bảng Tidy |
| Ngày nằm ngoài lịch `calendar.csv` | 0 | `temporal_coverage.csv`, cột `n_outside_calendar` |
| Doanh nghiệp thiếu cả tháng | 0 | `temporal_coverage.csv`, cột `n_missing_months` |

**Cách tính (công thức):**

$$W_{\text{chung}} = \Big[\max_i \min(\text{date}_i),\ \min_i \max(\text{date}_i)\Big] \qquad |W_{\text{chung}}| = \min_i \max(\text{date}_i) - \max_i \min(\text{date}_i) + 1$$

$$\text{Độ lệch cutoff} = \max_i(\text{cutoff}_i) - \min_i(\text{cutoff}_i) = \text{2026-09-30} - \text{2026-05-10} = 143\ \text{ngày}$$

$$\text{Tỷ lệ dòng không parse được ngày} = \frac{N_{\text{dòng lỗi ngày}}}{N_{\text{tổng dòng}}} \times 100\%$$

- `cutoff_i` = ngày kết thúc ghi nhận trong README của doanh nghiệp *i* (14 giá trị, lấy max − min).
- `W_chung` = **giao** của 14 khoảng `[min_date, max_date]`: mỗi doanh nghiệp có một đoạn riêng, đoạn chung là phần **nằm trong tất cả** các đoạn. Vì `dev_005` kết thúc sớm nhất (2026-05-10) và một DN khác bắt đầu muộn nhất (2025-07-01) nên đoạn giao bị bóc hẹp còn 314 ngày.
- Tỷ lệ lỗi ngày được tính **riêng trên 14 DN** ở Hồi 1 (bộ quét dùng chung cho mọi định dạng). Ở Hồi 2, mỗi DN có bộ chuẩn hoá riêng (số thứ tự Excel, `DD/MM/YYYY`, suy ra năm từ tên tệp) → 6 bảng Tidy cuối cùng có **0 dòng thiếu ngày**. Hai con số này không mâu thuẫn: chúng đo trên hai phạm vi khác nhau.

**Gợi ý biểu đồ:**
- **Dải trục thời gian ngang (Gantt), mỗi doanh nghiệp một hàng** — thanh từ `min_date` đến `max_date`, đầu thanh có ký hiệu đánh dấu `readme_cutoff_date`, phần từ `cutoff` trở đi tô xám nếu cần. Đây là biểu đồ **mạnh nhất của Hồi 1** vì nó cho thấy trực quan ba sự thật cùng lúc: độ dài khác nhau, lệch cutoff, và cửa sổ giao nhau.
- *Thay thế:* **dot plot** trục ngang là ngày, mỗi doanh nghiệp một điểm + đường nối `min_date`–`max_date`, kèm vùng tô sáng 314 ngày giao nhau.

**Ghi chú thuyết trình:**
> "Đây là slide quyết định phần còn lại của dự án. Mỗi doanh nghiệp dừng dữ liệu ở một ngày khác nhau, chênh nhau tới 143 ngày. Nếu ta cứ lấy tổng doanh thu rồi xếp hạng, thì ta đang so một doanh nghiệp 17 tháng với một doanh nghiệp 9 tháng — sai ngay từ gốc."
> "Còn 144.575 dòng có ngày chưa đọc được ở Hồi 1 — ví dụ `dev_003` lệch tới 68.082 dòng. Chúng ta không xóa, mà đánh dấu và đi xử lý từng doanh nghiệp ở Hồi 2; kết quả là 6 bảng Tidy cuối cùng có **0 dòng thiếu ngày**."
> "Hệ quả: cửa sổ so sánh chung của cả 14 chỉ còn 314 ngày. Đây sẽ là khung thời gian dùng cho mọi so sánh về sau."

**Không nói ở slide này:** vì sao lại chọn 6 doanh nghiệp (Slide 03); quy tắc loại đơn hủy (Slide 05).

---

#### Slide 03 — Bối cảnh được thu hẹp: từ 14 xuống 6 doanh nghiệp đại diện

**Thông điệp chủ động:**
> 6/14 doanh nghiệp đại diện phủ được 5 nhóm ngành, 3 định dạng lưu trữ và cả trường hợp chỉ có dữ liệu cấp đơn.

**Nội dung đưa lên slide:**

| Doanh nghiệp | Ngành | Định dạng | Cấp ghi nhận | Vai trò đại diện |
|---|---|---|---|---|
| `dev_007` | F&B (lai FMCG) | csv | dòng hàng | Giàu thuộc tính nhất (5 chiều), quan sát dài nhất (596 ngày) |
| `dev_006` | Nhà thuốc | sqlite | dòng hàng | CSDL 17 bảng, cấu trúc phức tạp nhất (6 chiều nâng cao) |
| `dev_002` | F&B | xlsx (18 tệp/tháng) | dòng hàng | Bài toán gộp nhiều tệp về Tidy Data |
| `dev_009` | Chưa xác định | csv | **cấp đơn** | Trường hợp đặc thù: không có chi tiết hàng |
| `dev_011` | Phụ kiện & thiết bị số | xlsx | dòng hàng | Cấu trúc đơn giản, có bảng `Ghi tắt` |
| `dev_012` | Sửa chữa & phụ tùng xe | xlsx | dòng hàng | Quan hệ 1-nhiều (lượt xe ↔ thợ) |

**Quy tắc chọn (công khai trên slide):** 5 tiêu chí có trọng số — độ giàu thuộc tính 30% · quy mô 20% · độ dài thời gian 20% · độ phức tạp cấu trúc 15% · chi tiết dòng hàng 15%. Nguồn: `representative_selection.csv`.

**Công thức chấm điểm (đầy đủ, để mọi người kiểm chứng được):**

$$\text{Điểm}_i = \sum_{k} w_k \cdot \tilde{x}_{ik}, \qquad \sum_k w_k = 1$$

Với 5 tiêu chí và trọng số:

| Tiêu chí $k$ | Cột đo | Biến đổi | Trọng số $w_k$ |
|---|---|---|---|
| `richness` — độ giàu thuộc tính | `n_advanced_dims` | không | **0,30** |
| `scale` — quy mô bảng giao dịch chính | `main_record_rows` | $\log_{10}$ | **0,20** |
| `time` — độ dài khoảng quan sát | `span_days` | không | **0,20** |
| `structure` — độ phức tạp cấu trúc | `n_objects` | $\log_{10}$ | **0,15** |
| `granularity` — có chi tiết dòng hàng | `granularity == "line_item"` | không | **0,15** |

**Cách tính từng bước:**

1. **Biến đổi phi tuyến** (cho quy mô & cấu trúc): $y_{ik} = \log_{10}\big(\max(x_{ik}, 1)\big)$ — vì cả hai đều là số đếm và phân phối lệch mạnh; còn lại giữ nguyên.
2. **Chuẩn hoá Min–Max về \([0, 1]\)** trên toàn bộ 14 ứng viên:
$$\tilde{x}_{ik} = \frac{y_{ik} - \min_j y_{jk}}{\max_j y_{jk} - \min_j y_{jk}}$$
   (nếu \(\max_j y_{jk} = \min_j y_{jk}\) thì đặt \(\tilde{x}_{ik} = 0\) — trường hợp không có phân tán).
3. **Điểm có trọng số:** $\text{Điểm}_i = 0{,}30\tilde{x}_{i,\text{richness}} + 0{,}20\tilde{x}_{i,\text{scale}} + 0{,}20\tilde{x}_{i,\text{time}} + 0{,}15\tilde{x}_{i,\text{structure}} + 0{,}15\tilde{x}_{i,\text{granularity}}$.
4. **Điểm chỉ dùng để *đề xuất*, không dùng để *quyết định*:** chọn ứng viên điểm cao nhất **trong từng ngành**, rồi áp 3 quy tắc phủ để chốt tập 6 DN — vì điểm số không thể tự bảo đảm tính đại diện.

**Vì sao dùng trọng số chứ không dùng điểm bình thường:** mỗi tiêu chí đã được chuẩn hoá về \([0,1]\) nên cùng thang đo, không tiêu chí nào áp đảo chỉ vì đơn vị lớn hơn (số dòng luôn lớn hơn số ngày). Trọng số là **quy ước phân bổ mức độ quan tâm** — nó phản ánh rằng tính *đa dạng cấu trúc* quan trọng hơn *quy mô*, nên được công khai và để người xem sửa được.

**Gợi ý biểu đồ:**
- **Ma trận "6 DN đại diện × 5 đặc trưng"** — hàng là doanh nghiệp, cột là: ngành · định dạng · cấp ghi nhận · số chiều nâng cao · độ phủ. Tô đậm các ô khác nhau để thấy "tính đại diện" là về *độ đa dạng*, không phải về điểm số cao.
- *Thay thế:* **bảng ma trận heatmap** điểm chuẩn hóa 5 tiêu chí, 14 hàng (6 được chọn được viền đậm) — làm nổi hiệu quả "tại sao 6 này".

**Ghi chú thuyết trình:**
> "Không thể chuẩn hoá cả 14 doanh nghiệp trong thời gian có hạn, và cũng không cần. Chúng ta chọn 6 doanh nghiệp đại diện theo 5 tiêu chí có trọng số — mục tiêu là *độ đa dạng*, không phải *điểm số cao*. Chú ý `dev_009`: chỉ có dữ liệu cấp đơn, không có chi tiết hàng. Chúng ta cố ý giữ nó, vì bỏ nó đi thì ta mất câu hỏi 'khi thiếu chi tiết hàng thì ta còn so sánh được gì'."

---

### Hồi 2 — Vấn đề & Bằng chứng vi mô (Slide 04–07)

---

#### Slide 04 — Bài toán chuẩn hoá: "doanh thu" nghĩa là gì, và vì sao phải trả lời trước khi vẽ

**Thông điệp chủ động:**
> Nếu định nghĩa chỉ số sai, mọi biểu đồ phía sau đều sai theo — và sai một cách rất thuyết phục.

**Nội dung đưa lên slide:**

Quy tắc lấy từ [`rulebook.md`](../data/public_test/rulebook.md) và kết quả đối chiếu:

| Quy tắc | Vì sao quan trọng | Kiểm chứng |
|---|---|---|
| Chỉ tính đơn **không hủy, không trả hàng** (trả một phần → loại cả đơn); đơn đang giao vẫn tính | Quyết định doanh thu thật | `dev_006` **37.833** đơn & `dev_007` **32.022** đơn → doanh thu tính được **khớp 100%** tổng tiền ghi trên đơn gốc |
| Kỳ tính theo **ngày đặt**, không theo ngày giao hay ngày thu tiền | Tránh dồn/trễ đơn qua kỳ | Đã áp dụng cho toàn bộ bảng Tết ở Slide 10 |
| Giá trị đơn = tổng thành tiền dòng hàng (đã trừ giảm giá dòng), **không** trừ giảm giá toàn đơn, **không** cộng VAT, **không** gồm phí giao hàng | Dễ bị hiểu sai ở bảng "doanh thu" | Đối chiếu 100% ở trên |
| Quy về **đơn vị cơ bản** trước khi tổng hợp | Không so "hộp" với "cái" | `dev_002` **60** dòng hộp → cái · `dev_006` **10.917** dòng → đơn vị cơ bản, tính lại khớp `SLQuyDoi` của tệp **100,00%** dòng · `dev_007` **561** dòng thùng/két, tỉ lệ khớp quy ước README **100,00%** dòng |
| Phân biệt **luồng** (doanh thu) và **tồn** (tồn kho) | Không cộng dồn tồn kho theo ngày | Áp dụng ở toàn bộ chỉ số Hồi 3 |

**Gợi ý biểu đồ:**
- **Diagram quy trình 5 bước** dạng khối: *Đọc file gốc → Áp rulebook (loại đơn hủy/trả) → Quy đổi đơn vị → Chuẩn hoá ngày → Bảng Tidy 1 dòng = 1 quan sát*. Đây là diagram *quy trình*, giúp người xem hiểu vì sao mỗi con số phía sau đều đã qua bộ lọc.
- *Thay thế:* **sơ đồ đối chiếu trước–sau** — hai cột bảng (số đơn gốc vs số đơn hợp lệ) cho `dev_002` và `dev_006`, thể hiện bằng số tuyệt đối + phần trăm bị loại.

**Ghi chú thuyết trình:**
> "Trước khi vẽ bất kỳ biểu đồ nào, chúng ta phải trả lời: 'doanh thu' ở đây nghĩa là gì? Nếu mỗi doanh nghiệp hiểu khác nhau thì biểu đồ so sánh sẽ vừa sai vừa trông rất thuyết phục — đây là loại lỗi tệ nhất trong trực quan hóa. Rulebook định nghĩa rõ, và chúng ta đã đối chiếu được: với 37.833 đơn của `dev_006` và 32.022 đơn của `dev_007`, doanh thu tính ra khớp 100% với tổng tiền ghi trên đơn gốc."

---

#### Slide 05 — Chất lượng dữ liệu: 26.798 dòng bị gắn cờ — và chúng ta *không* xóa chúng

**Thông điệp chủ động:**
> Ngoại lệ IQR không phải lỗi — nó có thể là sự kiện vận hành thật, nên chỉ gắn cờ chứ không tự động loại.

**Nội dung đưa lên slide:**

| Doanh nghiệp | `n` dòng | Ngoại lệ trên (IQR) | Tỉ lệ | Quyết định |
|---|---|---|---|---|
| `dev_002` | 83.202 | 8.341 | 10,03% | Gắn cờ để đối chiếu, **không tự động xóa** |
| `dev_006` | 69.623 | 7.997 | 11,49% | như trên |
| `dev_007` | 116.497 | 9.289 | 7,97% | như trên |
| `dev_011` | 5.998 | 1.171 | 19,52% | như trên |
| **Tổng 4 DN có dòng hàng** | **275.320** | **26.798** | 9,73% | |
| Dòng đơn hủy/trả bị loại theo rulebook | | **7.154** | | Loại *có lý do*, khác với gắn cờ |

> Lưu ý: `dev_009` (cấp đơn) và `dev_012` không có dòng hàng nên không có chỉ số `line_amount` — tổng mẫu ở đây là 275.320 dòng hợp lệ của 4 DN còn lại.

Nguồn: `quality_and_iqr_report.csv`.

**Công thức phát hiện ngoại lệ (IQR — Interquartile Range):**

$$\text{IQR} = Q_3 - Q_1, \qquad Q_1 = P_{25}(x),\quad Q_3 = P_{75}(x)$$

$$\text{Rào dưới} \ L = Q_1 - 1{,}5 \times \text{IQR}, \qquad \text{Rào trên} \ U = Q_3 + 1{,}5 \times \text{IQR}$$

$$\text{Gắn cờ ngoại lệ} \iff x < L \ \text{hoặc}\ x > U$$

$$\text{Tỷ lệ gắn cờ} = \frac{N_{\text{giá trị ngoài } [L, U]}}{n} \times 100\%$$

**Cách tính và cách áp dụng (để con số không bị hiểu nhầm):**

1. **Tính riêng cho từng doanh nghiệp và từng chỉ số** — không gộp dữ liệu 6 DN vào một bộ `Q1/Q3`, vì thang giá trị của mỗi ngành khác nhau. Ba chỉ số được chạy IQR: `line_amount` (VNĐ/dòng), `qty_base` (đơn vị cơ bản) và `order_revenue` (VNĐ/đơn).
2. **Chỉ chạy trên giao dịch hợp lệ** (`is_valid == True`), và **không** chạy trên cột mã/ID.
3. **Mẫu số `n`** là số giá trị *quan sát được* của chỉ số đó ở DN đó (ví dụ `dev_011`: \(n = 5.998\) dòng hợp lệ).
4. **Trường hợp `IQR = 0` (suy biến):** khi hơn 75% giá trị bằng nhau (ví dụ `qty_base` của `dev_002` và `dev_011` — phần lớn đơn mua số lượng = 1) thì \(L = U = Q_1 = Q_3\), rào bẹo thành một điểm và mọi giá trị lớn hơn sẽ bị gắn cờ sai. Xử lý: **không gắn cờ hàng loạt**, đánh dấu `degenerate_iqr = True` và ghi rõ trong báo cáo.
5. **Hai loại xử lý khác nhau — đây là điểm quan trọng nhất của slide:**

| Loại | Điều kiện | Hành động | Cơ sở |
|---|---|---|---|
| Ngoại lệ IQR | \(x \notin [L, U]\) | **Gắn cờ để đối chiếu, giữ nguyên** | Chỉ là *dấu hiệu cần xem lại*; một đơn 500 triệu có thể là sự kiện vận hành thật |
| Đơn hủy / trả hàng | `is_valid == False` theo rulebook §1 | **Loại khỏi phân tích doanh thu** | Có quy định nguồn rõ ràng, không phải suy đoán |

$$\text{Số dòng bị loại (rulebook)} = 7.154 \qquad \text{Số dòng gắn cờ (IQR)} = 26.798$$

**Gợi ý biểu đồ:**
- **Boxplot (thang log) của giá trị đơn theo doanh nghiệp** — 4 hộp cạnh nhau, nhãn trực tiếp trên trục, đánh dấu rõ các điểm nằm ngoài rào IQR bằng chấm mảnh thay vì vẽ đè. Nếu cần nhiều điểm ngoại lệ hơn thì **nhóm theo ngưỡng** (số điểm vượt rào ×2, ×3) và ghi rõ trong chú thích.
- *Thay thế:* **cột ngang tỉ lệ % ngoại lệ** theo doanh nghiệp (7,97% → 19,52%), sắp xếp tăng dần, nhãn trực tiếp, trục x là danh mục.
- *Bổ sung (nếu có slide thời gian):* **heatmap vị trí thiếu dữ liệu** theo cột × doanh nghiệp để chỉ ra "thiếu tập trung ở các trường không áp dụng theo grain" — đây là dữ liệu thật, không phải dữ liệu thiếu do lỗi.

**Ghi chú thuyết trình:**
> "Có 26.798 dòng nằm ngoài rào IQR, tỉ lệ cao nhất 19,52% ở `dev_011`. Chúng ta *không* xóa chúng. Vì sao? Vì trong dữ liệu vận hành, một đơn 500 triệu có thể là một sự kiện thật — dịp Tết, sự kiện lớn. Xóa tự động là xóa câu chuyện. Nên chúng ta gắn cờ, để đối chiếu thủ công, và ghi lại quyết định này trong báo cáo chất lượng."
> "Ngược lại với 7.154 dòng đơn hủy/trả — loại đi là có lý do quy định trong rulebook. Hai loại xử lý khác nhau, và sự khác nhau đó phải được nói ra."

---

#### Slide 06 — Bằng chứng vi mô 1: mỗi ngành có một "món chủ lực" khác nhau

**Thông điệp chủ động:**
> Trong 6 doanh nghiệp, cơ cấu doanh thu tập trung rất khác nhau — và sự tập trung đó là đặc trưng của ngành, không phải ngẫu nhiên.

**Nội dung đưa lên slide:**

- **`dev_002` (F&B, cấp món):** món dẫn đầu *Trà đào cam sả (M)* — 3.973 dòng, **4,97%** doanh thu; *Trà sữa trân châu (M)* 4,67%; *Cà phê sữa (M)* 4,36%. Top 3 ≈ **14,0%** → cơ cấu phẳng, không món nào "gánh" doanh thu. (15 món được liệt kê, mỗi món 2,6–5,0%.)
- **`dev_006` (nhà thuốc):** 11 nhóm hàng — dẫn đầu *thực phẩm chức năng* **25,63%**, *vitamin khoáng chất* 22,18%, *tiêu hoá* 10,40%. Top 3 = **58,22%** → tập trung mạnh.
- **`dev_007` (F&B, cấp nhóm):** 11 nhóm hàng — *lẩu* **22,85%**, *chiên xào* 18,46%, *nướng* 11,32%. Top 3 = **52,63%**.
- **`dev_011` (phụ kiện):** chỉ 3 nhóm — *máy mới* **73,85%**, *máy cũ* 20,42%, *phụ kiện* 5,73% → tập trung gần như toàn bộ vào một nhóm.
- **`dev_009` (cấp đơn):** **không có** phân tích cơ cấu hàng — dữ liệu không có chi tiết dòng. Đây là hệ quả trực tiếp của việc `granularity = order_level`, và cần nói ra chứ không nên giấu.
- **`dev_012` (sửa xe):** phân bổ lượt xe gần đều giữa các thợ → không bị một thợ chi phối.

**Công thức tỷ trọng doanh thu:**

$$\text{Tỷ trọng doanh thu của nhóm hàng } c = \frac{R_c}{\sum_{c' \in C} R_{c'}} \times 100\% \qquad R_c = \sum_{\text{dòng hàng } \in c} \text{line\_amount}$$

$$\text{Tỷ trọng tích lũy (Top-}k\text{)} = \sum_{j=1}^{k} \text{Tỷ trọng}_j \quad (\text{cột } j \text{ đã sắp xếp giảm dần})$$

**Cách tính:**
- `R_c` = **tổng thành tiền dòng** (`line_amount`) của các dòng hợp lệ (`is_valid == True`) thuộc nhóm hàng `c`; **không** dùng `revenue` cấp đơn để cộng dồn (sẽ double-count khi một đơn có nhiều dòng).
- Mẫu số là **tổng của cùng nhóm hàng trong cùng doanh nghiệp** → mỗi DN có một bộ tỷ trọng cộng đúng 100%.
- Tỷ trọng tích lũy cho phép đọc "Top 3 chiếm bao nhiêu %" mà không phải cộng tay trên sân khấu.
- Với `dev_002` có **15 nhóm hàng**, `dev_006`/`dev_007` có **11 nhóm**, `dev_011` có **3 nhóm** → đây là lý do số nhóm khác nhau, và lý do *cùng ngành vẫn khác mô hình*.

**Điểm đáng nói:** cùng là F&B nhưng `dev_002` có cơ cấu phẳng (Top 3 ≈ 14%) còn `dev_007` tập trung (Top 3 ≈ 53%) → *cùng ngành, không cùng mô hình kinh doanh*. Đây là lý do Slide 09 không kết luận chung cho "F&B".

**Gợi ý biểu đồ:**
- **Cột ngang "top 5 mặt hàng theo doanh thu", sắp xếp giảm dần, mỗi doanh nghiệp một panel nhỏ (small multiples), cùng thang %** — đây là trường hợp *đúng* cho Schwabish #4: 6 doanh nghiệp vẽ chung một trục sẽ thành spaghetti.
- *Nếu chỉ kể một ngành:* **cột ngang top-N của `dev_002`** với nhãn trực tiếp tên món + % doanh thu, đường cơ sở mờ nếu cần.
- *Với `dev_009`:* **panel trống có chú thích giải thích** — dùng để chuyển thông điệp "giới hạn của dữ liệu" thành một phần của câu chuyện, thay vì chỉ nói bằng lời.

**Ghi chú thuyết trình:**
> "Khi nhìn cơ cấu doanh thu, các ngành khác nhau rõ rệt. Nhưng cái đáng nói nhất là *cùng ngành vẫn khác nhau*: `dev_002` có cơ cấu phẳng — 15 món dẫn đầu mỗi món chỉ chiếm 2,6–5%, không món nào gánh cả quán; còn `dev_007` cũng là F&B nhưng 3 nhóm hàng đầu đã chiếm 53%. Hai quán cà phê, hai mô hình kinh doanh khác nhau."
> "Tệp phụ kiện thì ngược lại: một nhóm 'máy mới' đã chiếm 74% doanh thu. Đây là dấu hiệu một tiệm bán theo dòng sản phẩm chủ lực, khác hẳn với tiệm sửa xe mà một thợ có thể chiếm phần lớn công suất."
> "Và `dev_009` thì không có cơ cấu hàng nào để vẽ — vì dữ liệu nó chỉ ở cấp hóa đơn. Ta giữ nguyên sự trống đó và ghi rõ lý do, thay vì bỏ qua nó."

---

#### Slide 07 — Bằng chứng vi mô 2: phân phối giá trị đơn lệch phải — vì sao phải dùng trung vị chứ không phải trung bình

**Thông điệp chủ động:**
> Giá trị đơn không phân phối đối xứng ở bất kỳ doanh nghiệp nào — nên "đơn trung bình" là một con số không tồn tại.

**Nội dung đưa lên slide:**

- Phân phối giá trị đơn lệch phải rõ rệt ở cả 6 doanh nghiệp (đặc biệt F&B: nhiều đơn nhỏ + ít đơn lớn).
- Vì vậy: **trung vị là mốc đại diện**, không phải trung bình. Khi nói "giá trị đơn đặc trưng", phải nói trung vị.
- Số liệu kiểm chứng (từ `quality_and_iqr_report.csv`, đơn vị cơ bản):
  - `dev_002`: `order_revenue` — Q1 = 39.000 · **trung vị = 55.000** · Q3 = 93.000 (VNĐ/đơn) → trung bình **71.095** cao hơn trung vị **16.095 VNĐ** vì đuôi phải kéo lên.
  - `dev_011`: Q1 = 150.000 · Q3 = 3.519.000 (IQR = 3.369.000) → khoảng giá trị đơn trải rộng gấp hơn 23 lần giữa phân vị 25% và 75%; ngoại lệ 15,67%.
  - Ảnh hưởng tới Hồi 3: khi so sánh giữa các doanh nghiệp, chỉ dùng **%/Index/TB-ngày**, không dùng giá trị đơn tuyệt đối.

**Công thức các đại lượng mô tả:**

$$\text{Trung vị} = \tilde{x}_{n/2} \quad \text{(trung vị mẫu, } n \text{ sắp xếp tăng dần)} \qquad \text{Trung bình} = \frac{1}{n}\sum_{i=1}^{n} x_i$$

$$\text{Khoảng tứ phân vị} = Q_3 - Q_1, \qquad \text{Hệ số lệch} = \frac{Q_3 - Q_1}{Q_1 + Q_3}$$

$$\text{Độ lệch trung bình so với trung vị} = \bar{x} - \text{Trung vị}$$

**Cách tính và diễn giải:**

| Đại lượng | Ý nghĩa | Vì sao dùng |
|---|---|---|
| Trung vị | Giá trị đơn "điển hình" | Không bị đuôi phải kéo lên; là mốc đại diện của một đơn |
| Trung bình | Tổng doanh thu chia đều số đơn | **Bị** đuôi phải kéo lên → không mô tả được đơn nào |
| \(Q_1, Q_3\) | 25% đơn nằm dưới / trên | Khoảng "phần lớn" — dùng cho rào IQR ở Slide 05 |

- Với `dev_002`: \(\bar{x} = 71.095\) vs. trung vị \(= 55.000\) → chênh lệch **+16.095 VNĐ/đơn** (≈ **+29%** so với trung vị). Khoảng giữa bị bóp bởi đuôi phải.
- Với `dev_011`: \(\frac{Q_3}{Q_1} = \frac{3.519.000}{150.000} \approx 23{,}5\) lần — phần tứ trên trải rộng hơn phần tứ dưới 23,5 lần.
- **Quy tắc áp dụng xuyên suốt bài:** mọi khi nói "giá trị đơn đặc trưng" → dùng **trung vị**; mọi khi nói "doanh thu trung bình trên một đơn" → dùng **trung bình** và luôn ghi kèm chênh lệch với trung vị để người xem không nhầm.

**Gợi ý biểu đồ:**
- **Boxplot (thang log10) của giá trị đơn theo doanh nghiệp** — 4–6 hộp, cùng thang, nhãn trực tiếp; điểm ngoại lệ vẽ bằng chấm nhỏ mờ, phần rào IQR ghi rõ.
- *Thay thế:* **histogram thang log của một doanh nghiệp đại diện** (`dev_002`) để thấy rõ hình dạng lệch phải, kèm đường đánh dấu trung vị.
- *Gợi ý chú thích:* dùng **chú thích tại đỉnh** ("Trung vị 55.000 VNĐ/đơn — đây là mốc đại diện, không phải trung bình 71.095") đúng tinh thần Schwabish #3.

**Ghi chú thuyết trình:**
> "Đây là lý do nhiều biểu đồ phải dùng thang log, và lý do ta dùng trung vị chứ không dùng trung bình. Với `dev_002`, một phần tư đơn dưới 39 nghìn, một phần tư trên 93 nghìn — khoảng giữa bị bóp bởi một đuôi phải dày. Trung vị là 55 nghìn, nhưng trung bình là 71 nghìn. Nếu ta đưa 'trung bình 71 nghìn' lên slide thì con số đó không mô tả được đơn hàng nào trong dữ liệu — và 16 nghìn chênh lệch đó, tưởng nhỏ, lại là toàn bộ phần doanh thu bị đẩy lên bởi một nhóm đơn lớn."
> "Và nhớ: vì thế ở Hồi 3 chúng ta sẽ không so sánh giá trị đơn tuyệt đối giữa các doanh nghiệp."

---

### Hồi 3 — Bằng chứng đối chiếu (Slide 08–11)

---

#### Slide 08 — Luật chơi của phép so sánh: chỉ so những gì cùng nghĩa, cùng đơn vị, cùng thời gian

**Thông điệp chủ động:**
> 8/14 doanh nghiệp bị loại khỏi mọi phép so sánh — và đó là kết quả đúng, không phải thiếu sót.

**Nội dung đưa lên slide:**

| Chiều so sánh | Đủ điều kiện | Bị loại | Lý do kỹ thuật |
|---|---|---|---|
| Đối chiếu toàn bộ 14 DN | 6 DN đại diện | 8 DN còn lại (`dev_001`, `003`, `004`, `005`, `008`, `010`, `013`, `014`) | Mới dừng ở mức kiểm kê cấu trúc thô (Hồi 1), chưa chuẩn hoá đơn vị đo / quy tắc lọc đơn hủy / Tidy Data |
| Nhịp vận hành theo **khung giờ & ca** | **0/6 DN** | cả 6 DN | Dữ liệu nguồn chỉ ghi `order_date`, **không lưu HH:MM thực tế** |
| So sánh **tổng tuyệt đối** (doanh thu, số đơn) | Không so trực tiếp | mọi cặp khác quy mô | Chênh lệch quy mô (quán ăn ~100 đơn/ngày vs tiệm sửa xe ~15 lượt/ngày), khác cấp ghi nhận, khác ngày cutoff |
| Biến động **Tết Ất Tỵ 2025** | 2 DN (`dev_002`, `dev_009`) | 4 DN | Bắt đầu ghi nhận từ 02–07/2025 → không phủ đủ cửa sổ Trước Tết & Trong Tết 2025 |
| Biến động **Tết Bính Ngọ 2026** | 6/6 DN | — | Phủ trọn 17 ngày (2026-02-10 → 2026-02-26), 0 ngày trống |

**Cửa sổ so sánh chung:** **328 ngày** (2025-07-01 → 2026-05-24) — giao của 6 DN đại diện. *(Lưu ý: con số 314 ngày ở Slide 02 là của 14 DN; 328 ngày là của 6 DN. Hai phạm vi khác nhau, không mâu thuẫn.)*

**Công thức & cách xác định điều kiện tương thích:**

$$W_{\text{6 DN}} = \Big[\max_{i \in 6} \min(\text{date}_i),\ \min_{i \in 6} \max(\text{date}_i)\Big], \qquad |W| = \min_i \max(\text{date}_i) - \max_i \min(\text{date}_i) + 1 = 328$$

$$\text{Đủ điều kiện so sánh theo thứ trong tuần} \iff \text{DN đủ độ phủ } W_{\text{6 DN}} \ \wedge\ \text{có cột } \texttt{order\_id}, \texttt{line\_amount}, \texttt{is\_valid}$$

$$\text{Đủ điều kiện so sánh dịp Tết} \iff \min(\text{date}_i) \le \text{pre\_start} \ \wedge\ \max(\text{date}_i) \ge \text{post\_end}$$

- `pre_start` / `post_end` là biên của các cửa sổ Trước Tết / Sau Tết (mỗi cửa sổ 17 ngày) — xem Slide 10.
- Vì cửa sổ Tết nằm **bên trong** \(W_{\text{6 DN}}\), điều kiện phủ Tết chính là điều kiện phủ cửa sổ chung → 6/6 DN đủ điều kiện cho Tết 2026.
- Tết 2025 **nằm ngoài** \(W_{\text{6 DN}}\) (diễn ra trước 2025-07-01) → chỉ 2 DN có đủ dữ liệu (bắt đầu ghi nhận từ tháng 2–7/2025).

**Gợi ý biểu đồ:**
- **Ma trận "chiều so sánh × doanh nghiệp"** — mỗi hàng là một chiều so sánh, mỗi cột là 1 DN đại diện, ô tô đậm/xám theo mức độ tương thích (đủ điều kiện / không đủ / không thể so sánh). Ô không tương thích ghi lý do bằng ký hiệu chữ.
- *Thay thế:* **biểu đồ Gantt "phạm vi thời gian hoạt động và chiều đối chiếu hợp lệ"** — trục ngày, 14 hàng DN, tô đậm đoạn thuộc cửa sổ giao nhau 328 ngày, đánh dấu các mốc Tết.

**Ghi chú thuyết trình:**
> "Trước khi so sánh, phải biết được so sánh cái gì. Ma trận này cho thấy: sáu doanh nghiệp đại diện đủ điều kiện cho phép so sánh nhịp vận hành; riêng chiều theo khung giờ thì không doanh nghiệp nào đủ dữ liệu — vì cả sáu chỉ ghi ngày, không ghi giờ phút. Đó là lý do trong bộ bàn giao **không có** biểu đồ theo giờ: chúng ta không sinh ra một cái biểu đồ trống rỗng rồi giả vờ có phát hiện."
> "Và tám doanh nghiệp còn lại bị loại khỏi phép so sánh không phải vì dữ liệu kém, mà vì chưa qua bước chuẩn hoá. Chúng ta nói thẳng điều đó."

---

#### Slide 09 — Phát hiện 1: cuối tuần bận hơn — nhưng mức bận khác nhau gấp 12 lần

**Thông điệp chủ động:**
> Cả 6 doanh nghiệp đều bận hơn cuối tuần, nhưng chỉ số cuối tuần dao động từ 105 đến 156 — không có một quy luật "cuối tuần" chung.

**Nội dung đưa lên slide:**

Chỉ số cuối tuần trên **cửa sổ giao nhau 328 ngày** (Ngày thường = 100):

| Doanh nghiệp | Ngành | Chỉ số cuối tuần | Lift trên toàn vùng phủ riêng | Đơn/ngày thường → cuối tuần |
|---|---|---|---|---|
| `dev_007` | F&B | **155,57** | **+53,28%** | 45,6 → 69,9 |
| `dev_002` | F&B | 143,50 | +42,42% | 90,9 → 129,4 |
| `dev_011` | Phụ kiện | 136,73 | +36,12% | 8,1 → 11,0 |
| `dev_012` | Sửa xe | 131,47 | +32,96% | 13,0 → 17,3 |
| `dev_009` | Cấp đơn | 108,97 | +9,12% | 38,7 → 42,2 |
| `dev_006` | Nhà thuốc | **105,19** | **+4,48%** | 74,0 → 77,3 |

Nguồn: `normalized_cross_metrics.csv` (chỉ số trên cửa sổ chung) & `operating_rhythm_summary.csv` (lift trên vùng phủ riêng của từng DN).

**Công thức (đầy đủ):**

*Chỉ số cuối tuần — tính trên cửa sổ giao nhau 328 ngày:*

$$\text{Chỉ số cuối tuần} = \frac{\overline{x}_{\text{cuối tuần}}}{\overline{x}_{\text{ngày thường}}} \times 100 = \frac{N_{\text{đơn cuối tuần}} / N_{\text{ngày lịch cuối tuần}}}{N_{\text{đơn ngày thường}} / N_{\text{ngày lịch ngày thường}}} \times 100$$

*Phần vượt mức ngày thường — tính trên vùng phủ riêng của từng DN:*

$$\text{Lift} = \frac{\overline{x}_{\text{cuối tuần}} - \overline{x}_{\text{ngày thường}}}{\overline{x}_{\text{ngày thường}}} \times 100\% = \left(\frac{\text{Chỉ số cuối tuần}}{100} - 1\right) \times 100\%$$

*Chỉ số nhịp theo từng thứ trong tuần (dùng cho small multiples):*

$$\text{Chỉ số thứ } d = \frac{\overline{x}_d}{\overline{x}_{\text{trung bình toàn tuần}}} \times 100, \qquad \overline{x}_d = \frac{N_{\text{đơn thứ } d}}{N_{\text{ngày lịch thứ } d}}$$

**Cách tính — các bước và các quy ước quan trọng:**

1. **Đơn vị đếm:** dùng `nunique(order_id)` — số **đơn hợp lệ** (`is_valid == True`). Với DN cấp dòng hàng, một đơn có nhiều dòng nên phải đếm đơn, không đếm dòng; nếu đếm dòng thì F&B (nhiều món/đơn) sẽ bị thổi phóng so với DN cấp đơn.
2. **Mẫu số là ngày lịch thực tế, không phải ngày có phát sinh đơn.** Cửa sổ 328 ngày có \(N_{wd}\) ngày thường (T2–T6) và \(N_{we}\) ngày cuối tuần (T7–CN) theo lịch; ngày 0 đơn vẫn nằm trong mẫu số. Nếu chỉ chia cho "ngày có đơn" thì DN nghỉ nhiều ngày sẽ bị thổi phóng chỉ số.
3. **Chỉ số 100 = ngày thường.** Chỉ số > 100 nghĩa là cuối tuần bận hơn mức trung bình của ngày thường.
4. **Lift và Chỉ số là hai cách diễn đạt cùng một phép so sánh:** $\text{Lift} = (\text{Chỉ số}/100 - 1) \times 100\%$. Nhưng chúng **không cùng mẫu số** (xem ghi chú bên dưới) nên phải nói rõ khung nào.
5. **Chỉ số nhịp thứ \(d\)** dùng mẫu số là *trung bình toàn tuần của chính DN đó* (đứng ở 100) → dùng được để so sánh hình dạng nhịp giữa các DN khác nhau.

**Ghi chú quan trọng:** Hai cột này **không mâu thuẫn** — chỉ số 105,19 của `dev_006` được tính trên 328 ngày chung, còn lift +4,48% tính trên 495 ngày phủ riêng của `dev_006`. Khi trình bày phải nói rõ đang dùng khung nào.

**Tỷ lệ chênh lệch giữa hai đầu (vì sao nói "gấp 12 lần"):**

$$\frac{\text{Lift}_{\max}}{\text{Lift}_{\min}} = \frac{53{,}28}{4{,}48} \approx 11{,}89 \approx \mathbf{12\ \text{lần}}$$

*Đây là tỷ lệ giữa hai **mức vượt**, không phải tỷ lệ giữa hai chỉ số.* (Chỉ số: \(155{,}57 / 105{,}19 \approx 1{,}48\) lần.)

**Gợi ý biểu đồ:**
- **Cột ngang 6 doanh nghiệp, giá trị là chỉ số cuối tuần**, sắp xếp tăng dần, **đường tham chiếu dọc đậm tại 100** (mốc "Ngày thường"), nhãn trực tiếp giá trị trên đầu cột. Đây là cách làm nổi bật "càng xa 100 càng mạnh" mà không cần chú giải.
- *Bổ sung:* **cột ghép** hiển thị cả chỉ số (đường chuẩn 100) và lift % (nhãn phụ dưới trục) — tránh bắt người xem so sánh hai thang đo khác nhau trên cùng trục.
- *Nếu muốn nói về nhịp trong tuần:* **small multiples 6 panel, mỗi panel là cột 7 ngày T2→CN, cùng thang y, đánh dấu T7/CN bằng màu nhấn** — F&B nhảy vọt ở T6–CN, nhà thuốc phẳng.

**Ghi chú thuyết trình:**
> "Đây là phát hiện rõ nhất. Cả sáu doanh nghiệp đều bận hơn cuối tuần — nhưng phần vượt mức ngày thường khác nhau gấp mười hai lần: `dev_007` tăng 53%, còn `dev_006` chỉ tăng 4,5%. Nếu chúng ta kết luận chung chung 'cuối tuần bận hơn 30%' thì sẽ sai với cả hai đầu."
> "Điều thú vị hơn là *tại sao*: quán ăn và quán cà phê đông cuối tuần vì khách đi ăn; tiệm sửa xe và tiệm phụ kiện đông vì cuối tuần khách rảnh đem xe đi sửa; còn nhà thuốc thì gần như phẳng — vì nhu cầu thuốc không phụ thuộc ngày nghỉ. Nhưng đây là *cách giải thích*, không phải suy luận nhân quả từ dữ liệu — chúng ta chỉ mô tả điều quan sát được."

---

#### Slide 10 — Phát hiện 2: Tết đảo chiều — mỗi ngành một chiều

**Thông điệp chủ động:**
> Tết 2026 không có một tác động chung: hai doanh nghiệp giảm mạnh, hai doanh nghiệp tăng mạnh.

**Nội dung đưa lên slide:**

So sánh mật độ đơn **Trong Tết 2026** với **Trước Tết** (cửa sổ 17 ngày: 23 Chạp → 10 Giêng; 2026-02-10 → 2026-02-26), phủ trọn 6/6 DN, 0 ngày trống:

| Doanh nghiệp | Ngành | Trong Tết vs Trước Tết | Sau Tết vs Trước Tết |
|---|---|---|---|
| `dev_009` | Cấp đơn | **+144,22%** | +7,43% |
| `dev_006` | Nhà thuốc | **−0,30%** (gần như không đổi) | −0,89% |
| `dev_011` | Phụ kiện | +49,31% | +13,19% |
| `dev_012` | Sửa xe | +15,42% | −6,72% |
| `dev_002` | F&B | **−45,42%** | −3,82% |
| `dev_007` | F&B | **−54,47%** | −2,81% |

*Tết 2025 (chỉ 2 DN đủ cửa sổ): `dev_002` −41,19% · `dev_009` **+164,85%** — cùng chiều với Tết 2026, gợi ý đây là đặc trưng lặp lại chứ không phải nhiễu một lần.*

**Công thức (đầy đủ):**

**Bước 1 — Xác định cửa sổ (theo `calendar.csv`, không tự tính lịch âm):**

$$\begin{aligned}
W_{\text{Trong Tết}} &= [\text{23 tháng Chạp},\ \text{mùng 10 tháng Giêng}] \quad (n = 17\ \text{ngày}) \\ W_{\text{Trước Tết}} &= [\text{23 Chạp} - n,\ \text{23 Chạp} - 1] \quad (n = 17\ \text{ngày}) \\ W_{\text{Sau Tết}} &= [\text{10 Giêng} + 1,\ \text{10 Giêng} + n] \quad (n = 17\ \text{ngày}) \end{aligned}$$

$$\text{Với Tết 2026: } W_{\text{Trong Tết}} = [2026\text{-}02\text{-}10,\ 2026\text{-}02\text{-}26],\quad W_{\text{Trước Tết}} = [2026\text{-}01\text{-}24,\ 2026\text{-}02\text{-}09]$$

*Ba cửa sổ **cùng độ dài** — đó là điều kiện để so sánh được: cùng số ngày, cùng số lượng ngày lịch.*

**Bước 2 — Mật độ đơn trung bình mỗi ngày trong mỗi cửa sổ:**

$$\bar{x}_W = \frac{N_{\text{đơn hợp lệ trong } W}}{|W|}\ (\text{đơn/ngày})$$

*Trong mẫu số là **toàn bộ ngày lịch** của cửa sổ (kể cả ngày 0 đơn) → chính là lý do dùng "mật độ" thay vì "tổng", và cũng là nơi hiện ra hiệu ứng nghỉ Tết.*

**Bước 3 — Mức thay đổi:**

$$\Delta_{\text{Trong Tết}} = \frac{\bar{x}_{\text{Trong Tết}} - \bar{x}_{\text{Trước Tết}}}{\bar{x}_{\text{Trước Tết}}} \times 100\% \qquad \Delta_{\text{Sau Tết}} = \frac{\bar{x}_{\text{Sau Tết}} - \bar{x}_{\text{Trước Tết}}}{\bar{x}_{\text{Trước Tết}}} \times 100\%$$

$$\text{Số ngày nghỉ trong Tết} = |W_{\text{Trong Tết}}| - N_{\text{ngày có phát sinh đơn}}$$

**Cách tính & các quy ước quyết định:**

1. **Chỉ dùng đơn hợp lệ** (`is_valid == True`) và **chỉ tính theo ngày đặt** (`order_date`), không theo ngày giao/ngày thu tiền — nếu không, đơn cuối kỳ sẽ bị dồn sang kỳ sau và làm sai lệch cả hai phía.
2. **Mẫu số là ngày lịch của cửa sổ** (17 ngày), không phải ngày có đơn → nếu DN nghỉ Tết 5 ngày thì \(\bar{x}\) giảm đúng bằng 5/17, đúng như thực tế.
3. **Chỉ 6/6 DN được dùng** vì đều phủ trọn cả ba cửa sổ; DN thiếu phủ bị loại (Slide 08).
4. **Vì sao dùng mật độ/ngày mà không dùng tổng:** tổng đơn của một cửa sổ luôn có sẵn "độ dài cửa sổ" bị cộng sẵn vào → so sánh tổng giữa hai cửa sổ khác nhau sẽ gây ảo giác.
5. **Cảnh báo diễn giải:** ngày 0 đơn trong Tết có thể là *cửa hàng nghỉ Tết* **hoặc** *thiếu dữ liệu ghi nhận* — hai khả năng này dữ liệu không phân biệt được. Vì vậy slide phải nói "nghỉ 0/17 ngày" như một **quan sát**, không phải như một kết luận về nguyên nhân.

**Gợi ý biểu đồ:**
- **Diverging bar chart** (thang phân kỳ quanh 0): một cột cho mỗi doanh nghiệp, giá trị là % thay đổi, chia đôi quanh mốc 0 — tăng một màu, giảm một màu khác, nhãn trực tiếp có dấu +/−. Đây là cách hiển thị đúng nhất cho "tách đôi" và tuân thủ quy tắc bảng màu phân kỳ.
- *Bổ sung:* **đường mật độ đơn từng ngày quanh Tết** (Trước – Trong – Sau), tô vùng "Trong Tết", đánh dấu đỉnh/đáy — cho thấy *hình dạng* cú sốc chứ không chỉ con số.
- *Nếu muốn nói về 2 DN có Tết 2025:* **slope chart** 2 mốc (Tết 2025 → Tết 2026) cho `dev_002` và `dev_009`.

**Ghi chú thuyết trình:**
> "Tết 2026 cho thấy một hiện tượng rất đáng nói: tác động **đảo chiều** theo ngành. Hai quán F&B giảm mạnh — giảm một nửa trong Tết. Trong khi đó một doanh nghiệp cấp đơn tăng 144%. Nhà thuốc gần như không đổi, tiệm sửa xe tăng nhẹ 15%."
> "Vì sao lại thế? Nhà thuốc bán theo nhu cầu, mùa Tết thì người ta vẫn ốm; còn F&B thì khách nghỉ Tết nên không đi ăn ngoài — nên giảm. Nhưng chúng ta cần nói rõ: đây là *diễn giải*, dữ liệu chỉ cho ta thấy *hiện tượng*. Và lưu ý thêm — Tết 2025 cho kết quả cùng chiều, nên đây nhiều khả năng là đặc trưng lặp lại, không phải một năm lạ."

---

#### Slide 11 — Phát hiện 3: dữ liệu hủy đơn cũng kể một câu chuyện khác

**Thông điệp chủ động:**
> Tỉ lệ đơn hủy chênh nhau gấp nhiều lần giữa các doanh nghiệp — và nó không nằm trong cùng một câu chuyện với nhịp cuối tuần.

**Nội dung đưa lên slide:**

Tỉ lệ đơn hủy/trả trên cửa sổ chung 328 ngày (sau khi loại theo rulebook §1):

| Doanh nghiệp | Ngành | Tỉ lệ đơn hủy |
|---|---|---|
| `dev_009` | Cấp đơn | **4,63%** |
| `dev_002` | F&B | 2,37% |
| `dev_007` | F&B | 2,21% |
| `dev_006` | Nhà thuốc | 2,00% |
| `dev_011` | Phụ kiện | 0,75% |
| `dev_012` | Sửa xe | **0,00%** |

**Điểm cần nói ra:** chỉ số này **không** tương quan với nhịp cuối tuần — `dev_012` có chỉ số cuối tuần 131 (khá cao) nhưng tỉ lệ hủy bằng 0; `dev_009` có chỉ số 109 (thấp) nhưng hủy cao nhất. Hai chiều này độc lập.

**Công thức (đầy đủ):**

$$\text{Tỷ lệ đơn không hợp lệ} = \frac{N_{\text{đơn hủy hoặc trả hàng}}}{N_{\text{tổng số đơn}}} \times 100\%$$

**Cách tính — từng bước:**

1. **Đơn vị đếm là `order_id`, không phải dòng hàng.** Một đơn có 5 dòng mà bị hủy vẫn tính là **1 đơn hủy**, không phải 5 dòng hủy → nếu đếm dòng, F&B (nhiều món/đơn) sẽ bị thổi phóng tỷ lệ hủy so với DN cấp đơn. Ở `dev_006`/`dev_007` đây là khác biệt rất lớn.
2. **Một đơn bị tính là không hợp lệ nếu BẤT KỲ dòng nào của nó vi phạm** (`is_valid` là phép AND trên các dòng của đơn). Theo rulebook §1: đơn có một dòng hủy → **loại cả đơn** khỏi phân tích doanh thu (không chỉ bỏ dòng đó) → trả một phần cũng bị loại cả đơn.
3. **Mẫu số là tổng số đơn của DN đó trong cửa sổ 328 ngày** — bao gồm cả đơn không hợp lệ; nếu lấy mẫu số là "số đơn hợp lệ" thì tỷ lệ sẽ ra 0% một cách vô nghĩa.
4. **Kết quả:** \(\text{Tỷ lệ hủy} \in [0{,}00\%,\ 4{,}63\%]\); tổng số đơn của cả 6 DN nằm trong bảng `normalized_cross_metrics.csv` (cột `sample_n`).

$$\text{Kiểm tra độc lập: } \frac{N_{\text{hủy/trả}}}{N_{\text{tổng}}} \to 0 \text{ (dev\_012)} \quad \text{trong khi} \quad \text{Chỉ số cuối tuần}_{\text{dev\_012}} = 131{,}47 \ \text{(cao)}$$

**Gợi ý biểu đồ:**
- **Cột ngang 6 doanh nghiệp, giá trị là % đơn hủy**, sắp xếp giảm dần, nhãn trực tiếp, tô đậm hai giá trị đầu–cuối để thấy độ phân tán.
- *Thay thế:* **scatter 2 chiều** — trục x = chỉ số cuối tuần, trục y = % đơn hủy, 6 điểm được ghi nhãn tên doanh nghiệp trực tiếp. Mục đích: **chứng minh bằng hình ảnh** rằng không có quan hệ, thay vì chỉ nói. Đây là một slide dạng "phủ nhận" — có giá trị giáo dục cao vì nó dạy cách *kiểm tra* một giả thuyết thay vì mặc định nó đúng.

**Ghi chú thuyết trình:**
> "Một chiều nữa ít ai nghĩ tới: đơn hủy. Tỉ lệ hủy dao động từ 0% ở tiệm sửa xe tới 4,63% — chênh nhau rất xa trong khi cả hai đều bán dịch vụ có giá trị đơn lớn. Và chú ý: chiều này **không** đi cùng chiều cuối tuần. `dev_012` cuối tuần khá bận nhưng không hủy đơn nào; `dev_009` cuối tuần bình thường nhưng hủy nhiều nhất."
> "Chúng ta kiểm tra điều này bằng cách vẽ cả hai chiều lên cùng một trục thay vì chỉ nói bằng lời. Kết quả: không có quan hệ. Và nhớ — tương quan không đồng nghĩa nhân quả, kể cả khi có tương quan."

---

### Hồi 4 — Kết luận & Hạn chế/Hướng phát triển (Slide 12–14)

---

#### Slide 12 — Kết luận: ba điều chúng ta biết, và ba điều chúng ta *không* biết

**Thông điệp chủ động:**
> Dữ liệu này trả lời được câu hỏi về *mức độ khác nhau* — và không trả lời được câu hỏi về *nguyên nhân*.

**Nội dung đưa lên slide:**

**Ba điều chúng ta biết (mô tả được, đo được):**
1. **Cuối tuần luôn bận hơn ngày thường ở cả 6 doanh nghiệp** — nhưng chỉ số dao động 105,19 → 155,57, và phần *vượt* mức ngày thường khác nhau gấp 11,9 lần (+4,48% ở `dev_006` so với +53,28% ở `dev_007`).
2. **Tết tác động theo hai chiều** — F&B giảm 45–54%, cấp đơn tăng 144%, nhà thuốc không đổi; và hiện tượng lặp lại giữa Tết 2025 và Tết 2026.
3. **Không thể so sánh tuyệt đối giữa các doanh nghiệp** — vì khác quy mô, khác cấp ghi nhận, khác ngày cutoff; mọi so sánh đều phải đi qua %, Index hoặc TB/ngày.

**Ba điều chúng ta *không* biết (và không nên đoán):**
1. **Vì sao** cuối tuần bận hơn — đây là mô tả tương quan, không phải nhân quả.
2. **Nhịp theo khung giờ/ca** — 0/6 doanh nghiệp lưu HH:MM thực tế.
3. **8 doanh nghiệp còn lại** — chưa qua chuẩn hoá nên chưa đối chiếu được.

**Gợi ý biểu đồ:**
- **Slide hai cột dạng bảng so sánh đối lập** ("Biết" vs "Chưa biết") — không cần biểu đồ; dùng hai khối văn bản với icon/tick. Đây là slide mà *không* biểu đồ là lựa chọn đúng, và nên nói ra điều đó.
- *Thay thế:* **scatter chỉ số cuối tuần (x) × lift % (y)** cho 6 DN, đường xu hướng không vẽ — nhắc rằng ta không suy luận.

**Ghi chú thuyết trình:**
> "Hãy tách rõ hai tầng. Tầng một là những gì dữ liệu trả lời được: mức độ khác nhau giữa các doanh nghiệp — bằng chứng cụ thể, đo được, có cỡ mẫu và khoảng thời gian. Tầng hai là những gì nó *không* trả lời được: nguyên nhân, nhịp theo giờ, và 8 doanh nghiệp còn lại."
> "Chúng ta dừng ở tầng một. Đó không phải hạn chế kỹ thuật — đó là ranh giới trung thực."

---

#### Slide 13 — Kết luận cốt lõi: ba điều dữ liệu này thực sự nói, và ba bài học cho người trực quan hóa

**Thông điệp chủ động:**
> Giá trị của dữ liệu không nằm ở những con số, mà ở những kết luận nó buộc ta phải đặt câu hỏi — và ở những nguyên tắc trực quan hóa mà nó dạy ta.

**Nội dung đưa lên slide:**

**Phần A — Ba kết luận cốt lõi (về nghiệp vụ, không về kỹ thuật):**

| # | Kết luận | Bằng chứng đi kèm |
|---|---|---|
| 1 | **Không tồn tại "ngành" nào có một nhịp vận hành chung — mỗi doanh nghiệp có một nhịp riêng.** | Chỉ số cuối tuần 105,19 (nhà thuốc) → 155,57 (F&B); cùng ngành F&B vẫn cách nhau 12,07 điểm chỉ số |
| 2 | **Tết là phép thử chuẩn của mô hình kinh doanh, và nó đảo chiều theo mô hình.** | F&B giảm 45–54% (nghỉ Tết, khách không đi ăn ngoài) · cấp đơn tăng 144% · nhà thuốc không đổi (nhu cầu thiết yếu) |
| 3 | **Chất lượng dữ liệu quyết định độ tin cậy của biểu đồ — không phải độ đẹp của nó.** | Cùng một câu hỏi "cuối tuần bận hơn không?" nhưng trả lời sai nếu quy đơn vị hoặc lấy tổng thay vì trung bình/ngày |

**Phần B — Ba bài học trực quan hóa rút ra từ chính bài này:**

| # | Bài học | Nguồn trong câu chuyện |
|---|---|---|
| 1 | **Định nghĩa chỉ số TRƯỚC khi vẽ.** "Doanh thu" phải được định nghĩa bằng quy tắc nguồn và kiểm chứng bằng số (khớp 100%) — nếu không, biểu đồ sai một cách rất thuyết phục. | Slide 04 |
| 2 | **Khi so sánh khác quy mô, hãy so bằng tỷ lệ / chỉ số / trung bình mỗi ngày — và luôn nói rõ mẫu số.** | Slide 08–09 |
| 3 | **Đánh dấu cả những gì *không* biết.** Một ô trống có chú thích ("`dev_009` không có chi tiết dòng hàng") trung thực hơn là một biểu đồ bịa ra. | Slide 06, Slide 12 |

**Gợi ý biểu đồ:**
- **Slide hai khối đối lập** ("Kết luận cốt lõi" | "Bài học trực quan hóa") — dạng bảng/icon, **không cần biểu đồ**; đây là slide kết luận nên không biểu đồ là lựa chọn đúng.
- *Thay thế:* **3 cột ngang "độ lớn hiệu ứng"** (chỉ số cuối tuần / % đổi Tết / % hủy đơn) cho 6 DN dùng chung thang chuẩn hoá — nếu muốn một hình ảnh khép lại câu chuyện, đây là hình ảnh "6 doanh nghiệp, 3 chiều, không ai giống ai".

**Ghi chú thuyết trình:**
> "Nếu phải rút ra điều gì từ toàn bộ hành trình này, thì không phải là những con số — mà là ba kết luận. Một: không có nhịp chung cho ngành nào, mỗi quán có một nhịp riêng. Hai: Tết là phép thử của mô hình kinh doanh, và nó đảo chiều — quán ăn nghỉ Tết thì giảm, cửa hàng thiết yếu thì không đổi. Ba: chất lượng dữ liệu quyết định độ tin cậy của biểu đồ chứ không phải độ đẹp của nó — một biểu đồ rất đẹp vẽ trên dữ liệu chưa được định nghĩa thì vẫn sai.
> "Và ba bài học cho người trực quan hóa, rút ra từ chính những chỗ chúng ta vấp: định nghĩa chỉ số trước khi vẽ; khi khác quy mô thì so bằng tỷ lệ và nói rõ mẫu số; và đánh dấu cả những gì mình không biết — một ô trống có chú thích còn trung thực hơn một biểu đồ bịa."

---

#### Slide 14 — Hạn chế của phân tích, và hướng phát triển dự kiến

**Thông điệp chủ động:**
> Mọi kết luận ở trên đều đứng trên một nền tảng dữ liệu có giới hạn — biết rõ giới hạn ở đâu thì mới nói được điều gì còn đáng tin.

**Nội dung đưa lên slide:**

**Phần A — Hạn chế (bốn nhóm, nói thẳng):**

| Nhóm | Hạn chế cụ thể | Hệ quả đối với kết luận |
|---|---|---|
| **Độ phủ** | Chỉ **6/14** doanh nghiệp được đưa vào phép so sánh; 8 DN còn lại mới dừng ở mức kiểm kê cấu trúc thô | Kết luận ở Slide 06/09/10 có phạm vi 6 DN, **không** đại diện cho cả 14 |
| **Độ phân giải thời gian** | **0/6** doanh nghiệp lưu mốc giờ thực tế (`HH:MM`) — toàn bộ dữ liệu chỉ ở cấp ngày | Không trả lời được nhịp theo ca sáng/chiều, giờ vàng/giờ chiều |
| **Độ dài chuỗi** | Cửa sổ so sánh chung chỉ **328 ngày**; các DN lệch cutoff tới **143 ngày**; **một** kỳ Tết đầy đủ (2026) + 2 DN cho Tết 2025 | Chưa tách được "đặc trưng ngành" khỏi "đặc trưng một năm"; chưa nói được về xu hướng dài hạn |
| **Sức chứa của bộ dữ liệu** | Không có giá vốn / biên lợi nhuận, không có định danh khách hàng thống nhất, không có cột hàng hóa trong báo cáo doanh thu | Chỉ kết luận được về *doanh thu và số đơn*, không kết luận được về *lợi nhuận, khách hàng, hiệu quả vận hành* |

**Phần B — Hướng phát triển dự kiến (mỗi hướng gắn với đúng một hạn chế ở trên):**

| # | Hướng phát triển | Mở khoá hạn chế nào | Dấu hiệu đã hoàn thành |
|---|---|---|---|
| 1 | **Chuẩn hoá 8 doanh nghiệp còn lại** theo cùng bộ quy tắc | Độ phủ 6/14 → 14/14 | Chạy lại ma trận tương thích và thấy phép so sánh mở rộng ra 14 DN |
| 2 | **Ghi nhận mốc giờ thực tế (`HH:MM`) tại nguồn** | Độ phân giải 0/6 → 6/6 | Có thể vẽ được nhịp theo khung giờ và theo ca — mà không cần suy ra |
| 3 | **Thu thập thêm các kỳ Tết** (và nhiều chi nhánh cùng ngành) | Độ dài chuỗi 1 kỳ đầy đủ → nhiều kỳ | Tác động hai chiều được tách thành "đặc trưng ngành" và "nhiễu năm" |
| 4 | **Bổ sung chiều vốn – lợi nhuận và định danh khách hàng** | Sức chứa bộ dữ liệu | Chuyển từ "doanh thu" sang "lợi nhuận theo phân khúc khách hàng" |
| 5 | **Xây bộ chuẩn so sánh theo ngành** (benchmark) từ 6 DN đại diện | Độ phủ | Mỗi DN đặt được vị trí của mình so với mặt bằng chung của ngành, thay vì so với nhau |

**Gợi ý biểu đồ:**
- **Bảng 2 khối đối lập "Hạn chế → Hướng phát triển"** — mỗi hàng là một cặp (hạn chế ↔ việc cần làm để mở khoá), nối bằng mũi tên. Dạng bảng, không cần biểu đồ — vì đây là phần *cam kết*, không phải phần *khám phá*.
- *Thay thế:* **thang tiến bộ 3 bậc** cho hướng phát triển 1–3 (chiều đối chiếu: 6/14 → 14/14 DN; chiều theo giờ: 0/6 → 6/6; số kỳ Tết đầy đủ: 1 → 3+).

**Ghi chú thuyết trình:**
> "Trước khi kết thúc, nói rõ điều gì chưa đủ — vì đây là phần quyết định niềm tin vào những gì ta vừa kết luận.
> "Bốn nhóm hạn chế. Một: độ phủ — chỉ 6 trên 14 doanh nghiệp; tám doanh nghiệp còn lại mới dừng ở mức kiểm kê, chưa qua chuẩn hoá, nên mọi kết luận hôm nay có phạm vi 6 doanh nghiệp chứ không phải cả bộ. Hai: độ phân giải thời gian — không doanh nghiệp nào lưu giờ phút, nên câu hỏi 'ca sáng hay ca chiều bận hơn' không có dữ liệu để trả lời. Ba: độ dài chuỗi — chỉ 328 ngày so sánh chung, và chỉ một kỳ Tết đầy đủ, nên chưa phân biệt được 'đặc trưng ngành' với 'đặc trưng của một năm'. Bốn: sức chứa bộ dữ liệu — không có giá vốn, không có định danh khách hàng, nên ta chỉ nói được về doanh thu và số đơn, không nói được về lợi nhuận.
> "Và mỗi hạn chế ở đây đều có một hướng phát triển tương ứng — và lưu ý chúng đều là việc *thu thập thêm dữ liệu*, không phải phân tích sâu hơn. Vì phần phân tích đã ở giới hạn mà dữ liệu cho phép. Để trả lời câu hỏi tiếp theo thì cần đầu tư vào nguồn dữ liệu, không phải vào thêm thuật toán. Cảm ơn thầy/cô — mời thầy/cô đặt câu hỏi."

---

## 3. Sổ ký hiệu & tra cứu nhanh

### 3.1 Bảng tra cứu nhanh: slide nào dùng bằng chứng nào

| Slide | Hồi | Bằng chứng chính | Bảng artifact nguồn |
|---|---|---|---|
| 01 | H1 | 1.327.598 dòng · 8 ngành · 4 định dạng | `catalog_14.csv` |
| 02 | H1 | 143 ngày lệch cutoff · 314 ngày chung · 144.575 dòng lỗi ngày | `temporal_coverage.csv` |
| 03 | H1+H2 | 6 DN đại diện, 5 tiêu chí có trọng số | `representative_selection.csv` |
| 04 | H2 | Rulebook khớp 100% (37.833 & 32.022 đơn) | `rulebook.md`, `quality_and_iqr_report.csv` |
| 05 | H2 | 26.798 dòng gắn cờ IQR · 7.154 dòng loại theo rulebook | `quality_and_iqr_report.csv` |
| 06 | H2 | Top món `dev_002` 4,97% · `dev_009` không có chi tiết hàng | `business_findings_summary.csv` |
| 07 | H2 | Lệch phải, trung vị là mốc (Q1 39.000 / Q3 93.000 VNĐ) | `quality_and_iqr_report.csv` |
| 08 | H3 | 8/14 loại · 0/6 có HH:MM · 328 ngày chung | `cross_business_limitations.csv` |
| 09 | H3 | Chỉ số cuối tuần 105,19 → 155,57 · lift +4,48% → +53,28% | `normalized_cross_metrics.csv`, `operating_rhythm_summary.csv` |
| 10 | H3 | Tết 2026: −54,47% → +144,22% · Tết 2025 lặp lại | `tet_window_comparison.csv` |
| 11 | H3 | Hủy đơn 0,00% → 4,63% · không tương quan với cuối tuần | `normalized_cross_metrics.csv` |
| 12 | H4 | 3 biết / 3 chưa biết | — (tổng hợp) |
| 13 | H4 | 3 kết luận cốt lõi + 3 bài học trực quan hóa | — (tổng hợp) |
| 14 | H4 | 4 nhóm hạn chế + 5 hướng phát triển dự kiến | — (tổng hợp) |

### 3.2 Các con số cần nhớ (in ra để dùng khi trả lời câu hỏi)

| Nhóm | Con số |
|---|---|
| Bối cảnh | 14 DN · 8 ngành · 1.327.598 dòng · 143 ngày lệch cutoff · 314 ngày chung (14 DN) · 144.575 dòng lỗi ngày |
| Tập đại diện | 6/14 DN · 5 tiêu chí (30/20/20/15/15) · `dev_007` 596 ngày dài nhất · `dev_006` 17 bảng SQLite |
| Chuẩn hoá | `dev_006` 37.833 đơn & `dev_007` 32.022 đơn khớp 100% · `dev_002` 60 dòng hộp→cái · `dev_006` 10.917 dòng quy đổi · `dev_007` 561 dòng thùng/két |
| Chất lượng | 26.798 dòng ngoài IQR (7,97%–19,52%) · 7.154 dòng loại theo rulebook |
| Đối chiếu | 328 ngày chung (6 DN) · 0/6 có HH:MM · Tết 2026 17 ngày, 0 ngày trống · Tết 2025 chỉ 2/6 DN |
| Phát hiện | Cuối tuần 105,19–155,57 · lift +4,48%–+53,28% · Tết −54,47%…+144,22% · hủy đơn 0,00%–4,63% |
| Kết luận (Slide 13) | 3 kết luận cốt lõi + 3 bài học trực quan hóa |
| Hạn chế (Slide 14) | Độ phủ 6/14 · độ phân giải 0/6 HH:MM · độ dài 328 ngày / 1 kỳ Tết đủ · thiếu vốn–lợi nhuận & định danh khách hàng |
| Bàn giao *(để dành cho phần hỏi đáp, không lên slide)* | 33 biểu đồ kiểm định · 24 ảnh 300 DPI · 10/10 tiêu chí · 15/15 artifact · 0 lỗi |

### 3.3 Sổ công thức (để trả lời "con số này tính thế nào?")

| Chỉ số | Công thức | Slide |
|---|---|---|
| Cửa sổ so sánh chung | \(W = [\max_i \min(date_i),\ \min_i \max(date_i)]\) | 02, 08 |
| Độ lệch cutoff | \(\max_i(cutoff_i) - \min_i(cutoff_i)\) | 02 |
| Điểm chọn DN đại diện | \(\text{Điểm}_i = \sum_k w_k \tilde{x}_{ik}\), \(\tilde{x} = \text{MinMax}(\log_{10} x)\) | 03 |
| Rào ngoại lệ IQR | \(L = Q_1 - 1{,}5\,IQR\), \(U = Q_3 + 1{,}5\,IQR\), \(IQR = Q_3 - Q_1\) | 05, 07 |
| Tỷ trọng doanh thu | \(R_c / \sum R_{c'} \times 100\%\) | 06 |
| Chỉ số cuối tuần | \(\bar{x}_{WE} / \bar{x}_{WD} \times 100\) | 09 |
| Lift cuối tuần | \((\bar{x}_{WE} - \bar{x}_{WD}) / \bar{x}_{WD} \times 100\%\) | 09 |
| Chỉ số nhịp thứ \(d\) | \(\bar{x}_d / \bar{x}_{\text{tuần}} \times 100\) | 09 |
| Mật độ đơn/ngày | \(N_{\text{đơn}} / |W|\) | 10 |
| % đổi dịp Tết | \((\bar{x}_{Tết} - \bar{x}_{Trước}) / \bar{x}_{Trước} \times 100\%\) | 10 |
| Tỷ lệ đơn hủy | \(N_{\text{hủy}} / N_{\text{tổng đơn}} \times 100\%\) | 11 |

### 3.4 Quy ước trình bày số trên slide

- Dùng **dấu chấm phẩy** làm dấu phân cách nhóm (1.327.598) và **dấu phẩy** cho phần thập phân (4,97%) — nhất quán với văn bản tiếng Việt.
- **Mọi con số phần trăm đều kèm mẫu số** khi đưa lên slide: ví dụ "26.798 dòng gắn cờ IQR (n = 275.320 dòng hợp lệ)".
- **Khoảng ngày** luôn ghi dạng `YYYY-MM-DD → YYYY-MM-DD` khi nói về cửa sổ so sánh.

---

## 4. Những gì không được nói trên slide

Danh sách này là phần quan trọng nhất của kịch bản — cơ hội lớn nhất để biến một bài trình bày đầy dữ liệu thành một bài có câu chuyện là **bỏ đi những thứ không phục vụ câu chuyện**:

1. **Không mở đầu bằng "Tôi sẽ trình bày về…"** — mở bằng con số 1.327.598 và câu hỏi "chúng có so sánh được với nhau không".
2. **Không liệt kê cả 14 doanh nghiệp.** Chỉ nói tổng số ngành/định dạng; chi tiết từng DN dành cho slide ma trận.
3. **Không kể chi tiết quy trình làm sạch từng bước** (đọc file, quét sheet, kiểm tra kiểu dữ liệu…). Chỉ nói *kết quả* — khớp 100% và 26.798 dòng gắn cờ.
4. **Không giải thích thuật toán** (IQR tính thế nào, dot plot vẽ thế nào, `sharey` dùng khi nào). Kỹ thuật thuộc về slide phụ hoặc phần hỏi đáp.
5. **Không đọc tên hàm** (`fig.savefig`, `sns.despine`, `set_context`) trên slide chính.
6. **Không nói "chúng tôi đã xử lý 4 hồi"** như một danh sách công việc — bố cục 4 hồi là cấu trúc tư duy, không phải bảng thành tích.
7. **Không kết luận nhân quả.** Mọi câu về *vì sao* phải mở đầu bằng "Có thể giải thích bằng…" hoặc "Dữ liệu chỉ cho ta thấy…".
8. **Không dùng biểu đồ tròn** (giới hạn ≤ 5 lát theo chuẩn môn học) và **không có biểu đồ 3D / hai trục y** — đã được kiểm định ở Hồi 4, không được phá vỡ trên slide.
9. **Không đưa số tuyệt đối của doanh nghiệp khác quy mô lên cùng một trục** so sánh — đây là điều Slide 08 nói "không làm", đừng làm ngược lại trên slide.
10. **Không nói "kết quả này đại diện cho doanh nghiệp Việt Nam"** — phạm vi là 14 DN trong `public_test`.
11. **Không mô tả pipeline/quy trình kỹ thuật ở slide kết luận.** Slide 13 và 14 chỉ nói **kết luận**, **hạn chế** và **hướng phát triển dự kiến** — không kể "quy trình gồm mấy bước", không nhắc tên notebook/artifact, không vẽ sơ đồ pipeline. Kỹ thuật đã được kiểm định thì để dành cho phần hỏi đáp hoặc slide phụ.
12. **Không đưa công thức lên slide dưới dạng "đối tượng toán học trừu tượng".** Khi cần nói về cách tính, nói theo kiểu *đọc được*: "mẫu số là số ngày lịch thực tế, không phải số ngày có đơn" — kèm công thức ở phần tài liệu này để giảng viên đối chiếu.

---

[STATUS: ACTIVE]
