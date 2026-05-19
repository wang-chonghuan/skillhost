import { CodeBlock } from './CodeBlock';

type InstallSectionProps = {
  githubUrl: string;
  pypiUrl: string;
  docsUrl: string;
};

const installs = [
  { label: 'Recommended', description: 'Best default for a Python CLI installed as an isolated uv tool.', command: 'uv tool install skillhost' },
  { label: 'Alternative', description: 'Classic isolated Python CLI install path.', command: 'pipx install skillhost' },
  { label: 'Fallback', description: 'Use pip when your environment already manages CLI isolation.', command: 'pip install skillhost' },
];

export function InstallSection({ githubUrl, pypiUrl, docsUrl }: InstallSectionProps) {
  return (
    <section id="install" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="install-title">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Install</p>
            <h2 id="install-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Install Skillhost as a Python CLI.
            </h2>
            <p className="mt-5 leading-8 text-slate-400">
              Start with uv for a fast isolated tool install, or use pipx if that is already your team’s standard.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <a className="rounded-full border border-white/10 bg-white/[0.05] px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300/35 hover:bg-cyan-300/10" href={pypiUrl} rel="noreferrer">PyPI</a>
              <a className="rounded-full border border-white/10 bg-white/[0.05] px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300/35 hover:bg-cyan-300/10" href={githubUrl} rel="noreferrer">GitHub</a>
              <a className="rounded-full border border-white/10 bg-white/[0.05] px-5 py-3 text-sm font-semibold text-white transition hover:border-cyan-300/35 hover:bg-cyan-300/10" href={docsUrl} rel="noreferrer">README</a>
            </div>
          </div>
          <div className="grid gap-4">
            {installs.map((item) => (
              <article key={item.label} className="rounded-3xl border border-white/10 bg-white/[0.035] p-5">
                <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
                  <h3 className="text-lg font-semibold text-white">{item.label}</h3>
                  <p className="text-sm text-slate-400">{item.description}</p>
                </div>
                <CodeBlock code={item.command} />
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
