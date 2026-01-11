/**
 * Shared types and interfaces for agent communication
 */

export const AgentType = {
  HARVESTER: 'HARVESTER',
  ARCHITECT: 'ARCHITECT',
  CURATOR: 'CURATOR',
  CRITIC: 'CRITIC',
  OBSERVER: 'OBSERVER',
  ORCHESTRATOR: 'ORCHESTRATOR',
  SYSTEM: 'SYSTEM'
};

export const Intent = {
  INFO: 'INFO',
  TASK_START: 'TASK_START',
  TASK_COMPLETE: 'TASK_COMPLETE',
  CRITIQUE: 'CRITIQUE',
  GRAPH_UPDATE: 'GRAPH_UPDATE',
  ROUND_START: 'ROUND_START',
  HYPOTHESIS: 'HYPOTHESIS',
  TOOL_USE: 'TOOL_USE',
  EXPLAIN: 'EXPLAIN'
};

/**
 * AgentPacket - Standard message format for agent communication
 */
export class AgentPacket {
  constructor({
    sender,
    recipient = 'ALL',
    intent,
    content = {},
    timestamp = new Date().toISOString(),
    correlationId = null
  }) {
    this.sender = sender;
    this.recipient = recipient;
    this.intent = intent;
    this.content = content;
    this.timestamp = timestamp;
    this.correlationId = correlationId || `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  static fromJSON(json) {
    return new AgentPacket(json);
  }

  toJSON() {
    return {
      sender: this.sender,
      recipient: this.recipient,
      intent: this.intent,
      content: this.content,
      timestamp: this.timestamp,
      correlationId: this.correlationId
    };
  }
}

/**
 * Agent Status
 */
export class AgentStatus {
  constructor(name) {
    this.name = name;
    this.state = 'idle'; // idle, initializing, active, waiting, completed, error
    this.goal = 'Standby';
    this.lastActivity = null;
    this.metrics = {
      packetsProcessed: 0,
      errors: 0,
      avgProcessingTime: 0
    };
  }

  updateState(state, goal) {
    this.state = state;
    this.goal = goal;
    this.lastActivity = new Date();
  }
}

/**
 * Task definition
 */
export class AgentTask {
  constructor({
    id = null,
    agent,
    type,
    priority = 'medium',
    payload = {},
    createdAt = new Date()
  }) {
    this.id = id || `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.agent = agent;
    this.type = type;
    this.priority = priority;
    this.payload = payload;
    this.createdAt = createdAt;
    this.status = 'pending'; // pending, in_progress, completed, failed
    this.completedAt = null;
  }
}

