const cards = [
  {
    title: 'Stop copy drift',
    description: 'One Git source. No stale folders scattered across agents.',
    className: 'lg:col-span-2',
  },
  {
    title: 'Ship updates once',
    description: 'Pull, relink, done.',
    className: '',
  },
  {
    title: 'Keep scopes clean',
    description: 'Global skills stay global. Project skills stay local.',
    className: '',
  },
  {
    title: 'Use native agent folders',
    description: 'No registry. No new runtime. No lock-in.',
    className: '',
  },
  {
    title: 'Clean up safely',
    description: 'The manifest knows what SkillHost linked.',
    className: 'lg:col-span-2',
  },
];

export function ProblemSolutionBento() {
  return (
    <section className="px-5 py-16 sm:px-6 lg:px-8" aria-labelledby="problem-solution-title">
      <div className="mx-auto max-w-7xl">
        <div className="max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Why it matters</p>
          <h2 id="problem-solution-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            Skills should move like code.
          </h2>
          <p className="mt-4 leading-7 text-muted">
            SkillHost turns skill distribution, updates, and cleanup into a Git workflow.
          </p>
        </div>
        <div className="mt-8 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
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
