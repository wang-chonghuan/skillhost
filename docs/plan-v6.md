You are working in the `skillhost` repository.

Task:
Completely redesign the static website under `web/frontend`.

Use:
- React
- TypeScript
- Vite
- Tailwind CSS
- Static site only
- No backend
- No routing
- No shadcn
- Minimal dependencies
- English copy only

Product brand:
SkillHost

Package / CLI name:
skillhost

Domain:
skillhost.dev

Goal:
Create a clean, technical, premium landing page for SkillHost. The page must explain the product through exactly the structure below and remove all other sections/content.

Important:
Do not keep the old landing page structure.
Do not include feature grids, trust strips, security sections, repo layout sections, long marketing sections, fake metrics, testimonials, logos, or extra CTA blocks.
Only keep this structure:

1. Fixed top bar
2. Main hero/message section
3. Scenario 1
4. Scenario 2
5. Scenario 3
6. Quick docs section

Visual design:
- Tech industry feel.
- Premium developer-tool design.
- Default dark mode.
- Support light mode and dark mode.
- Add a theme toggle.
- Store selected theme in localStorage.
- If no stored preference exists, default to dark mode.
- Use system font stack.
- No external fonts.
- No stock images.
- No fake screenshots.
- Use cards, subtle borders, code blocks, and clean spacing.
- Must be responsive.
- Top bar must remain fixed.

Top bar requirements:
- Fixed at top.
- Left side: SkillHost logo / wordmark.
- Right side:
  1. Copy docs button
  2. GitHub icon link
  3. PyPI icon/link
  4. Theme toggle

Links:
Use constants so they are easy to change:
- GITHUB_URL = "https://github.com/skillhost-dev/skillhost"
- PYPI_URL = "https://pypi.org/project/skillhost/"
- DOCS_TEXT should contain a compact quick-start document that can be copied.
- The Copy docs button copies DOCS_TEXT to clipboard and shows a short copied state.

Icon requirements:
- You may use inline SVG icons for GitHub, PyPI/package, copy, moon/sun.
- Avoid adding icon libraries unless already installed.
- If lucide-react is already installed, using it is acceptable; otherwise use inline SVG.

Main content layout:
- Vertical single-column layout.
- Max width around 900-1040px.
- Top padding must account for fixed header.
- Use section cards or bordered panels.
- Each scenario must include concise explanation plus commands.
- Commands must be in readable terminal-style code blocks.
- Keep all copy tight and practical.

Hero / theme copy:
Title:
Shared skills for every AI agent.

Subtitle:
You need the same skills across Codex, Claude Code, OpenCode, and future agents.
Manual copying creates drift. Project-specific skills should not leak into every workspace.

Skillhost keeps skills in Git and links them into each agent’s native skill directory, either globally for the user or locally for a project.

install command block:
uv tool install skillhost
pipx install skillhost
pip install skillhost

Scenario 1:
Title:
Scenario 1 — You installed many skills. How do every agent see them, and how do you update them?

Explain:
Use user-level repositories when the skills should be available across your machine. SkillHost clones the repo once, then links discovered skills into each agent’s native user-level skill directory.

Commands:
skillhost add git@github.com:your-org/company-skills.git
skillhost link

Then update later:
skillhost update
skillhost link

Brief target explanation:
Codex: ~/.agents/skills
Claude Code: ~/.claude/skills
OpenCode: ~/.config/opencode/skills

Scenario 2:
Title:
Scenario 2 — Your team built shared skills. How does everyone install and keep them updated?

Explain:
Put the team skills in a normal Git repository. Every developer adds the same repo, links it once, then pulls future updates with one command.

Commands:
skillhost add git@github.com:your-org/team-skills.git
skillhost link

When the team updates skills:
skillhost update
skillhost link

Explain:
Git remains the source of truth. Reviews, branches, history, and rollback stay in the workflow your team already uses.

Scenario 3:
Title:
Scenario 3 — Some skills belong to one project, not the whole machine. How do you expose them only inside that repo?

Explain:
Use project-level repositories for skills that should only be visible inside a specific project checkout. SkillHost matches the current Git repository, then links project skills into local project-level agent directories.

Commands:
cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link

Update project skills:
skillhost project update my-project
skillhost project link

Brief target explanation:
Codex: .agents/skills
Claude Code: .claude/skills
OpenCode: .opencode/skills

Important project behavior copy:
Project linking only operates on the current Git repository root. SkillHost does not scan your disk.

Quick docs section:
Title:
Quick docs

Include compact documentation blocks for:

Install:
uv tool install skillhost
pipx install skillhost

User commands:
skillhost add <git-repo>
skillhost update
skillhost link
skillhost unlink
skillhost remove <name>
skillhost list
skillhost doctor

Project commands:
skillhost project register <project> --git <project-git-url>
skillhost project add <skill-git-repo> --project <project>
skillhost project update [project]
skillhost project link
skillhost project unlink
skillhost project remove <name> --project <project>
skillhost project list
skillhost project doctor

Skill repo formats:
Single skill:
my-skill/
  SKILL.md

Collection:
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md

Flat collection:
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md

Safety notes:
- SkillHost never executes code from skill repositories.
- Existing user-owned skills are not overwritten.
- Unlink only removes symlinks tracked by SkillHost manifests.
- Duplicate skill names are reported instead of silently resolved.

Copy docs behavior:
The top-bar "Copy docs" button should copy a compact markdown/plaintext version of the quick docs and scenario commands.
Implement this in React using navigator.clipboard.writeText.
If clipboard API is unavailable, fail gracefully and show a small message.

Implementation details:
- Keep components simple.
- Suggested files:
  web/frontend/src/App.tsx
  web/frontend/src/main.tsx
  web/frontend/src/styles.css
  web/frontend/src/components/Header.tsx
  web/frontend/src/components/CodeBlock.tsx
  web/frontend/src/components/ScenarioCard.tsx
  web/frontend/src/components/ThemeToggle.tsx
- You may adjust the component breakdown if simpler.
- Ensure `npm run build` passes.
- Ensure TypeScript passes.
- Do not modify Python package code.
- Do not add backend files.
- Do not add analytics.
- Do not add routing.
- Do not add extra sections beyond the required structure.

After implementation:
Run:
cd web/frontend
npm install
npm run build

Fix any TypeScript, Vite, or Tailwind errors.