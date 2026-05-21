type HeaderProps = {
  githubUrl: string;
  pypiUrl: string;
  copyState: string;
  onCopyDocs: () => void;
};

function GitHubIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
      <path d="M12 .5a12 12 0 0 0-3.8 23.38c.6.11.82-.26.82-.58v-2.02c-3.34.73-4.04-1.42-4.04-1.42-.55-1.38-1.34-1.75-1.34-1.75-1.09-.75.08-.73.08-.73 1.2.08 1.84 1.24 1.84 1.24 1.07 1.83 2.8 1.3 3.49.99.11-.78.42-1.3.76-1.6-2.67-.3-5.47-1.33-5.47-5.93 0-1.31.47-2.38 1.24-3.22-.12-.3-.54-1.52.12-3.18 0 0 1.01-.32 3.3 1.23a11.45 11.45 0 0 1 6 0c2.29-1.55 3.3-1.23 3.3-1.23.66 1.66.24 2.88.12 3.18.77.84 1.24 1.91 1.24 3.22 0 4.61-2.81 5.62-5.48 5.92.43.37.81 1.1.81 2.22v3.29c0 .32.22.69.83.57A12 12 0 0 0 12 .5Z" />
    </svg>
  );
}

function PackageIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="m12 2 8 4.5v9L12 20l-8-4.5v-9L12 2Z" />
      <path d="M4 6.5 12 11l8-4.5M12 11v9" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <rect x="9" y="9" width="11" height="11" rx="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

export function Header({ githubUrl, pypiUrl, copyState, onCopyDocs }: HeaderProps) {
  return (
    <header className="fixed inset-x-0 top-0 z-50 border-b border-slate-200/80 bg-white/80 backdrop-blur-xl dark:border-cyan-300/10 dark:bg-black/80">
      <div className="mx-auto flex h-16 w-full max-w-none items-center justify-between px-3 sm:px-4 lg:max-w-5xl lg:px-6">
        <a href="#top" className="flex min-w-0 items-center gap-2 sm:gap-3" aria-label="SkillHost home">
          <span className="grid h-9 w-9 place-items-center rounded-xl bg-slate-950 text-sm font-bold text-white shadow-sm dark:bg-cyan-300 dark:text-slate-950">
            SH
          </span>
          <span className="text-base font-semibold tracking-tight text-slate-950 dark:text-white">SkillHost</span>
        </a>
        <div className="flex shrink-0 items-center gap-1.5 sm:gap-2">
          <button
            type="button"
            onClick={onCopyDocs}
            className="inline-flex h-10 items-center gap-2 rounded-full border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
          >
            <CopyIcon />
            <span className="hidden sm:inline">{copyState || 'Copy docs'}</span>
          </button>
          <a
            href={githubUrl}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
            aria-label="View SkillHost on GitHub"
            rel="noreferrer"
          >
            <GitHubIcon />
          </a>
          <a
            href={pypiUrl}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
            aria-label="View skillhost on PyPI"
            rel="noreferrer"
          >
            <PackageIcon />
          </a>
        </div>
      </div>
    </header>
  );
}
