You are working inside the root of the `skillhost` Git repository.

Create a complete static marketing website under:

web/frontend/

The website is for a developer tool called Skillhost.

Domain:
skillhost.dev

Product:
Skillhost is a small Python CLI that installs Agent Skills from Git repositories into local agent skill directories using symlinks.

Core product philosophy:
- Git is the distribution system.
- Symlinks are the install system.
- No registry.
- No server.
- No account.
- No package resolution.
- No semver complexity.
- No code execution from skill repos.
- Safe unlink/remove through manifest tracking.

Audience:
- AI coding tool users
- Platform engineers
- Developer tooling teams
- Engineering teams using Codex, Claude Code, and OpenCode
- Companies that want to share internal agent skills through Git

Tone:
Professional, concise, technical, confident.
Avoid hype.
Avoid generic SaaS marketing language.
Use clear developer-tool copy similar in feel to Vercel, Linear, Astral, and modern open-source infrastructure tools.

Technology:
- React
- TypeScript
- Vite
- Tailwind CSS
- No backend
- No shadcn for now
- No external UI component library
- Optional: use lucide-react icons if you want, but keep dependencies minimal.
- The site must be static and deployable to Vercel, Netlify, Cloudflare Pages, or any static host.

Create these files:

web/frontend/
  package.json
  index.html
  vite.config.ts
  tsconfig.json
  tsconfig.node.json
  postcss.config.js
  tailwind.config.ts
  src/
    main.tsx
    App.tsx
    styles.css
    components/
      Header.tsx
      Hero.tsx
      CodeBlock.tsx
      FeatureGrid.tsx
      Workflow.tsx
      AgentSupport.tsx
      SecuritySection.tsx
      InstallSection.tsx
      Footer.tsx

Use a dark-first, premium developer-tool visual design:
- Background: near-black with subtle radial gradients.
- Typography: clean, modern, high contrast.
- Layout: centered max-width container.
- Hero: centered composition.
- Visual: terminal/code card showing realistic Skillhost commands.
- Use subtle borders, glassy panels, soft shadows, gradients, and precise spacing.
- No cartoon illustrations.
- No stock images.
- No fake screenshots.
- No heavy animation.
- Use lightweight hover transitions only.
- Fully responsive for mobile and desktop.
- Accessible semantic HTML.
- Good keyboard focus states.
- Use `prefers-reduced-motion` if adding any animation.

Brand:
Product name: Skillhost
Tagline options:
"Agent skills, distributed with Git."
"Install Agent Skills from Git repos into Codex, Claude Code, and OpenCode."
Use the strongest one in the hero.

Core headline:
"Agent skills, distributed with Git."

Hero subheadline:
"Skillhost links skills from Git repositories into Codex, Claude Code, and OpenCode. No registry, no server, no account — just Git, symlinks, and safe manifests."

Primary CTA:
"Install Skillhost"

Secondary CTA:
"View on GitHub"

Links:
Use constants in App.tsx or a small object:
- GITHUB_URL = "https://github.com/skillhost-dev/skillhost"
- PYPI_URL = "https://pypi.org/project/skillhost/"
- DOCS_URL = "https://github.com/skillhost-dev/skillhost#readme"

If the repo URL is unknown, still use these placeholders consistently and make them easy to change.

Install commands to display:

uv tool install skillhost

pipx install skillhost

pip install skillhost

uv and pipx are important because Skillhost is a Python CLI. The website should present `uv tool install skillhost` as the recommended path, and `pipx install skillhost` as the classic isolated Python CLI install path.

Main command examples:

User-level skills:

skillhost user add git@github.com:your-org/company-skills.git
skillhost user update
skillhost user link

Project-level skills:

cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link

Unlink/remove examples:

skillhost user unlink
skillhost user remove company-skills

skillhost project unlink
skillhost project remove project-skills --project my-project

Explain target directories:

User-level targets:
- Codex: ~/.agents/skills
- Claude Code: ~/.claude/skills
- OpenCode: ~/.config/opencode/skills

Project-level targets:
- Codex: .agents/skills
- Claude Code: .claude/skills
- OpenCode: .opencode/skills

Sections to build:

1. Header
- Left: Skillhost wordmark
- Right nav:
  - Install
  - Workflow
  - Agents
  - Security
  - GitHub
- Sticky or simple fixed top is fine.
- Keep it minimal.

2. Hero
Content:
- Small pill: "Open-source Python CLI"
- H1: "Agent skills, distributed with Git."
- Paragraph: "Skillhost links skills from Git repositories into Codex, Claude Code, and OpenCode. No registry, no server, no account — just Git, symlinks, and safe manifests."
- Primary button: "Install Skillhost" linking to #install
- Secondary button: "View on GitHub" linking to GITHUB_URL
- Terminal-style card showing:

$ skillhost user add git@github.com:acme/acme-skills.git
$ skillhost user link

linked codex   ~/.agents/skills/acme-git
linked claude  ~/.claude/skills/acme-git
linked opencode ~/.config/opencode/skills/acme-git

3. Trust / positioning strip
Short statements:
- "No hosted registry"
- "No agent lock-in"
- "No skill execution"
- "Manifest-safe unlink"

4. FeatureGrid
Use 6 features:
- Git-native distribution
  "Use the Git repositories your team already trusts. Clone, pull, review, and roll back with normal developer workflows."
- Symlink-based install
  "Skillhost links discovered skills into each agent’s native skill directory instead of copying or repackaging them."
- User and project scopes
  "Install shared personal skills globally, or link project-specific skills into the current repository."
- Multi-agent support
  "Codex, Claude Code, and OpenCode get their own native targets. No cross-agent hacks."
- Safe conflict policy
  "Existing user-owned skills are never overwritten. Duplicate skill names are reported instead of silently resolved."
- Manifest-tracked cleanup
  "Unlink and remove only touch symlinks created by Skillhost."

5. Workflow section
Show a 3-step flow:
Step 1: Add
"Register a Git repository containing one skill or a collection of skills."
Step 2: Update
"Pull the latest changes with fast-forward-only Git updates."
Step 3: Link
"Create symlinks into user-level or project-level agent directories."

Include command snippets for each step.

6. AgentSupport section
Show three cards:
- Codex
  User: ~/.agents/skills
  Project: .agents/skills
- Claude Code
  User: ~/.claude/skills
  Project: .claude/skills
- OpenCode
  User: ~/.config/opencode/skills
  Project: .opencode/skills

7. Repo layout section
Show supported layouts:

Single skill repo:
my-skill/
  SKILL.md

Collection repo:
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

Text:
"Skillhost discovers skills by looking for SKILL.md. A repository can be a single skill or a collection of skills."

8. SecuritySection
Content:
"Skillhost never executes code from skill repositories."
"Skillhost only clones, updates, discovers SKILL.md files, and creates or removes symlinks."
"Unlink and remove are manifest-driven, so user-owned directories are left alone."

Use a serious security-focused design. Avoid fear-based language.

9. InstallSection
ID: install

Show install tabs or stacked blocks:
Recommended:
uv tool install skillhost

Alternative:
pipx install skillhost

Fallback:
pip install skillhost

Buttons:
- PyPI
- GitHub
- README

Use placeholder links from constants.

10. Footer
- Product name
- One-line summary
- Links: GitHub, PyPI, Docs
- Copyright current year
- Text: "Git is the distribution system. Symlinks are the install system."

Implementation requirements:

Tailwind:
- Configure Tailwind content paths correctly.
- Use a custom theme if helpful:
  - colors for background, panel, border, muted text
  - font family: use system fonts, not external Google Fonts
- Do not fetch external fonts.

CSS:
- styles.css should include Tailwind directives.
- Add global body background and text color.
- Add smooth scrolling.
- Respect reduced motion.

React:
- Keep components simple and readable.
- Use typed props where appropriate.
- Avoid over-abstracting.
- All copy should be in English.
- No lorem ipsum.
- No fake customer logos.
- No fabricated star counts.
- No fabricated metrics.
- No claims like "trusted by thousands" unless there is real data.
- Use realistic placeholder links only where necessary.

CodeBlock component:
- Reusable component for terminal/code snippets.
- Support optional title.
- Use monospace.
- Preserve whitespace.
- Nice dark terminal style.
- Optional copy button if easy, but not required. If implemented, make it accessible.

Design details:
- Use a dark background: #05060A or similar.
- Use subtle gradients with blue/violet/cyan accents.
- Use thin borders: white/10.
- Use cards with bg-white/[0.03] or similar.
- Use rounded-2xl or rounded-3xl.
- Use max-w-7xl container.
- Use generous vertical spacing.
- Make the hero feel premium and technical.

Package scripts:
package.json should include:
- dev
- build
- preview
- lint if ESLint is configured; otherwise omit lint.
- typecheck

Prefer not to add ESLint unless you configure it fully.

Expected output:
Generate all files under web/frontend.
The app must run with:
cd web/frontend
npm install
npm run dev
npm run build

Do not modify the Python CLI package files outside web/frontend.

Keep the implementation elegant and complete, but do not add routing, backend calls, authentication, analytics, CMS, database, or documentation generation. This is a static landing page only.