type CodeBlockProps = {
  code: string;
  title?: string;
  className?: string;
};

export function CodeBlock({ code, title, className = '' }: CodeBlockProps) {
  return (
    <figure
      className={`overflow-hidden rounded-2xl border border-white/10 bg-black/45 shadow-panel backdrop-blur ${className}`}
    >
      {title ? (
        <figcaption className="flex items-center gap-2 border-b border-white/10 px-4 py-3 text-xs font-medium text-slate-400">
          <span className="h-2.5 w-2.5 rounded-full bg-rose-400/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-amber-300/80" />
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-400/80" />
          <span className="ml-2">{title}</span>
        </figcaption>
      ) : null}
      <pre className="overflow-x-auto p-5 text-left font-mono text-sm leading-7 text-slate-200 sm:text-[0.92rem]">
        <code>{code}</code>
      </pre>
    </figure>
  );
}
