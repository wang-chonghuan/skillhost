import { CodeBlock } from './CodeBlock';

const steps = [
  {
    number: '01',
    title: 'Add',
    description: 'Register a Git repository containing one skill or a collection of skills.',
    code: 'skillhost user add git@github.com:your-org/company-skills.git',
  },
  {
    number: '02',
    title: 'Update',
    description: 'Pull the latest changes with fast-forward-only Git updates.',
    code: 'skillhost user update',
  },
  {
    number: '03',
    title: 'Link',
    description: 'Create symlinks into user-level or project-level agent directories.',
    code: 'skillhost user link',
  },
];

const userCommands = `skillhost user add git@github.com:your-org/company-skills.git
skillhost user update
skillhost user link`;

const projectCommands = `cd ~/code/my-project
skillhost project register my-project --git git@github.com:your-org/my-project.git
skillhost project add git@github.com:your-org/my-project-skills.git --project my-project
skillhost project link`;

const removeCommands = `skillhost user unlink
skillhost user remove company-skills

skillhost project unlink
skillhost project remove project-skills --project my-project`;

export function Workflow() {
  return (
    <section id="workflow" className="px-5 py-20 sm:px-6 lg:px-8" aria-labelledby="workflow-title">
      <div className="mx-auto max-w-7xl">
        <div className="grid gap-10 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-cyan-200/80">Workflow</p>
            <h2 id="workflow-title" className="mt-4 text-3xl font-semibold tracking-tight text-white sm:text-4xl">
              Add, update, link.
            </h2>
            <p className="mt-5 max-w-xl leading-8 text-slate-400">
              Skillhost keeps distribution in Git and installation in each agent’s native skill directory. Project
              scopes make repository-local skills explicit without changing the agent workflow.
            </p>
            <div className="mt-8 grid gap-4">
              {steps.map((step) => (
                <article key={step.number} className="rounded-2xl border border-white/10 bg-white/[0.035] p-5">
                  <div className="flex items-start gap-4">
                    <span className="rounded-full border border-cyan-300/20 bg-cyan-300/10 px-3 py-1 font-mono text-xs text-cyan-100">
                      {step.number}
                    </span>
                    <div>
                      <h3 className="font-semibold text-white">{step.title}</h3>
                      <p className="mt-1 text-sm leading-6 text-slate-400">{step.description}</p>
                      <code className="mt-3 block overflow-x-auto rounded-xl bg-black/35 px-3 py-2 font-mono text-xs text-slate-300">
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
