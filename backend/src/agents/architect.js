/**
 * ARCHITECT Agent
 * Responsible for defining domains and creating semantic relationships
 */

import { BaseAgent } from '../shared/agent-base.js';
import { Intent, AgentType } from '../shared/types.js';

export class ArchitectAgent extends BaseAgent {
  constructor(options = {}) {
    super(AgentType.ARCHITECT, options);
  }

  async onInitialize() {
    console.log('[ARCHITECT] Initialized - Ready to define domains and relationships');
    
    this.onIntent(Intent.GRAPH_UPDATE, async (packet) => {
      await this.handleArchitectureRequest(packet);
    });
  }

  async handleArchitectureRequest(packet) {
    const { concepts, existingDomains = [] } = packet.content;
    
    if (!concepts || concepts.length === 0) {
      return;
    }

    this.updateState('active', 'Analyzing concepts for domain structure');

    try {
      // Define domains based on concepts
      const domains = await this.defineDomains(concepts, existingDomains);
      
      for (const domain of domains) {
        await this.send('ORCHESTRATOR', Intent.GRAPH_UPDATE, {
          domain: {
            ...domain,
            definedBy: this.name,
            timestamp: new Date().toISOString()
          }
        });
      }

      // Create semantic relationships
      const relationships = await this.createRelationships(concepts);
      
      for (const rel of relationships) {
        await this.send('ORCHESTRATOR', Intent.GRAPH_UPDATE, {
          relationship: {
            ...rel,
            createdBy: this.name,
            timestamp: new Date().toISOString()
          }
        });
      }

      await this.send('ORCHESTRATOR', Intent.TASK_COMPLETE, {
        agent: this.name,
        domainsDefined: domains.length,
        relationshipsCreated: relationships.length
      });

    } catch (error) {
      console.error('[ARCHITECT] Error:', error);
      this.updateState('error', `Error: ${error.message}`);
    }
  }

  async defineDomains(concepts, existingDomains) {
    // Group concepts by category/dataType to identify domains
    const domainMap = new Map();
    
    concepts.forEach(concept => {
      const category = concept.ui_group || concept.category || 'General';
      if (!domainMap.has(category)) {
        domainMap.set(category, {
          id: `dom_${category.toLowerCase().replace(/\s+/g, '_')}`,
          name: category,
          description: `Domain for ${category} concepts`,
          sensitivity: this.assessSensitivity(concept),
          concepts: []
        });
      }
      domainMap.get(category).concepts.push(concept.id);
    });

    // Convert to array and filter out existing domains
    const domains = Array.from(domainMap.values()).filter(domain => 
      !existingDomains.some(existing => existing.id === domain.id)
    );

    return domains;
  }

  assessSensitivity(concept) {
    const sensitiveTypes = ['legal', 'money', 'person'];
    if (sensitiveTypes.includes(concept.dataType)) {
      return 'HIGH';
    }
    return 'MEDIUM';
  }

  async createRelationships(concepts) {
    const relationships = [];
    
    // Create relationships based on concept proximity and semantic similarity
    // This is a simplified version - in production, use AI/ML for better relationship detection
    for (let i = 0; i < concepts.length; i++) {
      for (let j = i + 1; j < concepts.length; j++) {
        const c1 = concepts[i];
        const c2 = concepts[j];
        
        // Simple heuristic: same category = semantic relationship
        if (c1.ui_group === c2.ui_group && c1.ui_group !== 'General') {
          relationships.push({
            source: c1.id,
            target: c2.id,
            predicate: 'related_to',
            type: 'semantic'
          });
        }
      }
    }

    return relationships;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const agent = new ArchitectAgent();
  agent.start().catch(console.error);
  
  process.on('SIGINT', async () => {
    console.log('\n[ARCHITECT] Shutting down...');
    await agent.stop();
    process.exit(0);
  });
}

