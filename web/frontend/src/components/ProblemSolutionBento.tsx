const cards = [
  {
    title: 'Copy-paste creates drift',
    description: 'Manually copied skills become stale across machines, agents, and repositories. Nobody knows which version is installed where.',
    className: 'lg:col-span-2',
  },
  {
    title: 'Distribution should be boring',
    description: 'Put skills in Git, add the repository once, and let SkillHost link them into the agent directories that already exist.',
    className: '',
  },
  {
    title: 'Updates should not mean recopying',
    description: 'When a skill improves, pull from Git and relink. Teams keep review history, branches, rollback, and ownership.',
    className: '',
  },
  {
    title: 'Global where it belongs',
    description: 'User-level skills can be available across every supported agent on the machine.',
    className: '',
  },
  {
    title: 'Scoped when needed',
    description: 'Project-level skills stay attached to the repositories that need them, without polluting the user’s global skill set.',
    className: '',
  },
  {
    title: 'Cleanup should be safe',
    description: 'SkillHost tracks what it linked, so removal can be manifest-guided instead of guesswork.',
    className: 'lg:col-span-2',
  },
];

export function ProblemSolutionBento() {
  return (
    <section className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="problem-solution-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Why teams need it</p>
          <h2 id="problem-solution-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Skills should move like code, not like copied folders.
          </h2>
          <p className="mt-5 leading-8 text-muted">
            SkillHost solves the distribution, management, update, and cleanup problems that appear as soon as teams use more than one AI coding agent.
          </p>
        </div>
        <div className="mt-10 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {cards.map((card) => (
            <article key={card.title} className={`rounded-3xl border border-line bg-white/86 p-6 shadow-card transition hover:-translate-y-0.5 hover:shadow-soft ${card.className}`}>
              <div className="mb-5 h-10 w-10 rounded-2xl bg-gradient-to-br from-sky-100 to-blue-100" aria-hidden="true" />
              <h3 className="font-display text-xl font-semibold text-ink">{card.title}</h3>
              <p className="mt-3 leading-7 text-muted">{card.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
