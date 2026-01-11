import { Injectable, signal } from '@angular/core';

export interface ProxyConfig {
  endpoint: string;
  apiKey?: string;
  timeout: number;
  retryAttempts: number;
  retryDelay: number;
}

@Injectable({
  providedIn: 'root'
})
export class ConfigService {
  private defaultConfig: ProxyConfig = {
    endpoint: 'http://localhost:3000/api/v1/analyze',
    timeout: 60000, // 60 seconds
    retryAttempts: 3,
    retryDelay: 1000 // 1 second
  };

  public config = signal<ProxyConfig>(this.loadConfig());

  constructor() {
    // Allow runtime configuration updates
    if (typeof window !== 'undefined') {
      const configOverride = (window as any).__PROXY_CONFIG__;
      if (configOverride) {
        this.config.set({ ...this.defaultConfig, ...configOverride });
      }
    }
  }

  private loadConfig(): ProxyConfig {
    // Try to load from environment variables (for build-time config)
    const endpoint = this.getEnvVar('PROXY_API_ENDPOINT') || this.defaultConfig.endpoint;
    const apiKey = this.getEnvVar('PROXY_API_KEY');
    const timeout = parseInt(this.getEnvVar('PROXY_TIMEOUT') || '60000', 10);
    const retryAttempts = parseInt(this.getEnvVar('PROXY_RETRY_ATTEMPTS') || '3', 10);
    const retryDelay = parseInt(this.getEnvVar('PROXY_RETRY_DELAY') || '1000', 10);

    return {
      endpoint,
      apiKey,
      timeout,
      retryAttempts,
      retryDelay
    };
  }

  private getEnvVar(name: string): string | undefined {
    // Check for environment variables in different contexts
    if (typeof process !== 'undefined' && process.env) {
      return process.env[name];
    }
    // Check for global window variables (for browser-based config)
    if (typeof window !== 'undefined') {
      const win = window as any;
      if (win.__ENV__ && win.__ENV__[name]) {
        return win.__ENV__[name];
      }
    }
    return undefined;
  }

  updateConfig(updates: Partial<ProxyConfig>): void {
    this.config.update(current => ({ ...current, ...updates }));
  }

  getEndpoint(): string {
    return this.config().endpoint;
  }

  getApiKey(): string | undefined {
    return this.config().apiKey;
  }
}

