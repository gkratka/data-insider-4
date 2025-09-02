/**
 * Mock version of useApi hook that doesn't make real API calls
 */
import { useState, useEffect } from 'react';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(apiCall: () => Promise<T>): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refetch = () => {
    // For now, just provide mock data instead of making real API calls
    console.log('useApi (mock): Skipping API call in development mode');
    setData(null);
    setLoading(false);
    setError(null);
  };

  useEffect(() => {
    refetch();
  }, []);

  return { data, loading, error, refetch };
}