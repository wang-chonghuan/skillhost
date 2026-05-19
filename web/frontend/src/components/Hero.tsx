import { CodeBlock } from './CodeBlock';

type HeroProps = {
  githubUrl: string;
};

const heroCode = `$ skillhost add git@github.com:acme/acme-skills.git
$ skillhost link

linked codex   ~/.agents/skills/acme-git
linked claude  ~/.claude/skills/acme-git
linked opencode ~/.config/opencode/skills/acme-git`;

export function Hero({ githubUrl }: HeroProps) {
  return (
    <section id="top" className="relative overflow-hidden px-5 py-20 sm:px-6 sm:py-28 lg:px-8">
      <div className="absolute left-1/2 top-24 -z-10 h-72 w-72 -translate-x-1/2 rounded-full bg-cyan-400/15 blur-3xl" />
      <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.05fr_0.95fr]">
        <div className="text-center lg:text-left">
          <p className="mx-auto inline-flex rounded-full border border-cyan-300/20 bg-cyan-300/10 px-4 py-2 text-sm font-medium text-cyan-100 lg:mx-0">
            Open-source Python CLI
          </p>
          <h1 className="mt-7 max-w-4xl text-5xl font-semibold tracking-[-0.055em] text-white sm:text-6xl lg:text-7xl">
            Agent skills, distributed with Git.
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg leading-8 text-slate-300 lg:mx-0">
            Skillhost links skills from Git repositories into Codex, Claude Code, and OpenCode. No registry, no server, no account — just Git, symlinks, and safe manifests.
          </p>
          <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start">
            <a
              href="#install"
              className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 shadow-glow transition hover:bg-cyan-100"
            >
              Install Skillhost
            </a>
            <a
              href={githubUrl}
              className="rounded-full border border-white/10 bg-white/[0.04] px-6 py-3 text-sm font-semibold text-white transition hover:border-white/20 hover:bg-white/[0.08]"
              rel="noreferrer"
            >
              View on GitHub
            </a>
          </div>
        </div>
        <div className="relative">
          <div className="absolute -inset-6 -z-10 rounded-[2rem] bg-gradient-to-br from-cyan-400/15 via-violet-500/10 to-transparent blur-2xl" />
          <CodeBlock title="skillhost" code={heroCode} />
        </div>
      </div>
    </section>
  );
}
