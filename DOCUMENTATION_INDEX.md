# Documentation Index

## Overview

This document provides a complete index of all documentation organized by branch.

## Branch: `main` (Production)

**Location**: Root directory
- `README.md` - Main project overview
- `REQUIREMENTS.md` - Functional requirements
- `CONTEXT.md` - Project context
- `docs/production/README.md` - Production documentation guide

## Branch: `develop` (Integration)

**Location**: `docs/development/`
- `PARALLEL_DEVELOPMENT.md` - Coordination between tracks
- `REPO_STRUCTURE.md` - Repository structure
- `BRANCH_STRATEGY.md` - Git workflow
- `README.md` - Development docs index

**Location**: Root directory
- `START_HERE.md` - Entry point for developers
- `QUICK_START.md` - Quick reference (if exists)

## Branch: `track1-experiment` (Experimentation)

**Location**: `experiment-backend/`
- `README.md` - Experiment backend guide
- `QUICK_START.md` - Quick start for experiments
- `prompts/` - Prompt templates with documentation

**Location**: Root directory
- `CONTEXT.md` - Project context (shared)

## Branch: `track2-demo-machine` (Demo Machine)

**Location**: `docs/demo-machine/`
- `DEMO_ARCHITECTURE.md` - Full architecture design
- `DEMO_SETUP.md` - Detailed setup instructions
- `TASKS.md` - Task breakdown with dependencies
- `REFACTORING_PLAN.md` - Migration plan
- `DESIGN_HOOKS.md` - Design hooks reference
- `README.md` - Demo machine docs index

**Location**: `backend-python/`
- `README.md` - Backend guide

**Location**: Root directory
- `CONTEXT.md` - Project context (shared)

## Shared Documentation (All Branches)

**Location**: Root directory
- `CONTEXT.md` - Project context
- `.gitignore` - Git ignore rules
- `docker-compose.yml` - Local development setup

## Finding Documentation

### For Experimentation
1. Check `track1-experiment` branch
2. See `experiment-backend/README.md`
3. See `experiment-backend/QUICK_START.md`

### For Full Demo Machine
1. Check `track2-demo-machine` branch
2. See `docs/demo-machine/README.md`
3. See `docs/demo-machine/DEMO_SETUP.md`

### For Development Workflow
1. Check `develop` branch
2. See `docs/development/README.md`
3. See `docs/development/PARALLEL_DEVELOPMENT.md`

### For Production
1. Check `main` branch
2. See `README.md`
3. See `REQUIREMENTS.md`

## Documentation Updates

- **Production docs**: Update in `main` branch only
- **Development docs**: Update in `develop` branch
- **Track-specific docs**: Update in respective track branch
- **Shared docs**: Update in all branches as needed
