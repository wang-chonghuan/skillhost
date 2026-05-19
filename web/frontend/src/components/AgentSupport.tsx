const agents = [
  { name: 'Codex', user: '~/.agents/skills', project: '.agents/skills' },
  { name: 'Claude Code', user: '~/.claude/skills', project: '.claude/skills' },
  { name: 'OpenCode', user: '~/.config/opencode/skills', project: '.opencode/skills' },
];

export function AgentSupport() {
  return (
    <section id="agents" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="agents-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Agent targets</p>
          <h2 id="agents-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Native directories for each agent.
          </h2>
          <p className="mt-5 leading-8 text-muted">
            SkillHost links into the directories each agent already reads.
          </p>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {agents.map((agent) => (
            <article key={agent.name} className="rounded-3xl border border-line bg-white/86 p-6 shadow-card">
              <h3 className="font-display text-xl font-semibold text-ink">{agent.name}</h3>
              <dl className="mt-6 space-y-4 text-sm">
                <div>
                  <dt className="inline-flex rounded-full bg-skywash px-2.5 py-1 text-xs font-semibold text-primary-strong">user</dt>
                  <dd className="mt-2 rounded-xl bg-slate-50 px-3 py-2 font-mono text-slate-700">{agent.user}</dd>
                </div>
                <div>
                  <dt className="inline-flex rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-semibold text-emerald-700">project</dt>
                  <dd className="mt-2 rounded-xl bg-slate-50 px-3 py-2 font-mono text-slate-700">{agent.project}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
