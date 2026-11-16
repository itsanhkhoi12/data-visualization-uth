# REFACTOR_PUBLIC_TEST_ONLY.md — Thu hẹp pipeline EDA về một split `public_test`

- **Motivation/Background**: Pipeline EDA ban đầu được thiết kế cho hai split `raw_data/train` và `raw_data/public_test`. Commit `ee87364` đã chuyển cấu hình mặc định, `scripts/run_full.py`, `README.md` và notebook sang chỉ chạy `public_test`, nhưng mã xử lý riêng cho train (so sánh rulebook, hồ sơ đáp án tham chiếu, biểu đồ đáp án, gộp hồ sơ hai split) vẫn còn trong `src/eda/script/` và chỉ là nhánh chết.
- **Purpose**: Ghi lại phạm vi xóa mã train, thay đổi hành vi duy nhất nhìn thấy được (bảng `TBL16`), và cách kiểm chứng.
- **Overview Pipeline**: Không đổi thứ tự pha `IMP-00` đến `IMP-15`; chỉ bỏ các bước chỉ chạy khi có cả hai split hoặc có `answers.jsonl`.
- **Detailed Plan**: §1 Phạm vi thay đổi; §2 Thay đổi hành vi; §3 Kiểm chứng; §4 Phần giữ nguyên có chủ đích.
- **References**: `.agents/rules/COMMIT_CONVENTION.md`, `README.md`, `src/eda/script/orchestration/pipeline.py`.
- **Created**: 2026-11-14T20:00:00+07:00
- **Last Updated**: 2026-11-14T20:00:00+07:00

---

## 1. Phạm vi thay đổi

| Thành phần | Thay đổi |
| --- | --- |
| `rulebook/rule_diff.py` | Xóa. Chỉ dùng để so sánh rulebook train với public_test. |
| `questions/answer_profile.py` | Xóa. Chỉ lập hồ sơ `answers.jsonl` của train; public_test không có đáp án. |
| `orchestration/pipeline.py` | Bỏ tính `rule_diff`, gate `rulebook_diff`, artifact `rule_diff.json`, nhánh gộp hồ sơ train + public_test, trường `EdaRun.rule_diff`. |
| `orchestration/analysis.py`, `common/bundles.py` | Bỏ `answer_profile`. |
| `common/paths.py`, `common/config.py`, `common/errors.py` | Bỏ `answers_path`, `has_labels`, `require_labels`, `LabelLeakageError`. |
| `common/enums.py` | Bỏ `DatasetSplit.TRAIN`. |
| `questions/alignment.py`, `orchestration/tables.py` | `label_access` luôn là `no_labels_for_split`; bỏ tham số `has_labels`. |
| `cross_business/aggregate.py` | `combine_global_profiles` chỉ nhận `profiles`; bổ sung import `Mapping` còn thiếu. |
| `visualization/question_charts.py`, `chart_spec_catalogue.py`, `visualization_pipeline.py` | Xóa `build_answer_charts` và đặc tả `QNA04`–`QNA07` (đáp án Train, đối chiếu Train/Public Test). |
| `reporting/global_report.py` | Bỏ giới hạn khoa học nói về so sánh train/public test. |
| `src/eda/tests/` | Xóa 5 test chỉ dành cho train; đổi fixture `split="train"` sang `public_test`. |
| `README.md` | Mô tả `questions/`, `rulebook/`; thêm `pytest`, `jupyter`, lệnh Git Bash, lệnh chạy test và notebook, cảnh báo không copy `train/`. |

## 2. Thay đổi hành vi

- Bảng `TBL16` (mục 12 của notebook, "Quy tắc nghiệp vụ theo Rulebook Public Test") trước đây hiển thị chênh lệch rulebook train và public_test, nên luôn rỗng khi chỉ có public_test. Nay `TBL16` liệt kê các quy tắc trích từ `raw_data/public_test/rulebook.md` (`rule_id`, `section`, `rule_label`, `rule_text`, `source_line`), khớp với mô tả mục 12.
- Mọi biểu đồ và gate khác không đổi.

## 3. Kiểm chứng

Chạy trên một bộ `public_test` tổng hợp (3 doanh nghiệp) cho cả bản trước và sau refactor:

| Kiểm tra | Trước | Sau |
| --- | --- | --- |
| `scripts/run_full.py` | 176 biểu đồ: 156 PASS, 20 NOT APPLICABLE | Giống hệt |
| Gate ledger | 19 PASS, 1 PARTIAL | Giống hệt |
| Notebook chạy toàn bộ | Không lỗi | Không lỗi; `TBL16` có dữ liệu |
| `pytest src/eda/tests` | 101 pass | 96 pass (bớt 5 test train) |

Hai test `test_t059_raw_sources_are_not_modified` và `test_t060_ledger_has_expected_business_counts` thất bại trên dữ liệu tổng hợp ở cả hai bản vì chúng đối chiếu với hash và số doanh nghiệp (14) của dữ liệu thật. Cần chạy lại toàn bộ test và notebook trên dữ liệu thật trước khi merge.

## 4. Phần giữ nguyên có chủ đích

- Nhãn `split="both"` trên các artifact cấp lần chạy: đây là nhãn phạm vi toàn cục, không phải logic train; đổi tên sẽ ảnh hưởng nhiều module mà không thay đổi kết quả.
- Test `test_t060_train_split_is_not_required` và `test_public_test_only_architecture`: là hàng rào bảo đảm `raw_data/train` không tồn tại.
- Tài liệu kế hoạch trong `plan/` và `docs/DEFINE-THE-PROBLEM.md`: là tài liệu lịch sử, không thuộc phạm vi chạy.
