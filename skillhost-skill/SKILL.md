---
name: skillhost-skill
description: Load when the user asks to use SkillHost, manage agent skills, add or update skill repositories, control which skills are visible to an agent, register projects or agents, troubleshoot SkillHost, or says phrases like "add this skill repo", "sync my skills", "hide this skill from Codex", or "why can't my agent see this skill". Do not load for generic Git work or unrelated skill authoring.
---

# SkillHost Skill

Use this skill to turn natural-language requests into safe `skillhost` CLI actions and clear guidance.

First classify the request: install or upgrade SkillHost, inspect current state, add/update/relink/unlink/remove a skill repo, manage skill visibility for an agent, register an agent, register a project, or troubleshoot. When exact command behavior matters, inspect local help with `skillhost <command> --help`; SkillHost may be newer than this skill.

Read `references/skillhost-cli.md` when you need command syntax, target directories, project behavior, visibility rules, state files, or troubleshooting commands.

Before changing user state, identify the scope: user-level by default, or project-level only when the user names a registered project or asks for project-local skills. Never invent missing repo URLs, repo names, project names, or target agents. Ask a short clarification if the command cannot be made safe from context.

Prefer inspection before mutation. Useful first commands are `skillhost --version`, `skillhost agents`, `skillhost list --all`, `skillhost list --agent <agent>`, `skillhost projects`, `skillhost config`, and `skillhost doctor`.

Treat these as destructive or potentially surprising and require explicit user intent: `skillhost remove`, `skillhost unlink --all`, `skillhost unregister`, deleting files under `~/.skillhost`, and editing `config.json` by hand. Prefer SkillHost commands over manual state edits.

For visibility requests, use `skillhost list --agent <agent>` in an interactive terminal. In that menu, selected skills are visible and unselected skills are hidden from that agent. Hidden skills are persisted in SkillHost config and respected by later `update` and `relink`.

When reporting results, summarize what changed, which agent or project scope was affected, and any follow-up command the user should run. Do not claim a skill is visible unless you verified the target with `skillhost list --agent <agent>` or checked the relevant symlink/manifest.
