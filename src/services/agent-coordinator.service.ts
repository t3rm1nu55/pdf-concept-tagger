import { Injectable, signal, inject } from '@angular/core';
import { Subject, Observable, BehaviorSubject } from 'rxjs';
import { AgentPacket } from './gemini.service';
import { LogService } from './log.service';

export type AgentState = 'idle' | 'initializing' | 'active' | 'waiting' | 'completed' | 'error';

export interface AgentStatus {
  name: string;
  state: AgentState;
  goal: string;
  lastActivity: Date | null;
  metrics: {
    packetsProcessed: number;
    errors: number;
    avgProcessingTime: number;
  };
}

export interface AgentTask {
  id: string;
  agent: string;
  type: 'extract' | 'organize' | 'validate' | 'optimize' | 'observe';
  priority: 'low' | 'medium' | 'high' | 'critical';
  payload: any;
  createdAt: Date;
  completedAt?: Date;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
}

export interface Round {
  id: number;
  name: string;
  startedAt: Date;
  completedAt?: Date;
  tasks: AgentTask[];
  status: 'active' | 'completed' | 'failed';
}

/**
 * Agent Coordinator Service
 * Implements robust agent coordination patterns inspired by:
 * - ADK (Agent Development Kit): Lifecycle management
 * - A2A (Agent-to-Agent): Explicit communication protocols
 * - Microsoft Agent Framework: Task orchestration
 */
@Injectable({
  providedIn: 'root'
})
export class AgentCoordinatorService {
  private logService = inject(LogService);

  // Agent Registry
  private agents = new Map<string, AgentStatus>();
  
  // Message Bus (A2A Pattern)
  private messageBus$ = new Subject<AgentPacket>();
  public messages$ = this.messageBus$.asObservable();
  
  // Task Queue (Priority-based)
  private taskQueue: AgentTask[] = [];
  private activeTasks = new Map<string, AgentTask>();
  
  // Round Management
  private currentRound = signal<Round | null>(null);
  private rounds: Round[] = [];
  
  // State Management
  private agentStates = new Map<string, BehaviorSubject<AgentState>>();
  
  // Metrics
  private systemMetrics = signal({
    totalPackets: 0,
    totalTasks: 0,
    completedTasks: 0,
    failedTasks: 0,
    avgRoundDuration: 0
  });

  constructor() {
    this.initializeAgents();
    this.setupMessageHandling();
  }

  private initializeAgents(): void {
    const agentNames = ['HARVESTER', 'ARCHITECT', 'CURATOR', 'CRITIC', 'OBSERVER', 'ORCHESTRATOR'];
    
    agentNames.forEach(name => {
      const status: AgentStatus = {
        name,
        state: 'idle',
        goal: 'Standby',
        lastActivity: null,
        metrics: {
          packetsProcessed: 0,
          errors: 0,
          avgProcessingTime: 0
        }
      };
      
      this.agents.set(name, status);
      this.agentStates.set(name, new BehaviorSubject<AgentState>('idle'));
    });
  }

  private setupMessageHandling(): void {
    // Subscribe to messages and route them appropriately
    this.messages$.subscribe(packet => {
      this.handlePacket(packet);
    });
  }

  /**
   * Start a new round of agent coordination
   */
  startRound(roundId: number, roundName: string): Round {
    const round: Round = {
      id: roundId,
      name: roundName,
      startedAt: new Date(),
      tasks: [],
      status: 'active'
    };
    
    this.currentRound.set(round);
    this.rounds.push(round);
    
    this.logService.addSystemLog(`Round ${roundId}: ${roundName} started`);
    
    return round;
  }

  /**
   * Complete the current round
   */
  completeRound(): void {
    const round = this.currentRound();
    if (!round) return;
    
    round.completedAt = new Date();
    round.status = 'completed';
    
    const duration = round.completedAt.getTime() - round.startedAt.getTime();
    this.updateMetrics({ avgRoundDuration: duration });
    
    this.logService.addSystemLog(`Round ${round.id} completed in ${(duration / 1000).toFixed(2)}s`);
    
    this.currentRound.set(null);
  }

  /**
   * Submit a task to the agent coordinator
   */
  submitTask(task: Omit<AgentTask, 'id' | 'createdAt' | 'status'>): string {
    const fullTask: AgentTask = {
      ...task,
      id: `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      createdAt: new Date(),
      status: 'pending'
    };
    
    this.taskQueue.push(fullTask);
    this.taskQueue.sort((a, b) => this.getPriorityValue(b.priority) - this.getPriorityValue(a.priority));
    
    const round = this.currentRound();
    if (round) {
      round.tasks.push(fullTask);
    }
    
    this.updateMetrics({ totalTasks: this.systemMetrics().totalTasks + 1 });
    this.processTaskQueue();
    
    return fullTask.id;
  }

  /**
   * Process the task queue (priority-based)
   */
  private processTaskQueue(): void {
    // Process high-priority tasks first
    const availableAgents = Array.from(this.agents.values())
      .filter(a => a.state === 'idle' || a.state === 'waiting');
    
    if (availableAgents.length === 0 || this.taskQueue.length === 0) {
      return;
    }
    
    // Find highest priority task that matches an available agent
    for (const task of this.taskQueue) {
      const agent = availableAgents.find(a => a.name === task.agent);
      if (agent && agent.state === 'idle') {
        this.executeTask(task, agent);
        break;
      }
    }
  }

  /**
   * Execute a task with an agent
   */
  private executeTask(task: AgentTask, agent: AgentStatus): void {
    // Remove from queue
    const index = this.taskQueue.indexOf(task);
    if (index > -1) {
      this.taskQueue.splice(index, 1);
    }
    
    // Mark as active
    task.status = 'in_progress';
    this.activeTasks.set(task.id, task);
    
    // Update agent state
    this.updateAgentState(agent.name, 'active', task.type);
    
    // Simulate task execution (in real implementation, this would trigger actual work)
    // The actual work is done by the GeminiService, this coordinator manages the flow
  }

  /**
   * Complete a task
   */
  completeTask(taskId: string, result?: any): void {
    const task = this.activeTasks.get(taskId);
    if (!task) return;
    
    task.status = 'completed';
    task.completedAt = new Date();
    this.activeTasks.delete(taskId);
    
    const agent = this.agents.get(task.agent);
    if (agent) {
      agent.metrics.packetsProcessed++;
      this.updateAgentState(agent.name, 'idle', 'Standby');
    }
    
    this.updateMetrics({ 
      completedTasks: this.systemMetrics().completedTasks + 1 
    });
    
    // Continue processing queue
    this.processTaskQueue();
  }

  /**
   * Fail a task
   */
  failTask(taskId: string, error: Error): void {
    const task = this.activeTasks.get(taskId);
    if (!task) return;
    
    task.status = 'failed';
    this.activeTasks.delete(taskId);
    
    const agent = this.agents.get(task.agent);
    if (agent) {
      agent.metrics.errors++;
      this.updateAgentState(agent.name, 'error', `Error: ${error.message}`);
      
      // Auto-recover after error
      setTimeout(() => {
        this.updateAgentState(agent.name, 'idle', 'Standby');
      }, 2000);
    }
    
    this.updateMetrics({ 
      failedTasks: this.systemMetrics().failedTasks + 1 
    });
    
    this.logService.addSystemLog(`Task ${taskId} failed: ${error.message}`);
    
    // Continue processing queue
    this.processTaskQueue();
  }

  /**
   * Handle incoming packet (A2A communication)
   */
  private handlePacket(packet: AgentPacket): void {
    this.updateMetrics({ totalPackets: this.systemMetrics().totalPackets + 1 });
    
    const agent = this.agents.get(packet.sender);
    if (agent) {
      agent.lastActivity = new Date();
      agent.metrics.packetsProcessed++;
      
      // Update agent state based on intent
      if (packet.intent === 'TASK_START') {
        this.updateAgentState(packet.sender, 'active', 'Processing...');
      } else if (packet.intent === 'TASK_COMPLETE') {
        this.updateAgentState(packet.sender, 'completed', 'Task Complete');
        setTimeout(() => {
          this.updateAgentState(packet.sender, 'idle', 'Standby');
        }, 1000);
      }
    }
    
    // Route packet to recipient if specified
    if (packet.recipient && packet.recipient !== 'ALL') {
      const recipient = this.agents.get(packet.recipient);
      if (recipient) {
        // Notify recipient agent
        this.notifyAgent(packet.recipient, packet);
      }
    }
  }

  /**
   * Publish a packet to the message bus
   */
  publishPacket(packet: AgentPacket): void {
    this.messageBus$.next(packet);
  }

  /**
   * Update agent state (with state machine validation)
   */
  private updateAgentState(agentName: string, newState: AgentState, goal: string): void {
    const agent = this.agents.get(agentName);
    if (!agent) return;
    
    // State transition validation
    const validTransitions: Record<AgentState, AgentState[]> = {
      'idle': ['initializing', 'active', 'error'],
      'initializing': ['active', 'error'],
      'active': ['waiting', 'completed', 'error', 'idle'],
      'waiting': ['active', 'idle', 'error'],
      'completed': ['idle'],
      'error': ['idle']
    };
    
    const currentState = agent.state;
    const allowedStates = validTransitions[currentState] || [];
    
    if (!allowedStates.includes(newState) && currentState !== newState) {
      console.warn(`Invalid state transition for ${agentName}: ${currentState} -> ${newState}`);
      return;
    }
    
    agent.state = newState;
    agent.goal = goal;
    
    const stateSubject = this.agentStates.get(agentName);
    if (stateSubject) {
      stateSubject.next(newState);
    }
  }

  /**
   * Notify an agent (for A2A communication)
   */
  private notifyAgent(agentName: string, packet: AgentPacket): void {
    const agent = this.agents.get(agentName);
    if (agent && agent.state === 'idle') {
      // Agent can react to the notification
      this.updateAgentState(agentName, 'active', `Received: ${packet.intent}`);
    }
  }

  /**
   * Get agent status
   */
  getAgentStatus(agentName: string): AgentStatus | undefined {
    return this.agents.get(agentName);
  }

  /**
   * Get all agent statuses
   */
  getAllAgentStatuses(): AgentStatus[] {
    return Array.from(this.agents.values());
  }

  /**
   * Get agent state observable
   */
  getAgentState$(agentName: string): Observable<AgentState> | undefined {
    return this.agentStates.get(agentName)?.asObservable();
  }

  /**
   * Get current round
   */
  getCurrentRound(): Round | null {
    return this.currentRound();
  }

  /**
   * Get system metrics
   */
  getMetrics() {
    return this.systemMetrics();
  }

  /**
   * Helper: Get priority value for sorting
   */
  private getPriorityValue(priority: AgentTask['priority']): number {
    const values = { 'low': 1, 'medium': 2, 'high': 3, 'critical': 4 };
    return values[priority];
  }

  /**
   * Update system metrics
   */
  private updateMetrics(updates: Partial<typeof this.systemMetrics extends signal<infer T> ? T : never>): void {
    this.systemMetrics.update(current => ({ ...current, ...updates }));
  }

  /**
   * Reset coordinator state
   */
  reset(): void {
    this.taskQueue = [];
    this.activeTasks.clear();
    this.currentRound.set(null);
    this.rounds = [];
    
    this.agents.forEach(agent => {
      agent.state = 'idle';
      agent.goal = 'Standby';
      agent.lastActivity = null;
      agent.metrics = {
        packetsProcessed: 0,
        errors: 0,
        avgProcessingTime: 0
      };
      
      const stateSubject = this.agentStates.get(agent.name);
      if (stateSubject) {
        stateSubject.next('idle');
      }
    });
    
    this.systemMetrics.set({
      totalPackets: 0,
      totalTasks: 0,
      completedTasks: 0,
      failedTasks: 0,
      avgRoundDuration: 0
    });
  }
}

