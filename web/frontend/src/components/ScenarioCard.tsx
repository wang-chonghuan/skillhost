import { CodeBlock } from './CodeBlock';

type ScenarioCardProps = {
  title: string;
  children: React.ReactNode;
  commands: string;
  afterTitle?: string;
  afterCommands?: string;
  targets?: Array<{ label: string; path: string }>;
  note?: string;
};

export function ScenarioCard({ title, children, commands, afterTitle, afterCommands, targets, note }: ScenarioCardProps) {
  return (
    <section className="max-w-full overflow-hidden rounded-3xl border border-slate-200 bg-white/80 p-6 shadow-sm backdrop-blur dark:border-white/10 dark:bg-white/[0.04] sm:p-8" aria-labelledby={title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}
    >
      <h2 id={title.toLowerCase().replace(/[^a-z0-9]+/g, '-')} className="text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
        {title}
      </h2>
      <div className="mt-4 space-y-4 text-base leading-7 text-slate-800 dark:text-slate-300">{children}</div>
      <CodeBlock className="mt-6" code={commands} />
      {afterTitle && afterCommands ? (
        <>
          <p className="mt-6 text-sm font-semibold text-slate-950 dark:text-white">{afterTitle}</p>
          <CodeBlock className="mt-3" code={afterCommands} />
        </>
      ) : null}
      {targets ? (
        <dl className="mt-6 grid gap-3 text-sm sm:grid-cols-3">
          {targets.map((target) => (
            <div key={target.label} className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-white/10 dark:bg-white/[0.035]">
              <dt className="font-semibold text-slate-950 dark:text-white">{target.label}</dt>
              <dd className="mt-2 break-words font-mono text-slate-800 dark:text-slate-300">{target.path}</dd>
            </div>
          ))}
        </dl>
      ) : null}
      {note ? <p className="mt-6 rounded-2xl border border-cyan-500/20 bg-cyan-500/10 p-4 text-sm leading-6 text-cyan-900 dark:text-cyan-100">{note}</p> : null}
    </section>
  );
}
