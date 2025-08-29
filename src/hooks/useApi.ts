import { useState, useEffect, useCallback } from 'react';
import { AsyncState } from '@/types/api';

/**
 * Generic hook for API calls with loading states
 */
export function useApi<T>(
  apiCall: () => Promise<T>,
  dependencies: any[] = []
): AsyncState<T> & { refetch: () => Promise<void> } {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    isLoading: true,
    error: null,
  });

  const fetchData = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const data = await apiCall();
      setState({ data, isLoading: false, error: null });
    } catch (error) {
      setState({
        data: null,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Unknown error occurred',
      });
    }
  }, dependencies);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    ...state,
    refetch: fetchData,
  };
}

/**
 * Hook for API mutations (POST, PUT, DELETE)
 */
export function useApiMutation<T, Args extends any[]>(
  mutationFn: (...args: Args) => Promise<T>
): {
  mutate: (...args: Args) => Promise<T>;
  isLoading: boolean;
  error: string | null;
  data: T | null;
  reset: () => void;
} {
  const [state, setState] = useState({
    data: null as T | null,
    isLoading: false,
    error: null as string | null,
  });

  const mutate = useCallback(async (...args: Args): Promise<T> => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const data = await mutationFn(...args);
      setState({ data, isLoading: false, error: null });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setState(prev => ({ ...prev, isLoading: false, error: errorMessage }));
      throw error;
    }
  }, [mutationFn]);

  const reset = useCallback(() => {
    setState({ data: null, isLoading: false, error: null });
  }, []);

  return {
    mutate,
    ...state,
    reset,
  };
}

/**
 * Hook for paginated API calls
 */
export function usePaginatedApi<T>(
  apiCall: (page: number, limit: number) => Promise<{ data: T[]; total: number }>,
  initialPage: number = 1,
  limit: number = 20
) {
  const [page, setPage] = useState(initialPage);
  const [allData, setAllData] = useState<T[]>([]);
  const [hasMore, setHasMore] = useState(true);

  const { data, isLoading, error, refetch } = useApi(
    () => apiCall(page, limit),
    [page, limit]
  );

  useEffect(() => {
    if (data) {
      if (page === 1) {
        setAllData(data.data);
      } else {
        setAllData(prev => [...prev, ...data.data]);
      }
      setHasMore(data.data.length === limit);
    }
  }, [data, page, limit]);

  const loadMore = useCallback(() => {
    if (!isLoading && hasMore) {
      setPage(prev => prev + 1);
    }
  }, [isLoading, hasMore]);

  const refresh = useCallback(() => {
    setPage(1);
    setAllData([]);
    setHasMore(true);
    refetch();
  }, [refetch]);

  return {
    data: allData,
    isLoading,
    error,
    hasMore,
    loadMore,
    refresh,
    page,
  };
}

/**
 * Hook for managing loading states across multiple API calls
 */
export function useLoadingState() {
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});

  const setLoading = useCallback((key: string, loading: boolean) => {
    setLoadingStates(prev => ({ ...prev, [key]: loading }));
  }, []);

  const isLoading = useCallback((key?: string) => {
    if (key) {
      return loadingStates[key] || false;
    }
    return Object.values(loadingStates).some(Boolean);
  }, [loadingStates]);

  return { setLoading, isLoading };
}

/**
 * Hook for managing error states
 */
export function useErrorState() {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const setError = useCallback((key: string, error: string | null) => {
    setErrors(prev => {
      if (error === null) {
        const { [key]: _, ...rest } = prev;
        return rest;
      }
      return { ...prev, [key]: error };
    });
  }, []);

  const clearError = useCallback((key: string) => {
    setErrors(prev => {
      const { [key]: _, ...rest } = prev;
      return rest;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrors({});
  }, []);

  const getError = useCallback((key: string) => {
    return errors[key] || null;
  }, [errors]);

  const hasError = useCallback((key?: string) => {
    if (key) {
      return Boolean(errors[key]);
    }
    return Object.keys(errors).length > 0;
  }, [errors]);

  return {
    setError,
    clearError,
    clearAllErrors,
    getError,
    hasError,
    errors,
  };
}