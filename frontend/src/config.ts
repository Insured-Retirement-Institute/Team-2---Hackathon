declare global {
  interface Window {
    __APP_CONFIG__?: {
      useMocks?: boolean;
      apiBaseUrl?: string;
    };
  }
}

export const config = {
  get useMocks(): boolean {
    return window.__APP_CONFIG__?.useMocks ?? false;
  },
  get apiBaseUrl(): string {
    return window.__APP_CONFIG__?.apiBaseUrl ?? import.meta.env.VITE_API_BASE_URL ?? "/api";
  },
};
