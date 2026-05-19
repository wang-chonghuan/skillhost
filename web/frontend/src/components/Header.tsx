type HeaderProps = {
  githubUrl: string;
};

const navItems = [
  { label: 'Install', href: '#install' },
  { label: 'Workflow', href: '#workflow' },
  { label: 'Agents', href: '#agents' },
  { label: 'Security', href: '#security' },
];

export function Header({ githubUrl }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-ink/72 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-6 lg:px-8">
        <a href="#top" className="group flex items-center gap-3" aria-label="Skillhost home">
          <span className="grid h-8 w-8 place-items-center rounded-xl border border-cyan-300/20 bg-cyan-300/10 text-sm font-bold text-cyan-200 shadow-glow">
            S
          </span>
          <span className="text-base font-semibold tracking-tight text-white">Skillhost</span>
        </a>
        <nav className="hidden items-center gap-7 text-sm font-medium text-slate-300 md:flex" aria-label="Primary navigation">
          {navItems.map((item) => (
            <a key={item.href} href={item.href} className="transition hover:text-white">
              {item.label}
            </a>
          ))}
          <a href={githubUrl} className="transition hover:text-white" rel="noreferrer">
            GitHub
          </a>
        </nav>
        <a
          href="#install"
          className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm font-semibold text-white transition hover:border-cyan-300/40 hover:bg-cyan-300/10 md:hidden"
        >
          Install
        </a>
      </div>
    </header>
  );
}
