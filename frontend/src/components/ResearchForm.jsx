import { useState } from 'react';  // Import useState

const ResearchForm = ({ onSubmit, disabled }) => {
    const [topic, setTopic] = useState('');
    const [format, setFormat] = useState('');
    const [isOpen, setIsOpen] = useState(false);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (topic.trim()) {
            onSubmit(topic, format);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="research-form">
            <input
                type="text"
                placeholder="Enter topic..."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                disabled={disabled}
            />
            <input
                type="text"
                placeholder="Enter custom format (e.g., summary, bullet points, etc.)"
                value={format}
                onChange={(e) => setFormat(e.target.value)}
                disabled={disabled}
            />
            <button type="submit" disabled={disabled || !topic.trim()}>
                Research
            </button>
        </form>
    );
};

export default ResearchForm;
