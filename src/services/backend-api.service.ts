import { Injectable, signal, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AgentPacket } from './gemini.service';
import { ConfigService } from './config.service';
import { LogService } from './log.service';

/**
 * Backend API Service
 * Communicates with the multi-agent backend coordinator
 */
@Injectable({
  providedIn: 'root',
})
export class BackendApiService {
  private configService = inject(ConfigService);
  private logService = inject(LogService);
  public isInitialized = signal(false);
  
  private coordinatorUrl = signal<string>('http://localhost:4000');
  private wsUrl = signal<string>('ws://localhost:4001');
  private wsConnection: WebSocket | null = null;
  private wsMessageSubject = new Observable<AgentPacket>(observer => {
    // Will be set up when WebSocket connects
  });

  constructor() {
    // Load coordinator URL from config
    const backendUrl = this.getEnvVar('BACKEND_API_URL') || 'http://localhost:4000';
    const backendWs = this.getEnvVar('BACKEND_WS_URL') || 'ws://localhost:4001';
    
    this.coordinatorUrl.set(backendUrl);
    this.wsUrl.set(backendWs);
    this.isInitialized.set(true);
    
    // Optionally connect to WebSocket for real-time updates
    this.connectWebSocket();
  }

  private getEnvVar(name: string): string | undefined {
    if (typeof window !== 'undefined') {
      const win = window as any;
      if (win.__ENV__ && win.__ENV__[name]) {
        return win.__ENV__[name];
      }
    }
    return undefined;
  }

  /**
   * Analyze a PDF page using the backend coordinator
   */
  analyzePageStream(imageBase64: string, pageNumber: number, excludeTerms: string[] = []): Observable<AgentPacket> {
    return new Observable(observer => {
      const url = `${this.coordinatorUrl()}/api/v1/analyze`;
      
      const requestBody = {
        image: imageBase64.split(',')[1] || imageBase64,
        pageNumber,
        excludeTerms
      };

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      })
      .then(response => {
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status}`);
        }

        if (!response.body) {
          throw new Error('No response body');
        }

        // Read streaming response
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        const processChunk = (): Promise<void> => {
          return reader.read().then(({ done, value }) => {
            if (done) {
              observer.complete();
              return;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.trim()) {
                try {
                  const packet = JSON.parse(line) as AgentPacket;
                  
                  // Safety check
                  if (packet.content.concept && !packet.content.concept.ui_group) {
                    packet.content.concept.ui_group = 'General';
                  }
                  
                  this.logService.addLog(packet);
                  observer.next(packet);
                } catch (e) {
                  console.warn('JSON Parse Error:', line, e);
                }
              }
            }

            return processChunk();
          });
        };

        return processChunk();
      })
      .catch(error => {
        console.error('Backend API error:', error);
        observer.error(error);
      });
    });
  }

  /**
   * Connect to WebSocket for real-time agent updates
   */
  private connectWebSocket(): void {
    try {
      const ws = new WebSocket(this.wsUrl());
      
      ws.onopen = () => {
        console.log('[BackendAPI] WebSocket connected');
        this.wsConnection = ws;
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'agent:message') {
            const packet = data.data as AgentPacket;
            // Optionally handle real-time updates here
            // The main stream will handle most packets
          }
        } catch (e) {
          console.warn('[BackendAPI] WebSocket message parse error:', e);
        }
      };
      
      ws.onerror = (error) => {
        console.error('[BackendAPI] WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('[BackendAPI] WebSocket disconnected');
        this.wsConnection = null;
        // Reconnect after delay
        setTimeout(() => this.connectWebSocket(), 5000);
      };
    } catch (error) {
      console.warn('[BackendAPI] WebSocket connection failed:', error);
    }
  }

  /**
   * Get agent statuses
   */
  async getAgentStatuses(): Promise<any[]> {
    try {
      const response = await fetch(`${this.coordinatorUrl()}/api/v1/agents`);
      const data = await response.json();
      return data.agents || [];
    } catch (error) {
      console.error('Failed to get agent statuses:', error);
      return [];
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<boolean> {
    try {
      const response = await fetch(`${this.coordinatorUrl()}/health`);
      return response.ok;
    } catch (error) {
      return false;
    }
  }
}

