# PDF Concept Tagger - Prototype to Demo Requirements

## Executive Summary
Transition from prototype to production-ready demo focusing on robust agent coordination, optimized prompts, ontological structures, and operational efficiency.

## 1. API Proxy Integration

### 1.1 Proxy Architecture
- **Requirement**: Replace direct Gemini API calls with configurable proxy endpoint
- **Rationale**: 
  - Isolate API key management from client code
  - Enable rate limiting and request monitoring
  - Support multiple deployment environments without code changes
  - Maintain separation from surfsense testing infrastructure

### 1.2 Proxy Deployment Strategy
- **Separate Deployment**: Deploy proxy as distinct service/endpoint
- **Configuration**: Environment-based endpoint configuration
- **Fallback**: Graceful degradation if proxy unavailable
- **Versioning**: Support for proxy API versioning

### 1.3 Proxy Interface Requirements
- **Endpoint**: `/api/v1/analyze` (configurable)
- **Method**: POST
- **Request Format**:
  ```json
  {
    "image": "base64_encoded_image",
    "pageNumber": 1,
    "excludeTerms": ["term1", "term2"],
    "prompt": "custom_prompt_override",
    "model": "gemini-2.5-flash"
  }
  ```
- **Response**: Server-Sent Events (SSE) or streaming JSON
- **Error Handling**: Standardized error responses with retry guidance

## 2. Agent Coordination Framework

### 2.1 Architecture Patterns
Implement robust agent coordination inspired by:
- **ADK (Agent Development Kit)**: Structured agent lifecycle management
- **A2A (Agent-to-Agent)**: Explicit communication protocols
- **Microsoft Agent Framework**: Task orchestration and state management

### 2.2 Agent Lifecycle Management
- **States**: `idle`, `initializing`, `active`, `waiting`, `completed`, `error`
- **Transitions**: Explicit state machine with validation
- **Recovery**: Automatic retry with exponential backoff
- **Monitoring**: Real-time agent status and health metrics

### 2.3 Agent Communication Protocol
- **Message Bus**: Centralized event-driven communication
- **Packet Routing**: Explicit sender/recipient addressing
- **Priority Queue**: Critical messages processed first
- **Acknowledgment**: Confirmation of packet receipt/processing

### 2.4 Agent Responsibilities (Enhanced)
- **ORCHESTRATOR**: 
  - Coordinates agent execution order
  - Manages round-based processing
  - Handles task delegation
  - Monitors overall progress
  
- **HARVESTER**:
  - Extracts concepts with confidence scoring
  - Tracks extraction completeness
  - Reports extraction metrics
  
- **ARCHITECT**:
  - Defines domain structures
  - Creates semantic relationships
  - Validates graph consistency
  
- **CURATOR**:
  - Organizes taxonomical hierarchies
  - Ensures ontological consistency
  - Manages concept grouping
  
- **CRITIC**:
  - Evaluates graph quality
  - Proposes optimizations
  - Validates hypotheses
  
- **OBSERVER**:
  - Monitors system state
  - Provides explainability
  - Generates insights

## 3. Prompt Engineering & Optimization

### 3.1 Prompt Structure
- **Modular Prompts**: Separate prompt templates for each agent role
- **Context Injection**: Dynamic context based on current graph state
- **Few-Shot Examples**: Curated examples for each agent type
- **Chain-of-Thought**: Explicit reasoning steps for complex extractions

### 3.2 Prompt Versioning
- **Version Control**: Track prompt versions and their performance
- **A/B Testing**: Compare prompt variations
- **Rollback Capability**: Revert to previous prompt versions

### 3.3 Prompt Optimization Areas
- **Concept Extraction**: Improve entity recognition accuracy
- **Relationship Discovery**: Better semantic relationship identification
- **Taxonomy Construction**: More accurate hierarchical organization
- **Domain Identification**: Enhanced domain boundary detection

## 4. Ontological Structures

### 4.1 Core Ontology Model
- **Concepts**: Entities with rich metadata
- **Domains**: High-level knowledge areas
- **Taxonomies**: Hierarchical relationships (`is_a`, `part_of`)
- **Relationships**: Semantic connections (predicates)
- **Priors**: Axioms and rules
- **Hypotheses**: Testable claims with evidence

### 4.2 Ontology Validation
- **Consistency Checks**: Validate ontological constraints
- **Completeness Metrics**: Measure extraction coverage
- **Quality Scoring**: Assess ontological structure quality
- **Conflict Resolution**: Handle contradictory information

### 4.3 Ontology Evolution
- **Incremental Updates**: Support graph refinement
- **Version History**: Track ontology changes over time
- **Merge Strategies**: Combine multiple extraction sessions
- **Conflict Detection**: Identify and resolve inconsistencies

## 5. Performance & Efficiency

### 5.1 Streaming Optimization
- **Chunk Processing**: Efficient handling of large responses
- **Backpressure Management**: Prevent memory overflow
- **Progressive Rendering**: Update UI incrementally
- **Debouncing**: Reduce unnecessary graph updates

### 5.2 Caching Strategy
- **Concept Cache**: Avoid re-extracting known concepts
- **Page Cache**: Cache processed pages
- **Prompt Cache**: Cache prompt responses for similar content
- **Graph Cache**: Persist graph state efficiently

### 5.3 Resource Management
- **Memory Optimization**: Efficient data structures
- **Network Optimization**: Minimize API calls
- **CPU Optimization**: Offload heavy processing
- **Storage Optimization**: Efficient IndexedDB usage

## 6. Error Handling & Resilience

### 6.1 Error Categories
- **Network Errors**: Connection failures, timeouts
- **API Errors**: Rate limits, authentication failures
- **Parsing Errors**: Malformed JSON, schema violations
- **State Errors**: Invalid agent states, data inconsistencies

### 6.2 Recovery Strategies
- **Automatic Retry**: With exponential backoff
- **Partial Recovery**: Continue with available data
- **State Restoration**: Recover from crashes
- **User Notification**: Clear error messages

## 7. Testing & Validation

### 7.1 Unit Testing
- **Agent Services**: Test individual agent logic
- **Packet Processing**: Validate packet handling
- **State Management**: Test state transitions
- **Error Handling**: Test error scenarios

### 7.2 Integration Testing
- **End-to-End Flows**: Complete extraction workflows
- **API Integration**: Test proxy communication
- **Storage Integration**: Test persistence layer
- **UI Integration**: Test component interactions

### 7.3 Performance Testing
- **Load Testing**: Handle large PDFs
- **Stress Testing**: Multiple concurrent extractions
- **Memory Profiling**: Identify memory leaks
- **Performance Benchmarks**: Track improvement metrics

## 8. Documentation & Observability

### 8.1 API Documentation
- **Proxy API**: Complete endpoint documentation
- **Agent Protocol**: Packet format specifications
- **Configuration**: Environment variable documentation
- **Deployment**: Deployment guides

### 8.2 Logging & Monitoring
- **Structured Logging**: JSON-formatted logs
- **Log Levels**: Debug, Info, Warn, Error
- **Metrics Collection**: Performance metrics
- **Error Tracking**: Error aggregation and analysis

### 8.3 User Documentation
- **User Guide**: How to use the application
- **Troubleshooting**: Common issues and solutions
- **FAQ**: Frequently asked questions
- **Video Tutorials**: Visual guides

## 9. Future Considerations

### 9.1 Docling Integration
- **Migration Path**: Plan for Docling integration
- **API Compatibility**: Maintain compatibility layer
- **Feature Parity**: Ensure all features work with Docling
- **Performance Comparison**: Benchmark against current approach

### 9.2 Advanced Features
- **Multi-Document Analysis**: Cross-document relationships
- **Temporal Analysis**: Time-based concept evolution
- **Collaborative Editing**: Multi-user ontology editing
- **Export Formats**: Support multiple export formats

## 10. Success Criteria

### 10.1 Functional Requirements
- ✅ Proxy API integration working
- ✅ Agent coordination framework operational
- ✅ Improved prompt performance
- ✅ Robust error handling
- ✅ Complete documentation

### 10.2 Performance Requirements
- **Extraction Speed**: < 30 seconds per page
- **Memory Usage**: < 500MB for typical PDFs
- **UI Responsiveness**: < 100ms for interactions
- **API Latency**: < 2 seconds for initial response

### 10.3 Quality Requirements
- **Concept Accuracy**: > 90% precision
- **Relationship Accuracy**: > 85% precision
- **Taxonomy Accuracy**: > 90% precision
- **System Uptime**: > 99% availability

## 11. Implementation Phases

### Phase 1: Foundation (Week 1-2)
- Proxy API integration
- Basic agent coordination service
- Configuration management
- Error handling improvements

### Phase 2: Enhancement (Week 3-4)
- Advanced agent coordination
- Prompt optimization
- Performance improvements
- Testing infrastructure

### Phase 3: Polish (Week 5-6)
- Documentation completion
- UI/UX improvements
- Performance tuning
- Demo preparation

## 12. Dependencies & Constraints

### 12.1 Technical Constraints
- Angular 20+ (Zoneless, Signals)
- Browser-based (no Node.js backend required)
- IndexedDB for persistence
- Proxy API must support streaming

### 12.2 External Dependencies
- PDF.js for PDF rendering
- D3.js for graph visualization
- Proxy API service (to be deployed)
- Gemini API (via proxy)

### 12.3 Non-Functional Constraints
- Must not interfere with surfsense testing
- Separate deployment for proxy
- Backward compatibility with existing data
- Browser compatibility (Chrome, Firefox, Safari)

