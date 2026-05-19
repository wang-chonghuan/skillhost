const points = [
  'Skillhost never executes code from skill repositories.',
  'Skillhost only clones, updates, discovers SKILL.md files, and creates or removes symlinks.',
  'Unlink and remove are manifest-driven, so user-owned directories are left alone.',
];

export function SecuritySection() {
  return (
    <section id="security" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="security-title">
      <div className="mx-auto max-w-7xl overflow-hidden rounded-[2rem] border border-white/10 bg-gradient-to-br from-white/[0.06] via-white/[0.035] to-cyan-300/[0.04] p-6 shadow-panel sm:p-10 lg:p-12">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Security</p>
            <h2 id="security-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Serious defaults for shared skills.
            </h2>
            <p className="mt-5 leading-8 text-slate-400">
              Skillhost keeps repository contents inspectable and installation reversible. The tool manages links and
              manifests; it does not run installer hooks from skill repositories.
            </p>
          </div>
          <div className="grid gap-4">
            {points.map((point) => (
              <div key={point} className="rounded-2xl border border-white/10 bg-black/25 p-5 text-slate-200">
                <span className="mr-3 text-cyan-200" aria-hidden="true">◆</span>
                {point}
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
