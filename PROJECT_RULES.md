# PDF Concept Tagger - Project Rules

> **Adapted from**: Agent Development Guidelines  
> **Context**: Python/FastAPI/LangChain/LangGraph backend, React frontend  
> **Purpose**: Development rules and workflows for PDF Concept Tagger

## Core Development Principles

### 1. Incremental & Modular Development ✅

**Rule**: Small focused changes, build on existing patterns

**Application**:
- **Backend**: Create small, focused services (PDF processing, LLM abstraction, database services)
- **Agents**: Build agents incrementally (HARVESTER → ARCHITECT → CURATOR)
- **Frontend**: Create reusable components, build features incrementally
- **No Duplication**: Always `codebase_search` first, then `grep` for exact matches before creating new code

**Examples**:
```python
# ✅ GOOD: Small, focused service
class PDFProcessor:
    """Handles PDF parsing and text extraction"""
    def extract_text(self, pdf_path: str) -> str: ...
    def extract_structure(self, pdf_path: str) -> DocumentStructure: ...

# ❌ BAD: Monolithic function doing everything
def process_pdf(pdf_path: str) -> dict:  # Does too much
```

**Checklist**:
- [ ] Change is focused on single responsibility
- [ ] Reuses existing patterns/components
- [ ] No duplication (searched codebase first)
- [ ] Modular and testable
- [ ] Documented (docstrings for complex logic)

---

### 2. Critical Mocking Guidelines ✅

**Rule**: Never mock in production code. Mocks only in test files.

**Application**:
- **Backend Services**: Mock external APIs (OpenAI, Anthropic, Google), databases (for unit tests), file system
- **Agent Tests**: Mock LLM responses, database calls, external services
- **Integration Tests**: Use real services when possible
- **E2E Tests**: Always use real services

**Mock Identification**:
```python
# ✅ GOOD: Clear mock naming and location
# tests/__mocks__/llm_service.py
mock_openai_response = {
    "content": "Mock response",
    "model": "gpt-4"
}

# tests/test_harvester.py
from tests.__mocks__.llm_service import mock_openai_response

def test_harvester_extraction(mock_llm):
    # Mock: External API unavailable in unit tests
    mock_llm.return_value = mock_openai_response
    result = harvester.extract_concepts(...)
    assert result is not None

# ❌ BAD: Mock in production code
# app/services/llm_service.py
mock_response = {...}  # NEVER DO THIS
```

**When to Mock**:
- ✅ External API calls (OpenAI, Anthropic, Google Gemini)
- ✅ Database operations (in unit tests only)
- ✅ File system operations
- ✅ Time-dependent functions (dates, timers)
- ✅ Random number generation

**When NOT to Mock**:
- ❌ Production code (dev or prod environments)
- ❌ Integration tests (use real services when possible)
- ❌ E2E tests (always use real services)
- ❌ When real implementation is simpler than mock

**Mock Removal Checklist**:
- [ ] Real service is available and stable
- [ ] Tests still pass with real service
- [ ] Test execution time is acceptable
- [ ] No flaky tests introduced
- [ ] Mock file removed from codebase

---

### 3. Requirements → Design → Tasks Pipeline ✅

**Rule**: Structured workflow from user needs to implementation

**Current State**:
- ✅ **REQUIREMENTS.md** - Outcome-based requirements (563 lines)
- ✅ **DESIGN_HOOKS.md** - Design exercise flags
- ✅ **TASKS.md** - Task breakdown with dependencies

**Workflow**:
```
User Need → Requirements → Design → Tasks → Implementation
```

**Process**:

1. **Requirements Creation** (REQUIREMENTS.md)
   - Extract user needs from query
   - Define success criteria (measurable, testable)
   - Identify constraints (technical, time, resources)
   - Link to long-term objectives
   - Priority: High | Medium | Low

2. **Design Creation** (DESIGN_HOOKS.md, DEMO_ARCHITECTURE.md)
   - Analyze requirements
   - Research patterns (`codebase_search` for similar implementations)
   - Design approach (architecture, components, data flow)
   - Document design (update architecture docs)
   - Validate against requirements and success criteria
   - Flag design hooks where refinement needed

3. **Task Creation** (TASKS.md)
   - Review design specification
   - Break down into tasks (each <2 hours if possible)
   - Define dependencies (use dependency flags: 🟢🟡🔴🔵)
   - Assign tasks (Track 1 vs Track 2)
   - Set success criteria (testable acceptance criteria)
   - Link to requirements

**Example**:
```markdown
### REQ-001: PDF Analysis Endpoint
**User Need**: Analyze PDF pages and extract concepts
**Success Criteria**:
- [ ] Endpoint accepts PDF page image
- [ ] Returns streaming response with concepts
- [ ] Processes in <30 seconds
**Design**: See DEMO_ARCHITECTURE.md Section 6.1
**Tasks**: T6.1 (Analysis Endpoint)
**Priority**: High
```

**Alignment Check**:
- [ ] Requirements support long-term objectives
- [ ] Design meets requirements and success criteria
- [ ] Tasks trace back to requirements
- [ ] Success criteria are measurable and testable

---

### 4. State-Based Actions (Not Time-Based) ✅

**Rule**: Act when indicators show need, not on schedule

**Application**:
- **Technical Debt**: Clean up when indicators accumulate (unused imports, commented code, duplicates)
- **Performance**: Optimize when metrics show issues (slow queries, high memory usage)
- **Testing**: Add tests when coverage drops or bugs found
- **Documentation**: Update docs when code changes significantly

**Indicators**:

**Technical Debt Indicators**:
- Multiple unused imports across files
- Commented-out code blocks present
- Duplicate utility functions exist
- Outdated documentation references
- Unused dependencies in requirements.txt
- Build warnings accumulating

**Performance Indicators**:
- API response time >2 seconds
- Database query time >500ms
- Memory usage >80% of available
- CPU usage consistently high
- User reports lag/slowness

**How to Identify State**:
```bash
# Check for unused imports (Python)
pylint --disable=all --enable=unused-import backend-python/

# Find duplicate functions
grep -r "^def " backend-python/app/ | sort | uniq -d

# Check for commented code
grep -r "^[[:space:]]*#" backend-python/app/ | grep -v "^[[:space:]]*#.*[a-z]"

# Performance monitoring
# Add logging/metrics to track response times, query times
```

**Action Triggers**:
- **Cleanup**: When 5+ unused imports found, or commented code blocks present
- **Optimization**: When API response >2s, or database query >500ms
- **Testing**: When coverage drops below 70%, or bug found in untested code
- **Documentation**: When API changes, or new feature added

---

### 5. Transparency Requirements ✅

**Rule**: Document planning steps, show alternatives, explain decisions

**Application**:
- **Planning**: Document what, why, how in task tracking
- **Decisions**: Show alternatives considered, explain why chosen
- **Actions**: Log significant actions for debugging/learning
- **ADRs**: Create ADRs for architectural decisions

**Planning Documentation Format**:
```markdown
### Planning Notes
**Goal**: [What are we building?]
**Approach**: [How will we build it?]
**Alternatives Considered**:
- Option 1 (rejected): [Why rejected]
- Option 2 ✅ (chosen): [Why chosen]
**Dependencies**: [What blocks this?]
**Risks**: [What could go wrong?]
**Success Criteria**: [How do we know it's done?]
```

**Decision Documentation**:
```python
# ✅ GOOD: Document decision in code
# Decision: Using LangChain agents instead of custom implementation
# Reason: Industry standard, better ecosystem, easier maintenance
# Alternative considered: Custom agent framework (rejected: reinventing wheel)
from langchain.agents import initialize_agent

# ✅ GOOD: ADR for significant decisions
# docs/adr/001-langchain-agents.md
```

**Transparency Checklist**:
- [ ] Planning steps documented (what, why, how)
- [ ] Alternatives considered and documented
- [ ] Decision reasoning explained
- [ ] Assumptions documented
- [ ] Risks identified
- [ ] Success criteria defined

---

### 6. Agent Guide CLI System ⚠️

**Rule**: Contextual help system for development tasks

**Status**: ⚠️ To be implemented

**Proposed Implementation**:
```bash
# Create scripts/agent-guide.sh
./scripts/agent-guide.sh task new-agent      # Creating new LangChain agent
./scripts/agent-guide.sh task new-endpoint   # Creating new API endpoint
./scripts/agent-guide.sh task new-service    # Creating new service
./scripts/agent-guide.sh task bug-fix        # Fixing bugs
./scripts/agent-guide.sh stage planning      # Planning phase
./scripts/agent-guide.sh stage testing       # Testing phase
```

**Available Task Types** (for PDF Concept Tagger):
- `new-agent` - Creating new LangChain agent
- `new-endpoint` - Creating new FastAPI endpoint
- `new-service` - Creating new backend service
- `bug-fix` - Fixing bugs
- `library-selection` - Choosing libraries
- `testing` - Writing tests
- `refactor` - Refactoring code

**Available Stages**:
- `planning` - Planning and requirements
- `research` - Research and library selection
- `design` - Design and architecture
- `implementation` - Implementation and coding
- `testing` - Testing and quality
- `review` - Code review
- `documentation` - Documentation and ADRs

**Implementation Plan**:
- [ ] Create `scripts/agent-guide.sh`
- [ ] Extract relevant sections from AGENTS_GUIDE.md
- [ ] Add PDF Concept Tagger-specific guidance
- [ ] Test with common tasks
- [ ] Document usage in README

---

### 7. Pragmatic Decision-Making ✅

**Rule**: Balance ideal solutions with real-world constraints

**Application**:
- **MVP vs v1.0**: Use MVP for demo, full implementation for production
- **Library Choice**: Use proven libraries (LangChain) vs building custom
- **Architecture**: Start simple, refactor when needed
- **Testing**: Test critical paths first (80/20 rule)

**Decision Framework**:
```
Need to make a decision?
├─ Is there an existing solution? → Use it (pragmatic)
├─ Can we incrementally improve? → Do that (pragmatic)
├─ Is this a one-time need? → Simple solution (pragmatic)
├─ Will this scale? → Consider future, but don't over-engineer
└─ What's the maintenance cost? → Factor into decision
```

**Pragmatic Examples**:

**Library Choice**:
- ✅ **Pragmatic**: Use LangChain (proven, maintained, ecosystem)
- ❌ **Not Pragmatic**: Build custom agent framework (reinventing wheel)

**Architecture**:
- ✅ **Pragmatic**: Start with FastAPI + LangChain, add LangGraph when needed
- ❌ **Not Pragmatic**: Build everything upfront before validating

**Testing**:
- ✅ **Pragmatic**: Test critical paths (agent coordination, API endpoints) first
- ❌ **Not Pragmatic**: 100% coverage before MVP works

**MVP vs v1.0**:
- ✅ **Pragmatic**: MVP demo with basic features, v1.0 with full implementation
- ❌ **Not Pragmatic**: Build everything perfectly before demo

**When to Be Pragmatic**:
- ✅ MVP/prototype phase
- ✅ Time constraints exist
- ✅ Unclear future requirements
- ✅ Learning/experimentation
- ✅ Limited resources

**When to Be Less Pragmatic**:
- ⚠️ Core architecture decisions (LangChain/LangGraph)
- ⚠️ Security-critical code (API keys, authentication)
- ⚠️ Long-term maintainability concerns
- ⚠️ Team consensus needed

---

## Key Workflows

### Development Workflow ✅

**Process**:
1. Review REQUIREMENTS.md → `codebase_search` (semantic) → `grep` (exact) → Create todos
2. Review DESIGN_HOOKS.md if design needed
3. Review TASKS.md for task breakdown
4. Implement incrementally → Test → Document → Review → Commit
5. Verify: `pytest && ruff check && mypy app/`

**Example**:
```bash
# Starting new feature: PDF analysis endpoint
1. codebase_search "How do we handle API endpoints?"
2. grep "router.post" backend-python/app/api/
3. Review DEMO_ARCHITECTURE.md Section 6.1
4. Create todos for implementation
5. Implement incrementally
6. Test with pytest
7. Document with docstrings
8. Review and commit
```

---

### Bug Fix Workflow ✅

**Process**:
1. Reproduce issue
2. **Document findings**: What's broken, where, why
3. Investigate: `codebase_search` → `grep` → `read_file`
4. Write failing test (if needed)
5. Fix bug
6. **Verify**: Test passes, build succeeds, no regressions
7. Check for similar issues: `codebase_search` for similar patterns

**Example**:
```bash
# Bug: Agent not extracting concepts correctly
1. Reproduce: Upload PDF, check extracted concepts
2. Document: "HARVESTER agent returns empty concepts for PDF page 1"
3. codebase_search "How does HARVESTER extract concepts?"
4. grep "extract_concepts" backend-python/app/agents/
5. read_file backend-python/app/agents/harvester.py
6. Write failing test
7. Fix bug
8. Verify: pytest tests/test_agents/test_harvester.py
9. Check for similar issues in other agents
```

---

### Library Selection Workflow ✅

**Process**:
1. Check existing: `codebase_search` → `grep` for library name
2. Research with Context7 MCP (if available) or web search
3. Compare: bundle size, maintenance, docs, license
4. Decide (create ADR if significant)
5. Implement and test

**Example**:
```bash
# Need: Vector database for embeddings
1. codebase_search "How do we store embeddings?"
2. grep "pinecone\|weaviate\|qdrant" backend-python/
3. Research: Context7 MCP for Pinecone docs
4. Compare: Pinecone (managed) vs Weaviate (self-hosted)
5. Decision: Pinecone (pragmatic: managed, free tier)
6. Create ADR if significant decision
7. Implement and test
```

---

## Decision Frameworks

### When to Create New Service/Module? ✅

| Condition | Action |
|-----------|--------|
| Similar service exists | Reuse/extend existing |
| Need 2+ variations | Create base service + variants |
| One-time use, simple | Inline or small utility function |
| Complex, reusable | Create new service/module |

**Example**:
```python
# ✅ GOOD: Reuse existing
from app.services.pdf_service import PDFProcessor
processor = PDFProcessor()

# ✅ GOOD: Create new when needed
# app/services/rag_service.py - New service for RAG pipeline
class RAGService:
    """RAG pipeline for semantic search"""
    ...
```

---

### When to Create ADR? ✅

| Decision Type | ADR Needed? |
|---------------|-------------|
| New library choice (LangChain, Neo4j, Pinecone) | ✅ Yes |
| Architectural pattern (LangGraph workflow) | ✅ Yes |
| Small implementation detail | ❌ No (comment in code) |
| Bug fix approach | ❌ No |
| Performance optimization | ⚠️ Maybe (if significant) |

**Location**: `docs/adr/NNN-title.md`

**Format**:
```markdown
# ADR-001: Use LangChain for Agent Framework
**Status**: Accepted
**Date**: 2026-01-11
**Context**: Need agent orchestration framework
**Decision**: Use LangChain + LangGraph
**Options Considered**: 
- Custom framework (rejected: reinventing wheel)
- AutoGen (rejected: less mature)
- LangChain ✅ (chosen: industry standard, best ecosystem)
**Consequences**: 
- Positive: Proven framework, good docs, active community
- Negative: Learning curve, dependency on external library
```

---

### When to Write Tests? ✅

| Code Type | Test Level |
|-----------|-----------|
| Pure function | ✅ Unit test (`pytest`) |
| Service class | ✅ Unit test (mock dependencies) |
| API endpoint | ✅ Integration test (test client) |
| Agent logic | ✅ Unit test (mock LLM) |
| Complex business logic | ✅ All levels |
| Simple utility | ⚠️ Unit test (optional) |

**Testing Pyramid**:
```
        /\
       /  \      E2E Tests (few)
      /____\
     /      \    Integration Tests (some)
    /________\
   /          \  Unit Tests (many)
  /____________\
```

**Example**:
```python
# ✅ Unit test for pure function
def test_format_date():
    assert format_date("2026-01-11") == "Jan 11, 2026"

# ✅ Unit test for service (mock dependencies)
def test_pdf_processor_extract_text(mock_pdf_parser):
    processor = PDFProcessor()
    result = processor.extract_text("test.pdf")
    assert result == "extracted text"

# ✅ Integration test for API endpoint
def test_analyze_endpoint(client):
    response = client.post("/api/v1/analyze", json={"image_base64": "..."})
    assert response.status_code == 200
```

---

## Implementation Checklist

### For Each Development Task

**Before Starting**:
- [ ] Reviewed REQUIREMENTS.md (if applicable)
- [ ] Searched codebase (`codebase_search` → `grep`)
- [ ] Reviewed DESIGN_HOOKS.md (if design needed)
- [ ] Created todos (if complex task)
- [ ] Understood dependencies

**During Development**:
- [ ] Incremental changes (small, focused)
- [ ] No duplication (reused existing patterns)
- [ ] Documented complex logic (docstrings)
- [ ] Tested as I built
- [ ] Followed existing patterns

**Before Committing**:
- [ ] Tests pass (`pytest`)
- [ ] Linting passes (`ruff check`)
- [ ] Type checking passes (`mypy app/`)
- [ ] No secrets in code
- [ ] Documentation updated
- [ ] Self-reviewed code

---

## Quick Reference

### Essential Commands

```bash
# Development
cd backend-python
pytest                    # Run tests
pytest --watch            # Watch mode
ruff check .              # Lint
ruff check . --fix        # Auto-fix linting
mypy app/                 # Type check
black .                   # Format code

# Search
# Note: Cursor 2.0 Composer model has optimized semantic search built-in
# Use codebase_search tool (semantic) → grep (exact) → read_file workflow
codebase_search "query"   # Semantic search (always first) - Cursor optimized
grep "pattern" app/       # Exact pattern search
rg "pattern" app/         # Fast search (if ripgrep installed)

# Git
git commit -m "feat: description [YYYY-MM-DD HH:MM]"
git diff --cached         # Review staged changes
```

### Cursor 2.0 Integration

**Built-in Features** (verified from official docs - don't duplicate):
- ✅ **Semantic Search**: Composer model has optimized codebase-wide semantic search ([Cursor Blog](https://cursor.com/blog/2-0/))
- ✅ **Code Review**: Enhanced review interface for multi-file changes ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **Multi-Agent**: Interface for managing multiple agents in parallel ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **Team Commands**: Centralized custom commands and rules ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **ESLint Integration**: AI-powered lint fixing ([Docs](https://docs.cursor.com/en/guides/languages/javascript))

**This Project Adds**:
- ✅ Pre-commit hooks (automated quality checks)
- ✅ Project-specific rules (`.cursorrules`)
- ✅ Quality checklist (supplements Cursor's review)

### Key Files

- **REQUIREMENTS.md** - Outcome-based requirements
- **DESIGN_HOOKS.md** - Design exercise flags
- **TASKS.md** - Task breakdown with dependencies
- **DEMO_ARCHITECTURE.md** - Architecture design
- **AGENTS_GUIDE.md** - Comprehensive agent guidelines
- **PROJECT_RULES.md** - This file

---

## Related Documents

- **[AGENTS_GUIDE.md](docs/demo-machine/AGENTS_GUIDE.md)** - Full agent development guidelines (2059 lines)
- **[AGENTS_GUIDE_SUMMARY.md](docs/demo-machine/AGENTS_GUIDE_SUMMARY.md)** - Summary and analysis
- **[REQUIREMENTS.md](REQUIREMENTS.md)** - Functional requirements
- **[TASKS.md](docs/demo-machine/TASKS.md)** - Task breakdown

---

**Last Updated**: 2026-01-11  
**Version**: 1.0.0  
**Status**: Active
