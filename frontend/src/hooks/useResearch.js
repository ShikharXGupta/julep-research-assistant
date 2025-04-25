import { useState } from 'react';

// Change this to your deployed API URL when deploying to production
const API_URL = process.env.NODE_ENV === 'production'
    ? 'https://your-vercel-deployment-url.vercel.app/api'
    : 'http://localhost:8000/api';

const useResearch = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);

    const performResearch = async (topic, format) => {
        try {
            setIsLoading(true);
            setError(null);

            const response = await fetch(`${API_URL}/research`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, format }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get research results');
            }

            if (!data.success) {
                throw new Error(data.error || 'Research operation failed');
            }

            return data.result;
        } catch (err) {
            setError(err.message || 'An error occurred while fetching research results');
            return null;
        } finally {
            setIsLoading(false);
        }
    };

    return { performResearch, isLoading, error };
};

export default useResearch;