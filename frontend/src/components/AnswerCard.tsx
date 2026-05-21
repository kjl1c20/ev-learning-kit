import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { AskResponse } from "@/lib/api";

export default function AnswerCard({ result }: { result: AskResponse }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          h1: ({ children }) => <h1 className="mt-4 mb-2 text-xl font-semibold text-gray-900 first:mt-0">{children}</h1>,
          h2: ({ children }) => <h2 className="mt-4 mb-2 text-lg font-semibold text-gray-900 first:mt-0">{children}</h2>,
          h3: ({ children }) => <h3 className="mt-3 mb-1.5 text-base font-semibold text-gray-900 first:mt-0">{children}</h3>,
          p: ({ children }) => <p className="mb-3 text-sm leading-relaxed text-gray-800 last:mb-0">{children}</p>,
          ul: ({ children }) => <ul className="mb-3 list-disc space-y-1 pl-5 text-sm text-gray-800 last:mb-0">{children}</ul>,
          ol: ({ children }) => <ol className="mb-3 list-decimal space-y-1 pl-5 text-sm text-gray-800 last:mb-0">{children}</ol>,
          li: ({ children }) => <li className="leading-relaxed">{children}</li>,
          strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          code: ({ children }) => (
            <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-mono text-gray-800">{children}</code>
          ),
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {children}
            </a>
          ),
        }}
      >
        {result.answer}
      </ReactMarkdown>
    </div>
  );
}
