const safeguards = [
  {
    title: 'No hosted registry',
    description: 'Skills stay in your Git repositories. SkillHost does not require a server, account, or hosted package index.',
  },
  {
    title: 'No skill execution',
    description: 'SkillHost manages files and links. It does not run the skills it installs.',
  },
  {
    title: 'Conflict-aware by default',
    description: 'Existing user-owned skills are not overwritten. Conflicts are reported instead of silently resolved.',
  },
  {
    title: 'Git-backed updates',
    description: 'Updates use normal repository workflows, so teams keep history, review, ownership, and rollback.',
  },
  {
    title: 'Clean manifest-based unlink',
    description: 'Unlink uses the manifest to remove only symlinks created by SkillHost.',
  },
];

export function SecuritySection() {
  return (
    <section id="security" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="security-title">
      <div className="mx-auto max-w-7xl rounded-[2rem] border border-emerald-100 bg-gradient-to-br from-emerald-50 via-white to-skywash p-6 shadow-soft sm:p-10">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-emerald-700">Safety model</p>
          <h2 id="security-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Safe by being small.
          </h2>
          <p className="mt-5 leading-8 text-muted">
            Git distributes. Symlinks install. Manifests clean up.
          </p>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-5">
          {safeguards.map((item) => (
            <article key={item.title} className="rounded-2xl border border-white bg-white/82 p-5 shadow-sm">
              <h3 className="font-display font-semibold text-ink">{item.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted">{item.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
