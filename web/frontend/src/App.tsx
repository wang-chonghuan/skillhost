import { useEffect, useState } from 'react';
import { CodeBlock } from './components/CodeBlock';
import { Header } from './components/Header';
import { ScenarioCard } from './components/ScenarioCard';

const GITHUB_URL = 'https://github.com/wang-chonghuan/skillhost';
const PYPI_URL = 'https://pypi.org/project/skillhost/';

const heroInstallOptions = [
  { label: 'pip', command: 'pip install skillhost' },
  { label: 'uv', command: 'uv tool install skillhost' },
];

const installCommands = `uv tool install skillhost
pipx install skillhost
pip install skillhost
uv tool install git+https://github.com/wang-chonghuan/skillhost.git`;

const scenarioOneCommands = `skillhost add git@github.com:my-org/company-skills.git`;

const scenarioOneUpdateCommands = `skillhost update`;

const scenarioTwoCommands = `skillhost add git@github.com:my-org/team-skills.git`;

const scenarioTwoUpdateCommands = `skillhost update`;

const scenarioThreeCommands = `skillhost project register my-project --git git@github.com:my-org/my-project.git
skillhost project add git@github.com:my-org/my-project-skills.git --project my-project`;

const scenarioThreeUpdateCommands = `skillhost update --project my-project`;

const userTargets = [
  { label: 'Codex', path: '~/.agents/skills' },
  { label: 'Claude Code', path: '~/.claude/skills' },
  { label: 'OpenCode', path: '~/.config/opencode/skills' },
];

const projectTargets = [
  { label: 'Codex', path: '.agents/skills' },
  { label: 'Claude Code', path: '.claude/skills' },
  { label: 'OpenCode', path: '.opencode/skills' },
];

const userCommands = `skillhost add <git-repo>
skillhost update`;

const projectCommands = `skillhost project register <project> --git <project-git-url>
skillhost project add <skill-git-repo> --project <project>
skillhost update --project <project>`;

const repoFormats = `Single skill:
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
    SKILL.md`;

const safetyNotes = [
  'SkillHost never executes code from skill repositories.',
  'Existing user-owned skills are not overwritten.',
  'SkillHost tracks created symlinks in manifests for safe cleanup.',
  'Duplicate skill names are reported instead of silently resolved.',
];

const DOCS_TEXT = `# SkillHost quick start

Install:
uv tool install skillhost
pipx install skillhost
pip install skillhost
uv tool install git+https://github.com/wang-chonghuan/skillhost.git

Scenario 1 — many local skills for every agent:
skillhost add git@github.com:my-org/company-skills.git
skillhost update

User targets:
Codex: ~/.agents/skills
Claude Code: ~/.claude/skills
OpenCode: ~/.config/opencode/skills

Scenario 2 — team shared skills:
skillhost add git@github.com:my-org/team-skills.git
skillhost update

Scenario 3 — project-only skills:
skillhost project register my-project --git git@github.com:my-org/my-project.git
skillhost project add git@github.com:my-org/my-project-skills.git --project my-project

Update from the project checkout:
skillhost update --project my-project

Project targets:
Codex: .agents/skills
Claude Code: .claude/skills
OpenCode: .opencode/skills

User commands:
${userCommands}

Project commands:
${projectCommands}

Skill repo formats:
${repoFormats}

Safety notes:
- ${safetyNotes.join('\n- ')}
`;

type Theme = 'light' | 'dark';

function getInitialTheme(): Theme {
  if (typeof window === 'undefined') {
    return 'dark';
  }

  return window.localStorage.getItem('theme') === 'light' ? 'light' : 'dark';
}

type InstallCommandsPanelProps = {
  copiedInstallCommand: string;
  onCopyInstallCommand: (command: string) => void;
};

function InstallCommandsPanel({ copiedInstallCommand, onCopyInstallCommand }: InstallCommandsPanelProps) {
  return (
    <div className="grid gap-3 sm:grid-cols-2" aria-label="Install SkillHost commands">
      {heroInstallOptions.map((option) => (
        <div key={option.command} className="flex items-center justify-between gap-3 rounded-2xl border border-slate-200 bg-slate-950 p-4 shadow-sm dark:border-cyan-300/10 dark:bg-black/55">
          <code className="min-w-0 flex-1 whitespace-normal break-words font-mono text-sm leading-6 text-slate-100">{option.command}</code>
          <button
            type="button"
            onClick={() => onCopyInstallCommand(option.command)}
            className="shrink-0 rounded-full border border-cyan-300/20 px-3 py-1.5 text-xs font-bold text-cyan-100 transition hover:bg-cyan-950/50"
            aria-label={`Copy ${option.label} install command`}
          >
            {copiedInstallCommand === option.command ? 'Copied' : 'Copy'}
          </button>
        </div>
      ))}
    </div>
  );
}

function SkillhostDiagram() {
  return (
    <figure className="overflow-hidden rounded-2xl border border-cyan-200/25 bg-slate-950 p-3 shadow-2xl shadow-cyan-950/20" aria-label="SkillHost directory diagram">
      <svg viewBox="0 0 900 430" className="h-auto w-full" role="img" aria-labelledby="diagram-title diagram-desc">
        <title id="diagram-title">SkillHost basic mapping diagram</title>
        <desc id="diagram-desc">User and project skill directories connect to dot skillhost repository storage.</desc>

        <defs>
          <linearGradient id="diagram-bg" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#020617" />
            <stop offset="55%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#111827" />
          </linearGradient>
          <linearGradient id="diagram-line" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#67e8f9" />
            <stop offset="50%" stopColor="#e2e8f0" />
            <stop offset="100%" stopColor="#a78bfa" />
          </linearGradient>
          <marker id="repo-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M10 5 0 10 0 0Z" fill="#f8fafc" />
          </marker>
        </defs>

        <rect x="0" y="0" width="900" height="430" fill="url(#diagram-bg)" />

        <g fill="none" stroke="#f8fafc" strokeWidth="2.5" strokeLinecap="square" strokeLinejoin="miter">
          <path d="M190 220 H450" />
          <path d="M190 280 H450" />
          <path d="M190 340 H450" />

          <path d="M710 240 H450" />
          <path d="M710 310 H450" />

          <path d="M450 120 V340" />
        </g>
        <text x="450" y="382" textAnchor="middle" fill="#cbd5e1" fontFamily="ui-sans-serif,system-ui" fontSize="12" fontWeight="700">symlinks</text>

        <g fill="#020617" stroke="#67e8f9" strokeWidth="2">
          <rect x="330" y="40" width="240" height="80" rx="8" />
        </g>
        <text x="450" y="72" textAnchor="middle" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="16" fontWeight="700">~/.skillhost</text>
        <text x="450" y="95" textAnchor="middle" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="12">skill git repos</text>

        <g fill="none" stroke="#f8fafc" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
          <path d="M650 80 H570" markerEnd="url(#repo-arrow)" />
        </g>
        <text x="610" y="68" textAnchor="middle" fill="#c4b5fd" fontFamily="ui-sans-serif,system-ui" fontSize="11" fontWeight="700">add/update</text>
        <g fill="#111827" stroke="#a78bfa" strokeWidth="1.5">
          <rect x="670" y="32" width="160" height="58" rx="8" opacity="0.42" />
          <rect x="660" y="42" width="160" height="58" rx="8" opacity="0.68" />
          <rect x="650" y="52" width="160" height="58" rx="8" />
        </g>
        <text x="730" y="78" textAnchor="middle" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="14" fontWeight="700">skill git repo</text>
        <text x="730" y="96" textAnchor="middle" fill="#ddd6fe" fontFamily="ui-sans-serif,system-ui" fontSize="11">third-party/personal repos</text>

        <text x="40" y="180" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="12" fontWeight="700">USER SKILL DIRECTORIES</text>
        <g fill="#0f172a" stroke="#22d3ee" strokeWidth="1.5">
          <rect x="40" y="190" width="300" height="42" rx="6" />
          <rect x="40" y="250" width="300" height="42" rx="6" />
          <rect x="40" y="310" width="300" height="42" rx="6" />
        </g>
        <g fill="#e2e8f0" fontFamily="ui-monospace,SFMono-Regular,Menlo,monospace" fontSize="12">
          <text x="54" y="215">~/.agents/skills</text>
          <text x="54" y="275">~/.claude/skills</text>
          <text x="54" y="335">~/.config/agent/skills</text>
        </g>

        <text x="560" y="200" fill="#ddd6fe" fontFamily="ui-sans-serif,system-ui" fontSize="12" fontWeight="700">PROJECT SKILL DIRECTORIES</text>
        <g fill="#111827" stroke="#a78bfa" strokeWidth="1.5">
          <rect x="560" y="210" width="300" height="46" rx="6" />
          <rect x="560" y="280" width="300" height="46" rx="6" />
        </g>
        <g fill="#e5e7eb" fontFamily="ui-monospace,SFMono-Regular,Menlo,monospace" fontSize="12">
          <text x="574" y="238">project-a/.agents/skills</text>
          <text x="574" y="308">project-b/.claude/skills</text>
        </g>
      </svg>
    </figure>
  );
}

function QuickDocs() {
  return (
    <section className="rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/[0.04] sm:p-8" aria-labelledby="quick-docs-title">
      <h2 id="quick-docs-title" className="text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
        Quick docs
      </h2>
      <div className="mt-6 grid gap-5">
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Install</h3>
          <CodeBlock code={installCommands} />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">User commands</h3>
          <CodeBlock code={userCommands} />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Project commands</h3>
          <CodeBlock code={projectCommands} />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Skill repo formats</h3>
          <CodeBlock code={repoFormats} />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Safety notes</h3>
          <ul className="grid gap-3 text-sm leading-6 text-slate-600 dark:text-slate-300 sm:grid-cols-2">
            {safetyNotes.map((note) => (
              <li key={note} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-white/[0.035]">
                {note}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}

export default function App() {
  const [theme, setTheme] = useState<Theme>(getInitialTheme);
  const [copyState, setCopyState] = useState('');
  const [copiedInstallCommand, setCopiedInstallCommand] = useState('');

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark');
    document.documentElement.style.colorScheme = theme;
    window.localStorage.setItem('theme', theme);
  }, [theme]);

  async function copyText(text: string, onSuccess: () => void, onUnavailable?: () => void) {
    if (!navigator.clipboard?.writeText) {
      onUnavailable?.();
      return;
    }

    await navigator.clipboard.writeText(text);
    onSuccess();
  }

  async function copyInstallCommand(command: string) {
    try {
      await copyText(command, () => setCopiedInstallCommand(command));
    } catch {
      setCopiedInstallCommand('');
    } finally {
      window.setTimeout(() => setCopiedInstallCommand(''), 1800);
    }
  }

  async function copyDocs() {
    try {
      await copyText(DOCS_TEXT, () => setCopyState('Copied'), () => setCopyState('Copy unavailable'));
      if (!navigator.clipboard?.writeText) {
        return;
      }
    } catch {
      setCopyState('Copy failed');
    } finally {
      window.setTimeout(() => setCopyState(''), 1800);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 transition-colors dark:bg-slate-950 dark:text-white">
      <Header
        githubUrl={GITHUB_URL}
        pypiUrl={PYPI_URL}
        copyState={copyState}
        theme={theme}
        onCopyDocs={copyDocs}
        onToggleTheme={() => setTheme((current) => (current === 'dark' ? 'light' : 'dark'))}
      />
      <main id="top" className="mx-auto flex max-w-5xl flex-col gap-6 px-4 pb-20 pt-28 sm:px-6 lg:pt-32">
        <section className="rounded-[2rem] border border-slate-200 bg-white/82 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/[0.04] sm:p-10" aria-labelledby="hero-title">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-700 dark:text-cyan-300">skillhost.dev</p>
            <h1 id="hero-title" className="mt-5 max-w-4xl text-4xl font-semibold tracking-[-0.04em] text-slate-950 dark:text-white sm:text-6xl">
              Agent Skills should not be copied and updated manually.
            </h1>
            <div className="mt-6 max-w-4xl space-y-4 text-lg leading-8 text-slate-600 dark:text-slate-300">
              <p>SkillHost installs skills from Git repositories into Codex, Claude Code, and other AI agents. Add once, update with Git, and keep user-level and project-level skills cleanly separated.</p>
            </div>
          </div>
          <div className="mt-8">
            <SkillhostDiagram />
          </div>
          <div className="mt-5">
            <InstallCommandsPanel copiedInstallCommand={copiedInstallCommand} onCopyInstallCommand={copyInstallCommand} />
          </div>
        </section>

        <ScenarioCard
          title="Scenario 1 — Make one skill repo available to every local agent."
          commands={scenarioOneCommands}
          afterTitle="Then update later:"
          afterCommands={scenarioOneUpdateCommands}
          targets={userTargets}
        >
          <p>Use user-level repos when skills should be available across your machine. Add once, then update whenever the repo changes.</p>
        </ScenarioCard>

        <ScenarioCard
          title="Scenario 2 — Share team skills without copy-paste drift."
          commands={scenarioTwoCommands}
          afterTitle="When the team updates skills:"
          afterCommands={scenarioTwoUpdateCommands}
        >
          <p>Put team skills in a normal Git repository. Everyone adds the same repo and pulls future changes with one update command.</p>
          <p>Git remains the source of truth. Reviews, branches, history, and rollback stay in your existing workflow.</p>
        </ScenarioCard>

        <ScenarioCard
          title="Scenario 3 — Keep project-only skills inside one repo."
          commands={scenarioThreeCommands}
          afterTitle="Update project skills:"
          afterCommands={scenarioThreeUpdateCommands}
          targets={projectTargets}
          note="Project skills stay scoped to the current Git repository root. SkillHost does not scan your disk."
        >
          <p>Use project-level repos for skills that should only be visible inside a specific checkout. SkillHost matches the current Git repository and updates local project-level agent directories.</p>
        </ScenarioCard>

        <QuickDocs />
      </main>
    </div>
  );
}
