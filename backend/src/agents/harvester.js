/**
 * HARVESTER Agent
 * Responsible for extracting concepts (entities) from PDF pages
 */

import { BaseAgent } from '../shared/agent-base.js';
import { AgentPacket, Intent, AgentType } from '../shared/types.js';
import { GoogleGenAI } from '@google/genai';

export class HarvesterAgent extends BaseAgent {
  constructor(options = {}) {
    super(AgentType.HARVESTER, options);
    this.ai = null;
    this.initializeAI();
  }

  async initializeAI() {
    const apiKey = process.env.GEMINI_API_KEY;
    if (apiKey) {
      this.ai = new GoogleGenAI({ apiKey });
    } else {
      console.warn('[HARVESTER] GEMINI_API_KEY not set, agent will use proxy');
    }
  }

  async onInitialize() {
    console.log('[HARVESTER] Initialized - Ready to extract concepts');
    
    // Register intent handlers
    this.onIntent(Intent.GRAPH_UPDATE, async (packet) => {
      await this.handleExtractionRequest(packet);
    });
  }

  /**
   * Handle extraction request
   */
  async handleExtractionRequest(packet) {
    const { image, pageNumber, excludeTerms = [] } = packet.content;
    
    if (!image) {
      console.warn('[HARVESTER] No image provided in extraction request');
      return;
    }

    this.updateState('active', `Extracting concepts from page ${pageNumber || 'unknown'}`);

    try {
      // Extract concepts using AI
      const concepts = await this.extractConcepts(image, pageNumber, excludeTerms);
      
      // Send extracted concepts back
      for (const concept of concepts) {
        await this.send('ORCHESTRATOR', Intent.GRAPH_UPDATE, {
          concept: {
            ...concept,
            extractedBy: this.name,
            timestamp: new Date().toISOString()
          }
        });
      }

      // Signal completion
      await this.send('ORCHESTRATOR', Intent.TASK_COMPLETE, {
        agent: this.name,
        pageNumber,
        conceptsExtracted: concepts.length
      });

    } catch (error) {
      console.error('[HARVESTER] Extraction error:', error);
      await this.send('ORCHESTRATOR', Intent.INFO, {
        log: `Extraction failed: ${error.message}`,
        error: true
      });
      this.updateState('error', `Error: ${error.message}`);
    }
  }

  /**
   * Extract concepts from image
   */
  async extractConcepts(imageBase64, pageNumber, excludeTerms = []) {
    const prompt = this.buildExtractionPrompt(pageNumber, excludeTerms);
    
    if (this.ai) {
      // Direct API call
      return await this.extractViaDirectAPI(imageBase64, prompt);
    } else {
      // Use proxy
      return await this.extractViaProxy(imageBase64, prompt, pageNumber, excludeTerms);
    }
  }

  buildExtractionPrompt(pageNumber, excludeTerms) {
    const exclusionText = excludeTerms.length > 0 
      ? `\n\n**EXCLUSION LIST:** Ignore these previously found concepts:\n${excludeTerms.slice(0, 100).join(', ')}`
      : '';

    return `You are the HARVESTER agent in the Ontology Engine.

Your task is to extract concepts (entities) from this PDF page.

**EXTRACTION RULES:**
1. Extract all significant entities: organizations, people, locations, dates, legal terms, financial terms
2. Each concept must have:
   - id: unique identifier
   - term: the actual text/name
   - type: 'concept' or 'hypernode'
   - dataType: 'entity' | 'date' | 'location' | 'organization' | 'person' | 'money' | 'legal' | 'condition'
   - category: classification
   - explanation: brief description
   - confidence: 0.0-1.0
   - ui_group: grouping category
   - boundingBox: [ymin, xmin, ymax, xmax] if detectable

3. Be thorough but avoid duplicates
4. Focus on regulatory, legal, and business-relevant concepts

${exclusionText}

**CONTEXT:** Analyzing Page ${pageNumber}

Output a JSON array of concept objects.`;
  }

  async extractViaDirectAPI(imageBase64, prompt) {
    const imagePart = {
      inlineData: {
        mimeType: 'image/png',
        data: imageBase64.split(',')[1] || imageBase64
      }
    };

    const result = await this.ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: { parts: [imagePart, { text: prompt }] },
      config: {
        responseMimeType: 'application/json',
        maxOutputTokens: 4096
      }
    });

    const response = JSON.parse(result.text || '[]');
    return Array.isArray(response) ? response : [response];
  }

  async extractViaProxy(imageBase64, prompt, pageNumber, excludeTerms) {
    const proxyUrl = process.env.PROXY_API_ENDPOINT || 'http://localhost:3000/api/v1/analyze';
    
    const response = await fetch(proxyUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        image: imageBase64.split(',')[1] || imageBase64,
        pageNumber,
        excludeTerms,
        prompt,
        model: 'gemini-2.5-flash',
        agent: 'HARVESTER'
      })
    });

    if (!response.ok) {
      throw new Error(`Proxy error: ${response.status}`);
    }

    const data = await response.json();
    return Array.isArray(data.concepts) ? data.concepts : [];
  }
}

// Run as standalone process if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const agent = new HarvesterAgent();
  agent.start().catch(console.error);
  
  // Graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\n[HARVESTER] Shutting down...');
    await agent.stop();
    process.exit(0);
  });
}

