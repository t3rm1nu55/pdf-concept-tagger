# Code Quality Checklist

> **Based on**: [PROJECT_RULES.md](PROJECT_RULES.md)  
> **Use**: Before every commit, before PR, completing a task

## Pre-Commit Checklist

### Code Quality
- [ ] **No duplication** - Searched codebase first (`codebase_search` → `grep`)
- [ ] **Modular** - Small, focused changes, single responsibility
- [ ] **Documented** - Docstrings for complex logic, explain "why"
- [ ] **Typed** - Type hints for functions, Pydantic models for data
- [ ] **Linted** - `ruff check .` passes (or `npm run lint` for frontend)
- [ ] **Formatted** - `black .` formatted (or `npm run format` for frontend)

### Testing
- [ ] **Tests pass** - `pytest` (or `npm test` for frontend)
- [ ] **Coverage** - 70%+ coverage on business logic (pragmatic: critical paths first)
- [ ] **No mocks in production** - Mocks only in `tests/` or `__mocks__/`
- [ ] **Mock identification** - Clear naming (`mock*` prefix), isolated to tests

### Documentation
- [ ] **Docstrings** - Complex functions have docstrings explaining "why"
- [ ] **README updated** - If API/usage changed
- [ ] **ADR created** - If architectural decision made (see PROJECT_RULES.md)

### Review
- [ ] **Self-reviewed** - Code follows PROJECT_RULES.md patterns
- [ ] **No breaking changes** - Or documented with migration path
- [ ] **Error handling** - Try-catch for async operations, HTTPException for API errors
- [ ] **No secrets** - No hardcoded API keys, use environment variables

### Integration
- [ ] **Builds** - `uvicorn app.main:app` starts (or `npm run build` for frontend)
- [ ] **No console errors** - Check logs for errors
- [ ] **Type check** - `mypy app/` passes (or `npx tsc --noEmit` for frontend)

### Tracking
- [ ] **Todos updated** - If using todo tracking
- [ ] **Time documented** - If tracking time
- [ ] **PRs linked** - If applicable

## Quick Commands

```bash
# Backend (Python)
pytest                    # Run tests
ruff check .              # Lint
ruff check . --fix        # Auto-fix
black .                   # Format
mypy app/                 # Type check

# Frontend (when implemented)
npm test                  # Run tests
npm run lint              # Lint
npm run lint -- --fix     # Auto-fix
npm run build             # Build
npx tsc --noEmit          # Type check
```

## Common Issues to Avoid

❌ **Duplicated logic** → Extract to utility/service  
❌ **Magic numbers/strings** → Use constants  
❌ **Missing error handling** → Always try-catch async  
❌ **Missing TypeScript types** → Type all functions  
❌ **Mocking in production code** → Mocks only in test files  
❌ **Unidentified mocks** → Always use `mock` prefix  
❌ **No docstrings** → Document complex logic  
❌ **Hardcoded secrets** → Use environment variables  

## Reference

- **[PROJECT_RULES.md](PROJECT_RULES.md)** - Full development rules
- **[AGENTS_GUIDE.md](docs/demo-machine/AGENTS_GUIDE.md)** - Comprehensive agent guidelines
