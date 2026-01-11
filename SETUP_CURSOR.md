# Cursor 2.0 Setup Guide

## Overview

This project is optimized for **Cursor 2.0** with its built-in semantic search and multi-agent capabilities. This guide shows how to leverage Cursor's features alongside project-specific tools.

## Cursor 2.0 Built-in Features ✅

### 1. Semantic Search (Already Optimized)
**Cursor's Composer model** has optimized codebase-wide semantic search built-in. 

**✅ Use**: The `codebase_search` tool leverages Cursor's optimized semantic indexing - no need to add redundant mechanisms.

**Workflow**: `codebase_search` (semantic) → `grep` (exact) → `read_file` (specific)

### 2. Code Review (Built-in)
**Cursor 2.0** has an enhanced code review interface for viewing changes across multiple files.

**✅ Use**: Cursor's built-in review interface  
**✅ Supplement**: Use [CODE_QUALITY_CHECKLIST.md](CODE_QUALITY_CHECKLIST.md) for project-specific standards

### 3. Multi-Agent Interface
**Cursor 2.0** supports running multiple agents in parallel, each operating in isolated codebase copies.

**✅ Confirmed**: Multi-agent interface with sidebar for agents and plans  
**✅ Use**: Cursor's multi-agent interface for parallel development  
**✅ Align**: With our parallel tracks (Track 1: Experiment, Track 2: Demo Machine)

**Source**: [Cursor 2.0 Changelog](https://cursor.com/changelog/2-0/)

### 4. Team Commands & Custom Rules
**Cursor 2.0** supports Team Commands, allowing teams to define and share custom commands and rules centrally.

**✅ Confirmed**: Team Commands feature for project-specific guidelines  
**✅ Use**: `.cursorrules` file provides project context (if supported)  
**✅ Alternative**: Use Team Commands for team-wide rules

**Source**: [Cursor 2.0 Changelog](https://cursor.com/changelog/2-0/)

## Project-Specific Setup

### 1. Pre-Commit Hooks (Optional)

**Status**: Optional - Cursor 2.0 has built-in code review, but pre-commit hooks provide automated checks.

**Install** (if desired):
```bash
pip install pre-commit
pre-commit install
```

**What it does**:
- Auto-lints with `ruff`
- Auto-formats with `black`
- Type checks with `mypy`
- Checks for secrets, large files, etc.

**Note**: Cursor's built-in review may catch these, but pre-commit provides automated enforcement.

### 2. `.cursorrules` File

**Status**: ✅ Created - Provides project context to Cursor

**Location**: `.cursorrules` (root directory)

**Purpose**: 
- References PROJECT_RULES.md
- Provides quick context for Cursor's AI
- Supplements (not replaces) Cursor's built-in features

**Note**: While `.cursorrules` is a common convention, Cursor 2.0 officially supports **Team Commands** for shared rules. The `.cursorrules` file serves as project-level context that Cursor's AI can read.

### 3. CODE_QUALITY_CHECKLIST.md

**Status**: ✅ Created - Supplements Cursor's review

**Purpose**: 
- Project-specific quality standards
- Pre-commit checklist
- Quick reference for common commands

**Use**: Review before commits (Cursor's review + this checklist)

### 4. PROJECT_RULES.md

**Status**: ✅ Created - Primary development rules

**Purpose**: 
- Core development principles
- Workflows and decision frameworks
- Testing and mocking guidelines

**Use**: Reference for all development decisions

## Recommended Workflow

### For Development

1. **Start Task**: Cursor's semantic search (`codebase_search`) → `grep` → `read_file`
2. **Implement**: Incremental changes (Cursor's multi-agent if needed)
3. **Review**: Cursor's built-in review + CODE_QUALITY_CHECKLIST.md
4. **Commit**: Pre-commit hooks (if installed) + manual review

### For Code Quality

1. **Cursor's Review**: Built-in multi-file review interface
2. **Checklist**: CODE_QUALITY_CHECKLIST.md for project standards
3. **Rules**: PROJECT_RULES.md for decision frameworks

### For Testing

1. **Cursor's Sandbox**: Use sandboxed terminals for test execution
2. **Pre-commit**: Automated checks (if installed)
3. **Manual**: Follow PROJECT_RULES.md mocking guidelines

## What NOT to Duplicate

**Don't add**:
- ❌ Custom semantic search (Cursor's Composer model is optimized)
- ❌ Custom code review UI (Cursor's enhanced review interface is built-in)
- ❌ Custom multi-agent system (Cursor's multi-agent interface is native)
- ❌ Redundant quality checks (Cursor's ESLint integration handles many checks)

**Do add**:
- ✅ Project-specific rules (`.cursorrules`)
- ✅ Quality checklists (supplements Cursor's review)
- ✅ Pre-commit hooks (automated enforcement)
- ✅ Documentation (PROJECT_RULES.md, etc.)

## Quick Start

1. **Open in Cursor 2.0**: Project automatically uses optimized semantic search
2. **Read `.cursorrules`**: Provides project context
3. **Reference PROJECT_RULES.md**: For development decisions
4. **Use CODE_QUALITY_CHECKLIST.md**: Before commits
5. **Optional**: Install pre-commit hooks for automated checks

## Summary

**Cursor 2.0 Provides** (Confirmed from Official Docs):
- ✅ **Semantic Search**: Composer model with codebase-wide semantic search ([Cursor Blog](https://cursor.com/blog/2-0/))
- ✅ **Code Review**: Enhanced interface for viewing changes across multiple files ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **Multi-Agent**: Interface for managing multiple agents in parallel ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **Team Commands**: Centralized custom commands and rules ([Changelog](https://cursor.com/changelog/2-0/))
- ✅ **ESLint Integration**: AI-powered lint fixing capabilities ([Docs](https://docs.cursor.com/en/guides/languages/javascript))

**This Project Adds** (Supplements, Not Replacements):
- ✅ Project-specific rules (`.cursorrules` - project context)
- ✅ Quality checklists (supplements Cursor's review)
- ✅ Pre-commit hooks (optional automation - Cursor has built-in review)
- ✅ Documentation (PROJECT_RULES.md, etc.)

**Key Principle**: Leverage Cursor's optimizations, supplement with project-specific standards.

## Official Documentation References

- **Cursor 2.0 Blog**: https://cursor.com/blog/2-0/
- **Cursor 2.0 Changelog**: https://cursor.com/changelog/2-0/
- **Cursor Docs**: https://docs.cursor.com/

## Verification Status

✅ **Verified Features** (from official docs):
- Semantic search (Composer model)
- Enhanced code review interface
- Multi-agent interface
- Team Commands for shared rules
- ESLint integration

⚠️ **Assumed/Conventional**:
- `.cursorrules` file (common convention, not explicitly documented)
- Sandboxed terminals (mentioned in some contexts, not explicitly confirmed)

---

**Last Updated**: 2026-01-11  
**Status**: ✅ Optimized for Cursor 2.0 (verified against official docs)
