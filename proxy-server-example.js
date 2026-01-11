/**
 * Example Proxy Server for PDF Concept Tagger
 * 
 * This is a simple Node.js/Express proxy server that forwards requests
 * to the Gemini API while keeping API keys secure on the server side.
 * 
 * Deployment:
 * 1. Install dependencies: npm install express cors @google/genai
 * 2. Set GEMINI_API_KEY environment variable
 * 3. Run: node proxy-server-example.js
 * 
 * For production, consider:
 * - Adding rate limiting
 * - Adding authentication
 * - Adding request validation
 * - Adding error tracking (e.g., Sentry)
 * - Adding logging
 */

const express = require('express');
const cors = require('cors');
const { GoogleGenAI } = require('@google/genai');

const app = express();

// Middleware
app.use(cors({
  origin: process.env.FRONTEND_URL || '*', // Restrict in production
  credentials: true
}));
app.use(express.json({ limit: '50mb' })); // Support large image payloads

// Initialize Gemini AI
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

if (!process.env.GEMINI_API_KEY) {
  console.error('ERROR: GEMINI_API_KEY environment variable is required');
  process.exit(1);
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'pdf-concept-tagger-proxy'
  });
});

// Main analysis endpoint
app.post('/api/v1/analyze', async (req, res) => {
  try {
    const { image, pageNumber, excludeTerms, prompt, model, schema } = req.body;
    
    // Validation
    if (!image || typeof image !== 'string') {
      return res.status(400).json({ error: 'Invalid image data' });
    }
    
    if (image.length > 10 * 1024 * 1024) { // 10MB limit
      return res.status(400).json({ error: 'Image too large (max 10MB)' });
    }
    
    console.log(`[${new Date().toISOString()}] Processing request: page ${pageNumber || 'unknown'}`);
    
    // Prepare image part
    const imagePart = {
      inlineData: {
        mimeType: 'image/png',
        data: image
      }
    };
    
    // Set up streaming response
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Transfer-Encoding', 'chunked');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    // Generate content stream
    const result = await ai.models.generateContentStream({
      model: model || 'gemini-2.5-flash',
      contents: { parts: [imagePart, { text: prompt }] },
      config: {
        responseMimeType: 'application/json',
        responseSchema: schema,
        maxOutputTokens: 8192
      }
    });
    
    // Stream the response
    let chunkCount = 0;
    for await (const chunk of result) {
      const text = chunk.text || '';
      if (text) {
        res.write(text);
        chunkCount++;
      }
    }
    
    console.log(`[${new Date().toISOString()}] Completed: ${chunkCount} chunks sent`);
    res.end();
    
  } catch (error) {
    console.error(`[${new Date().toISOString()}] Error:`, error);
    
    // Don't send response if headers already sent
    if (!res.headersSent) {
      res.status(500).json({ 
        error: 'Internal server error',
        message: error.message 
      });
    } else {
      res.end();
    }
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`PDF Concept Tagger Proxy Server running on port ${PORT}`);
  console.log(`Health check: http://localhost:${PORT}/health`);
  console.log(`Analysis endpoint: http://localhost:${PORT}/api/v1/analyze`);
});

