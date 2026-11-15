from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import nbformat

NOTEBOOK_PATH = Path(__file__).resolve().parents[2] / "notebook" / "eda.ipynb"

PRELUDE_CODE = (
    "import sys\n"
    "from pathlib import Path\n"
    "\n"
    "SCRIPT_ROOT = Path.cwd() / 'src' / 'eda' / 'script'\n"
    "if not SCRIPT_ROOT.exists():\n"
    "    SCRIPT_ROOT = Path.cwd().resolve()\n"
    "    for candidate in SCRIPT_ROOT.parents:\n"
    "        if (candidate / 'src' / 'eda' / 'script').is_dir():\n"
    "            SCRIPT_ROOT = candidate / 'src' / 'eda' / 'script'\n"
    "            break\n"
    "if str(SCRIPT_ROOT) not in sys.path:\n"
    "    sys.path.insert(0, str(SCRIPT_ROOT))\n"
    "\n"
    "from IPython.display import HTML, Image, Markdown, display\n"
    "\n"
    "from common.config import load_config\n"
    "from orchestration.notebook_builder import course_figure_limits\n"
    "from orchestration.pipeline import run_eda\n"
    "from orchestration.study_examples import (\n"
    "    load_order_studies, order_audit, order_value_figure, weekly_activity_figure,\n"
    ")\n"
    "\n"
    "config = load_config()\n"
    "run = run_eda(config, figure_limits=course_figure_limits())\n"
    "run.run_id\n"
)

FIGURE_HELPER_CODE = (
    "def _show_figure(chart_id, split='public_test', limit=1):\n"
    "    html = run.figures_html(chart_id, split, limit)\n"
    "    if html:\n"
    "        display(HTML(html))\n"
)

TABLE_HELPER_CODE = (
    "def _show_table(table_id, split=None):\n"
    "    html = run.table_html(table_id, split)\n"
    "    if not html:\n"
    "        print(f'Bảng {table_id} không có dữ liệu cho split {split}')\n"
    "        return\n"
    "    display(HTML(html))\n"
)


def _section(
    section_id: str,
    title: str,
    objective: str,
    method: str,
    caveat: str,
    tables: tuple[tuple[str, str | None], ...] = (),
    charts: tuple[tuple[str, str | None, int], ...] = (),
    story_split: str | None = None,
    story_limit: int = 4,
    extra_code: str = "",
) -> dict[str, Any]:
    return {
        "id": section_id,
        "title": title,
        "objective": objective,
        "method": method,
        "caveat": caveat,
        "tables": tables,
        "charts": charts,
        "story_split": story_split,
        "story_limit": story_limit,
        "extra_code": extra_code,
    }


SECTIONS: tuple[dict[str, Any], ...] = (
    _section(
        "00",
        "Cấu hình, chạy pipeline và provenance",
        "Xác lập cấu hình, chạy pipeline EDA một lần và hiển thị ledger kiểm định "
        "cùng provenance của toàn bộ artifact sinh ra.",
        "Pipeline đọc nguồn ở chế độ chỉ đọc, tính toàn bộ chỉ số tại thời điểm nạp "
        "dữ liệu và ghi registry có hash cho từng artifact.",
        "Mọi con số trong notebook đều truy vết được về run_id, source hash và "
        "phương pháp tính; không có số liệu nào nhập tay.",
        tables=(("TBL20", None),),
    ),
    _section(
        "01",
        "Tổng quan bộ dữ liệu",
        "Mô tả phạm vi dữ liệu theo split, đơn vị đếm và mức độ bao phủ của "
        "từng doanh nghiệp.",
        "Đếm đối tượng siêu dữ liệu từ manifest và registry của từng split; "
        "số tệp và số giao dịch là hai đại lượng khác nhau.",
        "Tổng số tệp, số worksheet và số đối tượng CSDL là số đối tượng nguồn, "
        "không phải số giao dịch và không được cộng chéo.",
        tables=(("TBL01", None),),
        charts=(("INV01", "public_test", 1), ("GLOBAL06", "public_test", 1)),
    ),
    _section(
        "02",
        "Kiểm kê nguồn dữ liệu",
        "Liệt kê toàn bộ tệp, worksheet và đối tượng CSDL kèm trạng thái đọc, "
        "hash và siêu dữ liệu cấu trúc.",
        "Registry kiểm kê gom từ manifest nguồn và registry worksheet/database; "
        "mỗi bản ghi gắn content hash của tệp gốc.",
        "Nhiều tệp hơn không đồng nghĩa nhiều giao dịch hơn; tệp trong manifest "
        "được đọc ở chế độ chỉ đọc và không bị thay đổi.",
        tables=(("TBL02", "public_test"), ("TBL03", "public_test"), ("TBL04", "public_test")),
        charts=(("INV01", "public_test", 1), ("INV02", "public_test", 1), ("INV03", "public_test", 1),
                ("INV04", "public_test", 1)),
    ),
    _section(
        "03",
        "Khám phá schema và mối quan hệ",
        "Xác định kiểu vật lý và ngữ nghĩa của từng cột, cùng bằng chứng khóa "
        "chính và quan hệ giữa các bảng.",
        "Suy luận kiểu dữ liệu trên toàn bộ dòng đã đọc, kết hợp bằng chứng khóa "
        "ứng viên và kiểm tra số khóa lệch.",
        "Quan hệ ứng viên chưa được phê duyệt không được dùng để tính chỉ số; "
        "phép nối có rủi ro nhân bản bị chặn theo thiết kế.",
        tables=(("TBL05", "public_test"), ("TBL12", "public_test")),
        charts=(("GLOBAL02", "public_test", 1), ("QUAL07", "public_test", 1)),
    ),
    _section(
        "04",
        "Chất lượng dữ liệu",
        "Đo mức thiếu dữ liệu, trùng lặp, vi phạm quy tắc và mức độ phát hiện "
        "theo từng nguồn, kèm mẫu số rõ ràng.",
        "Mọi tỷ lệ đều chia cho mẫu số của chính trường hoặc chính quy tắc "
        "được hồ sơ; thiếu dữ liệu có cấu trúc tách riêng khỏi khoảng trống thực.",
        "Cờ thiếu dữ liệu và cờ trùng lặp là tín hiệu thống kê, chưa được xác định "
        "là bản ghi lỗi nếu chưa có đối chiếu rulebook.",
        tables=(("TBL06", "public_test"), ("TBL07", "public_test"), ("TBL08", "public_test"),
                ("TBL19", "public_test")),
        charts=(("QUAL01", "public_test", 1), ("QUAL02", "public_test", 1), ("QUAL04", "public_test", 1),
                ("QUAL05", "public_test", 1)),
        story_split="public_test",
        story_limit=2,
    ),
    _section(
        "05",
        "Phân tích định lượng",
        "Mô tả phân phối các đo lường định lượng trên toàn bộ dân số hợp lệ, "
        "kèm thống kê bền vững và cờ ngoại lệ theo IQR.",
        "Tính quantile, MAD, lệch và kurtosis trên toàn bộ quan sát hợp lệ; "
        "ngưỡng ngoại lệ IQR chỉ gắn cờ, không tự động loại bỏ.",
        "Kiểu vật lý không bảo đảm ngữ nghĩa đo lường; cột định danh dạng số "
        "được xử lý riêng và không đưa vào phân tích phân phối đo lường.",
        tables=(("TBL09", "public_test"),),
        charts=(("NUM01", "public_test", 2), ("NUM02", "public_test", 1), ("NUM06", "public_test", 1),
                ("NUM08", "public_test", 1)),
        story_split="public_test",
        story_limit=2,
    ),
    _section(
        "06",
        "Phân tích phân loại",
        "Khảo sát phân phối tần suất của các trường phân loại, giữ nguyên nhóm "
        "Others và ghi nhận ứng viên bí danh thay vì tự gộp.",
        "Đếm tần suất theo giá trị đã chuẩn hóa, sắp xếp theo tần suất giảm dần "
        "và ghi rõ phạm vi quan sát của mỗi trường.",
        "Cao độ lớp phụ thuộc quy tắc chuẩn hóa giá trị; các giá trị tương tự nhau "
        "về nghĩa chỉ được báo cáo là ứng viên, không tự ý hợp nhất.",
        tables=(("TBL10", "public_test"),),
        charts=(("CAT01", "public_test", 2), ("CAT02", "public_test", 1), ("CAT03", "public_test", 1)),
        story_split="public_test",
        story_limit=2,
    ),
    _section(
        "07",
        "Tương quan và phân tích đa biến",
        "Đo mức liên hệ giữa các đo lường và các trường phân loại trên cùng "
        "grain, chỉ dùng các phép nối đã được phê duyệt.",
        "Tính Pearson, Spearman, Kendall, Cramér V và bảng chéo trong phạm vi "
        "cùng một nguồn hoặc phép nối không nhân bản.",
        "Tương quan không phải quan hệ nhân quả; phép nối ứng viên chỉ được hiển thị "
        "để đánh giá rủi ro nhân bản, không dùng cho tính chỉ số.",
        tables=(("TBL12", "public_test"),),
        charts=(("REL03", "public_test", 1), ("REL06", "public_test", 1),
                ("REL08", "public_test", 1), ("REL09", "public_test", 1),
                ("REL10", "public_test", 1)),
        story_split="public_test",
        story_limit=2,
    ),
    _section(
        "08",
        "Hồ sơ thời gian và lịch",
        "Xác định ngữ nghĩa trường ngày, khoảng phủ thời gian, số ngày có hoạt "
        "động và các kỳ bị thiếu theo lịch của split.",
        "Đọc và chuẩn hóa giá trị ngày theo quy tắc từng split, đối chiếu với "
        "lịch và báo cáo khoảng phủ theo doanh nghiệp.",
        "Mỗi trường ngày giữ vai trò sự kiện riêng nên các khoảng phủ không thể so "
        "sánh trực tiếp; thiếu dữ liệu theo kỳ không được coi là giá trị bằng không.",
        tables=(("TBL11", "public_test"),),
        charts=(("TIME01", "public_test", 1), ("TIME02", "public_test", 1), ("TIME03", "public_test", 1),
                ("TIME07", "public_test", 1)),
        story_split="public_test",
        story_limit=2,
    ),
    _section(
        "09",
        "Phân tích theo từng doanh nghiệp",
        "Trình bày hồ sơ, phân loại ngành và các chỉ số kinh doanh đủ điều kiện "
        "của từng doanh nghiệp trong split.",
        "Chỉ số được tính trên grain đã xác định, tuân thủ quy tắc trạng thái của "
        "rulebook split và chỉ hiển thị khi doanh nghiệp đủ điều kiện.",
        "Doanh nghiệp thiếu điều kiện bị ghi trạng thái rõ ràng, không được thay bằng "
        "số liệu của doanh nghiệp khác để lấp chỗ trống.",
        tables=(("TBL13", "public_test"), ("TBL14", "public_test")),
    ),
    _section(
        "10",
        "Giá trị đơn hàng và ngoại lệ tại dev_001",
        "Giá trị tiền hàng điển hình của một đơn là bao nhiêu? Các đơn lớn nằm ở đâu trong phân phối?",
        "Tại dev_001, khóa là mã đơn và doanh thu là tổng Thành tiền các dòng cùng đơn. "
        "Tại dev_009, khóa là mã hóa đơn và doanh thu lấy từ Giá trị hàng. Bảng kiểm tra ghi "
        "số dòng thiếu mã, dòng trùng y hệt và số đơn thiếu dữ liệu hoặc mâu thuẫn. "
        "Giữ đơn hoàn thành và đang giao khi tính doanh thu. Xác định ngoại lệ ở cấp đơn bằng "
        "hai ngưỡng Q1 − 1,5 × IQR và Q3 + 1,5 × IQR, với IQR = Q3 − Q1.",
        "Dòng thiếu mã được loại khỏi phân tích đơn vì chưa thể xác minh thuộc đơn nào. "
        "Cờ IQR dùng để kiểm tra lại chứng từ. Các đơn ngoài ngưỡng vẫn góp vào thống kê.",
        extra_code=(
            "studies = load_order_studies(config.split_root('public_test'))\n"
            "case_figures = run.output_root / 'figures' / 'course'\n"
            "display(order_audit(studies))\n"
            "_, iqr_summary = order_value_figure(studies[0], case_figures)\n"
            "display(iqr_summary.round(2))\n"
            "display(Image(filename=str(case_figures / 'phan-phoi-gia-tri-don.png'), width=960))"
        ),
    ),
    _section(
        "11",
        "Đối chiếu nhịp bán giữa dev_001 và dev_009",
        "Số đơn hợp lệ trung bình trên từng thứ trong tuần thay đổi thế nào giữa hai doanh nghiệp?",
        "Chọn hai nguồn có mã đơn, ngày và trạng thái đủ để xác định đơn hợp lệ, với hai cách ghi khác nhau. "
        "Giữ các tháng mà mỗi ngày đều có ít nhất một đơn ghi nhận được ở cả hai nguồn. "
        "Chia số đơn hợp lệ theo thứ cho số ngày lịch của thứ đó trong các tháng chung.",
        "Mỗi cột luôn bắt đầu từ 0 và hai ô biểu đồ dùng chung thang đo. Kết quả mô tả hai doanh nghiệp "
        "trong các tháng ghi dưới bảng.",
        extra_code=(
            "weekly_plot, weekly_summary = weekly_activity_figure(studies, case_figures)\n"
            "if weekly_plot is None:\n"
            "    display(Markdown('Hai doanh nghiệp chưa có tháng nào cùng đủ ngày quan sát.'))\n"
            "else:\n"
            "    display(Markdown('Các tháng đối chiếu: ' + weekly_summary.attrs['months']))\n"
            "    display(weekly_summary.round(2))\n"
            "    display(Image(filename=str(case_figures / 'nhip-ban-theo-thu.png'), width=960))"
        ),
    ),
    _section(
        "12",
        "Quy tắc nghiệp vụ theo Rulebook Public Test",
        "Tổng hợp các quy tắc định nghĩa chỉ số và chuẩn nghiệp vụ trong rulebook.md của Public Test.",
        "Trích xuất quy tắc theo bảng và mục từ rulebook.md của Public Test.",
        "Quy tắc của Public Test là chuẩn duy nhất áp dụng cho toàn bộ phân tích nghiệp vụ.",
        tables=(("TBL16", None),),
    ),
    _section(
        "13",
        "So sánh doanh nghiệp trên toàn hệ thống",
        "Đối chiếu sự hiện diện của vai trò trường ngữ nghĩa giữa các doanh "
        "nghiệp và khả năng dựng biểu đồ theo nhóm.",
        "Phát hiện vai trò trường theo tên và đối chiếu trạng thái đủ điều kiện "
        "của từng nhóm biểu đồ theo doanh nghiệp.",
        "Cùng một vai trò ngữ nghĩa không đồng nghĩa với khóa nối tương đương; "
        "đủ điều kiện về schema không bảo đảm biểu đồ dựng được.",
        tables=(("TBL17", "public_test"),),
        charts=(("GLOBAL02", "public_test", 1), ("GLOBAL03", "public_test", 1),
                ("GLOBAL04", "public_test", 1), ("GLOBAL05", None, 1)),
        story_split="public_test",
        story_limit=1,
    ),
    _section(
        "14",
        "Phân tích dữ liệu toàn cục",
        "Kiểm tra mức độ bao phủ của 14 doanh nghiệp ở mức siêu dữ liệu.",
        "Tổng hợp số tệp, số doanh nghiệp, số worksheet, số đối tượng CSDL và "
        "số phát hiện chất lượng theo từng split.",
        "Số lượng đối tượng siêu dữ liệu không phải số giao dịch và không được "
        "cộng chéo giữa các loại đối tượng.",
        tables=(("TBL18", None),),
        charts=(("GLOBAL01", "public_test", 1), ("GLOBAL06", "public_test", 1)),
    ),
    _section(
        "15",
        "Chất lượng và mức độ sẵn sàng cho tác nhân",
        "Trình bày ledger kiểm định theo phase, trạng thái phát hiện chất lượng "
        "và danh mục phát hiện có bằng chứng.",
        "Mỗi gate ghi rõ phase, trạng thái, lý do và artifact chứng minh; mỗi "
        "phát hiện gắn mức độ, tỷ lệ và bằng chứng nguồn.",
        "Phân biệt phát hiện có bằng chứng với lỗi đã xác nhận; trạng thái BLOCKED "
        "là kết quả hợp lệ và không được nâng lên PASS để đạt hình thức.",
        tables=(("TBL19", "public_test"), ("TBL20", None)),
        charts=(("QUAL06", "public_test", 1), ("QUAL08", None, 1)),
        story_split="public_test",
        story_limit=1,
    ),
    _section(
        "16",
        "Kết luận khoa học và bàn giao",
        "Tổng hợp kết luận khoa học, hạn chế đã xác định và dòng dẫn tới từng "
        "artifact có hash để tái lập.",
        "Mỗi kết luận gắn mức tin cậy và đường dẫn bằng chứng; thẻ chuyện khoa "
        "học đính kèm theo từng nhóm nghiên cứu.",
        "Không có kết luận nào vượt quá phạm vi bằng chứng đã ghi; phần chưa đủ "
        "bằng chứng được nêu rõ thay vì bị lược bỏ.",
        tables=(),
        charts=(("GLOBAL07", "public_test", 1),),
        story_split="public_test",
        story_limit=6,
    ),
)


def course_figure_limits() -> dict[str, int]:
    limits: dict[str, int] = {}
    for section in SECTIONS:
        for chart_id, _, limit in section["charts"]:
            limits[chart_id] = max(limits.get(chart_id, 0), limit)
    return limits


NOTEBOOK_METADATA = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    },
    "language_info": {
        "name": "python",
        "version": "3.11",
        "mimetype": "text/x-python",
        "codemirror_mode": {"name": "ipython", "version": 3},
        "pygments_lexer": "ipython3",
        "nbconvert_exporter": "python",
        "file_extension": ".py",
    },
}


def _markdown_section(section: dict[str, Any]) -> str:
    return (
        f"## {section['id']}. {section['title']}\n"
        "\n"
        f"**Mục tiêu:** {section['objective']}\n"
        "\n"
        f"**Phương pháp:** {section['method']}\n"
        "\n"
        f"**Cách đọc và hạn chế:** {section['caveat']}\n"
    )


def _code_section(section: dict[str, Any]) -> str:
    lines: list[str] = []
    for table_id, split in section["tables"]:
        if split is None:
            lines.append(f"_show_table('{table_id}')")
        else:
            lines.append(f"_show_table('{table_id}', '{split}')")
    if section["tables"]:
        lines.append("")
    for chart_id, split, limit in section["charts"]:
        if split is None:
            lines.append(f"_show_figure('{chart_id}', None, {limit})")
        else:
            lines.append(f"_show_figure('{chart_id}', '{split}', {limit})")
    if section["charts"]:
        lines.append("")
    if section["story_split"] is not None:
        lines.append("display(Markdown(run.story_cards_markdown(")
        lines.append(f"    '{section['story_split']}'")
        lines.append(f")[:{section['story_limit'] * 2600}]))")
        lines.append("")
    if section["extra_code"]:
        lines.append(section["extra_code"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_notebook() -> nbformat.NotebookNode:
    notebook = nbformat.v4.new_notebook()
    notebook.metadata.update(NOTEBOOK_METADATA)
    cells: list[Any] = [
        nbformat.v4.new_markdown_cell(
            source=(
                "# Khám phá dữ liệu vận hành của 14 doanh nghiệp\n"
                "\n"
                "Nguồn phân tích là bộ DataMate `public_test`. Bắt đầu từ các câu hỏi "
                "về độ phủ và chất lượng của 14 doanh nghiệp, sau đó tìm hiểu phân phối "
                "giá trị đơn ở dev_001 và đối chiếu nhịp bán với dev_009.\n"
                "\n"
                "**Cách kiểm tra số liệu.** Xác định một dòng đại diện cho điều gì, "
                "đọc README và rulebook, kiểm tra ngày và trạng thái, rồi mới gộp dòng "
                "về mã đơn. Kết luận chỉ áp dụng cho các nguồn và kỳ được ghi trên biểu đồ.\n"
            )
        ),
        nbformat.v4.new_code_cell(source=PRELUDE_CODE),
        nbformat.v4.new_code_cell(source=FIGURE_HELPER_CODE),
        nbformat.v4.new_code_cell(source=TABLE_HELPER_CODE),
    ]
    for section in SECTIONS:
        cells.append(nbformat.v4.new_markdown_cell(source=_markdown_section(section)))
        cells.append(nbformat.v4.new_code_cell(source=_code_section(section)))
    notebook.cells = cells
    return notebook


def write_notebook(target: Path | None = None) -> Path:
    destination = target or NOTEBOOK_PATH
    notebook = build_notebook()
    nbformat.validate(notebook)
    destination.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(notebook, str(destination))
    return destination


def notebook_payload() -> dict[str, Any]:
    return {
        "sections": [
            {
                "id": section["id"],
                "title": section["title"],
                "tables": [item[0] for item in section["tables"]],
                "charts": [item[0] for item in section["charts"]],
            }
            for section in SECTIONS
        ],
        "section_count": len(SECTIONS),
    }


if __name__ == "__main__":
    path = write_notebook()
    print(json.dumps({"path": str(path), **notebook_payload()}, ensure_ascii=False))
