import { Injectable, signal, inject } from '@angular/core';
import { GoogleGenAI, Type, Schema } from '@google/genai';
import { Observable } from 'rxjs';
import { LogService } from './log.service';
import { ConfigService } from './config.service';

export interface AgentPacket {
  sender: 'SYSTEM' | 'HARVESTER' | 'ARCHITECT' | 'CRITIC' | 'ORCHESTRATOR' | 'OBSERVER';
  recipient: string;
  intent: 'INFO' | 'TASK_START' | 'TASK_COMPLETE' | 'CRITIQUE' | 'GRAPH_UPDATE' | 'ROUND_START' | 'HYPOTHESIS' | 'TOOL_USE' | 'EXPLAIN';
  content: {
    log?: string;
    round_id?: number;
    round_name?: string;
    
    // Standard Node
    concept?: {
      id: string;
      term: string;
      type: 'concept' | 'hypernode';
      dataType?: 'entity' | 'date' | 'location' | 'organization' | 'person' | 'money' | 'legal' | 'condition';
      category: string;
      explanation: string;
      confidence: number;
      boundingBox?: number[];
      ui_group?: string; 
    };
    
    // Ontology Hub
    domain?: {
        id: string;
        name: string;
        description: string;
        sensitivity: 'LOW' | 'MEDIUM' | 'HIGH';
    };

    // Hierarchical Link
    taxonomy?: {
        parent: string;
        child: string;
        type: 'is_a' | 'part_of';
    };

    // Axiom/Context
    prior?: {
        id: string;
        axiom: string;
        weight: number;
    };

    relationship?: {
      source: string;
      target: string;
      predicate: string;
      type: 'structural' | 'semantic' | 'hyperlink';
    };
    hypothesis?: {
      id: string;
      target_concept_id: string;
      claim: string;
      evidence: string;
      status: 'PROPOSED' | 'ACCEPTED' | 'REJECTED';
    };
    optimization?: {
      score: number;
      suggestion: string;
      focus_nodes: string[];
    };
  };
}

const AgentProtocolSchema: Schema = {
  type: Type.ARRAY,
  items: {
    type: Type.OBJECT,
    properties: {
      sender: { 
        type: Type.STRING, 
        enum: ['SYSTEM', 'HARVESTER', 'ARCHITECT', 'CRITIC', 'ORCHESTRATOR', 'OBSERVER'] 
      },
      recipient: { type: Type.STRING },
      intent: { 
        type: Type.STRING, 
        enum: ['INFO', 'TASK_START', 'TASK_COMPLETE', 'CRITIQUE', 'GRAPH_UPDATE', 'ROUND_START', 'HYPOTHESIS', 'TOOL_USE', 'EXPLAIN'] 
      },
      content: {
        type: Type.OBJECT,
        properties: {
          log: { type: Type.STRING },
          round_id: { type: Type.INTEGER },
          round_name: { type: Type.STRING },
          
          concept: {
            type: Type.OBJECT,
            properties: {
               id: { type: Type.STRING },
               term: { type: Type.STRING },
               type: { type: Type.STRING, enum: ['concept', 'hypernode'] },
               dataType: { 
                   type: Type.STRING, 
                   enum: ['entity', 'date', 'location', 'organization', 'person', 'money', 'legal', 'condition'] 
               },
               category: { type: Type.STRING },
               explanation: { type: Type.STRING },
               confidence: { type: Type.NUMBER },
               boundingBox: { type: Type.ARRAY, items: { type: Type.NUMBER } },
               ui_group: { type: Type.STRING }
            },
            required: ['id', 'term', 'type', 'ui_group']
          },

          domain: {
             type: Type.OBJECT,
             properties: {
                 id: { type: Type.STRING },
                 name: { type: Type.STRING },
                 description: { type: Type.STRING },
                 sensitivity: { type: Type.STRING, enum: ['LOW', 'MEDIUM', 'HIGH'] }
             },
             required: ['id', 'name']
          },

          taxonomy: {
              type: Type.OBJECT,
              properties: {
                  parent: { type: Type.STRING },
                  child: { type: Type.STRING },
                  type: { type: Type.STRING, enum: ['is_a', 'part_of'] }
              },
              required: ['parent', 'child', 'type']
          },

          prior: {
              type: Type.OBJECT,
              properties: {
                  id: { type: Type.STRING },
                  axiom: { type: Type.STRING },
                  weight: { type: Type.NUMBER }
              },
              required: ['id', 'axiom']
          },
          
          relationship: {
             type: Type.OBJECT,
             properties: {
                source: { type: Type.STRING },
                target: { type: Type.STRING },
                predicate: { type: Type.STRING },
                type: { type: Type.STRING, enum: ['structural', 'semantic', 'hyperlink'] }
             },
             required: ['source', 'target', 'predicate']
          },
          
          hypothesis: {
            type: Type.OBJECT,
            properties: {
              id: { type: Type.STRING },
              target_concept_id: { type: Type.STRING },
              claim: { type: Type.STRING },
              evidence: { type: Type.STRING },
              status: { type: Type.STRING, enum: ['PROPOSED', 'ACCEPTED', 'REJECTED'] },
              alternative_to: { type: Type.STRING }
            },
            required: ['id', 'claim', 'status', 'evidence']
          },

          optimization: {
             type: Type.OBJECT,
             properties: {
               score: { type: Type.NUMBER },
               suggestion: { type: Type.STRING },
               focus_nodes: { type: Type.ARRAY, items: { type: Type.STRING } }
             }
          }
        }
      }
    },
    required: ['sender', 'intent', 'content']
  }
};

@Injectable({
  providedIn: 'root',
})
export class GeminiService {
  private ai: GoogleGenAI | null = null;
  public isInitialized = signal(false);
  private logService = inject(LogService);
  private configService = inject(ConfigService);
  private useProxy = signal(true); // Default to proxy, fallback to direct API

  constructor() {
    // Check if we should use proxy or direct API
    const useProxy = this.configService.getEndpoint() !== 'direct';
    
    if (useProxy) {
      // Using proxy - no need for direct API initialization
      this.useProxy.set(true);
      this.isInitialized.set(true);
    } else {
      // Fallback to direct API (for backward compatibility)
      const apiKey = (typeof process !== 'undefined' && process.env) ? process.env.API_KEY : undefined;
      if (apiKey) {
        this.ai = new GoogleGenAI({ apiKey: apiKey });
        this.isInitialized.set(true);
        this.useProxy.set(false);
      } else {
        console.error('API_KEY environment variable not found and proxy not configured.');
      }
    }
  }

  analyzePageStream(imageBase64: string, pageNumber: number, excludeTerms: string[] = []): Observable<AgentPacket> {
    if (this.useProxy()) {
      return this.analyzePageStreamViaProxy(imageBase64, pageNumber, excludeTerms);
    } else {
      return this.analyzePageStreamDirect(imageBase64, pageNumber, excludeTerms);
    }
  }

  private analyzePageStreamViaProxy(imageBase64: string, pageNumber: number, excludeTerms: string[] = []): Observable<AgentPacket> {
    return new Observable(observer => {
      const config = this.configService.config();
      const isContinuation = excludeTerms.length > 0;
      const termsList = excludeTerms.join(', ');

      const prompt = this.buildPrompt(pageNumber, isContinuation, termsList);

      const requestBody = {
        image: imageBase64.split(',')[1], // Remove data:image/png;base64, prefix
        pageNumber,
        excludeTerms,
        prompt,
        model: 'gemini-2.5-flash',
        schema: AgentProtocolSchema
      };

      (async () => {
        let retryCount = 0;
        const maxRetries = config.retryAttempts;

        while (retryCount <= maxRetries) {
          try {
            const headers: Record<string, string> = {
              'Content-Type': 'application/json'
            };

            if (config.apiKey) {
              headers['Authorization'] = `Bearer ${config.apiKey}`;
            }

            const response = await fetch(config.endpoint, {
              method: 'POST',
              headers,
              body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
              const errorText = await response.text();
              throw new Error(`Proxy API error: ${response.status} ${errorText}`);
            }

            // Handle streaming response
            if (!response.body) {
              throw new Error('No response body');
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';
            let arrayStarted = false;

            while (true) {
              const { done, value } = await reader.read();
              
              if (done) break;

              const chunk = decoder.decode(value, { stream: true });
              buffer += chunk;

              // Process complete JSON objects from buffer
              if (!arrayStarted) {
                const startIdx = buffer.indexOf('[');
                if (startIdx >= 0) {
                  buffer = buffer.slice(startIdx + 1);
                  arrayStarted = true;
                } else {
                  continue;
                }
              }

              while (true) {
                const { extracted, remaining } = this.extractNextJsonObject(buffer);
                if (extracted) {
                  try {
                    const packet = JSON.parse(extracted) as AgentPacket;
                    
                    // Safety Check
                    if (packet.content.concept && !packet.content.concept.ui_group) {
                      packet.content.concept.ui_group = 'General';
                    }
                    
                    this.logService.addLog(packet);
                    observer.next(packet);
                  } catch (e) {
                    console.warn('JSON Parse Error:', extracted);
                  }
                  buffer = remaining;
                } else {
                  break;
                }
              }
            }

            observer.complete();
            return; // Success, exit retry loop

          } catch (error) {
            retryCount++;
            console.error(`Proxy request failed (attempt ${retryCount}/${maxRetries + 1}):`, error);

            if (retryCount > maxRetries) {
              observer.error(error);
              return;
            }

            // Exponential backoff
            await new Promise(resolve => 
              setTimeout(resolve, config.retryDelay * Math.pow(2, retryCount - 1))
            );
          }
        }
      })();
    });
  }

  private analyzePageStreamDirect(imageBase64: string, pageNumber: number, excludeTerms: string[] = []): Observable<AgentPacket> {
    return new Observable(observer => {
      if (!this.ai) {
        observer.error('Gemini AI client is not initialized.');
        return;
      }

      const imagePart = {
        inlineData: {
          mimeType: 'image/png',
          data: imageBase64.split(',')[1],
        },
      };

      const isContinuation = excludeTerms.length > 0;
      const termsList = excludeTerms.join(', ');
      const prompt = this.buildPrompt(pageNumber, isContinuation, termsList);

      (async () => {
        try {
          const result = await this.ai!.models.generateContentStream({
            model: 'gemini-2.5-flash',
            contents: { parts: [imagePart, { text: prompt }] },
            config: {
              responseMimeType: 'application/json',
              responseSchema: AgentProtocolSchema,
              maxOutputTokens: 8192
            }
          });

          let buffer = '';
          let arrayStarted = false;

          for await (const chunk of result) {
            const text = chunk.text || ''; 
            buffer += text;
            
            if (!arrayStarted) {
                const startIdx = buffer.indexOf('[');
                if (startIdx >= 0) {
                    buffer = buffer.slice(startIdx + 1);
                    arrayStarted = true;
                } else {
                    continue;
                }
            }

            while (true) {
                const { extracted, remaining } = this.extractNextJsonObject(buffer);
                if (extracted) {
                    try {
                        const packet = JSON.parse(extracted) as AgentPacket;
                        
                        // Safety Check
                        if (packet.content.concept && !packet.content.concept.ui_group) {
                            packet.content.concept.ui_group = 'General';
                        }
                        
                        this.logService.addLog(packet);
                        observer.next(packet);
                    } catch (e) {
                        console.warn('JSON Parse Error:', extracted);
                    }
                    buffer = remaining;
                } else {
                    break;
                }
            }
          }
          
          observer.complete();

        } catch (error) {
          console.error('Stream error:', error);
          observer.error(error);
        }
      })();
    });
  }

  private buildPrompt(pageNumber: number, isContinuation: boolean, termsList: string): string {
    return `
      You are the **Ontology Engine (v6.1)**. Your task is to extract a Deep Knowledge Graph.

      **AGENTS & RESPONSIBILITIES:**
      - **ARCHITECT**: Defines 'domains' (Hub nodes like 'Legal', 'Financial', 'Spatial').
      - **HARVESTER**: Extracts 'concepts' (Leaf nodes).
      - **CURATOR**: Defines 'taxonomies' (Hierarchical 'is_a' or 'part_of' links between concepts).
      - **SYSTEM**: Defines 'priors' (Axioms or rules derived from the text).

      **EXECUTION MODE:** ${isContinuation ? 'CONTINUATION (Phase 2+)' : 'INITIALIZATION (Phase 1)'}
      
      ${isContinuation ? `
      **EXCLUSION LIST:** Ignore these previously found concepts:
      [ ${termsList.slice(0, 5000)}... ]
      ` : ''}

      **PROTOCOL STEPS:**
      1. **CONTEXT**: The System MUST extract 2-3 'priors' (axioms) that define the rules of this document.
      2. **DOMAINS**: The Architect MUST identify 2-3 broad domains relevant to the page.
      3. **CONCEPTS**: The Harvester finds entities.
      4. **HIERARCHY**: The Curator links concepts to domains or other concepts using 'taxonomy' packets.
      5. **RELATIONS**: The Architect links concepts using semantic 'relationship' packets.
      6. **FINISH**: Emit 'TASK_COMPLETE' when exhausted.

      **STRICT JSON RULES:**
      - Output a single JSON Array \`[\`.
      - **CONCISE LOGS**: Minimal log messages.
      
      **EXAMPLE PACKET SEQUENCE:**
      [
        { "sender": "SYSTEM", "intent": "GRAPH_UPDATE", "content": { "prior": { "id": "ax_1", "axiom": "All data centers must comply with GDPR", "weight": 0.9 } } },
        { "sender": "ARCHITECT", "intent": "GRAPH_UPDATE", "content": { "domain": { "id": "dom_legal", "name": "Legal Framework", "description": "Laws and regulations", "sensitivity": "HIGH" } } },
        { "sender": "HARVESTER", "intent": "GRAPH_UPDATE", "content": { "concept": { "id": "c1", "term": "GDPR", "type": "concept", "dataType": "legal", "ui_group": "Regulations" } } },
        { "sender": "CURATOR", "intent": "GRAPH_UPDATE", "content": { "taxonomy": { "parent": "dom_legal", "child": "c1", "type": "is_a" } } }
      ]
      
      **CONTEXT:** Analyzing Page ${pageNumber}.
      `;
  }

  private extractNextJsonObject(buffer: string): { extracted: string | null, remaining: string } {
      buffer = buffer.trimStart();
      if (!buffer.startsWith('{')) {
           if (buffer.startsWith(',')) buffer = buffer.slice(1).trimStart();
           if (!buffer.startsWith('{')) return { extracted: null, remaining: buffer };
      }

      let depth = 0;
      let inString = false;
      let escape = false;

      for (let i = 0; i < buffer.length; i++) {
          const char = buffer[i];
          if (escape) { escape = false; continue; }
          if (char === '\\') { escape = true; continue; }
          if (char === '"') { inString = !inString; continue; }

          if (!inString) {
              if (char === '{') depth++;
              else if (char === '}') {
                  depth--;
                  if (depth === 0) return { extracted: buffer.slice(0, i + 1), remaining: buffer.slice(i + 1) };
              }
          }
      }
      return { extracted: null, remaining: buffer };
  }
}