---
name: nx-workspace
description: "Explore and understand Nx workspaces. USE WHEN answering questions about the workspace, projects, or tasks. ALSO USE WHEN an nx command fails or you need to check available targets/configuration before running a task. EXAMPLES: 'What projects are in this workspace?', 'How is project X configured?', 'What depends on library Y?', 'What targets can I run?', 'Cannot find configuration for task', 'debug nx task failure'."
---

# 🧭 NX-WORKSPACE SKILL — Read-only Nx Workspace Exploration

> **Mirror Nx skill `nx-workspace` cho Gemini Agent — cho phép khám phá read-only Nx workspace: project structure, target configuration, available generators, dependencies.**
> **Primary principle:** Clarify First · No Assumptions · Read-only · Always Prefer Resolved JSON · Human Owns the Decision.

<div align="center">

<img src="https://img.shields.io/badge/SKILL-nx--workspace-111827?style=for-the-badge&logo=nrwl&logoColor=FFFFFF" alt="nx-workspace" />
<img src="https://img.shields.io/badge/MODE-Read%20Only-0B1220?style=for-the-badge&logo=lock&logoColor=2F81F7" alt="Read-Only Mode" />
<img src="https://img.shields.io/badge/COMMANDS-nx%20CLI-0B1220?style=for-the-badge&logo=nx&logoColor=0A9EDC" alt="Nx CLI" />
<img src="https://img.shields.io/badge/AGENT-Gemini%20Mirror-0B1220?style=for-the-badge&logo=googlegemini&logoColor=FF6B6B" alt="Gemini Mirror" />

</div>

<div align="center">
<table>
<tr>
<td align="center"><strong>7</strong><br/>Skill Sections</td>
<td align="center"><strong>1</strong><br/>Reference (`AFFECTED.md`)</td>
<td align="center"><strong>10+</strong><br/>CLI Recipes</td>
<td align="center"><strong>100%</strong><br/>Read-only</td>
</tr>
<tr>
<td align="center"><strong>1</strong><br/>JSON-first Approach</td>
<td align="center"><strong>0</strong><br/>Direct `project.json` Reads</td>
<td align="center"><strong>0</strong><br/>Hollow Praise Allowed</td>
<td align="center"><strong>30</strong><br/>Working Rule Chapters</td>
</tr>
</table>
</div>

---

## DOCUMENT CONTROL

| Field | Value |
|---|---|
| **Skill** | `nx-workspace` (NPM name) |
| **File** | `.gemini/skills/nx-workspace/skill.md` |
| **Purpose** | Khám phá read-only Nx workspace (projects, targets, generators, dependencies) |
| **Primary Language** | Tiếng Anh (skill content); tiếng Việt dùng cho header/metadata |
| **Source Mirror** | `.cursor/skills/nx-workspace/SKILL.md` (byte-identical) |
| **Last Refactor Date** | 2026-10-08 |
| **Visual Strategy** | Markdown-native + shields.io badges + GFM tables + frontmatter preserved |
| **Decision Authority** | Human / Project Owner |

> [!IMPORTANT]
> File này là **skill SKILL.md mirror** cho Gemini Agent. YAML frontmatter (`name` + `description`) ở đầu file là bắt buộc và không được sửa. Nội dung skill bên dưới được **bảo toàn nguyên văn** từ `.cursor/skills/nx-workspace/SKILL.md`. Refactor chỉ thêm header/badges/metadata/TOC phong cách; không chỉnh sửa logic SKILL instructions.

> [!TIP]
> Skill này là **read-only**: luôn dùng `nx show ... --json` rồi xử lý bằng `jq`. Đừng đọc `project.json` trực tiếp — nó chỉ chứa partial configuration. Schema đầy đủ nằm ở `node_modules/nx/schemas/`.

> [!WARNING]
> Không parallel-hóa các task trong skill: parent governance cấm parallel execution. Sequential theo `--nxBail` / `--affected` đúng scope.

## TABLE OF CONTENTS

| Section | Topic |
|---:|---|
| [01](#01-listing-projects) | Listing Projects |
| [02](#02-project-configuration) | Project Configuration |
| [03](#03-target-information) | Target Information |
| [04](#04-workspace-configuration) | Workspace Configuration |
| [05](#05-affected-projects) | Affected Projects |
| [06](#06-common-exploration-patterns) | Common Exploration Patterns |
| [07](#07-programmatic-answers) | Programmatic Answers |
| [08](#08-troubleshooting) | Troubleshooting |
| [09](#xac-nhan-quy-tac-2026-10-07-codex) | Xác nhận quy tắc (2026-10-07) |

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


# Nx Workspace Exploration

This skill provides read-only exploration of Nx workspaces. Use it to understand workspace structure, project configuration, available targets, and dependencies.

Keep in mind that you might have to prefix commands with `npx`/`pnpx`/`yarn` if nx isn't installed globally. Check the lockfile to determine the package manager in use.

<a id="01-listing-projects"></a>

## 🧭 Listing Projects

Use `nx show projects` to list projects in the workspace.

The project filtering syntax (`-p`/`--projects`) works across many Nx commands including `nx run-many`, `nx release`, `nx show projects`, and more. Filters support explicit names, glob patterns, tag references (e.g. `tag:name`), directories, and negation (e.g. `!project-name`).

```bash
# List all projects
nx show projects

# Filter by pattern (glob)
nx show projects --projects "apps/*"
nx show projects --projects "shared-*"

# Filter by tag
nx show projects --projects "tag:publishable"
nx show projects -p 'tag:publishable,!tag:internal'

# Filter by target (projects that have a specific target)
nx show projects --withTarget build

# Combine filters
nx show projects --type lib --withTarget test
nx show projects --affected --exclude="*-e2e"
nx show projects -p "tag:scope:client,packages/*"

# Negate patterns
nx show projects -p '!tag:private'
nx show projects -p '!*-e2e'

# Output as JSON
nx show projects --json
```

<a id="02-project-configuration"></a>

## 🧭 Project Configuration

Use `nx show project <name> --json` to get the full resolved configuration for a project.

**Important**: Do NOT read `project.json` directly - it only contains partial configuration. The `nx show project --json` command returns the full resolved config including inferred targets from plugins.

You can read the full project schema at `node_modules/nx/schemas/project-schema.json` to understand nx project configuration options.

```bash
# Get full project configuration
nx show project my-app --json

# Extract specific parts from the JSON
nx show project my-app --json | jq '.targets'
nx show project my-app --json | jq '.targets.build'
nx show project my-app --json | jq '.targets | keys'


# Check project metadata
nx show project my-app --json | jq '{name, root, sourceRoot, projectType, tags}'
```

<a id="03-target-information"></a>

## 🧭 Target Information

Targets define what tasks can be run on a project.

```bash
# List all targets for a project
nx show project my-app --json | jq '.targets | keys'

# Get full target configuration
nx show project my-app --json | jq '.targets.build'

# Check target executor/command
nx show project my-app --json | jq '.targets.build.executor'
nx show project my-app --json | jq '.targets.build.command'

# View target options
nx show project my-app --json | jq '.targets.build.options'

# Check target inputs/outputs (for caching)
nx show project my-app --json | jq '.targets.build.inputs'
nx show project my-app --json | jq '.targets.build.outputs'

# Find projects with a specific target
nx show projects --withTarget serve
nx show projects --withTarget e2e
```

<a id="04-workspace-configuration"></a>

## 🧭 Workspace Configuration

Read `nx.json` directly for workspace-level configuration.
You can read the full project schema at `node_modules/nx/schemas/nx-schema.json` to understand nx project configuration options.

```bash
# Read the full nx.json
cat nx.json

# Or use jq for specific sections
cat nx.json | jq '.targetDefaults'
cat nx.json | jq '.namedInputs'
cat nx.json | jq '.plugins'
cat nx.json | jq '.generators'
```

Key nx.json sections:

- `targetDefaults` - Default configuration applied to all targets of a given name
- `namedInputs` - Reusable input definitions for caching
- `plugins` - Nx plugins and their configuration
- ...and much more, read the schema or nx.json for details

<a id="05-affected-projects"></a>

## 🧭 Affected Projects

If the user is asking about affected projects, read the [affected projects reference](references/AFFECTED.md) for detailed commands and examples.

<a id="06-common-exploration-patterns"></a>

## 🧭 Common Exploration Patterns

### "What's in this workspace?"

```bash
nx show projects
nx show projects --type app
nx show projects --type lib
```

### "How do I build/test/lint project X?"

```bash
nx show project X --json | jq '.targets | keys'
nx show project X --json | jq '.targets.build'
```

### "What depends on library Y?"

```bash
# Use the project graph to find dependents
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "Y") | .key'
```

<a id="07-programmatic-answers"></a>

## 🧭 Programmatic Answers

When processing nx CLI results, use command-line tools to compute the answer programmatically rather than counting or parsing output manually. Always use `--json` flags to get structured output that can be processed with `jq`, `grep`, or other tools you have installed locally.

### Listing Projects

```bash
nx show projects --json
```

Example output:

```json
["my-app", "my-app-e2e", "shared-ui", "shared-utils", "api"]
```

Common operations:

```bash
# Count projects
nx show projects --json | jq 'length'

# Filter by pattern
nx show projects --json | jq '.[] | select(startswith("shared-"))'

# Get affected projects as array
nx show projects --affected --json | jq '.'
```

### Project Details

```bash
nx show project my-app --json
```

Example output:

```json
{
  "root": "apps/my-app",
  "name": "my-app",
  "sourceRoot": "apps/my-app/src",
  "projectType": "application",
  "tags": ["type:app", "scope:client"],
  "targets": {
    "build": {
      "executor": "@nx/vite:build",
      "options": { "outputPath": "dist/apps/my-app" }
    },
    "serve": {
      "executor": "@nx/vite:dev-server",
      "options": { "buildTarget": "my-app:build" }
    },
    "test": {
      "executor": "@nx/vite:test",
      "options": {}
    }
  },
  "implicitDependencies": []
}
```

Common operations:

```bash
# Get target names
nx show project my-app --json | jq '.targets | keys'

# Get specific target config
nx show project my-app --json | jq '.targets.build'

# Get tags
nx show project my-app --json | jq '.tags'

# Get project root
nx show project my-app --json | jq -r '.root'
```

### Project Graph

```bash
nx graph --print
```

Example output:

```json
{
  "graph": {
    "nodes": {
      "my-app": {
        "name": "my-app",
        "type": "app",
        "data": { "root": "apps/my-app", "tags": ["type:app"] }
      },
      "shared-ui": {
        "name": "shared-ui",
        "type": "lib",
        "data": { "root": "libs/shared-ui", "tags": ["type:ui"] }
      }
    },
    "dependencies": {
      "my-app": [
        { "source": "my-app", "target": "shared-ui", "type": "static" }
      ],
      "shared-ui": []
    }
  }
}
```

Common operations:

```bash
# Get all project names from graph
nx graph --print | jq '.graph.nodes | keys'

# Find dependencies of a project
nx graph --print | jq '.graph.dependencies["my-app"]'

# Find projects that depend on a library
nx graph --print | jq '.graph.dependencies | to_entries[] | select(.value[].target == "shared-ui") | .key'
```

<a id="08-troubleshooting"></a>

## 🧭 Troubleshooting

### "Cannot find configuration for task X:target"

```bash
# Check what targets exist on the project
nx show project X --json | jq '.targets | keys'

# Check if any projects have that target
nx show projects --withTarget target
```

### "The workspace is out of sync"

```bash
nx sync
nx reset  # if sync doesn't fix stale cache
```


---

<a id="xac-nhan-quy-tac-2026-10-07-codex"></a>

## 🧭 Xác nhận quy tắc — 2026-10-07 — Codex

- **Đại diện ký**: Codex (Main Agent) — sgod-sam-v2 coordinator.
- **Thời điểm**: 2026-10-07T15:52:38+07:00.
- **Authorization**: Yêu cầu trực tiếp của Human ngày 2026-10-07: đọc, phổ biến và ký từng file/thư mục quy tắc; multitask cho phần đọc, ghi tuần tự.
- **Nguồn được ký nhận**: [.gemini/skills/nx-workspace/skill.md](skill.md); SHA-256 trước ký: `7023b26c33bb88b64189a111587dbda3c0a3a7a39a5fb640ff83db092122b861`.
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
