const features = [
  {
    title: 'Git-native distribution',
    description: 'Use the Git repositories your team already trusts. Clone, pull, review, and roll back with normal developer workflows.',
  },
  {
    title: 'Symlink-based install',
    description: 'Skillhost links discovered skills into each agent’s native skill directory instead of copying or repackaging them.',
  },
  {
    title: 'User and project scopes',
    description: 'Install shared personal skills globally, or link project-specific skills into the current repository.',
  },
  {
    title: 'Multi-agent support',
    description: 'Codex, Claude Code, and OpenCode get their own native targets. No cross-agent hacks.',
  },
  {
    title: 'Safe conflict policy',
    description: 'Existing user-owned skills are never overwritten. Duplicate skill names are reported instead of silently resolved.',
  },
  {
    title: 'Manifest-tracked cleanup',
    description: 'Unlink and remove only touch symlinks created by Skillhost.',
  },
];

export function FeatureGrid() {
  return (
    <section className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="features-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Core model</p>
          <h2 id="features-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            Small primitives. Predictable behavior.
          </h2>
        </div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <article key={feature.title} className="rounded-3xl border border-white/10 bg-white/[0.035] p-6 shadow-panel transition hover:-translate-y-0.5 hover:border-cyan-300/25 hover:bg-white/[0.055]">
              <div className="mb-5 h-1 w-10 rounded-full bg-gradient-to-r from-cyan-300 to-violet-300" />
              <h3 className="text-lg font-semibold text-white">{feature.title}</h3>
              <p className="mt-3 leading-7 text-slate-400">{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
