/**
 * Base class for all agents
 * Provides common functionality: message handling, state management, lifecycle
 */

import { getMessageBus } from './message-bus.js';
import { AgentStatus, AgentPacket, Intent } from './types.js';
import EventEmitter from 'events';

export class BaseAgent extends EventEmitter {
  constructor(name, options = {}) {
    super();
    this.name = name;
    this.status = new AgentStatus(name);
    this.messageBus = getMessageBus(options.transport || 'memory');
    this.options = options;
    this.isRunning = false;
    this.messageHandlers = new Map();
    this.setupMessageHandlers();
  }

  /**
   * Initialize the agent
   */
  async initialize() {
    this.status.updateState('initializing', 'Starting up...');
    
    // Subscribe to messages
    this.unsubscribe = this.messageBus.subscribe(
      { recipient: this.name },
      (message) => this.handleMessage(message)
    );
    
    // Also listen to broadcasts
    this.broadcastUnsubscribe = this.messageBus.subscribe(
      { recipient: 'ALL' },
      (message) => this.handleMessage(message)
    );
    
    await this.onInitialize();
    this.status.updateState('idle', 'Ready');
    this.isRunning = true;
    this.emit('initialized');
  }

  /**
   * Override in subclasses for agent-specific initialization
   */
  async onInitialize() {
    // Override in subclasses
  }

  /**
   * Start the agent
   */
  async start() {
    if (!this.isRunning) {
      await this.initialize();
    }
    this.status.updateState('active', 'Running');
    this.emit('started');
  }

  /**
   * Stop the agent
   */
  async stop() {
    this.isRunning = false;
    this.status.updateState('idle', 'Stopped');
    
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    if (this.broadcastUnsubscribe) {
      this.broadcastUnsubscribe();
    }
    
    await this.onStop();
    this.emit('stopped');
  }

  /**
   * Override in subclasses for cleanup
   */
  async onStop() {
    // Override in subclasses
  }

  /**
   * Handle incoming message
   */
  async handleMessage(message) {
    try {
      this.status.lastActivity = new Date();
      this.status.metrics.packetsProcessed++;
      
      const packet = AgentPacket.fromJSON(message);
      
      // Route to specific handler based on intent
      const handler = this.messageHandlers.get(packet.intent);
      if (handler) {
        const startTime = Date.now();
        await handler.call(this, packet);
        const duration = Date.now() - startTime;
        this.updateAvgProcessingTime(duration);
      } else {
        // Default handler
        await this.onMessage(packet);
      }
    } catch (error) {
      this.status.metrics.errors++;
      this.status.updateState('error', `Error: ${error.message}`);
      this.emit('error', error);
      console.error(`[${this.name}] Error handling message:`, error);
    }
  }

  /**
   * Register message handler for specific intent
   */
  onIntent(intent, handler) {
    this.messageHandlers.set(intent, handler);
  }

  /**
   * Override in subclasses for default message handling
   */
  async onMessage(packet) {
    console.log(`[${this.name}] Received message:`, packet.intent);
  }

  /**
   * Send message to another agent
   */
  async send(recipient, intent, content) {
    const packet = new AgentPacket({
      sender: this.name,
      recipient,
      intent,
      content
    });
    
    await this.messageBus.publish(packet);
  }

  /**
   * Broadcast message to all agents
   */
  async broadcast(intent, content) {
    await this.send('ALL', intent, content);
  }

  /**
   * Update agent state
   */
  updateState(state, goal) {
    this.status.updateState(state, goal);
    this.emit('stateChanged', { state, goal });
  }

  /**
   * Update average processing time
   */
  updateAvgProcessingTime(duration) {
    const current = this.status.metrics.avgProcessingTime;
    const count = this.status.metrics.packetsProcessed;
    this.status.metrics.avgProcessingTime = 
      (current * (count - 1) + duration) / count;
  }

  /**
   * Get agent status
   */
  getStatus() {
    return {
      name: this.status.name,
      state: this.status.state,
      goal: this.status.goal,
      lastActivity: this.status.lastActivity,
      metrics: { ...this.status.metrics }
    };
  }

  /**
   * Setup default message handlers
   */
  setupMessageHandlers() {
    this.onIntent(Intent.TASK_START, async (packet) => {
      this.updateState('active', 'Processing task...');
      await this.onTaskStart(packet);
    });

    this.onIntent(Intent.TASK_COMPLETE, async (packet) => {
      this.updateState('completed', 'Task complete');
      await this.onTaskComplete(packet);
      setTimeout(() => {
        this.updateState('idle', 'Standby');
      }, 1000);
    });
  }

  /**
   * Override in subclasses
   */
  async onTaskStart(packet) {
    // Override in subclasses
  }

  async onTaskComplete(packet) {
    // Override in subclasses
  }
}

