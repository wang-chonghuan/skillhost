const features = [
  { title: 'Distribute from Git', description: 'Review, version, pull, and roll back skills like code.' },
  { title: 'Update without recopying', description: 'Refresh linked skills instead of chasing old copies.' },
  { title: 'Global or project-local', description: 'Put each skill exactly where it belongs.' },
  { title: 'Native agent directories', description: 'Codex, Claude Code, and OpenCode keep reading their own folders.' },
  { title: 'Conflict-aware linking', description: 'Existing user-owned skills are not overwritten.' },
  { title: 'Manifest-safe cleanup', description: 'Remove only what SkillHost created.' },
];

export function FeatureGrid() {
  return (
    <section className="px-5 py-16 sm:px-6 lg:px-8" aria-labelledby="features-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">What you get</p>
          <h2 id="features-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            One workflow for every agent.
          </h2>
        </div>
        <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => (
            <article key={feature.title} className="rounded-3xl border border-line bg-white/86 p-6 shadow-card transition hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-soft">
              <div className="mb-5 h-1 w-10 rounded-full bg-gradient-to-r from-primary to-blue" />
              <h3 className="font-display text-lg font-semibold text-ink">{feature.title}</h3>
              <p className="mt-3 leading-7 text-muted">{feature.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
