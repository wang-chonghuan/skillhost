import { CodeBlock } from './CodeBlock';

type InstallSectionProps = {
  githubUrl: string;
  pypiUrl: string;
  docsUrl: string;
};

const installs = [
  { label: 'Recommended with uv', description: 'Fast isolated CLI install', command: 'uv tool install skillhost' },
  { label: 'Install with pipx', description: 'Isolated Python CLI install', command: 'pipx install skillhost' },
  { label: 'Install with pip', description: 'Works when pip is all you have', command: 'pip install skillhost' },
];

const nextSteps = `skillhost add git@github.com:your-org/company-skills.git
skillhost link
skillhost project register my-project --git git@github.com:your-org/my-project.git`;

export function InstallSection({ githubUrl, pypiUrl, docsUrl }: InstallSectionProps) {
  return (
    <section id="install" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="install-title">
      <div className="mx-auto max-w-7xl rounded-[2rem] border border-line bg-white/88 p-6 shadow-soft sm:p-10">
        <div className="grid gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-start">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Install</p>
            <h2 id="install-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
              Install. Add. Link.
            </h2>
            <p className="mt-5 leading-8 text-muted">
              Start with any standard Python installer.
            </p>
            <CodeBlock className="mt-6" title="next steps" code={nextSteps} />
            <div className="mt-8 flex flex-wrap gap-3">
              <a className="rounded-full bg-ink px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:-translate-y-0.5 hover:bg-primary-strong" href={pypiUrl} rel="noreferrer">PyPI</a>
              <a className="rounded-full border border-sky-200 bg-white px-5 py-3 text-sm font-semibold text-primary-strong shadow-sm transition hover:-translate-y-0.5 hover:bg-skywash" href={githubUrl} rel="noreferrer">GitHub</a>
              <a className="rounded-full border border-sky-200 bg-white px-5 py-3 text-sm font-semibold text-primary-strong shadow-sm transition hover:-translate-y-0.5 hover:bg-skywash" href={docsUrl} rel="noreferrer">README</a>
            </div>
          </div>
          <div className="grid gap-4">
            {installs.map((item) => (
              <article key={item.label} className="rounded-3xl border border-line bg-surface-soft p-5 shadow-sm">
                <div className="mb-4 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
                  <h3 className="font-display text-lg font-semibold text-ink">{item.label}</h3>
                  <p className="text-sm text-muted">{item.description}</p>
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
