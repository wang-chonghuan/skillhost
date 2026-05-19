type FooterProps = {
  githubUrl: string;
  pypiUrl: string;
  docsUrl: string;
};

export function Footer({ githubUrl, pypiUrl, docsUrl }: FooterProps) {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-sky-100 bg-white/70 px-5 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm text-muted md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-display font-semibold text-ink">SkillHost</p>
          <p className="mt-2">SkillHost distributes, updates, and manages AI coding skills from Git.</p>
          <p className="mt-2 text-subtle">Git is the distribution system. Symlinks are the install system.</p>
          <p className="mt-2 text-subtle">© {year} SkillHost.</p>
        </div>
        <nav className="flex gap-5" aria-label="Footer navigation">
          <a className="transition hover:text-primary-strong" href={githubUrl} rel="noreferrer">GitHub</a>
          <a className="transition hover:text-primary-strong" href={pypiUrl} rel="noreferrer">PyPI</a>
          <a className="transition hover:text-primary-strong" href={docsUrl} rel="noreferrer">Docs</a>
        </nav>
      </div>
    </footer>
  );
}
