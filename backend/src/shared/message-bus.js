/**
 * Message Bus for agent-to-agent communication
 * Supports multiple transport mechanisms: WebSocket, Redis, HTTP
 */

import EventEmitter from 'events';

export class MessageBus extends EventEmitter {
  constructor(transport = 'memory') {
    super();
    this.transport = transport;
    this.subscribers = new Map();
    this.messageQueue = [];
    this.redisClient = null;
    this.wsServer = null;
  }

  /**
   * Initialize transport layer
   */
  async initialize(options = {}) {
    if (this.transport === 'redis') {
      const redis = await import('redis');
      this.redisClient = redis.createClient({
        url: options.redisUrl || process.env.REDIS_URL || 'redis://localhost:6379'
      });
      await this.redisClient.connect();
      
      // Subscribe to agent messages channel
      await this.redisClient.subscribe('agent:messages', (message) => {
        const packet = JSON.parse(message);
        this.emit('message', packet);
      });
    } else if (this.transport === 'websocket') {
      // WebSocket setup would be handled by the coordinator
      this.wsServer = options.wsServer;
    }
    
    // Memory transport is always available
    this.setMaxListeners(100);
  }

  /**
   * Publish a message to the bus
   */
  async publish(packet) {
    const message = packet.toJSON ? packet.toJSON() : packet;
    
    if (this.transport === 'redis') {
      await this.redisClient.publish('agent:messages', JSON.stringify(message));
    } else if (this.transport === 'websocket' && this.wsServer) {
      // Broadcast to all connected WebSocket clients
      this.wsServer.clients.forEach(client => {
        if (client.readyState === 1) { // OPEN
          client.send(JSON.stringify({ type: 'agent:message', data: message }));
        }
      });
    }
    
    // Always emit locally for in-process subscribers
    this.emit('message', message);
    
    // Store in queue for replay/recovery
    this.messageQueue.push(message);
    if (this.messageQueue.length > 1000) {
      this.messageQueue.shift(); // Keep last 1000 messages
    }
  }

  /**
   * Subscribe to messages
   */
  subscribe(filter, callback) {
    const handler = (message) => {
      // Filter messages
      if (filter) {
        if (typeof filter === 'function') {
          if (!filter(message)) return;
        } else if (filter.recipient && message.recipient !== filter.recipient && message.recipient !== 'ALL') {
          return;
        }
        if (filter.sender && message.sender !== filter.sender) return;
        if (filter.intent && message.intent !== filter.intent) return;
      }
      
      callback(message);
    };
    
    this.on('message', handler);
    
    // Return unsubscribe function
    return () => {
      this.off('message', handler);
    };
  }

  /**
   * Send message to specific agent
   */
  async sendToAgent(agentName, packet) {
    packet.recipient = agentName;
    await this.publish(packet);
  }

  /**
   * Broadcast to all agents
   */
  async broadcast(packet) {
    packet.recipient = 'ALL';
    await this.publish(packet);
  }

  /**
   * Get message history
   */
  getHistory(limit = 100) {
    return this.messageQueue.slice(-limit);
  }

  /**
   * Cleanup
   */
  async disconnect() {
    if (this.redisClient) {
      await this.redisClient.quit();
    }
    this.removeAllListeners();
  }
}

// Singleton instance
let messageBusInstance = null;

export function getMessageBus(transport = 'memory') {
  if (!messageBusInstance) {
    messageBusInstance = new MessageBus(transport);
  }
  return messageBusInstance;
}

