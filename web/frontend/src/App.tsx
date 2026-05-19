import { AgentSupport } from './components/AgentSupport';
import { CodeBlock } from './components/CodeBlock';
import { FeatureGrid } from './components/FeatureGrid';
import { Footer } from './components/Footer';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { InstallSection } from './components/InstallSection';
import { ProblemSolutionBento } from './components/ProblemSolutionBento';
import { SecuritySection } from './components/SecuritySection';
import { Workflow } from './components/Workflow';

export const LINKS = {
  GITHUB_URL: 'https://github.com/skillhost-dev/skillhost',
  PYPI_URL: 'https://pypi.org/project/skillhost/',
  DOCS_URL: 'https://github.com/skillhost-dev/skillhost#readme',
} as const;

const positioning = [
  'Distribute from Git',
  'Update without recopying',
  'User and project scopes',
  'Manifest-safe cleanup',
];

const repoLayouts = `Single skill repo:
my-skill/
  SKILL.md

Collection repo:
company-skills/
  skills/
    git/
      SKILL.md
    db/
      SKILL.md

Flat collection:
company-skills/
  git/
    SKILL.md
  db/
    SKILL.md`;

function PositioningStrip() {
  return (
    <section className="px-5 sm:px-6 lg:px-8" aria-label="SkillHost positioning">
      <div className="mx-auto grid max-w-7xl gap-3 rounded-3xl border border-line bg-white/80 p-3 shadow-card sm:grid-cols-2 lg:grid-cols-4">
        {positioning.map((item) => (
          <div key={item} className="rounded-2xl border border-sky-100 bg-skywash/70 px-5 py-4 text-center text-sm font-semibold text-primary-strong">
            {item}
          </div>
        ))}
      </div>
    </section>
  );
}

function RepoLayoutSection() {
  return (
    <section className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="repo-layout-title">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Repository layout</p>
          <h2 id="repo-layout-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
            One skill or many skills.
          </h2>
          <p className="mt-5 leading-8 text-muted">
            One repo can hold one skill or a collection. SkillHost discovers every SKILL.md.
          </p>
        </div>
        <CodeBlock title="supported layouts" code={repoLayouts} />
      </div>
    </section>
  );
}

export default function App() {
  return (
    <div className="min-h-screen overflow-hidden bg-canvas text-ink">
      <Header githubUrl={LINKS.GITHUB_URL} />
      <main>
        <Hero githubUrl={LINKS.GITHUB_URL} />
        <PositioningStrip />
        <ProblemSolutionBento />
        <FeatureGrid />
        <Workflow />
        <AgentSupport />
        <RepoLayoutSection />
        <SecuritySection />
        <InstallSection githubUrl={LINKS.GITHUB_URL} pypiUrl={LINKS.PYPI_URL} docsUrl={LINKS.DOCS_URL} />
      </main>
      <Footer githubUrl={LINKS.GITHUB_URL} pypiUrl={LINKS.PYPI_URL} docsUrl={LINKS.DOCS_URL} />
    </div>
  );
}
