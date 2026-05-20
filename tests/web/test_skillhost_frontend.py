import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "web" / "frontend"


def read(path: str) -> str:
    return (FRONTEND / path).read_text(encoding="utf-8")


def app_sources() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*.tsx"))


class SkillhostFrontendV6AcceptanceTests(unittest.TestCase):
    def test_required_files_exist_and_removed_old_sections(self):
        required = [
            "package.json",
            "index.html",
            "tsconfig.json",
            "vite.config.ts",
            "tailwind.config.ts",
            "postcss.config.js",
            "src/App.tsx",
            "src/main.tsx",
            "src/styles.css",
            "src/vite-env.d.ts",
            "src/components/Header.tsx",
            "src/components/CodeBlock.tsx",
            "src/components/ScenarioCard.tsx",
            "src/components/ThemeToggle.tsx",
        ]
        missing = [path for path in required if not (FRONTEND / path).is_file()]
        self.assertEqual(missing, [])

        removed = [
            "src/components/FeatureGrid.tsx",
            "src/components/SecuritySection.tsx",
            "src/components/AgentSupport.tsx",
            "src/components/Workflow.tsx",
            "src/components/Hero.tsx",
            "src/components/Footer.tsx",
            "src/components/InstallSection.tsx",
        ]
        still_present = [path for path in removed if (FRONTEND / path).exists()]
        self.assertEqual(still_present, [])

    def test_add_update_only_recommended_commands(self):
        combined = app_sources()
        expected = [
            "skillhost add git@github.com:my-org/company-skills.git",
            "skillhost add git@github.com:my-org/team-skills.git",
            "skillhost update",
            "skillhost project register my-project --git git@github.com:my-org/my-project.git",
            "skillhost project add git@github.com:my-org/my-project-skills.git --project my-project",
            "skillhost update --project my-project",
            "skillhost add <git-repo>",
            "skillhost update --project <project>",
        ]
        for text in expected:
            self.assertIn(text, combined)

        forbidden = [
            "skillhost " + suffix
            for suffix in [
                "link",
                "project link",
                "unlink",
                "project unlink",
                "remove",
                "project remove",
                "list",
                "project list",
                "doctor",
                "project doctor",
                "user " + "add",
                "user " + "update",
                "user " + "link",
            ]
        ]
        for text in forbidden:
            self.assertNotIn(text, combined)

    def test_v6_exact_structure_and_copy(self):
        app = read("src/App.tsx")
        combined = app_sources()
        expected = [
            "Agent Skills should not be copied and updated manually.",
            "SkillHost installs skills from Git repositories into Codex, Claude Code, and other AI agents.",
            "Add once, update with Git, and keep user-level and project-level skills cleanly separated.",
            "Scenario 1 — Make one skill repo available to every local agent.",
            "Scenario 2 — Share team skills without copy-paste drift.",
            "Scenario 3 — Keep project-only skills inside one repo.",
            "Quick docs",
            "Project skills stay scoped to the current Git repository root. SkillHost does not scan your disk.",
        ]
        for text in expected:
            self.assertIn(text, combined)

        self.assertNotIn("FeatureGrid", app)
        self.assertNotIn("SecuritySection", app)
        self.assertNotIn("RepoLayoutSection", app)
        self.assertNotIn("PositioningStrip", app)

    def test_links_theme_toggle_copy_docs_and_dark_topbar(self):
        combined = app_sources()
        index = read("index.html")
        tailwind = read("tailwind.config.ts")
        expected = [
            "https://github.com/wang-chonghuan/skillhost",
            "https://pypi.org/project/skillhost/",
            "DOCS_TEXT",
            "navigator.clipboard.writeText(text)",
            "Copy docs",
            "InstallCommandsPanel",
            "Install SkillHost commands",
            "Copy ${option.label} install command",
            "copiedInstallCommand === option.command ? 'Copied' : 'Copy'",
            "Copied",
            "Copy unavailable",
            "localStorage.setItem('theme', theme)",
            "localStorage.getItem('theme') === 'light' ? 'light' : 'dark'",
            "ThemeToggle",
            "darkMode: 'class'",
            "dark:bg-black/80",
            "dark:bg-slate-950/80",
            "dark:border-cyan-300/10",
            "SkillhostDiagram",
            "SkillHost directory diagram",
            "~/.skillhost",
                                    "break-words",
            "flex items-center justify-between gap-3 rounded-2xl",
                                                            "SkillHost basic mapping diagram",
            "skill git repos",
            "third-party/personal repos",
            "symlinks",
            "M710 240 H450",
            "M450 120 V340",
            "M190 220 H450",
            'stroke="#f8fafc"',
            'fill="url(#diagram-bg)"',
            "SkillHost basic mapping diagram",
            "diagram-bg",
            "#67e8f9",
            "#a78bfa",
        ]
        for text in expected:
            self.assertIn(text, combined + tailwind)
        self.assertIn('class="dark"', index)

    def test_quick_docs_targets_formats_and_safety_notes(self):
        combined = app_sources()
        expected = [
            "uv tool install skillhost",
            "pipx install skillhost",
            "pip install skillhost",
            "uv tool install git+https://github.com/wang-chonghuan/skillhost.git",
            "~/.agents/skills",
            "~/.claude/skills",
            "~/.config/opencode/skills",
            ".agents/skills",
            ".claude/skills",
            ".opencode/skills",
            "Single skill:",
            "Collection:",
            "Flat collection:",
            "SkillHost never executes code from skill repositories.",
            "Existing user-owned skills are not overwritten.",
            "SkillHost tracks created symlinks in manifests for safe cleanup.",
            "Duplicate skill names are reported instead of silently resolved.",
            "sm:grid-cols-2",
        ]
        for text in expected:
            self.assertIn(text, combined)

    def test_package_scripts_and_static_stack(self):
        package_json = read("package.json")
        self.assertIn('"dev": "vite"', package_json)
        self.assertIn('"build": "tsc --noEmit && vite build"', package_json)
        self.assertIn('"preview": "vite preview"', package_json)
        self.assertIn('"typecheck": "tsc --noEmit"', package_json)
        self.assertIn('"react"', package_json)
        self.assertIn('"typescript"', package_json)
        self.assertIn('"tailwindcss"', package_json)
        self.assertNotIn('"shadcn', package_json.lower())

    def test_css_accessibility_and_no_external_fonts(self):
        styles = read("src/styles.css")
        combined = app_sources()
        self.assertIn("@tailwind base;", styles)
        self.assertIn("@tailwind components;", styles)
        self.assertIn("@tailwind utilities;", styles)
        self.assertIn("prefers-reduced-motion", styles)
        self.assertIn("scroll-behavior: smooth", styles)
        self.assertIn("font-family: ui-sans-serif", styles)
        self.assertNotIn("Google Fonts", combined + styles)
        self.assertIn("aria-label", combined)
        self.assertIn("aria-labelledby", combined)


if __name__ == "__main__":
    unittest.main()
