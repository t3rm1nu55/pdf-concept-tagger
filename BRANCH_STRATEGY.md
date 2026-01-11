# Branch Strategy

## Branch Structure

### Main Branches

- **`main`** - Production-ready code (stable releases)
- **`develop`** - Integration branch for all features

### Feature Branches

- **`track1-experiment`** - Experimentation backend (fast iteration)
- **`track2-demo-machine`** - Full demo machine development
- **`feature/*`** - Individual features (e.g., `feature/rag-pipeline`)

### Other Branches

- **`docs/*`** - Documentation updates
- **`fix/*`** - Bug fixes
- **`refactor/*`** - Code refactoring

## Workflow

### Track 1 (Experiment Backend)
```bash
git checkout track1-experiment
# Make changes
git commit -m "Experiment: test new prompt"
git push origin track1-experiment
# Merge to develop when validated
```

### Track 2 (Demo Machine)
```bash
git checkout track2-demo-machine
# Make changes
git commit -m "Implement LangChain agents"
git push origin track2-demo-machine
# Merge to develop when complete
```

### Integration
```bash
git checkout develop
git merge track1-experiment  # When Track 1 features validated
git merge track2-demo-machine  # When Track 2 features ready
```

### Release
```bash
git checkout main
git merge develop
git tag v1.0.0
git push origin main --tags
```

## Branch Protection

- `main`: Requires PR review, CI passing
- `develop`: Requires CI passing
- Feature branches: No restrictions

## Naming Conventions

- Feature: `feature/description`
- Fix: `fix/description`
- Refactor: `refactor/description`
- Docs: `docs/description`
