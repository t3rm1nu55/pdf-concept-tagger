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
**Cursor 2.0** can run up to 8 agents in parallel, each in isolated codebase copies.

**✅ Use**: Cursor's multi-agent interface for parallel development  
**✅ Align**: With our parallel tracks (Track 1: Experiment, Track 2: Demo Machine)

### 4. Sandboxed Terminals
**Cursor 2.0** provides sandboxed terminals for secure command execution.

**✅ Use**: Cursor's sandboxed terminals for testing and development

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
- ❌ Custom semantic search (Cursor's is optimized)
- ❌ Custom code review UI (Cursor's is built-in)
- ❌ Custom multi-agent system (Cursor's is native)
- ❌ Custom terminal sandboxing (Cursor's is secure)

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

**Cursor 2.0 Provides**:
- ✅ Optimized semantic search (Composer model)
- ✅ Enhanced code review interface
- ✅ Multi-agent parallel development
- ✅ Sandboxed terminals

**This Project Adds**:
- ✅ Project-specific rules (`.cursorrules`)
- ✅ Quality checklists (supplements)
- ✅ Pre-commit hooks (optional automation)
- ✅ Documentation (PROJECT_RULES.md, etc.)

**Key Principle**: Leverage Cursor's optimizations, supplement with project-specific standards.

---

**Last Updated**: 2026-01-11  
**Status**: ✅ Optimized for Cursor 2.0
