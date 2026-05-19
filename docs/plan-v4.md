# plan-v4：SkillHost Web 日间模式新版设计方案

日期：2026-05-19
状态：设计方案，暂不实现
范围：`web/frontend` 站点视觉、文案、组件结构、测试与验收标准

## 1. 背景与目标

当前 `web/frontend` 是以纯黑 / 深色为主的开发者工具落地页。整体气质偏早期 CLI 项目展示，问题是：

- 背景过黑，视觉压迫感强，不够现代。
- 深色玻璃卡片、低对比边框、青色光晕的组合已经常见且显旧。
- 首屏文案没有清晰分段表达“为什么需要 SkillHost”。
- 缺少能解释产品机制的主视觉图片 / 图解。

新版目标：

1. **只做日间模式**，不加入暗色主题切换。
2. 采用 2025/2026 AI 工具、SaaS、开发者工具官网常见的轻量、明亮、可信赖风格。
3. 首屏必须使用用户提供的宣传语，并注意分段和强调。
4. 引入合适的产品图解，而不是随机插画或图库照片。
5. 品牌名称统一写作 **SkillHost**；只有 CLI 命令、PyPI 包名、仓库名等技术标识继续使用小写 `skillhost`。
6. 保持 SkillHost 的定位清晰：Git 保存 skills，按 user / project 级别链接到各 AI coding agent 的原生 skill 目录。
7. 更强地击中用户痛点：解决 skills 在多个 AI coding agents、多台机器、多个团队仓库之间的**分发、管理、同步、更新、回滚和清理**问题。
8. 保持命令体系正确：用户级命令是 `skillhost add`、`skillhost link`，不再出现 `skillhost user ...`；项目级命令仍使用 `skillhost project ...`。

## 2. 线上调研摘要

调研对象包括 2025/2026 Web/UI trend 文章、SaaS landing page 案例集合、AI / developer-tool 站点常见模式。重点结论如下：

### 2.1 当前趋势

- **浅色画布 + 柔和渐变**：纯白或 near-white 背景上加入浅蓝、浅紫、浅青的 radial gradient，既有 AI 感，又保持清爽。
- **Bento grid / modular cards**：用不对称卡片组织密集信息，适合展示功能点、工作流、安全策略和 agent 兼容性。
- **产品机制图替代抽象装饰图**：开发者工具落地页越来越强调“它到底怎么工作”，首屏右侧常用架构图、流程图、terminal card、repo tree mockup。
- **大字号、短句、强层级标题**：首屏主张要一句话打透，副文案拆成短行，降低阅读负担。
- **代码 / 终端卡片仍可用深色**：页面整体为 light mode，但局部 terminal/code block 使用深 navy 是开发者工具的常见做法，用于突出命令和输出。
- **微交互克制**：150–300ms hover、轻微浮动、滚动渐显即可；避免大面积 3D/WebGL 导致性能和维护成本升高。
- **可访问性成为基础要求**：足够颜色对比、清晰 focus ring、移动端布局、`prefers-reduced-motion`。

### 2.2 调研参考

- Figma Resource Library: Web Design Trends 2026
  - 重点：沉浸感、鲜明色彩、现代交互，但需要服务于可用性。
  - https://www.figma.com/resource-library/web-design-trends/
- Midrocket: UI Design Trends 2026
  - 重点：bento grids、modular layouts、glassmorphism、variable fonts、spatial design。
  - https://midrocket.com/en/guides/ui-design-trends-2026/
- Landdding: UI Design Trends 2026
  - 重点：现代网站的模式化趋势，包括 bento、AI interface、motion、layered depth。
  - https://landdding.com/blog/ui-design-trends-2026
- Leadpages: Landing Page Trends 2025
  - 重点：landing page 需要快速传达价值、减少摩擦、引导转化。
  - https://leadpages.com/blog/landing-page-trends-2025
- SaaSpo Bento SaaS Landing Pages
  - 重点：SaaS 常用 bento 卡片组织功能、对比和集成信息。
  - https://saaspo.com/style/bento

### 2.3 对 SkillHost 的设计启发

SkillHost 不应该做成“黑客工具”风格，而应做成“面向团队的 AI coding infrastructure 小工具”：

- 用浅色、干净、偏云和代码基础设施的配色建立信任。
- 用图解说明 Git repository、SkillHost manifest、symlink、Codex / Claude / OpenCode 目录之间的关系。
- 用短句解释 user scope 与 project scope 的差异。
- 把命令示例做成清晰的 install / add / link 流程，让新用户 30 秒内知道怎么安装。

### 2.4 核心用户痛点与产品价值

新版网站不应只说 “links skills from Git”，而要更直接地说清楚 SkillHost 解决的真实问题。

目标用户的痛点：

- **分发难**：团队写好的 skills 分散在不同仓库、文档、聊天记录或本地目录里，新成员不知道去哪里拿。
- **复制会漂移**：手动复制到 Codex、Claude Code、OpenCode 后，多个 agent、多个机器之间很快版本不一致。
- **更新不可控**：skill 改进后，很难确认谁已经更新、谁还在用旧版本。
- **项目边界混乱**：有些 skills 应该全局可用，有些只应该跟随特定 repository，手动管理容易污染全局环境。
- **清理和回滚麻烦**：不知道哪些文件是工具创建的，删除时容易误删用户自己的 skill。
- **团队协作缺少审计**：如果 skills 不在 Git 里，就缺少 review、history、branch、rollback 这些成熟工程流程。

SkillHost 的优越性：

- **Git-native distribution**：skills 像代码一样分发、review、版本化和回滚。
- **One command to install, one command to link**：安装后用 `skillhost add` + `skillhost link` 就能把 skills 放到支持的 agent 原生目录。
- **User and project scopes**：常用 skills 全局可用，项目 skills 只进入对应 repo。
- **Native directories, no lock-in**：不发明新运行时，不要求托管服务，直接链接到各 agent 自己识别的 skill 目录。
- **Update-friendly workflow**：Git pull / repo update 后重新 link，即可让本地 agent 目录跟随最新 skill 内容。
- **Manifest-safe cleanup**：记录自己链接过的内容，unlink 时只清理受管对象，降低误删风险。

## 3. 总体视觉方向

### 3.1 设计关键词

- Bright developer infrastructure
- Git-native skill distribution
- Skills distribution, management, and updates
- Calm AI tooling
- Team-ready, not toy-like
- Light, layered, trustworthy
- Fast to adopt, easy to leave, safe to clean up

### 3.2 页面气质

新版应避免：

- 大面积 `#000` 或接近纯黑的背景。
- 全站暗色玻璃拟态。
- 炫技式 3D、过度动效、随机 AI 插画。
- 只给口号、不解释机制。

新版应采用：

- 淡蓝灰页面底色。
- 白色 / 半透明白色卡片。
- 柔和蓝色主色，少量橙色 CTA。
- 细边框、柔和阴影、圆角卡片。
- 首屏产品图解 + terminal mock。
- Bento 信息区块。

## 4. 设计系统

### 4.1 色彩

建议在 `tailwind.config.ts` 扩展如下 token，或者直接替换现有暗色 token：

| 用途 | Token | Hex | 说明 |
| --- | --- | --- | --- |
| 页面背景 | `canvas` | `#F8FAFC` | 主背景，接近 slate-50 |
| 蓝色浅背景 | `skywash` | `#F0F9FF` | hero / section 渐变背景 |
| 卡片背景 | `surface` | `#FFFFFF` | 主卡片 |
| 次级卡片 | `surface-soft` | `#F8FBFF` | bento 内部浅底 |
| 主文本 | `ink` | `#0F172A` | slate-900 |
| 次级文本 | `muted` | `#475569` | slate-600 |
| 弱文本 | `subtle` | `#64748B` | slate-500 |
| 边框 | `line` | `#DCEBFA` | 蓝灰边框 |
| 主色 | `primary` | `#0EA5E9` | sky-500 |
| 主色深 | `primary-strong` | `#0369A1` | sky-700，用于文字 / hover |
| 辅助蓝 | `blue` | `#2563EB` | link / diagram 节点 |
| 强 CTA | `accent` | `#F97316` | install CTA，少量使用 |
| 成功色 | `success` | `#10B981` | linked / safe 状态 |
| code 背景 | `code` | `#0F172A` | 仅 terminal/code card 内使用 |

页面整体背景示例：

```css
background:
  radial-gradient(circle at 20% 10%, rgba(14, 165, 233, 0.18), transparent 32rem),
  radial-gradient(circle at 82% 18%, rgba(37, 99, 235, 0.12), transparent 30rem),
  linear-gradient(180deg, #F0F9FF 0%, #F8FAFC 46%, #FFFFFF 100%);
```

注意：允许 terminal/code block 使用深 navy，但它只能是局部内容卡片，不能成为页面主背景。

### 4.2 字体

建议：

- Heading：`Space Grotesk`
- Body：`DM Sans`
- Mono：保持系统 mono stack

如果不想引入外部字体，也可继续使用现有系统字体，但需要通过更大的字号、字重和间距改进层级。

CSS 建议：

```css
:root {
  font-family: 'DM Sans', Inter, ui-sans-serif, system-ui, sans-serif;
}

h1, h2, h3, .font-display {
  font-family: 'Space Grotesk', Inter, ui-sans-serif, system-ui, sans-serif;
}
```

### 4.3 圆角、阴影、边框

- 页面容器：`max-w-7xl`。
- 大卡片圆角：`rounded-[2rem]` 或 `rounded-3xl`。
- 小卡片圆角：`rounded-2xl`。
- 边框：`border border-sky-100` / `border-slate-200`。
- 阴影：柔和、低透明度，不要黑色重阴影。

建议 shadow token：

```ts
boxShadow: {
  soft: '0 24px 70px rgba(15, 23, 42, 0.08)',
  card: '0 16px 40px rgba(2, 132, 199, 0.10)',
  glow: '0 20px 60px rgba(14, 165, 233, 0.18)',
}
```

### 4.4 动效

- hover：150–250ms，`translate-y-[-2px]` + shadow 增强。
- section reveal：可以保留静态，也可后续加 CSS-only subtle reveal；第一版不必引入动画库。
- 必须保留 / 更新 `prefers-reduced-motion`。
- 不使用 heavy 3D / WebGL。

## 5. 首屏文案方案

首屏开头必须使用以下文案，并按语义分段展示：

```md
**Developers and teams need shared skills across multiple AI coding agents.**

Manual copying creates drift.
Global skills should be available everywhere.
Project skills should stay scoped to the repositories that need them.

**SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.**
```

### 5.1 推荐视觉分段

在 `Hero.tsx` 中建议拆成：

1. 顶部 pill：`Git-native skill distribution for AI coding agents`
2. 主标题 H1：
   - `Developers and teams need shared skills across multiple AI coding agents.`
3. 三条问题陈述：放在一个浅色 problem stack 中，每条一行：
   - `Manual copying creates drift.`
   - `Global skills should be available everywhere.`
   - `Project skills should stay scoped to the repositories that need them.`
4. 解决方案强调段：
   - `SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.`
5. 补充价值句：
   - `Distribute, update, and clean up shared skills without copying folders by hand.`
6. CTA：
   - Primary：`Install SkillHost`
   - Secondary：`View on GitHub`
7. 迷你信任行：
   - `Git-backed updates · User and project scopes · Native agent directories · Manifest-safe cleanup`

### 5.2 文案注意事项

- 不要把用户提供的三段文案压成一个长 paragraph。
- 不要把 “user or project level” 改成模糊说法。
- 页面所有命令示例必须使用：
  - `skillhost add ...`
  - `skillhost link`
  - `skillhost project ...`
- 禁止出现：
  - `skillhost user add`
  - `skillhost user link`
  - `skillhost user ...`

## 6. 图片 / 主视觉策略

用户希望“最好引入合适的图片”。推荐使用**产品机制图**，不推荐真人照片、抽象 stock photo 或不相关 AI 机器人图。

### 6.1 首选：自绘 SVG / React 图解组件

新增组件：

```text
web/frontend/src/components/SkillFlowIllustration.tsx
```

图解内容：

```text
Git repositories
  ├─ team-skills.git
  └─ project-skills.git
        ↓
SkillHost
  ├─ manifest
  ├─ discover SKILL.md
  └─ symlink
        ↓
Native agent skill directories
  ├─ Codex ~/.agents/skills + .agents/skills
  ├─ Claude ~/.claude/skills + .claude/skills
  └─ OpenCode ~/.config/opencode/skills + .opencode/skills
```

视觉表现：

- 背景：白色卡片 + 浅蓝渐变 blob。
- 节点：rounded rectangle。
- 连线：蓝色细线 / 虚线。
- 状态 chip：`linked`、`project scoped`、`manifest tracked`。
- 右下角叠加 terminal mini card：展示 `skillhost add` 和 `skillhost link` 输出。

优点：

- 和产品真实机制强相关。
- 不依赖外部图片版权。
- 可响应式缩放。
- 更符合开发者工具官网趋势。

### 6.2 备选：静态 SVG 文件

如果希望组件更轻，可以新增：

```text
web/frontend/src/assets/skill-flow.svg
```

并由 `Hero.tsx` 引用。但第一版建议用 React/Tailwind 直接写，便于维护和颜色统一。

### 6.3 不建议使用

- 随机 AI 头像 / 机器人。
- Unsplash 办公场景照片。
- 过重 3D 模型。
- 黑底 neon “cyber” 图。

## 7. 页面信息架构

新版建议保留现有页面的单页结构，但重新排序和视觉升级：

1. `Header`
   - 浅色 sticky header。
   - 左侧 logo / wordmark。
   - 右侧 anchors：`Workflow`、`Agents`、`Security`、`Install`、`GitHub`。
2. `Hero`
   - 用户提供宣传语。
   - CTA。
   - 产品机制图。
3. `PositioningStrip` / 可重命名为 `TrustStrip`
   - `Distribute from Git`
   - `Update without recopying`
   - `User and project scopes`
   - `Manifest-safe cleanup`
4. `ProblemSolutionBento`
   - Copy-paste distribution creates drift.
   - Git-backed skills stay reviewable and updateable.
   - Global skills are available everywhere.
   - Project skills stay scoped to the repositories that need them.
5. `FeatureGrid`
   - Git-native distribution。
   - Update-friendly management。
   - User and project scopes。
   - Native agent directories。
   - Conflict-aware linking。
   - Manifest-tracked cleanup。
6. `Workflow`
   - Step 1：Add Git repo。
   - Step 2：Discover `SKILL.md`。
   - Step 3：Link into native agent directories。
   - Step 4：Pull updates and relink。
   - Step 5：Unlink safely by manifest。
7. `AgentSupport`
   - Codex / Claude Code / OpenCode 目标目录。
   - user scope 与 project scope 清晰分列。
8. `RepoLayoutSection`
   - 支持 single skill、collection、flat collection。
   - 用浅色说明卡 + 深 navy code card。
9. `SecuritySection`
   - 不执行技能。
   - 不托管 registry。
   - 冲突策略。
   - manifest 清理。
10. `InstallSection`
    - `uv tool install skillhost`
    - `pipx install skillhost`
    - `pip install skillhost`
    - next steps：`skillhost add`、`skillhost link`。
11. `Footer`
    - GitHub / PyPI / Docs。

## 8. 组件级改造计划

### 8.1 `web/frontend/tailwind.config.ts`

改造点：

- 移除或弃用暗色命名如 `ink` 如果其含义是黑色背景；如果保留，则让 `ink` 表示主文本色。
- 增加 light design tokens。
- 增加 `fontFamily.display`。
- 增加 `boxShadow.soft/card/glow`。
- 保持 content 路径 `./src/**/*.{ts,tsx}`。

### 8.2 `web/frontend/src/styles.css`

改造点：

- `body` 背景改为浅色渐变。
- 默认文字色改为 `#0F172A`。
- 保留 `scroll-behavior: smooth`。
- 保留 `prefers-reduced-motion`。
- 增加可复用 utility：
  - `.text-balance`
  - `.surface-card`
  - `.gradient-border`（可选）
- 如果引入 Google Fonts，在 `index.html` 或 CSS 中处理；若避免外部网络依赖，则使用系统字体。

### 8.3 `web/frontend/src/App.tsx`

改造点：

- 根容器从 `bg-ink text-bright` 改为浅色：
  - `min-h-screen overflow-hidden bg-canvas text-ink`
- `PositioningStrip` 从暗色 strip 改为白底 / 浅蓝卡片。
- `RepoLayoutSection` 从深色文案改为 light section。
- 确认所有 section 背景和间距统一。

### 8.4 `Header.tsx`

改造点：

- 使用浅色 sticky header：
  - `bg-white/80 backdrop-blur-xl border-b border-sky-100`
- logo 可用浅蓝渐变 icon：
  - 方形 rounded mark，内部用简单 chain/link glyph 或 `S`。
- nav 文案：
  - `Workflow`
  - `Agents`
  - `Security`
  - `Install`
- GitHub button：白底边框或深蓝文字。
- focus state 明确：`focus-visible:ring-2 focus-visible:ring-sky-500`。

### 8.5 `Hero.tsx`

改造点：

- 替换现有 `Agent skills, distributed with Git.` 为用户提供的首屏文案。
- 左侧：pill、H1、problem stack、solution paragraph、CTA。
- 右侧：引入 `SkillFlowIllustration`。
- 命令示例：

```text
$ skillhost add git@github.com:acme/acme-skills.git
$ skillhost link

linked codex    ~/.agents/skills/acme-git
linked claude   ~/.claude/skills/acme-git
linked opencode ~/.config/opencode/skills/acme-git
```

- 背景：浅蓝 radial gradient + optional dotted grid。
- CTA：
  - Primary：橙色或蓝色实心按钮。
  - Secondary：白底边框按钮。

### 8.6 新增 `SkillFlowIllustration.tsx`

职责：

- 展示 SkillHost 的核心机制，而不是装饰。
- 使用 semantic HTML / SVG。
- 可以在卡片中用 div + CSS 连接线实现，不一定需要复杂 SVG。

建议结构：

```tsx
export function SkillFlowIllustration() {
  return (
    <div aria-label="SkillHost links Git-hosted skills into native agent directories">
      {/* Git repos */}
      {/* SkillHost hub */}
      {/* Agent directories */}
      {/* Mini terminal */}
    </div>
  );
}
```

可访问性：

- 如果纯装饰，使用 `aria-hidden="true"`，并在 hero 文案中解释。
- 如果传递信息，使用 `aria-label` 或隐藏文本说明。

### 8.7 `CodeBlock.tsx`

改造点：

- 可以保留深 navy terminal 风格。
- 增加 light 外壳：外部白底卡片，内部深色代码区。
- 代码文本使用浅色，边框用 `slate-800`。
- title bar 可以加入三个小圆点，但不要太拟物。

### 8.8 `FeatureGrid.tsx`

改造点：

- 从暗色卡片改为 bento card。
- 使用浅色 icon capsule。
- 每个 feature 的标题更短、更直接。
- 建议卡片文案：
  - `Distribute skills from Git`
  - `Update without recopying`
  - `Manage user-level skills`
  - `Keep project skills scoped`
  - `Link native agent directories`
  - `Clean up from the manifest`

### 8.9 `Workflow.tsx`

改造点：

- 做成横向 / 纵向 stepper。
- 每步一个编号圆点，蓝色连接线。
- 文案强调：
  1. Add a Git repository that contains one or many skills。
  2. Discover every `SKILL.md` automatically。
  3. Link skills into each agent’s native directory。
  4. Pull updates from Git and relink instead of copying folders again。
  5. Unlink safely from the manifest when skills are no longer needed。

### 8.10 `AgentSupport.tsx`

改造点：

- 使用三列卡片展示 Codex、Claude Code、OpenCode。
- 每个 agent 卡片分 user/project 两行：
  - Codex：`~/.agents/skills`、`.agents/skills`
  - Claude：`~/.claude/skills`、`.claude/skills`
  - OpenCode：`~/.config/opencode/skills`、`.opencode/skills`
- 可加入 small badge：`user`、`project`。

### 8.11 `SecuritySection.tsx`

改造点：

- 改为浅绿色 / 浅蓝色安全说明区。
- 文案强调 SkillHost 的边界：
  - It links files; it does not execute skills.
  - It records what it links.
  - It refuses unsafe conflicts.
  - It can unlink cleanly from the manifest.

### 8.12 `InstallSection.tsx`

改造点：

- 安装方式按推荐程度展示：
  1. `uv tool install skillhost`
  2. `pipx install skillhost`
  3. `pip install skillhost`
- 保留 PyPI / GitHub / Docs 链接。
- Next steps 示例必须是：

```text
skillhost add git@github.com:your-org/company-skills.git
skillhost link
skillhost project register my-project --git git@github.com:your-org/my-project.git
```

- 禁止出现 `skillhost user`。

### 8.13 `Footer.tsx`

改造点：

- 浅色 footer，顶部 border。
- 简短复述：`SkillHost distributes, updates, and manages AI coding skills from Git.`
- 链接：GitHub、PyPI、Docs。

## 9. 文案总表

### 9.1 Hero

```text
Git-native skill distribution for AI coding agents

Developers and teams need shared skills across multiple AI coding agents.

Manual copying creates drift.
Global skills should be available everywhere.
Project skills should stay scoped to the repositories that need them.

SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.

Distribute, update, and clean up shared skills without copying folders by hand.

Install SkillHost
View on GitHub
Git-backed updates · User and project scopes · Native agent directories · Manifest-safe cleanup
```

### 9.2 Problem / solution cards

```text
Copy-paste creates drift
Manually copied skills become stale across machines, agents, and repositories. Nobody knows which version is installed where.

Distribution should be boring
Put skills in Git, add the repository once, and let SkillHost link them into the agent directories that already exist.

Updates should not mean recopying
When a skill improves, pull from Git and relink. Teams keep review history, branches, rollback, and ownership.

Global where it belongs
User-level skills can be available across every supported agent on the machine.

Scoped when needed
Project-level skills stay attached to the repositories that need them, without polluting the user’s global skill set.

Cleanup should be safe
SkillHost tracks what it linked, so removal can be manifest-guided instead of guesswork.
```

### 9.3 Feature titles

```text
Distribute skills from Git
Update without recopying
Manage user-level skills
Keep project skills scoped
Link native agent directories
Clean up from the manifest
```

### 9.4 Workflow titles

```text
Add a Git repo
Discover SKILL.md files
Link native directories
Pull updates and relink
Unlink safely
```

### 9.5 Security titles

```text
No hosted registry
No skill execution
Conflict-aware by default
Git-backed updates
Clean manifest-based unlink
```

## 10. 测试更新计划

更新：

```text
tests/web/test_skillhost_frontend.py
```

### 10.1 需要新增 / 更新断言

- 品牌名规范：
  - UI 文案中的品牌名统一为 `SkillHost`。
  - CLI 命令、PyPI 包名、GitHub repo slug 等技术标识继续使用小写 `skillhost`。
- 首屏新文案存在：
  - `Developers and teams need shared skills across multiple AI coding agents.`
  - `Manual copying creates drift.`
  - `Global skills should be available everywhere.`
  - `Project skills should stay scoped to the repositories that need them.`
  - `SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.`
  - `Distribute, update, and clean up shared skills without copying folders by hand.`
- 痛点 / 价值文案存在：
  - `Copy-paste creates drift`
  - `Update without recopying`
  - `Distribute skills from Git`
  - `Clean up from the manifest`
- 新组件存在：
  - `src/components/SkillFlowIllustration.tsx`
- 日间模式 token 存在：
  - `bg-canvas`
  - `text-ink`
  - 或 `#F8FAFC` / `#0F172A`
- 旧纯黑主背景不应作为根容器：
  - 根容器不再使用 `bg-ink text-bright`。
- 命令规则：
  - 包含 `skillhost add`。
  - 包含 `skillhost link`。
  - 包含 `skillhost project register`。
  - 不包含 `skillhost user`。

### 10.2 保留断言

- 必需文件存在。
- Vite / React / TypeScript / Tailwind stack 存在。
- `aria-label` / `aria-labelledby` 存在。
- `prefers-reduced-motion` 存在。
- agent 目录存在。
- PyPI / GitHub / Docs links 存在。

## 11. 实施步骤

### Phase 1：设计 token 与全局样式

1. 更新 `tailwind.config.ts`。
2. 更新 `styles.css`。
3. 确保页面整体变为浅色背景。

### Phase 2：首屏重构

1. 新增 `SkillFlowIllustration.tsx`。
2. 重写 `Hero.tsx`。
3. 保证用户提供文案完整、分段清晰。
4. 确保 CTA 和命令示例正确。

### Phase 3：主体内容 light/bento 化

1. 改造 `PositioningStrip`，突出分发、更新、scope、清理四个信任点。
2. 新增或改造 `ProblemSolutionBento`，用痛点驱动用户理解为什么需要 SkillHost。
3. 改造 `FeatureGrid`，从功能罗列改为“分发 / 管理 / 更新 / 清理”的价值表达。
4. 改造 `Workflow`，加入 pull updates and relink 步骤。
5. 改造 `AgentSupport`。
6. 改造 `RepoLayoutSection`。
7. 改造 `SecuritySection`。
8. 改造 `InstallSection`。
9. 改造 `Footer`。

### Phase 4：测试与验收

1. 更新 `tests/web/test_skillhost_frontend.py`。
2. 运行前端构建。
3. 运行 Python 测试。
4. 手动检查响应式布局。

## 12. 验收标准

### 12.1 视觉验收

- 页面主背景是日间浅色，不是纯黑或深色。
- 首屏有明确宣传语，并按用户要求分段。
- 首屏包含产品机制图或等价的产品图解。
- 页面风格符合现代 AI / SaaS / developer-tool 官网：浅色、卡片化、柔和渐变、清晰信息层级。
- 文案能在首屏和前两个内容区明确说明 SkillHost 解决 skills 分发、管理、更新和清理问题。
- 局部 terminal/code card 可以是深 navy，但页面整体不能回到 dark mode。

### 12.2 文案验收

- 品牌显示不出现 `Skillhost`，统一使用 `SkillHost`。
- 不出现 `skillhost user`。
- 用户级命令使用：
  - `skillhost add`
  - `skillhost link`
- 项目级命令使用：
  - `skillhost project register`
  - `skillhost project add` / `skillhost project remove` 如需展示。
- 保留安装方式：
  - `uv tool install skillhost`
  - `pipx install skillhost`
  - `pip install skillhost`

### 12.3 技术验收

运行：

```bash
cd web/frontend && npm run build
```

运行：

```bash
uv run --with pytest --with ruff pytest -q
```

如果只验证 web acceptance tests，可运行：

```bash
uv run --with pytest pytest tests/web/test_skillhost_frontend.py -q
```

### 12.4 响应式验收

手动检查宽度：

- 375px：移动端首屏文案不拥挤，CTA 垂直排列，图解可下移。
- 768px：卡片 2 列布局合理。
- 1024px：hero 左右布局成立。
- 1440px：max width 限制生效，不要过度拉伸。

### 12.5 可访问性验收

- 所有链接和按钮有 visible focus state。
- 正文颜色对比足够，浅灰文字不低于可读标准。
- 图解如果传达信息，应有 `aria-label` 或 sr-only 说明。
- 保留 `prefers-reduced-motion`。

## 13. 风险与规避

| 风险 | 影响 | 规避 |
| --- | --- | --- |
| 过度追逐趋势 | 页面变花，维护复杂 | 只采用浅色、bento、图解、微交互这些低风险趋势 |
| 图解过复杂 | 移动端难读 | 首屏图解做响应式，移动端简化层级 |
| CTA 颜色太跳 | 与开发者工具气质冲突 | 橙色只用于主 CTA，其他使用蓝色 / slate |
| 仍残留黑色全局样式 | 与“只要日间模式”冲突 | 测试检查根容器与全局背景 |
| 命令文案回退到 `skillhost user` | 与 CLI v2 方向冲突 | 测试全量搜索 `skillhost user` |

## 14. 最终完成清单

- [ ] `tailwind.config.ts` 已更新 light design tokens。
- [ ] `styles.css` 已更新浅色全局背景。
- [ ] UI 品牌名已统一为 `SkillHost`，技术命令仍使用小写 `skillhost`。
- [ ] `Hero.tsx` 已使用用户提供宣传语并正确分段。
- [ ] 网站文案已突出 skills 的分发、管理、更新、清理价值。
- [ ] `SkillFlowIllustration.tsx` 已新增并用于首屏。
- [ ] 所有主要 section 已从暗色改为浅色 / bento 风格。
- [ ] `CodeBlock.tsx` 只在局部使用深 navy。
- [ ] 所有 web 文案不包含 `skillhost user`。
- [ ] `tests/web/test_skillhost_frontend.py` 已更新。
- [ ] `npm run build` 通过。
- [ ] `pytest` 通过。
- [ ] 375 / 768 / 1024 / 1440 响应式检查通过。
