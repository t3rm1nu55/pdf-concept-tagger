import { Injectable, signal } from '@angular/core';
import { AgentPacket } from './gemini.service';

export interface LogEntry {
  timestamp: string;
  type: 'SYSTEM' | 'AGENT_MSG' | 'EXPLANATION' | 'ERROR';
  agent?: string;
  message: string;
  rawPacket?: AgentPacket;
}

@Injectable({
  providedIn: 'root'
})
export class LogService {
  // UI Logs (filtered, pretty)
  public uiLogs = signal<LogEntry[]>([]);
  
  // Deep Logs (everything)
  private deepLogs: any[] = [];

  addLog(packet: AgentPacket) {
    const timestamp = new Date().toISOString();
    
    // 1. Add to Deep Log (for download)
    this.deepLogs.push({
      timestamp,
      packet
    });

    // 2. Process for UI Log
    // We filter out high-frequency raw updates to keep the UI readable, 
    // but keep high-value signals.
    let type: LogEntry['type'] = 'AGENT_MSG';
    let message = packet.content.log || '';

    if (packet.sender === 'OBSERVER') {
        type = 'EXPLANATION';
        message = packet.content.log || 'Analysing system state...';
    } else if (packet.sender === 'SYSTEM') {
        type = 'SYSTEM';
    } else if (packet.intent === 'GRAPH_UPDATE') {
        // Summarize graph updates instead of flooding
        if (packet.content.concept) message = `Identified: ${packet.content.concept.term}`;
        else return; // Skip minor relation updates in UI log
    }

    if (message) {
        this.uiLogs.update(logs => [...logs, {
            timestamp,
            type,
            agent: packet.sender,
            message,
            rawPacket: packet
        }]);
    }
  }

  addSystemLog(message: string) {
      this.uiLogs.update(logs => [...logs, {
          timestamp: new Date().toISOString(),
          type: 'SYSTEM',
          agent: 'SYSTEM',
          message
      }]);
      this.deepLogs.push({ timestamp: new Date().toISOString(), source: 'INTERNAL', message });
  }

  downloadFullLog() {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.deepLogs, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", `ontology_engine_full_log_${Date.now()}.json`);
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  }

  clear() {
      this.uiLogs.set([]);
      this.deepLogs = [];
  }
}