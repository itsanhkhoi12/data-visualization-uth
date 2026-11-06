---
name: nx-generate
description: Generate code using nx generators. INVOKE IMMEDIATELY when user mentions scaffolding, setup, structure, creating apps/libs, or setting up project structure. Trigger words - scaffold, setup, create a ... app, create a ... lib, project structure, generate, add a new project. ALWAYS use this BEFORE calling nx_docs or exploring - this skill handles discovery internally.
---

# 🧭 NX-GENERATE SKILL — Run Nx Generators (Scaffolding Discovery)

> **Mirror Nx skill `nx-generate` cho Gemini Agent — chạy generators để scaffold apps/libs/migration code; ưu tiên local generator và luôn dùng `--no-interactive`.**
> **Primary principle:** Clarify First · No Assumptions · Discover All Generators · Always `--no-interactive` · Dry-run First · Verify Generated Code · Human Owns the Decision.

<div align="center">

<img src="https://img.shields.io/badge/SKILL-nx--generate-111827?style=for-the-badge&logo=nrwl&logoColor=FFFFFF" alt="nx-generate" />
<img src="https://img.shields.io/badge/MODE-Scaffold-0B1220?style=for-the-badge&logo=stackblitz&logoColor=2F81F7" alt="Scaffold Mode" />
<img src="https://img.shields.io/badge/FLOW-9%20Steps-0B1220?style=for-the-badge&logo=flow&logoColor=0A9EDC" alt="9-Step Flow" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=FF6B6B" alt="Gemini Mirror" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>9</strong><br/>Discovery → Verify Steps</td>
<td align="center"><strong>1</strong><br/>Local-vs-External Rule</td>
<td align="center"><strong>4</strong><br/>Buildable Strategies</td>
<td align="center"><strong>100%</strong><br/>Dry-Run First</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>Mirror Byte-Identical</td>
<td align="center"><strong>0</strong><br/>Empty Test Suites</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Skill** | `nx-generate` (NPM name) |
| **File** | `.gemini/skills/nx-generate/skill.md` |
| **Purpose** | Chạy Nx generators để scaffold apps/libs/migration code (luôn `--no-interactive`) |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/nx-generate/SKILL.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables + frontmatter preserved |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **skill SKILL.md mirror** cho Gemini Agent. YAML frontmatter (`name` + `description`) ở đầu file là bắt buộc và không được sửa. Nội dung skill bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/nx-generate/SKILL.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic SKILL instructions.

> [!TIP]
> Generator có thể có schema đầy đủ nhưng không nói rõ side-effects hay file structure — **đọc source code của generator là bắt buộc**. Nếu generator không support `--dry-run` (vd nó cài npm package), chạy thật với `--no-interactive` sau khi đã verify.
> Khi cả local workspace generator và external plugin generator đều khả thi, **luôn ưu tiên local generator** vì đã được customize cho repo pattern.

> [!WARNING]
> Generated code phải pass `nx run-many -t build,lint,test,typecheck`; không chỉ chạy target cho project vừa tạo. Empty `*.spec.ts` sẽ khiến `nx test` fail — nếu xóa, phải xóa luôn `test` target khỏi project config.

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-overview) | Run Nx Generator — Overview |
| [02](#02-key-principles) | Key Principles |
| [03](#03-steps) | Steps |
| [04](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

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


<a id="01-overview"></a>

# 🧭 Run Nx Generator

Nx generators are powerful tools that scaffold projects, make automated code migrations or automate repetitive tasks in a monorepo. They ensure consistency across the codebase and reduce boilerplate work.

This skill applies when the user wants to:

- Create new projects like libraries or applications
- Scaffold features or boilerplate code
- Run workspace-specific or custom generators
- Do anything else that an nx generator exists for

<a id="02-key-principles"></a>

## 🧭 Key Principles

1. **Always use `--no-interactive`** - Prevents prompts that would hang execution
2. **Read the generator source code** - The schema alone is not enough; understand what the generator actually does
3. **Match existing repo patterns** - Study similar artifacts in the repo and follow their conventions
4. **Verify with lint/test/build/typecheck etc.** - Generated code must pass verification. The listed targets are just an example, use what's appropriate for this workspace.

<a id="03-steps"></a>

## 🧭 Steps

### 1. Discover Available Generators

Use the Nx CLI to discover available generators:

- List all generators for a plugin: `npx nx list @nx/react`
- View available plugins: `npx nx list`

This includes plugin generators (e.g., `@nx/react:library`) and local workspace generators.

### 2. Match Generator to User Request

Identify which generator(s) could fulfill the user's needs. Consider what artifact type they want, which framework is relevant, and any specific generator names mentioned.

**IMPORTANT**: When both a local workspace generator and an external plugin generator could satisfy the request, **always prefer the local workspace generator**. Local generators are customized for the specific repo's patterns.

If no suitable generator exists, you can stop using this skill. However, the burden of proof is high—carefully consider all available generators before deciding none apply.

### 3. Get Generator Options

Use the `--help` flag to understand available options:

```bash
npx nx g @nx/react:library --help
```

Pay attention to required options, defaults that might need overriding, and options relevant to the user's request.

### Library Buildability

**Default to non-buildable libraries** unless there's a specific reason for buildable.

| Type                        | When to use                                                       | Generator flags                     |
| --------------------------- | ----------------------------------------------------------------- | ----------------------------------- |
| **Non-buildable** (default) | Internal monorepo libs consumed by apps                           | No `--bundler` flag                 |
| **Buildable**               | Publishing to npm, cross-repo sharing, stable libs for cache hits | `--bundler=vite` or `--bundler=swc` |

Non-buildable libs:

- Export `.ts`/`.tsx` source directly
- Consumer's bundler compiles them
- Faster dev experience, less config

Buildable libs:

- Have their own build target
- Useful for stable libs that rarely change (cache hits)
- Required for npm publishing

**If unclear, ask the user:** "Should this library be buildable (own build step, better caching) or non-buildable (source consumed directly, simpler setup)?"

### 4. Read Generator Source Code

**This step is critical.** The schema alone does not tell you everything. Reading the source code helps you:

- Know exactly what files will be created/modified and where
- Understand side effects (updating configs, installing deps, etc.)
- Identify behaviors and options not obvious from the schema
- Understand how options interact with each other

To find generator source code:

- For plugin generators: Use `node -e "console.log(require.resolve('@nx/<plugin>/generators.json'));"` to find the generators.json, then locate the source from there
- If that fails, read directly from `node_modules/<plugin>/generators.json`
- For local generators: Typically in `tools/generators/` or a local plugin directory. Search the repo for the generator name.

After reading the source, reconsider: Is this the right generator? If not, go back to step 2.

> **⚠️ `--directory` flag behavior can be misleading.**
> It should specify the full path of the generated library or component, not the parent path that it will be generated in.
>
> ```bash
> # ✅ Correct - directory is the full path for the library
> nx g @nx/react:library --directory=libs/my-lib
> # generates libs/my-lib/package.json and more
>
> # ❌ Wrong - this will create files at libs and libs/src/...
> nx g @nx/react:library --name=my-lib --directory=libs
> # generates libs/package.json and more
> ```

### 5. Examine Existing Patterns

Before generating, examine the target area of the codebase:

- Look at similar existing artifacts (other libraries, applications, etc.)
- Identify naming conventions, file structures, and configuration patterns
- Note which test runners, build tools, and linters are used
- Configure the generator to match these patterns

### 6. Dry-Run to Verify File Placement

**Always run with `--dry-run` first** to verify files will be created in the correct location:

```bash
npx nx g @nx/react:library --name=my-lib --dry-run --no-interactive
```

Review the output carefully. If files would be created in the wrong location, adjust your options based on what you learned from the generator source code.

Note: Some generators don't support dry-run (e.g., if they install npm packages). If dry-run fails for this reason, proceed to running the generator for real.

### 7. Run the Generator

Execute the generator:

```bash
nx generate <generator-name> <options> --no-interactive
```

> **Tip:** New packages often need workspace dependencies wired up (e.g., importing shared types, being consumed by apps). The `link-workspace-packages` skill can help add these correctly.

### 8. Modify Generated Code (If Needed)

Generators provide a starting point. Modify the output as needed to:

- Add or modify functionality as requested
- Adjust imports, exports, or configurations
- Integrate with existing code patterns

**Important:** If you replace or delete generated test files (e.g., `*.spec.ts`), either write meaningful replacement tests or remove the `test` target from the project configuration. Empty test suites will cause `nx test` to fail.

### 9. Format and Verify

Format all generated/modified files:

```bash
nx format --fix
```

This example is for built-in nx formatting with prettier. There might be other formatting tools for this workspace, use these when appropriate.

Then verify the generated code works. Keep in mind that the changes you make with a generator or subsequent modifications might impact various projects so it's usually not enough to only run targets for the artifact you just created.

```bash
# these targets are just an example!
nx run-many -t build,lint,test,typecheck
```

These targets are common examples used across many workspaces. You should do research into other targets available for this workspace and its projects. CI configuration is usually a good guide for what the critical targets are that have to pass.

If verification fails with manageable issues (a few lint errors, minor type issues), fix them. If issues are extensive, attempt obvious fixes first, then escalate to the user with details about what was generated, what's failing, and what you've attempted.


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/nx-generate/skill.md](skill.md); SHA-256 trước ký: `291ab89f4189e299e319e211bb20bf3e32fd415d2f94bfada152cc39bc951014`.
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
