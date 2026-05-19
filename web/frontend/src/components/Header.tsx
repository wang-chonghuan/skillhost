type HeaderProps = {
  githubUrl: string;
};

const navItems = [
  { label: 'Workflow', href: '#workflow' },
  { label: 'Agents', href: '#agents' },
  { label: 'Security', href: '#security' },
  { label: 'Install', href: '#install' },
];

export function Header({ githubUrl }: HeaderProps) {
  return (
    <header className="sticky top-0 z-50 border-b border-sky-100 bg-white/80 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-5 py-4 sm:px-6 lg:px-8">
        <a href="#top" className="group flex items-center gap-3 rounded-full" aria-label="SkillHost home">
          <span className="grid h-9 w-9 place-items-center rounded-2xl bg-gradient-to-br from-primary to-blue text-sm font-bold text-white shadow-glow transition group-hover:scale-105">
            S
          </span>
          <span className="font-display text-base font-semibold tracking-tight text-ink">SkillHost</span>
        </a>
        <nav className="hidden items-center gap-7 text-sm font-medium text-muted md:flex" aria-label="Primary navigation">
          {navItems.map((item) => (
            <a key={item.href} href={item.href} className="transition hover:text-primary-strong">
              {item.label}
            </a>
          ))}
          <a href={githubUrl} className="transition hover:text-primary-strong" rel="noreferrer">
            GitHub
          </a>
        </nav>
        <a
          href="#install"
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white shadow-soft transition hover:-translate-y-0.5 hover:bg-primary-strong md:hidden"
        >
          Install
        </a>
      </div>
    </header>
  );
}
