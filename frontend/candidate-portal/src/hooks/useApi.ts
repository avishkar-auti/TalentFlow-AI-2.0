import { useState, useCallback } from 'react';
import api from '../utils/api';
import { AxiosRequestConfig, AxiosError } from 'axios';

export function useApi<T>() {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const request = useCallback(async (
    method: 'get' | 'post' | 'put' | 'delete',
    url: string,
    payload?: any,
    config?: AxiosRequestConfig
  ) => {
    setLoading(true);
    setError(null);
    try {
      const response = await api({
        method,
        url,
        data: payload,
        ...config
      });
      setData(response.data);
      return response.data;
    } catch (err) {
      const e = err as AxiosError<{detail?: string}>;
      const errorMsg = e.response?.data?.detail || e.message || 'An error occurred';
      setError(errorMsg);
      throw e;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, error, loading, request };
}
