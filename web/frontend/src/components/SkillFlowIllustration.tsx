const agentTargets = [
  { agent: 'Codex', user: '~/.agents/skills', project: '.agents/skills' },
  { agent: 'Claude', user: '~/.claude/skills', project: '.claude/skills' },
  { agent: 'OpenCode', user: '~/.config/opencode/skills', project: '.opencode/skills' },
];

export function SkillFlowIllustration() {
  return (
    <div
      className="relative overflow-hidden rounded-[2rem] border border-line bg-white/88 p-5 shadow-soft backdrop-blur"
      aria-label="SkillHost links Git-hosted skills into native agent directories"
    >
      <div className="absolute -right-16 -top-16 h-40 w-40 rounded-full bg-sky-200/60 blur-3xl" />
      <div className="absolute -bottom-20 left-12 h-44 w-44 rounded-full bg-blue-200/45 blur-3xl" />

      <div className="relative grid gap-4">
        <div className="grid gap-3 sm:grid-cols-2">
          {['team-skills.git', 'project-skills.git'].map((repo) => (
            <div key={repo} className="rounded-2xl border border-sky-100 bg-skywash/80 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary-strong">Git repo</p>
              <p className="mt-2 font-mono text-sm font-semibold text-ink">{repo}</p>
              <p className="mt-1 text-xs text-muted">reviewed · versioned · pullable</p>
            </div>
          ))}
        </div>

        <div className="flex justify-center" aria-hidden="true">
          <div className="h-8 w-px bg-gradient-to-b from-primary/10 via-primary to-primary/10" />
        </div>

        <div className="rounded-3xl border border-primary/20 bg-gradient-to-br from-white to-skywash p-5 text-center shadow-card">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-primary-strong">SkillHost</p>
          <h3 className="mt-2 font-display text-2xl font-semibold text-ink">Manifest-aware skill linking</h3>
          <div className="mt-4 flex flex-wrap justify-center gap-2 text-xs font-semibold">
            <span className="rounded-full bg-white px-3 py-1 text-primary-strong shadow-sm">discover SKILL.md</span>
            <span className="rounded-full bg-white px-3 py-1 text-primary-strong shadow-sm">symlink</span>
            <span className="rounded-full bg-white px-3 py-1 text-primary-strong shadow-sm">update</span>
            <span className="rounded-full bg-white px-3 py-1 text-primary-strong shadow-sm">clean up</span>
          </div>
        </div>

        <div className="flex justify-center" aria-hidden="true">
          <div className="h-8 w-px bg-gradient-to-b from-primary/10 via-primary to-primary/10" />
        </div>

        <div className="grid gap-3">
          {agentTargets.map((target) => (
            <div key={target.agent} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
              <div className="flex items-center justify-between gap-3">
                <p className="font-semibold text-ink">{target.agent}</p>
                <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">linked</span>
              </div>
              <div className="mt-3 grid gap-2 text-xs sm:grid-cols-2">
                <code className="rounded-xl bg-slate-50 px-3 py-2 font-mono text-slate-700">user {target.user}</code>
                <code className="rounded-xl bg-slate-50 px-3 py-2 font-mono text-slate-700">project {target.project}</code>
              </div>
            </div>
          ))}
        </div>

        <div className="rounded-2xl bg-code p-4 font-mono text-xs leading-6 text-slate-200 shadow-card">
          <p><span className="text-sky-300">$</span> skillhost add git@github.com:acme/acme-skills.git</p>
          <p><span className="text-sky-300">?</span> Link discovered skills now? 1</p>
          <p className="mt-2 text-emerald-300">linked codex user skills</p>
        </div>
      </div>
    </div>
  );
}
