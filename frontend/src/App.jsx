import { useState } from 'react';  // Import useState
import Header from './components/Header';
import ResearchForm from './components/ResearchForm';
import ResultDisplay from './components/ResultDisplay';
import LoadingIndicator from './components/LoadingIndicator';
import useResearch from './hooks/useResearch';
import './styles/global.css';

function App() {
  const [result, setResult] = useState(null);
  const { performResearch, isLoading, error } = useResearch();

  const handleSubmit = async (topic, format) => {
    const researchResult = await performResearch(topic, format);
    if (researchResult) {
      setResult(researchResult);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-400 via-blue-500 to-blue-700 text-gray-100 font-sans transition-all duration-300 ease-in-out">
      <div className="container mx-auto px-4 py-10">
        <Header />

        <div className="max-w-4xl mx-auto mt-10 bg-white rounded-3xl shadow-2xl overflow-hidden transform transition hover:scale-[1.01]">
          <div className="p-8">
            <ResearchForm onSubmit={handleSubmit} disabled={isLoading} />

            {isLoading && (
              <div className="mt-8 flex justify-center">
                <LoadingIndicator />
              </div>
            )}

            {error && (
              <div className="mt-8 p-4 bg-red-100 border border-red-300 text-red-800 rounded-lg">
                <p>{error}</p>
              </div>
            )}

            {result && !isLoading && (
              <div className="mt-8">
                <ResultDisplay result={result} />
              </div>
            )}
          </div>
        </div>

        <footer className="mt-12 text-center text-white opacity-90 text-sm">
          <p>Julep AI Research Assistant &copy; {new Date().getFullYear()}</p>
        </footer>
      </div>
    </div>
  );
}

export default App;
