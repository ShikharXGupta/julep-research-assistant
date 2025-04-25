import { motion } from 'framer-motion';

const ResultDisplay = ({ result }) => {
  if (!result) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="bg-white p-6 rounded-2xl border border-transparent shadow-lg ring-1 ring-gray-200 overflow-hidden"
    >
      <h2 className="text-2xl font-bold text-violet-700 mb-4">📚 Research Results</h2>
      <div className="prose max-w-none text-gray-800 space-y-3 overflow-y-auto max-h-[400px] scrollbar-thin scrollbar-thumb-violet-400 scrollbar-track-gray-100 pr-2">
        {result.split('\n').map((paragraph, index) => {
          const trimmed = paragraph.trim();
          
          if (trimmed.startsWith('-') || trimmed.startsWith('•')) {
            return (
              <ul key={index} className="list-disc pl-6">
                <li>{trimmed.replace(/^[-•]\s*/, '')}</li>
              </ul>
            );
          }

          return trimmed ? <p key={index}>{trimmed}</p> : null;
        })}
      </div>
    </motion.div>
  );
};

export default ResultDisplay;
