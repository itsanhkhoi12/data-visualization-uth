---
name: nx-plugins
description: Find and add Nx plugins. USE WHEN user wants to discover available plugins, install a new plugin, or add support for a specific framework or technology to the workspace.
---

# 🧭 NX-PLUGINS SKILL — Discover & Install Nx Plugins

> **Mirror Nx skill `nx-plugins` cho Gemini Agent — khám phá plugin có sẵn và cài plugin mới để mở rộng Nx workspace.**
> **Primary principle:** Clarify First · No Assumptions · Discover Before Install · Dependency Authorization · Sequential Execution.

<div align="center">

<img src="https://img.shields.io/badge/SKILL-nx--plugins-111827?style=for-the-badge&logo=nrwl&logoColor=FFFFFF" alt="nx-plugins" />
<img src="https://img.shields.io/badge/MODE-Discover%20%26%20Install-0B1220?style=for-the-badge&logo=puzzle&logoColor=2F81F7" alt="Discover & Install" />
<img src="https://img.shields.io/badge/COMMANDS-pnpm%20nx%20add-0B1220?style=for-the-badge&logo=pnpm&logoColor=0A9EDC" alt="pnpm nx add" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=FF6B6B" alt="Gemini Mirror" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>2</strong><br/>Skill Sections</td>
<td align="center"><strong>2</strong><br/>CLI Commands</td>
<td align="center"><strong>1</strong><br/>Install Method</td>
<td align="center"><strong>100%</strong><br/>Authorization Discipline</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>Mirror Byte-Identical</td>
<td align="center"><strong>0</strong><br/>Implicit Dependency Adds</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Skill** | `nx-plugins` (NPM name) |
| **File** | `.gemini/skills/nx-plugins/skill.md` |
| **Purpose** | Khám phá và cài Nx plugins cho workspace |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/nx-plugins/SKILL.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables + frontmatter preserved |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **skill SKILL.md mirror** cho Gemini Agent. YAML frontmatter (`name` + `description`) ở đầu file là bắt buộc và không được sửa. Nội dung skill bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/nx-plugins/SKILL.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic SKILL instructions.

> [!TIP]
> Trước khi `pnpm nx add <plugin>`, hãy `pnpm nx list` để xác nhận plugin đã có sẵn trong workspace version. Parent governance yêu cầu **dependency authorization** rõ ràng trước khi thêm plugin, không tự ý inject.

> [!WARNING]
> Không tự ý cài plugin trong task ký — chỉ thực hiện khi đã có dependency authorization từ Human; tránh thay đổi `package.json`/`pnpm-lock.yaml` ngoài scope.

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-finding-and-installing-new-plugins) | Finding and Installing new plugins |
| [02](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

---

# skill.md — Xác nhận quản trị quy tắc

- **Motivation/Background**: Human yêu cầu đọc, phổ biến và ký xác nhận các quy tắc trước khi làm việc với app.
- **Purpose**: Ghi nhận người đại diện, phạm vi đọc và cam kết áp dụng; bảo toàn nội dung nguồn bên dưới.
- **Overview Pipeline**: Kiểm kê → đọc theo phạm vi → review → phổ biến → ký tuần tự → kiểm chứng.
- **Detailed Plan**: Nội dung nguồn (nếu có); xác nhận; manifest và cách áp dụng tại bản xác nhận dùng chung.
- **References**: [working_rule.md](../../../working_rule.md)
- **Created**: 2026-10-07T15:52:38+07:00
- **Last Updated**: 2026-10-08T05:18:00+07:00

---


<a id="01-finding-and-installing-new-plugins"></a>

## 🧭 Finding and Installing new plugins

- List plugins: `pnpm nx list`
- Install plugins `pnpm nx add <plugin>`. Example: `pnpm nx add @nx/react`.


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/nx-plugins/skill.md](skill.md); SHA-256 trước ký: `96659fc0ea92b133445cf5d356f4ee710396fc4da22aaa515ad7a6f7ef39a5dd`.
- **Đọc nguồn**: /root/agent_configs (đọc toàn bộ nguồn được giao; bản mirror giống byte được đối chiếu); Main Agent (review tổng hợp).
- **Bản phổ biến và inventory**: [.agents/SIGNATURE.md](../../../.agents/SIGNATURE.md).
- **Cam kết**: Áp dụng quy tắc liên quan trước mỗi task, bảo vệ scope/code ổn định/kiến trúc/dữ liệu, báo rõ conflict và validation; không tuyên bố kết quả chưa kiểm chứng. Quy tắc project được áp dụng theo thứ tự ưu tiên chỉ dẫn hiện hành.
- **Phạm vi đại diện**: Main Agent và các subagent được huy động trong phiên này. Bản ký tại các thư mục Claude/Cursor/Gemini là thông báo đại diện theo yêu cầu Human; không phải xác nhận các agent bên ngoài đã trực tiếp nhận hoặc tự ký. Agent tương lai phải đọc nguồn hiện hành trước khi làm việc.
- **Giới hạn ghi nhớ**: File xác nhận là record để đọc lại ở phiên sau; không cam kết mọi hệ thống AI tự ghi nhớ vĩnh viễn.
- **Signature**: `Codex — Main Agent — sgod-sam-v2 coordinator — 2026-10-07 (+07:00)`.

---

<div align="center">

**[⬆ Back to Top](#table-of-contents)**

<sub>Maintained by Gemini Agent · Last Updated `2026-10-08T05:18:00+07:00`</sub>

</div>
