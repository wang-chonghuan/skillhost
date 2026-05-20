type CodeBlockProps = {
  code: string;
  title?: string;
  className?: string;
};

export function CodeBlock({ code, title, className = '' }: CodeBlockProps) {
  return (
    <figure className={`overflow-hidden rounded-2xl border border-slate-200/80 bg-slate-950 shadow-sm dark:border-white/10 dark:bg-black/55 ${className}`}>
      {title ? (
        <figcaption className="flex items-center justify-between border-b border-white/10 bg-slate-900 px-4 py-3 text-xs font-medium text-slate-400">
          <span>{title}</span>
          <span className="flex gap-1.5" aria-hidden="true">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
            <span className="h-2.5 w-2.5 rounded-full bg-emerald-400" />
          </span>
        </figcaption>
      ) : null}
      <pre className="overflow-x-auto p-5 text-left font-mono text-sm leading-7 text-slate-100">
        <code>{code}</code>
      </pre>
    </figure>
  );
}
