---
name: link-workspace-packages
description: 'Link workspace packages in monorepos (npm, yarn, pnpm, bun). USE WHEN: (1) you just created or generated new packages and need to wire up their dependencies, (2) user imports from a sibling package and needs to add it as a dependency, (3) you get resolution errors for workspace packages (@org/*) like "cannot find module", "failed to resolve import", "TS2307", or "cannot resolve". DO NOT patch around with tsconfig paths or manual package.json edits - use the package manager''s workspace commands to fix actual linking.'
---

# 🧭 LINK-WORKSPACE-PACKAGES SKILL — Monorepo Workspace Linking

> **Mirror Nx skill `link-workspace-packages` cho Gemini Agent — wire up inter-package dependencies trong monorepo đúng cách (pnpm/yarn/npm/bun workspace commands).**
> **Primary principle:** Clarify First · No Assumptions · Detect Package Manager · Use Real Workspace Commands · Never Patch with TSConfig Paths.

<div align="center">

<img src="https://img.shields.io/badge/SKILL-link--workspace--packages-111827?style=for-the-badge&logo=npm&logoColor=FFFFFF" alt="link-workspace-packages" />
<img src="https://img.shields.io/badge/PM%20SUPPORT-4-0B1220?style=for-the-badge&logo=pnpm&logoColor=2F81F7" alt="4 Package Managers" />
<img src="https://img.shields.io/badge/WORKSPACE-Protocol%20Aware-0B1220?style=for-the-badge&logo=protocol&logoColor=0A9EDC" alt="Workspace Protocol" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=FF6B6B" alt="Gemini Mirror" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>4</strong><br/>Package Managers</td>
<td align="center"><strong>4</strong><br/>Lockfile Heuristics</td>
<td align="center"><strong>3</strong><br/>Debug Examples</td>
<td align="center"><strong>100%</strong><br/>Real Workspace Commands</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>Mirror Byte-Identical</td>
<td align="center"><strong>0</strong><br/>tsconfig Path Patches</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Skill** | `link-workspace-packages` (NPM name) |
| **File** | `.gemini/skills/link-workspace-packages/skill.md` |
| **Purpose** | Wire up inter-package dependencies trong monorepo (pnpm/yarn/npm/bun) |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/link-workspace-packages/SKILL.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables + frontmatter preserved |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **skill SKILL.md mirror** cho Gemini Agent. YAML frontmatter (`name` + `description`) ở đầu file là bắt buộc và không được sửa. Nội dung skill bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/link-workspace-packages/SKILL.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic SKILL instructions.

> [!WARNING]
> **NEVER patch around với tsconfig paths hoặc manual `package.json` edits** — phải dùng package manager workspace commands thực sự. Mask lỗi resolution bằng hack là anti-pattern; gây ra phantom deps, hoisting inconsistency, publish issues sau này.

> [!TIP]
> Detect package manager theo thứ tự: `packageManager` field → lockfile (`pnpm-lock.yaml` / `yarn.lock` / `bun.lock` / `package-lock.json`). Workspace protocol: pnpm/yarn/bun dùng `workspace:*`, npm không có nhưng auto-symlink. Hoisting khác nhau giữa các manager (npm/bun: hoisted root; pnpm: strict; yarn berry: PnP).

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-link-workspace-packages) | Link Workspace Packages |
| [02](#02-detect-package-manager) | Detect Package Manager |
| [03](#03-workflow) | Workflow |
| [04](#04-pnpm) | pnpm |
| [05](#05-yarn-v2-berry) | yarn (v2+/berry) |
| [06](#06-npm) | npm |
| [07](#07-bun) | bun |
| [08](#08-examples) | Examples |
| [09](#09-notes) | Notes |
| [10](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

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


<a id="01-link-workspace-packages"></a>

# 🧭 Link Workspace Packages

Add dependencies between packages in a monorepo. All package managers support workspaces but with different syntax.

<a id="02-detect-package-manager"></a>

## 🧭 Detect Package Manager

Check whether there's a `packageManager` field in the root-level `package.json`.

Alternatively check lockfile in repo root:

- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `bun.lock` / `bun.lockb` → bun
- `package-lock.json` → npm

<a id="03-workflow"></a>

## 🧭 Workflow

1. Identify consumer package (the one importing)
2. Identify provider package(s) (being imported)
3. Add dependency using package manager's workspace syntax
4. Verify symlinks created in consumer's `node_modules/`

---

<a id="04-pnpm"></a>

## 🧭 pnpm

Uses `workspace:` protocol - symlinks only created when explicitly declared.

```bash
# From consumer directory
pnpm add @org/ui --workspace

# Or with --filter from anywhere
pnpm add @org/ui --filter @org/app --workspace
```

Result in `package.json`:

```json
{ "dependencies": { "@org/ui": "workspace:*" } }
```

---

<a id="05-yarn-v2-berry"></a>

## 🧭 yarn (v2+/berry)

Also uses `workspace:` protocol.

```bash
yarn workspace @org/app add @org/ui
```

Result in `package.json`:

```json
{ "dependencies": { "@org/ui": "workspace:^" } }
```

---

<a id="06-npm"></a>

## 🧭 npm

No `workspace:` protocol. npm auto-symlinks workspace packages.

```bash
npm install @org/ui --workspace @org/app
```

Result in `package.json`:

```json
{ "dependencies": { "@org/ui": "*" } }
```

npm resolves to local workspace automatically during install.

---

<a id="07-bun"></a>

## 🧭 bun

Supports `workspace:` protocol (pnpm-compatible).

```bash
cd packages/app && bun add @org/ui
```

Result in `package.json`:

```json
{ "dependencies": { "@org/ui": "workspace:*" } }
```

---

<a id="08-examples"></a>

## 🧭 Examples

**Example 1: pnpm - link ui lib to app**

```bash
pnpm add @org/ui --filter @org/app --workspace
```

**Example 2: npm - link multiple packages**

```bash
npm install @org/data-access @org/ui --workspace @org/dashboard
```

**Example 3: Debug "Cannot find module"**

1. Check if dependency is declared in consumer's `package.json`
2. If not, add it using appropriate command above
3. Run install (`pnpm install`, `npm install`, etc.)

<a id="09-notes"></a>

## 🧭 Notes

- Symlinks appear in `<consumer>/node_modules/@org/<package>`
- **Hoisting differs by manager:**
  - npm/bun: hoist shared deps to root `node_modules`
  - pnpm: no hoisting (strict isolation, prevents phantom deps)
  - yarn berry: uses Plug'n'Play by default (no `node_modules`)
- Root `package.json` should have `"private": true` to prevent accidental publish


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/link-workspace-packages/skill.md](skill.md); SHA-256 trước ký: `f1f4a8dfc3e6392fe834807587f86de69109738b2b75ae4d2c21ddaec84fe454`.
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
