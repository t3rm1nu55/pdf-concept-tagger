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
  
  private coordinatorUrl = signal<string>('http://localhost:8000');
  private wsUrl = signal<string>('ws://localhost:8000');
  private wsConnection: WebSocket | null = null;
  private wsMessageSubject = new Observable<AgentPacket>(observer => {
    // Will be set up when WebSocket connects
  });

  constructor() {
    // Load coordinator URL from config
    const backendUrl = this.getEnvVar('BACKEND_API_URL') || 'http://localhost:8000';
    const backendWs = this.getEnvVar('BACKEND_WS_URL') || 'ws://localhost:8000';
    
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
   * Note: WebSocket connections are established per-document in the analyze endpoint.
   * This method is kept for backward compatibility but WebSocket updates come via
   * the streaming response from analyzePageStream.
   */
  private connectWebSocket(): void {
    // MVP: WebSocket is handled per-document in analyzePageStream
    // Global connection not needed - updates come via streaming response
    console.log('[BackendAPI] WebSocket will be connected per-document during analysis');
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

