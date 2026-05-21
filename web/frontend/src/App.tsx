import { useEffect, useState, type ReactNode } from 'react';
import { CodeBlock } from './components/CodeBlock';
import { Header } from './components/Header';
import { ScenarioCard } from './components/ScenarioCard';
import readmeText from '../../../README.md?raw';

const GITHUB_URL = 'https://github.com/wang-chonghuan/skillhost';
const LINKEDIN_URL = 'https://www.linkedin.com/in/chonghuan/';
const PYPI_URL = 'https://pypi.org/project/skillhost/';

const heroInstallOptions = [
  { label: 'pipx', command: 'pipx install skillhost' },
  { label: 'uv', command: 'uv tool install skillhost' },
  { label: 'pip', command: 'pip install skillhost' },
];

const installCommands = `pipx install skillhost
uv tool install skillhost
pip install skillhost`;

const scenarioOneCommands = `skillhost add git@github.com:my-org/company-skills.git`;

const scenarioOneUpdateCommands = `skillhost update`;

const scenarioTwoCommands = `skillhost add git@github.com:my-org/team-skills.git`;

const scenarioTwoUpdateCommands = `skillhost update`;

const scenarioThreeCommands = `skillhost register --project my-project --git git@github.com:my-org/my-project.git
skillhost add git@github.com:my-org/my-project-skills.git --project my-project`;

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

const projectCommands = `skillhost register --project <project> --git <project-git-url>
skillhost add <skill-git-repo> --project <project>
skillhost update --project <project>`;

const skillFlowText = `Skill flow:
skill repo -> SkillHost -> Codex ~/.agents/skills
skill collection repo -> SkillHost -> Claude Code ~/.claude/skills
skill collection repo -> SkillHost -> teammate Codex ~/.agents/skills

A skill repo contains one SKILL.md. A skill collection repo contains multiple skill folders, each with its own SKILL.md. SkillHost discovers those skills and links them into the selected agent directories.`;

const safetyNotes = [
  'SkillHost never executes code from skill repositories.',
  'Existing user-owned skills are not overwritten.',
  'SkillHost tracks created symlinks in manifests for safe cleanup.',
  'Duplicate skill names are reported instead of silently resolved.',
];

const DOCS_TEXT = readmeText;

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
    <figure className="max-w-full overflow-hidden rounded-2xl border border-cyan-200/25 bg-slate-950 p-3 shadow-2xl shadow-cyan-950/20" aria-label="SkillHost directory diagram">
      <svg viewBox="0 0 900 430" className="block h-auto w-full max-w-full" role="img" aria-labelledby="diagram-title diagram-desc">
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


function SkillFlowDiagram() {
  const agentRows = [
    { y: 72, label: 'Codex', path: '~/.agents/skills', stroke: '#155e75', dot: '#67e8f9' },
    { y: 132, label: 'Claude Code', path: '~/.claude/skills', stroke: '#155e75', dot: '#67e8f9' },
    { y: 192, label: 'Teammate Codex', path: '~/.agents/skills', stroke: '#16a34a', dot: '#86efac' },
  ];

  return (
    <figure className="max-w-full overflow-hidden rounded-2xl border border-cyan-200/25 bg-slate-950 p-3 shadow-sm dark:border-cyan-300/10 sm:p-4" aria-label="SkillHost skill distribution flow">
      <svg viewBox="0 0 900 270" className="block h-auto w-full max-w-full" role="img" aria-labelledby="skill-flow-title skill-flow-desc">
        <title id="skill-flow-title">SkillHost skill distribution flow</title>
        <desc id="skill-flow-desc">A skill repository or a skill collection repository flows through SkillHost into multiple agent skill directories.</desc>
        <defs>
          <linearGradient id="flow-card" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#0f172a" />
            <stop offset="100%" stopColor="#111827" />
          </linearGradient>
          <filter id="flow-glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="1.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect x="0" y="0" width="900" height="270" rx="22" fill="#020617" />
        <text x="58" y="42" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="13" fontWeight="800" letterSpacing="1.5">REPOS</text>
        <text x="412" y="42" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="13" fontWeight="800" letterSpacing="1.5">SKILLHOST</text>
        <text x="636" y="42" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="13" fontWeight="800" letterSpacing="1.5">AGENT DIRECTORIES</text>

        <g>
          <rect x="38" y="70" width="220" height="58" rx="16" fill="url(#flow-card)" stroke="#67e8f9" />
          <text x="148" y="96" textAnchor="middle" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="15" fontWeight="800">skill repo</text>
          <text x="148" y="116" textAnchor="middle" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="12">one skill</text>

          <rect x="38" y="158" width="220" height="64" rx="16" fill="url(#flow-card)" stroke="#a78bfa" />
          <text x="148" y="184" textAnchor="middle" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="15" fontWeight="800">skill collection repo</text>
          <text x="148" y="204" textAnchor="middle" fill="#c4b5fd" fontFamily="ui-sans-serif,system-ui" fontSize="12">many skills</text>
        </g>

        <g fill="none" stroke="#f8fafc" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" filter="url(#flow-glow)">
          <path d="M258 99 C306 99 322 135 360 135" />
          <path d="M258 190 C306 190 322 135 360 135" />
        </g>

        <g>
          <rect x="370" y="88" width="132" height="94" rx="22" fill="#08111f" stroke="#67e8f9" strokeWidth="2" />
          <text x="436" y="128" textAnchor="middle" fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="18" fontWeight="900">SkillHost</text>
          <text x="436" y="152" textAnchor="middle" fill="#a5f3fc" fontFamily="ui-sans-serif,system-ui" fontSize="12">discover + link</text>
        </g>

        <g fill="none" stroke="#f8fafc" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" filter="url(#flow-glow)">
          <path d="M512 118 C560 118 574 72 618 72" />
          <path d="M512 135 H618" />
          <path d="M512 152 C560 152 574 192 618 192" />
        </g>

        {agentRows.map((agent) => (
          <g key={agent.label}>
            <rect x="628" y={agent.y - 24} width="230" height="48" rx="15" fill="url(#flow-card)" stroke={agent.stroke} />
            <circle cx="654" cy={agent.y} r="6" fill={agent.dot} />
            <text x="674" y={agent.y - 4} fill="#f8fafc" fontFamily="ui-sans-serif,system-ui" fontSize="14" fontWeight="800">{agent.label}</text>
            <text x="674" y={agent.y + 14} fill="#94a3b8" fontFamily="ui-monospace,SFMono-Regular,Menlo,monospace" fontSize="11">{agent.path}</text>
          </g>
        ))}
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
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Skill flow</h3>
          <p className="mb-4 text-sm leading-6 text-slate-800 dark:text-slate-300">Put one skill or a whole collection in Git. SkillHost discovers each SKILL.md and links the skills into the agent directories you choose.</p>
          <SkillhostDiagram />
        </div>
        <div>
          <h3 className="mb-3 text-sm font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">Safety notes</h3>
          <ul className="grid gap-3 text-sm leading-6 text-slate-800 dark:text-slate-300 sm:grid-cols-2">
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

type DocsPageProps = {
  copyState: string;
  docsText: string;
  onCopyDocs: () => void;
};

function renderInlineMarkdown(text: string) {
  const parts = text.split(/(`[^`]+`|https?:\/\/\S+)/g);

  return parts.map((part, index) => {
    if (!part) {
      return null;
    }

    if (part.startsWith('`') && part.endsWith('`')) {
      return (
        <code key={index} className="rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[0.9em] font-semibold text-cyan-800 dark:bg-slate-900 dark:text-cyan-200">
          {part.slice(1, -1)}
        </code>
      );
    }

    if (/^https?:\/\//.test(part)) {
      return (
        <a key={index} href={part} className="font-semibold text-cyan-700 underline decoration-cyan-300 underline-offset-4 hover:text-cyan-900 dark:text-cyan-300 dark:decoration-cyan-700 dark:hover:text-cyan-100" rel="noreferrer">
          {part}
        </a>
      );
    }

    return part;
  });
}

function renderMarkdownDocs(markdown: string) {
  const lines = markdown.split('\n');
  const blocks: ReactNode[] = [];
  let index = 0;

  while (index < lines.length) {
    const line = lines[index];

    if (!line.trim()) {
      index += 1;
      continue;
    }

    const fenceMatch = line.match(/^```(\w+)?/);
    if (fenceMatch) {
      const language = fenceMatch[1];
      const codeLines: string[] = [];
      index += 1;

      while (index < lines.length && !lines[index].startsWith('```')) {
        codeLines.push(lines[index]);
        index += 1;
      }

      if (index < lines.length) {
        index += 1;
      }

      blocks.push(
        <div key={blocks.length} className="my-5 overflow-hidden rounded-xl border border-slate-200 bg-slate-950 shadow-sm dark:border-cyan-300/10 dark:bg-black/70">
          {language ? (
            <div className="border-b border-white/10 px-4 py-2 font-mono text-xs font-semibold uppercase tracking-[0.18em] text-cyan-200">
              {language}
            </div>
          ) : null}
          <pre className="whitespace-pre-wrap break-words p-4 text-sm leading-6 text-slate-100">
            <code>{codeLines.join('\n')}</code>
          </pre>
        </div>,
      );
      continue;
    }

    const headingMatch = line.match(/^(#{1,3})\s+(.+)$/);
    if (headingMatch) {
      const level = headingMatch[1].length;
      const content = renderInlineMarkdown(headingMatch[2]);

      if (level === 1) {
        blocks.push(
          <h1 key={blocks.length} className="mb-5 text-4xl font-semibold tracking-tight text-slate-950 dark:text-white sm:text-5xl">
            {content}
          </h1>,
        );
      } else if (level === 2) {
        blocks.push(
          <h2 key={blocks.length} className="mb-4 mt-10 border-t border-slate-200 pt-8 text-2xl font-semibold tracking-tight text-slate-950 dark:border-white/10 dark:text-white">
            {content}
          </h2>,
        );
      } else {
        blocks.push(
          <h3 key={blocks.length} className="mb-3 mt-7 text-lg font-semibold text-slate-950 dark:text-white">
            {content}
          </h3>,
        );
      }

      index += 1;
      continue;
    }

    if (line.startsWith('- ')) {
      const items: string[] = [];

      while (index < lines.length && lines[index].startsWith('- ')) {
        items.push(lines[index].slice(2));
        index += 1;
      }

      blocks.push(
        <ul key={blocks.length} className="my-5 grid gap-3 pl-0 text-base leading-7 text-slate-700 dark:text-slate-300">
          {items.map((item) => (
            <li key={item} className="flex gap-3">
              <span className="mt-3 h-1.5 w-1.5 shrink-0 rounded-full bg-cyan-500" />
              <span>{renderInlineMarkdown(item)}</span>
            </li>
          ))}
        </ul>,
      );
      continue;
    }

    const paragraphLines = [line];
    index += 1;

    while (
      index < lines.length
      && lines[index].trim()
      && !lines[index].startsWith('```')
      && !lines[index].match(/^(#{1,3})\s+/)
      && !lines[index].startsWith('- ')
    ) {
      paragraphLines.push(lines[index]);
      index += 1;
    }

    blocks.push(
      <p key={blocks.length} className="my-4 text-base leading-8 text-slate-700 dark:text-slate-300">
        {renderInlineMarkdown(paragraphLines.join(' '))}
      </p>,
    );
  }

  return blocks;
}

function DocsPage({ copyState, docsText, onCopyDocs }: DocsPageProps) {
  return (
    <section className="w-full border-y border-slate-200 bg-white/92 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/[0.04] sm:p-6 lg:rounded-[2rem] lg:border lg:p-10" aria-labelledby="docs-title">
      <div className="mb-8 flex flex-col gap-4 border-b border-slate-200 pb-6 dark:border-white/10 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-700 dark:text-cyan-300">Documentation</p>
          <h1 id="docs-title" className="mt-3 text-4xl font-semibold tracking-tight text-slate-950 dark:text-white">
            Docs
          </h1>
        </div>
        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={onCopyDocs}
            className="inline-flex h-10 items-center rounded-full border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
          >
            {copyState || 'Copy'}
          </button>
        </div>
      </div>
      <article className="mx-auto max-w-3xl">
        {renderMarkdownDocs(docsText)}
      </article>
    </section>
  );
}

export default function App() {
  const [copyState, setCopyState] = useState('');
  const [copiedInstallCommand, setCopiedInstallCommand] = useState('');
  const [isDocsOpen, setIsDocsOpen] = useState(false);

  useEffect(() => {
    document.documentElement.classList.remove('dark');
    document.documentElement.style.colorScheme = 'light';
  }, []);

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

  function toggleDocs() {
    setIsDocsOpen((current) => !current);
    window.requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: 'smooth' }));
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-950 transition-colors dark:bg-slate-950 dark:text-white">
      <Header
        isDocsOpen={isDocsOpen}
        githubUrl={GITHUB_URL}
        linkedinUrl={LINKEDIN_URL}
        pypiUrl={PYPI_URL}
        onToggleDocs={toggleDocs}
      />
      <main id="top" className="mx-auto flex w-full max-w-none flex-col gap-6 px-0 pb-20 pt-24 lg:max-w-5xl lg:px-6 lg:pt-32">
        {isDocsOpen ? (
          <DocsPage
            copyState={copyState}
            docsText={DOCS_TEXT}
            onCopyDocs={copyDocs}
          />
        ) : (
          <>
            <section className="w-full border-y border-slate-200 bg-white/82 p-5 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/[0.04] sm:p-6 lg:rounded-[2rem] lg:border lg:p-10" aria-labelledby="hero-title">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-700 dark:text-cyan-300">skillhost.dev</p>
                <h1 id="hero-title" className="mt-5 max-w-4xl text-4xl font-semibold tracking-[-0.04em] text-slate-950 dark:text-white sm:text-6xl">
                  Share skills across your agents.
                </h1>
                <div className="mt-6 max-w-4xl space-y-4 text-lg leading-8 text-slate-800 dark:text-slate-300">
                  <p>SkillHost keeps your AI agent skills easy to share, update, and organize. Use the same skills across agents, teammates, and projects.</p>
                </div>
              </div>
              <div className="mt-8">
                <SkillFlowDiagram />
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
          </>
        )}
      </main>
      <footer className="border-t border-slate-200 bg-white/70 px-5 py-6 text-center text-sm text-slate-600 dark:border-white/10 dark:bg-black/30 dark:text-slate-400">
        Copyright &copy; {new Date().getFullYear()} SkillHost. All rights reserved.
      </footer>
    </div>
  );
}
