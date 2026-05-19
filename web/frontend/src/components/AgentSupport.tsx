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
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Agent targets</p>
          <h2 id="agents-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Native directories for each agent.
          </h2>
          <p className="mt-5 leading-8 text-slate-400">
            Skillhost does not invent a registry path. It links skills into the directories Codex, Claude Code, and
            OpenCode already read.
          </p>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-3">
          {agents.map((agent) => (
            <article key={agent.name} className="rounded-3xl border border-white/10 bg-white/[0.035] p-6">
              <h3 className="text-xl font-semibold text-white">{agent.name}</h3>
              <dl className="mt-6 space-y-4 text-sm">
                <div>
                  <dt className="text-slate-500">User</dt>
                  <dd className="mt-1 rounded-xl bg-black/30 px-3 py-2 font-mono text-slate-200">{agent.user}</dd>
                </div>
                <div>
                  <dt className="text-slate-500">Project</dt>
                  <dd className="mt-1 rounded-xl bg-black/30 px-3 py-2 font-mono text-slate-200">{agent.project}</dd>
                </div>
              </dl>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
