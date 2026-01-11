/**
 * CURATOR Agent
 * Responsible for organizing taxonomical hierarchies
 */

import { BaseAgent } from '../shared/agent-base.js';
import { Intent, AgentType } from '../shared/types.js';

export class CuratorAgent extends BaseAgent {
  constructor(options = {}) {
    super(AgentType.CURATOR, options);
  }

  async onInitialize() {
    console.log('[CURATOR] Initialized - Ready to organize taxonomies');
    
    this.onIntent(Intent.GRAPH_UPDATE, async (packet) => {
      await this.handleCurationRequest(packet);
    });
  }

  async handleCurationRequest(packet) {
    const { concepts, domains } = packet.content;
    
    if (!concepts || concepts.length === 0) {
      return;
    }

    this.updateState('active', 'Organizing concept hierarchies');

    try {
      // Create taxonomical relationships
      const taxonomies = await this.createTaxonomies(concepts, domains || []);
      
      for (const taxonomy of taxonomies) {
        await this.send('ORCHESTRATOR', Intent.GRAPH_UPDATE, {
          taxonomy: {
            ...taxonomy,
            createdBy: this.name,
            timestamp: new Date().toISOString()
          }
        });
      }

      await this.send('ORCHESTRATOR', Intent.TASK_COMPLETE, {
        agent: this.name,
        taxonomiesCreated: taxonomies.length
      });

    } catch (error) {
      console.error('[CURATOR] Error:', error);
      this.updateState('error', `Error: ${error.message}`);
    }
  }

  async createTaxonomies(concepts, domains) {
    const taxonomies = [];
    
    // Link concepts to domains
    concepts.forEach(concept => {
      const domain = domains.find(d => 
        d.name === concept.ui_group || 
        d.id === `dom_${concept.ui_group?.toLowerCase().replace(/\s+/g, '_')}`
      );
      
      if (domain) {
        taxonomies.push({
          parent: domain.id,
          child: concept.id,
          type: 'is_a'
        });
      }
    });

    // Create hierarchical relationships between concepts
    // Group by category and create parent-child relationships
    const categoryGroups = new Map();
    concepts.forEach(concept => {
      const category = concept.category || concept.ui_group || 'General';
      if (!categoryGroups.has(category)) {
        categoryGroups.set(category, []);
      }
      categoryGroups.get(category).push(concept);
    });

    // For each category, create a hierarchy (simplified - first concept as parent)
    categoryGroups.forEach((groupConcepts, category) => {
      if (groupConcepts.length > 1) {
        const parent = groupConcepts[0];
        for (let i = 1; i < groupConcepts.length; i++) {
          taxonomies.push({
            parent: parent.id,
            child: groupConcepts[i].id,
            type: 'is_a'
          });
        }
      }
    });

    return taxonomies;
  }
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const agent = new CuratorAgent();
  agent.start().catch(console.error);
  
  process.on('SIGINT', async () => {
    console.log('\n[CURATOR] Shutting down...');
    await agent.stop();
    process.exit(0);
  });
}

