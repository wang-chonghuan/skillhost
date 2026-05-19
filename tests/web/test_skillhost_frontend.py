import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "web" / "frontend"


def read(path: str) -> str:
    return (FRONTEND / path).read_text(encoding="utf-8")


class SkillhostFrontendAcceptanceTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "package.json",
            "index.html",
            "vite.config.ts",
            "tsconfig.json",
            "tsconfig.node.json",
            "postcss.config.js",
            "tailwind.config.ts",
            "src/main.tsx",
            "src/App.tsx",
            "src/styles.css",
            "src/vite-env.d.ts",
            "src/components/Header.tsx",
            "src/components/Hero.tsx",
            "src/components/CodeBlock.tsx",
            "src/components/FeatureGrid.tsx",
            "src/components/Workflow.tsx",
            "src/components/AgentSupport.tsx",
            "src/components/SecuritySection.tsx",
            "src/components/InstallSection.tsx",
            "src/components/Footer.tsx",
        ]
        missing = [path for path in required if not (FRONTEND / path).is_file()]
        self.assertEqual(missing, [])

    def test_package_scripts_and_static_stack(self):
        package_json = read("package.json")
        self.assertIn('"dev": "vite"', package_json)
        self.assertIn('"build": "tsc --noEmit && vite build"', package_json)
        self.assertIn('"preview": "vite preview"', package_json)
        self.assertIn('"typecheck": "tsc --noEmit"', package_json)
        self.assertIn('"react"', package_json)
        self.assertIn('"typescript"', package_json)
        self.assertIn('"tailwindcss"', package_json)
        self.assertIn('"@vitejs/plugin-react"', package_json)
        self.assertNotIn('"shadcn', package_json.lower())

    def test_copy_links_and_commands_match_plan(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*.tsx"))
        expected = [
            "Agent skills, distributed with Git.",
            "Skillhost links skills from Git repositories into Codex, Claude Code, and OpenCode.",
            "No registry, no server, no account",
            "https://github.com/skillhost-dev/skillhost",
            "https://pypi.org/project/skillhost/",
            "https://github.com/skillhost-dev/skillhost#readme",
            "uv tool install skillhost",
            "pipx install skillhost",
            "pip install skillhost",
            "skillhost user add git@github.com:your-org/company-skills.git",
            "skillhost project register my-project --git git@github.com:your-org/my-project.git",
            "skillhost project remove project-skills --project my-project",
        ]
        for text in expected:
            self.assertIn(text, combined)

    def test_sections_and_agent_targets_are_present(self):
        combined = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*.tsx"))
        expected = [
            "id=\"install\"",
            "id=\"workflow\"",
            "id=\"agents\"",
            "id=\"security\"",
            "No hosted registry",
            "No agent lock-in",
            "No package resolution",
            "No semver complexity",
            "No skill execution",
            "Manifest-safe unlink",
            "Git-native distribution",
            "Symlink-based install",
            "User and project scopes",
            "Multi-agent support",
            "Safe conflict policy",
            "Manifest-tracked cleanup",
            "~/.agents/skills",
            ".agents/skills",
            "~/.claude/skills",
            ".claude/skills",
            "~/.config/opencode/skills",
            ".opencode/skills",
            "Single skill repo:",
            "Collection repo:",
            "Flat collection:",
        ]
        for text in expected:
            self.assertIn(text, combined)

    def test_tailwind_and_accessibility_basics(self):
        styles = read("src/styles.css")
        tailwind = read("tailwind.config.ts")
        app_sources = "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*.tsx"))
        self.assertIn("@tailwind base;", styles)
        self.assertIn("@tailwind components;", styles)
        self.assertIn("@tailwind utilities;", styles)
        self.assertIn("prefers-reduced-motion", styles)
        self.assertIn("scroll-behavior: smooth", styles)
        self.assertIn("./src/**/*.{ts,tsx}", tailwind)
        self.assertIn("aria-label", app_sources)
        self.assertIn("aria-labelledby", app_sources)


if __name__ == "__main__":
    unittest.main()
