# Documentation Organization by Branch

## Branch-Specific Documentation Strategy

### `main` Branch (Production/Stable)
**Purpose**: Production-ready documentation
- README.md - Main project overview
- REQUIREMENTS.md - Final requirements
- CONTEXT.md - Project context
- LICENSE - License file (if exists)

### `develop` Branch (Integration)
**Purpose**: Development coordination and workflow
- PARALLEL_DEVELOPMENT.md - Coordination between tracks
- REPO_STRUCTURE.md - Repository structure
- BRANCH_STRATEGY.md - Git workflow
- START_HERE.md - Entry point for developers
- QUICK_START.md - Quick reference

### `track1-experiment` Branch
**Purpose**: Experimentation backend documentation
- experiment-backend/README.md - Experiment backend guide
- experiment-backend/QUICK_START.md - Quick start for experiments
- experiment-backend/PROMPTS.md - Prompt experimentation guide
- CONTEXT.md - Project context (shared)

### `track2-demo-machine` Branch
**Purpose**: Full demo machine documentation
- DEMO_ARCHITECTURE.md - Full architecture design
- DEMO_SETUP.md - Detailed setup instructions
- TASKS.md - Task breakdown
- REFACTORING_PLAN.md - Migration plan
- DESIGN_HOOKS.md - Design hooks reference
- backend-python/README.md - Backend guide
- CONTEXT.md - Project context (shared)

### Shared Documentation (All Branches)
- CONTEXT.md - Project context
- .gitignore - Git ignore rules
- docker-compose.yml - Local development setup

## Implementation Plan

1. Organize docs into branch-specific directories
2. Keep shared docs in root
3. Update READMEs to point to branch-specific docs
4. Ensure each branch has what it needs
