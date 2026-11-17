---
name: nx-run-tasks
description: Helps with running tasks in an Nx workspace. USE WHEN the user wants to execute build, test, lint, serve, or run any other tasks defined in the workspace.
---

# 🧭 NX-RUN-TASKS SKILL — Execute Nx Tasks (Single · Many · Affected)

> **Mirror Nx skill `nx-run-tasks` cho Gemini Agent — chạy tasks trong Nx workspace: `nx run`, `nx run-many`, `nx affected` với package manager phù hợp.**
> **Primary principle:** Clarify First · No Assumptions · Correct Package Manager · Affected Boundary Verification · Sequential Execution.

<div align="center">

<img src="https://img.shields.io/badge/SKILL-nx--run--tasks-111827?style=for-the-badge&logo=nrwl&logoColor=FFFFFF" alt="nx-run-tasks" />
<img src="https://img.shields.io/badge/MODE-Execute%20Tasks-0B1220?style=for-the-badge&logo=play&logoColor=2F81F7" alt="Execute Mode" />
<img src="https://img.shields.io/badge/COMMANDS-nx%20CLI-0B1220?style=for-the-badge&logo=nx&logoColor=0A9EDC" alt="Nx CLI" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=FF6B6B" alt="Gemini Mirror" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>4</strong><br/>Task Execution Modes</td>
<td align="center"><strong>3</strong><br/>CLI Wrappers</td>
<td align="center"><strong>4</strong><br/>Useful Flags</td>
<td align="center"><strong>100%</strong><br/>Sequential Discipline</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>pm-aware Strategy</td>
<td align="center"><strong>0</strong><br/>Parallel CLI Default</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Skill** | `nx-run-tasks` (NPM name) |
| **File** | `.gemini/skills/nx-run-tasks/skill.md` |
| **Purpose** | Chạy build/test/lint/serve và các task khác trong Nx workspace |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/nx-run-tasks/SKILL.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables + frontmatter preserved |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **skill SKILL.md mirror** cho Gemini Agent. YAML frontmatter (`name` + `description`) ở đầu file là bắt buộc và không được sửa. Nội dung skill bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/nx-run-tasks/SKILL.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic SKILL instructions.

> [!TIP]
> Detect package manager từ `pnpm-lock.yaml` / `yarn.lock` / `package-lock.json` / `bun.lock` rồi mới prefix `npx`/`pnpx`/`yarn` cho `nx`. `--parallel` mặc định = 3, nhưng parent governance cấm parallel execution — chỉnh về `--parallel=1` cho task thuộc scope sequential governance.

> [!WARNING]
> `--configuration` production chỉ dùng khi đã được Human approve cho deployment. Không tự ý chuyển configuration trong mid-development.

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-understand-which-tasks-can-be-run) | Understand which tasks can be run |
| [02](#02-run-a-single-task) | Run a single task |
| [03](#03-run-multiple-tasks) | Run multiple tasks |
| [04](#04-run-tasks-for-affected-projects) | Run tasks for affected projects |
| [05](#05-useful-flags) | Useful flags |
| [06](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

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


You can run tasks with Nx in the following way.

Keep in mind that you might have to prefix things with npx/pnpx/yarn if the user doesn't have nx installed globally. Look at the package.json or lockfile to determine which package manager is in use.

For more details on any command, run it with `--help` (e.g. `nx run-many --help`, `nx affected --help`).

<a id="01-understand-which-tasks-can-be-run"></a>

## 🧭 Understand which tasks can be run

You can check those via `nx show project <projectname> --json`, for example `nx show project myapp --json`. It contains a `targets` section which has information about targets that can be run. You can also just look at the `package.json` scripts or `project.json` targets, but you might miss out on inferred tasks by Nx plugins.

<a id="02-run-a-single-task"></a>

## 🧭 Run a single task

```
nx run <project>:<task>
```

where `project` is the project name defined in `package.json` or `project.json` (if present).

<a id="03-run-multiple-tasks"></a>

## 🧭 Run multiple tasks

```
nx run-many -t build test lint typecheck
```

You can pass a `-p` flag to filter to specific projects, otherwise it runs on all projects. You can also use `--exclude` to exclude projects, and `--parallel` to control the number of parallel processes (default is 3).

Examples:

- `nx run-many -t test -p proj1 proj2` — test specific projects
- `nx run-many -t test --projects=*-app --exclude=excluded-app` — test projects matching a pattern
- `nx run-many -t test --projects=tag:api-*` — test projects by tag

<a id="04-run-tasks-for-affected-projects"></a>

## 🧭 Run tasks for affected projects

Use `nx affected` to only run tasks on projects that have been changed and projects that depend on changed projects. This is especially useful in CI and for large workspaces.

```
nx affected -t build test lint
```

By default it compares against the base branch. You can customize this:

- `nx affected -t test --base=main --head=HEAD` — compare against a specific base and head
- `nx affected -t test --files=libs/mylib/src/index.ts` — specify changed files directly

<a id="05-useful-flags"></a>

## 🧭 Useful flags

These flags work with `run`, `run-many`, and `affected`:

- `--skipNxCache` — rerun tasks even when results are cached
- `--verbose` — print additional information such as stack traces
- `--nxBail` — stop execution after the first failed task
- `--configuration=<name>` — use a specific configuration (e.g. `production`)


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/nx-run-tasks/skill.md](skill.md); SHA-256 trước ký: `544e773afd7eb6d22b7768f8932a150f6767becb61b34608060d0f11bcb722f3`.
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
