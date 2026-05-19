import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "web" / "frontend"


def read(path: str) -> str:
    return (FRONTEND / path).read_text(encoding="utf-8")


def app_sources() -> str:
    return "\n".join(path.read_text(encoding="utf-8") for path in (FRONTEND / "src").rglob("*.tsx"))


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
            "src/components/SkillFlowIllustration.tsx",
            "src/components/ProblemSolutionBento.tsx",
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

    def test_brand_copy_links_and_commands_match_plan_v4(self):
        combined = app_sources()
        expected = [
            "SkillHost",
            "Developers and teams need shared skills across multiple AI coding agents.",
            "Manual copying creates drift.",
            "Global skills should be available everywhere.",
            "Project skills should stay scoped to the repositories that need them.",
            "SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.",
            "Distribute, update, and clean up shared skills without copying folders by hand.",
            "Git-backed updates · User and project scopes · Native agent directories · Manifest-safe cleanup",
            "https://github.com/skillhost-dev/skillhost",
            "https://pypi.org/project/skillhost/",
            "https://github.com/skillhost-dev/skillhost#readme",
            "uv tool install skillhost",
            "pipx install skillhost",
            "pip install skillhost",
            "skillhost add git@github.com:your-org/company-skills.git",
            "skillhost link",
            "skillhost project register my-project --git git@github.com:your-org/my-project.git",
            "skillhost project add git@github.com:your-org/my-project-skills.git --project my-project",
            "skillhost project remove project-skills --project my-project",
        ]
        for text in expected:
            self.assertIn(text, combined)
        self.assertNotIn("Skillhost", combined)
        self.assertNotIn("skillhost " + "user ", combined)

    def test_pain_points_value_props_and_agent_targets_are_present(self):
        combined = app_sources()
        expected = [
            "Copy-paste creates drift",
            "Distribution should be boring",
            "Updates should not mean recopying",
            "Global where it belongs",
            "Scoped when needed",
            "Cleanup should be safe",
            "Distribute from Git",
            "Update without recopying",
            "Manifest-safe cleanup",
            "Distribute skills from Git",
            "Manage user-level skills",
            "Keep project skills scoped",
            "Link native agent directories",
            "Clean up from the manifest",
            "Add a Git repo",
            "Discover SKILL.md files",
            "Pull updates and relink",
            "No hosted registry",
            "No skill execution",
            "Conflict-aware by default",
            "Git-backed updates",
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

    def test_light_mode_design_system_and_accessibility_basics(self):
        styles = read("src/styles.css")
        tailwind = read("tailwind.config.ts")
        app = read("src/App.tsx")
        combined = app_sources()
        self.assertIn("@tailwind base;", styles)
        self.assertIn("@tailwind components;", styles)
        self.assertIn("@tailwind utilities;", styles)
        self.assertIn("color-scheme: light", styles)
        self.assertIn("#f8fafc", styles.lower())
        self.assertIn("#0f172a", styles.lower())
        self.assertIn("prefers-reduced-motion", styles)
        self.assertIn("scroll-behavior: smooth", styles)
        self.assertIn("bg-canvas", app)
        self.assertIn("text-ink", app)
        self.assertNotIn("bg-ink text-bright", app)
        self.assertIn("canvas", tailwind)
        self.assertIn("skywash", tailwind)
        self.assertIn("surface", tailwind)
        self.assertIn("primary", tailwind)
        self.assertIn("accent", tailwind)
        self.assertIn("fontFamily", tailwind)
        self.assertIn("display", tailwind)
        self.assertIn("./src/**/*.{ts,tsx}", tailwind)
        self.assertIn("aria-label", combined)
        self.assertIn("aria-labelledby", combined)


if __name__ == "__main__":
    unittest.main()
