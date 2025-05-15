import { getCsrfToken } from '../api';

/**
 * Authentication and CSRF helper utility.
 * Centralizes authentication and CSRF-related functions.
 */

/**
 * Ensures a valid CSRF token exists before performing protected operations
 * @returns A promise that resolves when a CSRF token is available
 */
export const ensureCsrfToken = async (): Promise<void> => {
  try {
    await getCsrfToken();
  } catch (error) {
    console.error('Failed to fetch CSRF token:', error);
    throw new Error('无法获取CSRF令牌，请刷新页面');
  }
};

/**
 * Wrapper function to ensure CSRF token is present before executing a function
 * @param fn The function to wrap with CSRF token handling
 * @returns A function that ensures CSRF token before executing the original function
 */
export const withCsrf = <T extends (...args: any[]) => Promise<any>>(fn: T): T => {
  return (async (...args: Parameters<T>): Promise<ReturnType<T>> => {
    await ensureCsrfToken();
    return fn(...args) as ReturnType<T>;
  }) as T;
};

/**
 * Initializes the authentication state by fetching a CSRF token
 */
export const initAuth = async (): Promise<void> => {
  try {
    await getCsrfToken();
    console.log('Authentication initialized with CSRF token');
  } catch (error) {
    console.error('Failed to initialize authentication:', error);
  }
};

export default {
  ensureCsrfToken,
  withCsrf,
  initAuth
};
