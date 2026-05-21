type HeaderProps = {
  isDocsOpen: boolean;
  githubUrl: string;
  linkedinUrl: string;
  pypiUrl: string;
  onToggleDocs: () => void;
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

function LinkedInIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="currentColor" aria-hidden="true">
      <path d="M20.45 20.45h-3.56v-5.58c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.95v5.67H9.34V8.98h3.42v1.57h.05a3.75 3.75 0 0 1 3.37-1.85c3.61 0 4.27 2.37 4.27 5.46v6.29ZM5.33 7.41a2.06 2.06 0 1 1 0-4.12 2.06 2.06 0 0 1 0 4.12Zm1.78 13.04H3.55V8.98h3.56v11.47ZM22.23 0H1.77C.79 0 0 .77 0 1.72v20.56C0 23.23.79 24 1.77 24h20.46c.98 0 1.77-.77 1.77-1.72V1.72C24 .77 23.21 0 22.23 0Z" />
    </svg>
  );
}

function DocsIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true">
      <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
      <path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15Z" />
      <path d="M8 7h8M8 11h8" />
    </svg>
  );
}

export function Header({ isDocsOpen, githubUrl, linkedinUrl, pypiUrl, onToggleDocs }: HeaderProps) {
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
            onClick={onToggleDocs}
            className="inline-flex h-10 items-center gap-2 rounded-full border border-slate-200 bg-white px-3 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
          >
            <DocsIcon />
            <span className="hidden sm:inline">{isDocsOpen ? 'Home' : 'Docs'}</span>
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
            href={linkedinUrl}
            className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 transition hover:bg-slate-50 dark:border-cyan-300/10 dark:bg-slate-950/80 dark:text-slate-100 dark:hover:bg-cyan-950/50"
            aria-label="View Chonghuan Wang on LinkedIn"
            rel="noreferrer"
          >
            <LinkedInIcon />
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
