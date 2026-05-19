import { AgentSupport } from './components/AgentSupport';
import { CodeBlock } from './components/CodeBlock';
import { FeatureGrid } from './components/FeatureGrid';
import { Footer } from './components/Footer';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { InstallSection } from './components/InstallSection';
import { SecuritySection } from './components/SecuritySection';
import { Workflow } from './components/Workflow';

export const LINKS = {
  GITHUB_URL: 'https://github.com/skillhost-dev/skillhost',
  PYPI_URL: 'https://pypi.org/project/skillhost/',
  DOCS_URL: 'https://github.com/skillhost-dev/skillhost#readme',
} as const;

const positioning = [
  'No hosted registry',
  'No agent lock-in',
  'No package resolution',
  'No semver complexity',
  'No skill execution',
  'Manifest-safe unlink',
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
    <section className="px-5 sm:px-6 lg:px-8" aria-label="Skillhost positioning">
      <div className="mx-auto grid max-w-7xl gap-3 rounded-3xl border border-white/10 bg-white/[0.035] p-3 shadow-panel sm:grid-cols-2 lg:grid-cols-3">
        {positioning.map((item) => (
          <div key={item} className="rounded-2xl border border-white/10 bg-black/20 px-5 py-4 text-center text-sm font-medium text-slate-200">
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
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Repository layout</p>
          <h2 id="repo-layout-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
            One skill or many skills.
          </h2>
          <p className="mt-5 leading-8 text-slate-400">
            Skillhost discovers skills by looking for SKILL.md. A repository can be a single skill or a collection of
            skills.
          </p>
        </div>
        <CodeBlock title="supported layouts" code={repoLayouts} />
      </div>
    </section>
  );
}

export default function App() {
  return (
    <div className="min-h-screen overflow-hidden bg-ink text-bright">
      <Header githubUrl={LINKS.GITHUB_URL} />
      <main>
        <Hero githubUrl={LINKS.GITHUB_URL} />
        <PositioningStrip />
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
