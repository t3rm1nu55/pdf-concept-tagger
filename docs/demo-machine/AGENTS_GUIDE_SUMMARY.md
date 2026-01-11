# Agents Guide Summary & Analysis

## Overview

The **Agent Development Guidelines** (2059 lines) is a comprehensive guide for AI agents working on software development tasks. It provides structured workflows, decision frameworks, and best practices.

## Core Proposals

### 1. **Semantic-First Search Strategy**
**Proposal**: Always use `codebase_search` (semantic) before `grep` (exact)
- **Why**: Semantic search understands meaning and relationships, not just keywords
- **Workflow**: Semantic search → Exact grep → Read specific files
- **Benefit**: Finds related code automatically, reduces missed patterns

### 2. **Progressive Disclosure Pattern**
**Proposal**: Start broad (semantic), narrow (exact), then read (specific)
- **Pattern**: `codebase_search` → `grep` → `read_file`
- **Rationale**: Leverages semantic indexing to understand codebase structure
- **Efficiency**: Reduces unnecessary tool calls, finds context faster

### 3. **Tool Calling Decision Framework**
**Proposal**: Clear decision tree for when to call tools vs. think/read
- **Always Call**: Starting tasks, searching codebase, making changes, verifying
- **Don't Call**: When answer is known, info in current context, speculating
- **Decision Framework**: Mermaid diagrams + YAML for machine parsing

### 4. **Incremental & Modular Development**
**Proposal**: Small focused changes, build on existing patterns
- **Principles**: No duplication, modular components, document as you go
- **Workflow**: Plan → Implement incrementally → Test → Document → Review
- **Quality**: Typed, tested, documented, no breaking changes

### 5. **Mocking Guidelines (Critical)**
**Proposal**: Strict rules about when/where/how to mock
- **NEVER Mock In**: Production code, integration tests, E2E tests
- **Mock Only**: External APIs, file system, time-dependent functions
- **Identification**: Clear naming (`mock*` prefix), isolated to test files
- **Removal**: Remove mocks when real implementation available

### 6. **Requirements → Design → Tasks Pipeline**
**Proposal**: Structured workflow from user needs to implementation
- **Requirements**: User needs → Success criteria → Constraints → Documentation
- **Design**: Requirements → Research patterns → Design approach → Document
- **Tasks**: Design → Break down → Dependencies → Assignment → Tracking
- **Alignment**: Link to long-term objectives, validate success criteria

### 7. **State-Based Actions (Not Time-Based)**
**Proposal**: Act when indicators show need, not on schedule
- **Examples**: Cleanup when technical debt accumulates, optimize when performance issues detected
- **Indicators**: Unused imports, commented code, duplicate functions, build warnings
- **Benefit**: Proactive maintenance, efficient resource usage

### 8. **Transparency Requirements**
**Proposal**: Document planning, show alternatives, explain decisions
- **Planning**: Document what, why, how in task tracking
- **Decisions**: Show alternatives considered, explain why chosen
- **Actions**: Log significant actions for debugging/learning
- **Format**: Structured notes with alternatives, risks, dependencies

### 9. **Agent Guide CLI System**
**Proposal**: Contextual help system via CLI script
- **Usage**: `./scripts/agent-guide.sh task [type]` or `stage [stage]`
- **Stages**: Planning, research, design, implementation, testing, review, documentation, complete
- **Task Types**: new-component, bug-fix, new-feature, library-selection, testing, refactor
- **Output**: Relevant sections from guide with line numbers

### 10. **Pragmatic Decision-Making Framework**
**Proposal**: Balance ideal solutions with real-world constraints
- **Principles**: Good enough > perfect, reuse > build, incremental > big bang
- **Framework**: Decision tree for when to be pragmatic vs. thorough
- **Examples**: Use proven libraries, start simple and refactor, test critical paths first

### 11. **Long-Run Objective Focus**
**Proposal**: Ensure all work aligns with long-term platform objectives
- **Process**: Identify objectives → Link work → Evaluate alignment → Document → Review
- **Alignment Check**: Explicitly link tasks/features to objectives
- **Maintenance**: Review alignment during code reviews, before starting work

### 12. **Success Criteria Alignment**
**Proposal**: Ensure success criteria are measurable and aligned
- **Process**: Define criteria → Align with requirements → Make measurable → Validate → Verify
- **Format**: Clear, testable criteria with verification methods
- **Principles**: Each criterion supports requirement, testable, measurable, aligned with objectives

### 13. **Issue Management System**
**Proposal**: Structured approach to identifying, storing, reviewing, and solving issues
- **Identification**: When to create issues (bugs, blockers, unexpected behavior)
- **Storage**: Critical → immediate, Non-critical → backlog, Quick fix → immediate
- **Review**: Daily (critical), Weekly (all), Before sprint, After incident
- **Solving**: Immediate (critical/blocking), Soon (high severity), Defer (low impact)

### 14. **Testing Pyramid Strategy**
**Proposal**: Many unit tests → Some integration → Few E2E
- **Unit**: `*.test.ts` next to source, Vitest, 80%+ coverage
- **Component**: React Testing Library, test user interactions
- **Integration**: `tests/integration/`, Playwright for E2E
- **Naming**: `it('should do X')`, AAA pattern

### 15. **Code Review Checklist**
**Proposal**: Comprehensive checklist before every commit/PR
- **Self-Review**: Design principles, no duplication, tests pass, docs updated, lint/build pass
- **Security**: No secrets, input validation, no sensitive data in logs
- **Quality**: Error handling, accessibility, performance, consistency
- **Reviewing Others**: Understand change, check edge cases, verify tests, constructive feedback

## Key Workflows

### Development Workflow
1. Review DESIGN.md → `codebase_search` → `grep` → Create todos
2. Implement incrementally → Test → Document → Review → Commit
3. Verify: `npm run lint && npm test && npm run build`

### Task Workflow
1. **Planning**: Understand goal → Research → Break down → Document plan
2. **Execution**: Start small (MVP) → Iterate → Document decisions → Verify
3. **Completion**: Review → Test → Document → Commit

### Bug Fix Workflow
1. Reproduce issue
2. Document findings (what, where, why)
3. Investigate (codebase_search → grep → read_file)
4. Write failing test
5. Fix bug
6. Verify (test passes, build succeeds, no regressions)
7. Check for similar issues

### Library Selection Workflow
1. Check existing (`codebase_search` → `grep`)
2. Research with Context7 MCP
3. Compare (bundle size, maintenance, docs)
4. Decide (ADR if significant)
5. Implement and test

## Decision Frameworks

### When to Create Component?
- Similar exists? → Reuse/extend
- Need 2+ variations? → Base component + variants
- One-time use? → Inline or utility
- Complex, reusable? → Create new component

### When to Create ADR?
- New library? → ✅ Yes
- Architectural pattern? → ✅ Yes
- Small implementation detail? → ❌ No (comment in code)
- Bug fix? → ❌ No

### When to Write Tests?
- Pure function? → ✅ Unit test
- React component? → ✅ Component test
- API integration? → ✅ Integration test
- Complex business logic? → ✅ All levels

## Critical Rules

1. **Never mock in production code** - Mocks only in `*.test.ts` or `__mocks__/`
2. **Never hardcode secrets** - Use environment variables
3. **Always search codebase first** - `codebase_search` (semantic) → `grep` (exact)
4. **State-based actions** - Act when indicators show need, not time-based
5. **Document as you go** - JSDoc for complex logic, explain "why"

## Key Principles

1. **Incremental & Modular** - Small focused changes, reusable components
2. **No Duplication** - Search first, extract common patterns
3. **Best-in-Class Libraries** - Use proven tools (MUI v6, Zustand, React Query)
4. **Security First** - Validate inputs, no secrets in code
5. **Test Critical Paths** - Write tests for business logic
6. **Transparency** - Document planning, show alternatives, explain decisions

## Tools & Utilities

### Essential Tools
- **Agent Guide CLI**: `./scripts/agent-guide.sh task [type]` - Contextual help
- **Context7 MCP**: Library research and documentation
- **codebase_search**: Semantic search (always use first)
- **grep/rg**: Exact pattern matching (after semantic search)

### Development Tools
- **Type Check**: `npx tsc --noEmit`
- **Lint**: `npm run lint -- --fix`
- **Test**: `npm test -- --watch`
- **Build**: `npm run build`

## Patterns & Examples

### Component Pattern
- TypeScript interfaces
- React Query for data fetching
- Error handling with try-catch
- Loading/error states
- JSDoc documentation
- MUI components

### Hook Pattern
- TypeScript interfaces for options/return
- useState for local state
- useCallback for handlers
- useEffect for side effects
- Error handling
- JSDoc documentation

### API Hook Pattern (React Query)
- useQuery for fetching
- useMutation for mutations
- Query invalidation on success
- Error handling in onError

## Special Features

### Machine-Readable Format
- YAML structured data alongside markdown
- Mermaid diagrams for visual workflows
- Pattern IDs for automated detection
- Hook triggers for automated guidance

### Section Metadata
- `SECTION_ID`: Unique identifier
- `READ_FOR`: When to read this section
- `MUST_READ`: Critical sections
- `HOOK_TRIGGERS`: When to reference this section

### Anthropic Plugin Comparison
- References to Anthropic's 23 official plugins
- When to use Anthropic tools vs. our documentation
- Gap analysis and recommendations

## Applicability to PDF Concept Tagger

### Highly Applicable
- ✅ Semantic-first search strategy (works for any codebase)
- ✅ Tool calling decision framework (universal)
- ✅ Incremental & modular development (best practice)
- ✅ Mocking guidelines (critical for testing)
- ✅ Requirements → Design → Tasks pipeline (structured workflow)
- ✅ State-based actions (efficient resource usage)
- ✅ Transparency requirements (good for collaboration)
- ✅ Pragmatic decision-making (balances ideal vs. practical)

### Needs Adaptation
- ⚠️ Agent Guide CLI (needs script creation)
- ⚠️ Repository structure (specific to React/Next.js, needs Python equivalent)
- ⚠️ Component patterns (React-specific, needs Python/FastAPI equivalents)
- ⚠️ Testing strategy (Vitest/React Testing Library, needs pytest equivalents)
- ⚠️ Library selection (MUI/Zustand/React Query, needs Python equivalents)

### Not Applicable (Yet)
- ❌ Frontend-specific patterns (we're building backend first)
- ❌ React component patterns (we're using Python/FastAPI)
- ❌ Next.js specific workflows (we're using FastAPI)

## Recommendations for PDF Concept Tagger

### Immediate Actions
1. **Adapt semantic search strategy** - Use `codebase_search` first, then `grep`
2. **Implement tool calling framework** - Use decision trees for when to call tools
3. **Create requirements → design → tasks pipeline** - Structure our development
4. **Establish mocking guidelines** - Critical for testing backend services
5. **Set up transparency requirements** - Document planning and decisions

### Short Term
1. **Create Python/FastAPI equivalents** - Adapt component patterns for backend
2. **Set up pytest testing strategy** - Adapt testing pyramid for Python
3. **Create agent guide CLI** - Adapt for our Python/LangChain stack
4. **Establish ADR process** - Document architectural decisions

### Long Term
1. **Adapt for LangChain agents** - Create agent-specific patterns
2. **Set up monitoring & evaluation** - Track agent performance
3. **Create Python code patterns** - FastAPI, Pydantic, LangChain patterns
4. **Establish review process** - Code review checklist for Python

## Key Insights

1. **Semantic search is powerful** - Understanding meaning > text matching
2. **Progressive disclosure works** - Start broad, narrow, then read specific
3. **State-based actions are efficient** - Act on indicators, not schedules
4. **Transparency enables learning** - Document planning and decisions
5. **Pragmatic > perfect** - Balance ideal solutions with constraints
6. **Mocking must be obvious** - Clear identification and justification required
7. **Long-term alignment matters** - Link work to objectives
8. **Success criteria must be measurable** - Testable, verifiable outcomes

## Conclusion

The Agents Guide proposes a **comprehensive, structured approach** to AI-assisted software development with:
- Clear decision frameworks
- Progressive disclosure patterns
- Semantic-first search strategy
- Transparency requirements
- Pragmatic decision-making
- Long-term objective alignment

**For PDF Concept Tagger**: Highly applicable concepts, but needs adaptation for Python/FastAPI/LangChain stack. The core principles and workflows are universal and valuable.
