import { SkillFlowIllustration } from './SkillFlowIllustration';

type HeroProps = {
  githubUrl: string;
};

const painPoints = [
  'Manual copying creates drift.',
  'Global skills should be available everywhere.',
  'Project skills should stay scoped to the repositories that need them.',
];

export function Hero({ githubUrl }: HeroProps) {
  return (
    <section id="top" className="relative overflow-hidden px-5 py-20 sm:px-6 sm:py-28 lg:px-8">
      <div className="absolute left-1/2 top-16 -z-10 h-80 w-80 -translate-x-1/2 rounded-full bg-sky-300/30 blur-3xl" />
      <div className="mx-auto grid max-w-7xl items-center gap-12 lg:grid-cols-[1.02fr_0.98fr]">
        <div className="text-center lg:text-left">
          <p className="mx-auto inline-flex rounded-full border border-sky-200 bg-white/75 px-4 py-2 text-sm font-semibold text-primary-strong shadow-sm lg:mx-0">
            Git-native skill distribution for AI coding agents
          </p>
          <h1 className="text-balance mt-7 max-w-4xl font-display text-5xl font-semibold tracking-[-0.055em] text-ink sm:text-6xl lg:text-7xl">
            Developers and teams need shared skills across multiple AI coding agents.
          </h1>
          <div className="mx-auto mt-7 grid max-w-2xl gap-3 lg:mx-0">
            {painPoints.map((point) => (
              <p key={point} className="rounded-2xl border border-sky-100 bg-white/78 px-4 py-3 text-base font-medium text-muted shadow-sm">
                {point}
              </p>
            ))}
          </div>
          <p className="mx-auto mt-7 max-w-2xl text-lg font-semibold leading-8 text-ink lg:mx-0">
            SkillHost keeps skills in Git and links them into each agent’s native skill directory at the user or project level.
          </p>
          <p className="mx-auto mt-4 max-w-2xl text-lg leading-8 text-muted lg:mx-0">
            Distribute, update, and clean up shared skills without copying folders by hand.
          </p>
          <div className="mt-9 flex flex-col justify-center gap-3 sm:flex-row lg:justify-start">
            <a
              href="#install"
              className="rounded-full bg-accent px-6 py-3 text-sm font-semibold text-white shadow-card transition hover:-translate-y-0.5 hover:bg-orange-600"
            >
              Install SkillHost
            </a>
            <a
              href={githubUrl}
              className="rounded-full border border-sky-200 bg-white/80 px-6 py-3 text-sm font-semibold text-primary-strong shadow-sm transition hover:-translate-y-0.5 hover:border-primary/40 hover:bg-skywash"
              rel="noreferrer"
            >
              View on GitHub
            </a>
          </div>
          <p className="mt-6 text-sm font-medium text-subtle">
            Git-backed updates · User and project scopes · Native agent directories · Manifest-safe cleanup
          </p>
        </div>
        <SkillFlowIllustration />
      </div>
    </section>
  );
}
