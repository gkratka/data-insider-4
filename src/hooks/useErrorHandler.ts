import { useCallback } from 'react';
import { toast } from 'sonner';

export interface ErrorHandlerOptions {
  showToast?: boolean;
  toastMessage?: string;
  logError?: boolean;
  rethrow?: boolean;
}

export const useErrorHandler = () => {
  const handleError = useCallback((
    error: Error | unknown,
    options: ErrorHandlerOptions = {}
  ) => {
    const {
      showToast = true,
      toastMessage,
      logError = true,
      rethrow = false
    } = options;

    // Extract error message
    const errorMessage = error instanceof Error 
      ? error.message 
      : typeof error === 'string' 
        ? error 
        : 'An unexpected error occurred';

    // Log error to monitoring service in production
    if (logError && process.env.NODE_ENV === 'production') {
      // Replace with your error monitoring service
      // e.g., Sentry.captureException(error);
    }

    // Show toast notification
    if (showToast) {
      toast.error(toastMessage || errorMessage);
    }

    // Development logging
    if (process.env.NODE_ENV === 'development') {
      console.error('Error handled by useErrorHandler:', error);
    }

    // Rethrow if requested
    if (rethrow) {
      throw error;
    }
  }, []);

  return { handleError };
};

// Wrapper for async functions
export const useAsyncErrorHandler = () => {
  const { handleError } = useErrorHandler();

  const wrapAsync = useCallback(<T extends any[], R>(
    asyncFn: (...args: T) => Promise<R>,
    options: ErrorHandlerOptions = {}
  ) => {
    return async (...args: T): Promise<R | undefined> => {
      try {
        return await asyncFn(...args);
      } catch (error) {
        handleError(error, options);
        return undefined;
      }
    };
  }, [handleError]);

  return { wrapAsync };
};