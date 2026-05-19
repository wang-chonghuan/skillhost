import { CodeBlock } from './CodeBlock';

const steps = [
  {
    number: '01',
    title: 'Add a Git repo',
    description: 'Register a repository containing one skill or a collection of skills.',
    code: 'skillhost add git@github.com:your-org/company-skills.git',
  },
  {
    number: '02',
    title: 'Discover SKILL.md files',
    description: 'SkillHost finds every valid skill layout automatically.',
    code: 'skillhost list',
  },
  {
    number: '03',
    title: 'Link native directories',
    description: 'Create symlinks into user-level or project-level agent directories.',
    code: 'skillhost link',
  },
  {
    number: '04',
    title: 'Pull updates and relink',
    description: 'Update from Git and refresh links instead of copying folders again.',
    code: 'skillhost update && skillhost link',
  },
  {
    number: '05',
    title: 'Unlink safely',
    description: 'Remove only manifest-tracked links when skills are no longer needed.',
    code: 'skillhost unlink',
  },
];

const userCommands = `skillhost add git@github.com:your-org/company-skills.git
skillhost update
skillhost link`;

const projectCommands = `cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link`;

const removeCommands = `skillhost unlink
skillhost remove company-skills

skillhost project unlink
skillhost project remove project-skills --project my-project`;

export function Workflow() {
  return (
    <section id="workflow" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="workflow-title">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-primary-strong">Workflow</p>
            <h2 id="workflow-title" className="mt-4 font-display text-3xl font-semibold tracking-tight text-ink sm:text-4xl">
              Add, link, update.
            </h2>
            <p className="mt-5 max-w-xl leading-8 text-muted">
              A tiny CLI flow for shared skills across agents.
            </p>
            <div className="mt-8 grid gap-4">
              {steps.map((step) => (
                <article key={step.number} className="rounded-2xl border border-line bg-white/86 p-5 shadow-sm">
                  <div className="flex items-start gap-4">
                    <span className="rounded-full border border-sky-200 bg-skywash px-3 py-1 font-mono text-xs font-semibold text-primary-strong">
                      {step.number}
                    </span>
                    <div>
                      <h3 className="font-display font-semibold text-ink">{step.title}</h3>
                      <p className="mt-1 text-sm leading-6 text-muted">{step.description}</p>
                      <code className="mt-3 block overflow-x-auto rounded-xl bg-slate-50 px-3 py-2 font-mono text-xs text-slate-700">
                        {step.code}
                      </code>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
          <div className="grid gap-4">
            <CodeBlock title="user-level skills" code={userCommands} />
            <CodeBlock title="project-level skills" code={projectCommands} />
            <CodeBlock title="unlink and remove" code={removeCommands} />
          </div>
        </div>
      </div>
    </section>
  );
}
