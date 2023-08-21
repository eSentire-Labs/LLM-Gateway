import React, { useEffect, useRef } from 'react';
import { FiSend } from 'react-icons/fi';

export const Chatbar = ({
    rows,
    setRows,
    text,
    setText,
    sendMessage
}) => {
    const textareaRef = useRef(null);
    useEffect(() => {
        if (rows > 6 && textareaRef.current) {
            textareaRef.current.scrollTop = textareaRef.current.scrollHeight;
        }
    }, [rows]);

    useEffect(() => {
        if (text === '') {
            setRows(1);
        }
    }, [text, setRows]);

    const insertAtCursor = (textarea, valueToInsert, currentValue) => {
        const startPos = textarea.selectionStart;
        const endPos = textarea.selectionEnd;
        return (
            currentValue.substring(0, startPos) +
            valueToInsert +
            currentValue.substring(endPos, currentValue.length)
        );
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (e.shiftKey) {
                if (rows < 6) {
                    setRows(rows + 1);
                }
                // Insert newline character at the current cursor position
                setText(insertAtCursor(e.target, '\n', text));

            } else {
                sendMessage();
            }
        }
    }

    const handlePaste = (e) => {
        const pastedText = e.clipboardData.getData('text');
        const newLineCount = pastedText.split('\n').length - 1;

        if (newLineCount > 5) {
            setRows(6);
        } else {
            setRows(newLineCount + 1);
        }

    };

    const handleScroll = () => {
        const textarea = textareaRef.current;
        if (textarea.scrollHeight > textarea.clientHeight) {
            // Perform necessary actions when overflow occurs
            if (rows < 6) {
                setRows(rows + 1)
            }
        }
    };


    return (
        <div className="w-full mx-auto max-w-screen-lg bg-gray-200 p-2 rounded flex items-center">
            <textarea
                ref={textareaRef}
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="w-full text-gray-500 resize-none bg-transparent focus:outline-none custom-scrollbar-light"
                placeholder="Type your message..."
                rows={rows}
                onKeyDown={handleKeyPress}
                onPaste={handlePaste}
                onScroll={handleScroll}
            />
            <button
                onClick={sendMessage}
                className="bg-gray-200 text-gray-600 p-2 rounded-r">
                <FiSend />
            </button>
        </div>
    )
}
