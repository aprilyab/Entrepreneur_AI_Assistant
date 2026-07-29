import { ReactNode } from 'react';

function inlineFormat(text: string): ReactNode[] {
  return text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean).map((part, index) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={index} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>;
    }
    return <span key={index}>{part}</span>;
  });
}

export default function FormattedContent({
  content,
  compact = false,
}: {
  content: string;
  compact?: boolean;
}) {
  const lines = content.split('\n');

  return (
    <div className={`rich-content ${compact ? 'text-sm' : ''}`}>
      {lines.map((rawLine, index) => {
        const line = rawLine.trim();
        if (!line) return <div key={index} className="h-3" />;

        if (line.startsWith('### ')) {
          return <h4 key={index}>{inlineFormat(line.slice(4))}</h4>;
        }
        if (line.startsWith('## ')) {
          return <h3 key={index}>{inlineFormat(line.slice(3))}</h3>;
        }
        if (line.startsWith('# ')) {
          return <h2 key={index}>{inlineFormat(line.slice(2))}</h2>;
        }
        if (/^[-*]\s+/.test(line)) {
          return (
            <div key={index} className="rich-list-item">
              <span className="rich-bullet" />
              <p>{inlineFormat(line.replace(/^[-*]\s+/, ''))}</p>
            </div>
          );
        }
        const numbered = line.match(/^(\d+)\.\s+(.+)/);
        if (numbered) {
          return (
            <div key={index} className="rich-list-item">
              <span className="rich-number">{numbered[1]}</span>
              <p>{inlineFormat(numbered[2])}</p>
            </div>
          );
        }

        return <p key={index}>{inlineFormat(line)}</p>;
      })}
    </div>
  );
}
