# 🧭 NX-WORKSPACE AFFECTED REFERENCE — Affected Projects Discovery

> **Mirror reference doc `AFFECTED.md` của skill `nx-workspace` cho Gemini Agent — công thức CLI để khám phá affected projects với base/head/uncommitted/untracked đúng scope.**
> **Primary principle:** Clarify First · No Assumptions · Explicit Base/Head · Affected Boundary Verification · Sequential Execution.

<div align="center">

<img src="https://img.shields.io/badge/REF-nx--workspace--affected-111827?style=for-the-badge&logo=nrwl&logoColor=FFFFFF" alt="nx-workspace affected" />
<img src="https://img.shields.io/badge/COMMANDS-affected-0B1220?style=for-the-badge&logo=nx&logoColor=2F81F7" alt="affected CLI" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=0A9EDC" alt="Gemini Mirror" />
<img src="https://img.shields.io/badge/COMPLIANCE-Sequential-0B1220?style=for-the-badge&logo=shield&logoColor=FF6B6B" alt="Sequential Compliance" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>1</strong><br/>Topic (Affected Projects)</td>
<td align="center"><strong>9</strong><br/>CLI Recipes</td>
<td align="center"><strong>4</strong><br/>Affected Modes</td>
<td align="center"><strong>100%</strong><br/>Explicit Base/Head</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>Mirror Byte-Identical</td>
<td align="center"><strong>0</strong><br/>Implicit Base Reads</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Reference** | `nx-workspace` → `references/AFFECTED.md` |
| **File** | `.gemini/skills/nx-workspace/references/AFFECTED.md` |
| **Purpose** | Reference doc cho affected-project discovery trong Nx workspace |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/nx-workspace/references/AFFECTED.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **reference doc mirror** cho Gemini Agent. Nội dung reference bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/nx-workspace/references/AFFECTED.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic recipes.

> [!TIP]
> Luôn xác định **explicit base/head** hoặc `--files` để giới hạn scope affected boundary. Auto-detect base có thể trả về false positives nếu branch hiện tại chưa được track đúng. Members plan của workspace này là lịch sử, không authorization app task hiện tại.

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-affected-projects) | Affected Projects |
| [02](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

---

# AFFECTED.md — Xác nhận quản trị quy tắc

- **Motivation/Background**: Human yêu cầu đọc, phổ biến và ký xác nhận các quy tắc trước khi làm việc với app.
- **Purpose**: Ghi nhận người đại diện, phạm vi đọc và cam kết áp dụng; bảo toàn nội dung nguồn bên dưới.
- **Overview Pipeline**: Kiểm kê → đọc theo phạm vi → review → phổ biến → ký tuần tự → kiểm chứng.
- **Detailed Plan**: Nội dung nguồn (nếu có); xác nhận; manifest và cách áp dụng tại bản xác nhận dùng chung.
- **References**: [working_rule.md](../../../../working_rule.md)
- **Created**: 2026-10-07T15:52:38+07:00
- **Last Updated**: 2026-10-08T05:18:00+07:00

---

<a id="01-affected-projects"></a>

## 🧭 Affected Projects

Find projects affected by changes in the current branch.

```bash
# Affected since base branch (auto-detected)
nx show projects --affected

# Affected with explicit base
nx show projects --affected --base=main
nx show projects --affected --base=origin/main

# Affected between two commits
nx show projects --affected --base=abc123 --head=def456

# Affected apps only
nx show projects --affected --type app

# Affected excluding e2e projects
nx show projects --affected --exclude="*-e2e"

# Affected by uncommitted changes
nx show projects --affected --uncommitted

# Affected by untracked files
nx show projects --affected --untracked
```


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/nx-workspace/references/AFFECTED.md](AFFECTED.md); SHA-256 trước ký: `5c3243ced18c3cd7b3f330accbfd87df55e076c689f12ea0e4191a9604d6a8b9`.
- **Đọc nguồn**: /root/agent_configs (đọc toàn bộ nguồn được giao; bản mirror giống byte được đối chiếu); Main Agent (review tổng hợp).
- **Bản phổ biến và inventory**: [.agents/SIGNATURE.md](../../../../.agents/SIGNATURE.md).
- **Cam kết**: Áp dụng quy tắc liên quan trước mỗi task, bảo vệ scope/code ổn định/kiến trúc/dữ liệu, báo rõ conflict và validation; không tuyên bố kết quả chưa kiểm chứng. Quy tắc project được áp dụng theo thứ tự ưu tiên chỉ dẫn hiện hành.
- **Phạm vi đại diện**: Main Agent và các subagent được huy động trong phiên này. Bản ký tại các thư mục Claude/Cursor/Gemini là thông báo đại diện theo yêu cầu Human; không phải xác nhận các agent bên ngoài đã trực tiếp nhận hoặc tự ký. Agent tương lai phải đọc nguồn hiện hành trước khi làm việc.
- **Giới hạn ghi nhớ**: File xác nhận là record để đọc lại ở phiên sau; không cam kết mọi hệ thống AI tự ghi nhớ vĩnh viễn.
- **Signature**: `Codex — Main Agent — sgod-sam-v2 coordinator — 2026-10-07 (+07:00)`.

---

<div align="center">

**[⬆ Back to Top](#table-of-contents)**

<sub>Maintained by Gemini Agent · Last Updated `2026-10-08T05:18:00+07:00`</sub>

</div>
