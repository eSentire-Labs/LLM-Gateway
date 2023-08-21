import React, { forwardRef } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { materialDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

import { CopyToClipboard } from 'react-copy-to-clipboard';
import { FaCopy } from 'react-icons/fa';


const CodeBlock = ({ code, language }) => {
    const [copyButtonText, setCopyButtonText] = React.useState('Copy code');

    const handleCopy = () => {
        setCopyButtonText('Copied!');
        setTimeout(() => {
            setCopyButtonText('Copy code');
        }, 1000);
    };

    return (
        <div className="relative">
            <SyntaxHighlighter
                showLineNumbers
                useInlineStyles
                language={language || 'javascript'}
                style={materialDark}>
                {code}
            </SyntaxHighlighter>
            <div className="absolute top-0 right-0 mt-2 mr-2">
                <CopyToClipboard text={code} onCopy={handleCopy}>
                    <button className="text-gray-400">
                        <FaCopy className='inline mr-2' />{copyButtonText}
                    </button>
                </CopyToClipboard>
            </div>
        </div>
    );
};

export default forwardRef(({ role, content }, ref) => {
    if (!content || content.trim() === '') return null; // Check for empty content and return null if empty

    const regex = /```(\w+)?\s?([\s\S]*?)```/gm;
    let index = 0;
    let match;
    let parts = [];

    while ((match = regex.exec(content)) !== null) {
        const [wholeMatch, language, code] = match;
        const start = match.index;
        const end = start + wholeMatch.length;
        if (start !== index) {
            parts.push({ type: 'text', content: content.slice(index, start) });
        }
        parts.push({ type: 'code', content: code, language });
        index = end;
    }
    if (index !== content.length) {
        parts.push({ type: 'text', content: content.slice(index) });
    }

    return (
        <div ref={ref}
            className={`w-full mx-auto max-w-screen-lg p-2 mb-2 rounded-lg 
            ${role === 'user' ? 'bg-slate-700' : 'bg-gray-500'
                }`}
        >
            {parts.map((part, index) => {
                if (part.type === 'text') {
                    return <p key={index} className="mb-0 whitespace-pre-wrap">{part.content}</p>;
                } else {
                    return <CodeBlock key={index} code={part.content} language={part.language} />;
                }
            })}
        </div>
    );
});
