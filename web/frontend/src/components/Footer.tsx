type FooterProps = {
  githubUrl: string;
  pypiUrl: string;
  docsUrl: string;
};

export function Footer({ githubUrl, pypiUrl, docsUrl }: FooterProps) {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-white/10 px-5 py-10 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col gap-6 text-sm text-slate-400 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="font-semibold text-white">Skillhost</p>
          <p className="mt-2">Agent skills for Codex, Claude Code, and OpenCode.</p>
          <p className="mt-2 text-slate-500">Git is the distribution system. Symlinks are the install system.</p>
          <p className="mt-2 text-slate-600">© {year} Skillhost.</p>
        </div>
        <nav className="flex gap-5" aria-label="Footer navigation">
          <a className="transition hover:text-white" href={githubUrl} rel="noreferrer">GitHub</a>
          <a className="transition hover:text-white" href={pypiUrl} rel="noreferrer">PyPI</a>
          <a className="transition hover:text-white" href={docsUrl} rel="noreferrer">Docs</a>
        </nav>
      </div>
    </footer>
  );
}
