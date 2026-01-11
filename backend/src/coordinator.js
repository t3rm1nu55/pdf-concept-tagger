/**
 * Orchestrator/Coordinator Service
 * Coordinates all agents and manages the overall workflow
 */

import express from 'express';
import cors from 'cors';
import { WebSocketServer } from 'ws';
import { getMessageBus } from './shared/message-bus.js';
import { AgentPacket, Intent, AgentType } from './shared/types.js';
import { HarvesterAgent } from './agents/harvester.js';
import { ArchitectAgent } from './agents/architect.js';
import { CuratorAgent } from './agents/curator.js';

const app = express();
app.use(cors());
app.use(express.json({ limit: '50mb' }));

const PORT = process.env.PORT || 4000;
const WS_PORT = process.env.WS_PORT || 4001;

// Initialize message bus
const messageBus = getMessageBus(process.env.MESSAGE_BUS_TRANSPORT || 'memory');
await messageBus.initialize();

// Agent registry
const agents = new Map();
let currentRound = null;

// Initialize agents
async function initializeAgents() {
  console.log('Initializing agents...');
  
  const harvester = new HarvesterAgent();
  const architect = new ArchitectAgent();
  const curator = new CuratorAgent();
  
  await harvester.start();
  await architect.start();
  await curator.start();
  
  agents.set(AgentType.HARVESTER, harvester);
  agents.set(AgentType.ARCHITECT, architect);
  agents.set(AgentType.CURATOR, curator);
  
  console.log('All agents initialized');
}

// WebSocket server for real-time updates
const wss = new WebSocketServer({ port: WS_PORT });
const clients = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  console.log(`[WS] Client connected (${clients.size} total)`);
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log(`[WS] Client disconnected (${clients.size} total)`);
  });
  
  ws.on('error', (error) => {
    console.error('[WS] Error:', error);
    clients.delete(ws);
  });
});

// Broadcast to WebSocket clients
function broadcastToClients(data) {
  const message = JSON.stringify(data);
  clients.forEach(client => {
    if (client.readyState === 1) { // OPEN
      client.send(message);
    }
  });
}

// Subscribe to message bus and forward to clients
messageBus.subscribe(null, (packet) => {
  broadcastToClients({ type: 'agent:message', data: packet });
});

// API Routes

app.get('/health', (req, res) => {
  const agentStatuses = Array.from(agents.values()).map(agent => agent.getStatus());
  res.json({
    status: 'ok',
    agents: agentStatuses,
    round: currentRound
  });
});

app.post('/api/v1/analyze', async (req, res) => {
  try {
    const { image, pageNumber, excludeTerms = [] } = req.body;
    
    if (!image) {
      return res.status(400).json({ error: 'Image is required' });
    }

    // Start new round
    currentRound = {
      id: Date.now(),
      name: `Page ${pageNumber || 'Unknown'}`,
      startedAt: new Date().toISOString(),
      status: 'active'
    };

    // Set up streaming response
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Transfer-Encoding', 'chunked');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');

    // Send round start
    const roundStartPacket = new AgentPacket({
      sender: AgentType.ORCHESTRATOR,
      intent: Intent.ROUND_START,
      content: {
        round_id: currentRound.id,
        round_name: currentRound.name
      }
    });
    
    res.write(JSON.stringify(roundStartPacket.toJSON()) + '\n');
    broadcastToClients({ type: 'agent:message', data: roundStartPacket.toJSON() });

    // Collect all packets
    const packets = [];
    
    // Subscribe to messages for this round
    const unsubscribe = messageBus.subscribe(null, (packet) => {
      if (packet.intent === Intent.GRAPH_UPDATE || 
          packet.intent === Intent.TASK_COMPLETE ||
          packet.intent === Intent.HYPOTHESIS) {
        packets.push(packet);
        res.write(JSON.stringify(packet) + '\n');
      }
    });

    // Trigger harvester to extract concepts
    const harvesterPacket = new AgentPacket({
      sender: AgentType.ORCHESTRATOR,
      recipient: AgentType.HARVESTER,
      intent: Intent.GRAPH_UPDATE,
      content: {
        image,
        pageNumber,
        excludeTerms
      }
    });

    await messageBus.publish(harvesterPacket);

    // Wait for completion (simplified - in production use proper async handling)
    setTimeout(async () => {
      // Trigger architect to define domains
      const architectPacket = new AgentPacket({
        sender: AgentType.ORCHESTRATOR,
        recipient: AgentType.ARCHITECT,
        intent: Intent.GRAPH_UPDATE,
        content: {
          concepts: packets.filter(p => p.content?.concept).map(p => p.content.concept)
        }
      });
      
      await messageBus.publish(architectPacket);

      // Wait a bit more for architect to complete
      setTimeout(async () => {
        // Trigger curator
        const curatorPacket = new AgentPacket({
          sender: AgentType.ORCHESTRATOR,
          recipient: AgentType.CURATOR,
          intent: Intent.GRAPH_UPDATE,
          content: {
            concepts: packets.filter(p => p.content?.concept).map(p => p.content.concept),
            domains: packets.filter(p => p.content?.domain).map(p => p.content.domain)
          }
        });
        
        await messageBus.publish(curatorPacket);

        // Complete round after a delay
        setTimeout(() => {
          currentRound.status = 'completed';
          currentRound.completedAt = new Date().toISOString();
          
          const completePacket = new AgentPacket({
            sender: AgentType.ORCHESTRATOR,
            intent: Intent.TASK_COMPLETE,
            content: {
              round_id: currentRound.id,
              packetsGenerated: packets.length
            }
          });
          
          res.write(JSON.stringify(completePacket.toJSON()) + '\n');
          res.end();
          unsubscribe();
        }, 2000);
      }, 2000);
    }, 3000);

  } catch (error) {
    console.error('[Coordinator] Error:', error);
    if (!res.headersSent) {
      res.status(500).json({ error: error.message });
    } else {
      res.end();
    }
  }
});

app.get('/api/v1/agents', (req, res) => {
  const statuses = Array.from(agents.values()).map(agent => agent.getStatus());
  res.json({ agents: statuses });
});

// Start server
async function start() {
  await initializeAgents();
  
  app.listen(PORT, () => {
    console.log(`\n🚀 Coordinator API running on port ${PORT}`);
    console.log(`📡 WebSocket server running on port ${WS_PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  /health`);
    console.log(`  POST /api/v1/analyze`);
    console.log(`  GET  /api/v1/agents`);
    console.log(`\nWebSocket: ws://localhost:${WS_PORT}\n`);
  });
}

start().catch(console.error);

// Graceful shutdown
process.on('SIGINT', async () => {
  console.log('\n🛑 Shutting down...');
  for (const agent of agents.values()) {
    await agent.stop();
  }
  await messageBus.disconnect();
  process.exit(0);
});

