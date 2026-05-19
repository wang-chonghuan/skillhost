const features = [
  {
    title: 'Distribute skills from Git',
    description: 'Keep shared skills in repositories your team already reviews, versions, and trusts.',
  },
  {
    title: 'Update without recopying',
    description: 'Pull repository changes and relink instead of chasing stale copies across machines and agents.',
  },
  {
    title: 'Manage user-level skills',
    description: 'Make everyday skills available across Codex, Claude Code, and OpenCode on the developer’s machine.',
  },
  {
    title: 'Keep project skills scoped',
    description: 'Attach repository-specific skills to the projects that need them without polluting global skill directories.',
  },
  {
    title: 'Link native agent directories',
    description: 'Use each agent’s existing skill locations instead of introducing a hosted registry or custom runtime.',
  },
  {
    title: 'Clean up from the manifest',
    description: 'Unlink only the symlinks SkillHost created, so cleanup is explicit and safe.',
  },
];

export function FeatureGrid() {
  return (
    <section className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="features-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-2xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Core model</p>
          <h2 id="features-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Distribution, management, updates, cleanup.
          </h2>
          <p className="mt-5 leading-8 text-muted">
            Small primitives make SkillHost predictable: Git stores the skills, manifests track the links, and agents keep using their native directories.
          </p>
        </div>
        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
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
