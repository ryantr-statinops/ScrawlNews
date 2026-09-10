import ReactMarkdown from "react-markdown";
import rehypeSanitize from "rehype-sanitize";
import remarkGfm from "remark-gfm";

export function MarkdownContent({ content }: { content: string }) {
  return <ReactMarkdown remarkPlugins={[remarkGfm]} rehypePlugins={[rehypeSanitize]} components={{
    a: ({ node: _node, ...props }) => <a {...props} target="_blank" rel="noreferrer noopener" />,
  }}>{content}</ReactMarkdown>;
}
