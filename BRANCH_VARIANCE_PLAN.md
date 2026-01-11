# Branch Variance Plan

## Current State Analysis

### What Should Differ Between Branches

#### `main` Branch (Production)
**Purpose**: Production-ready, stable code
**Should Have**:
- ✅ Clean root documentation (README, REQUIREMENTS, CONTEXT)
- ✅ Production-ready code (when ready)
- ✅ Stable releases only
- ❌ No development code
- ❌ No experimental features

**Current State**: ✅ Correct - Only documentation, no code differences yet

#### `develop` Branch (Integration)
**Purpose**: Integration branch for all features
**Should Have**:
- ✅ All shared documentation
- ✅ Merged features from both tracks
- ✅ Integration testing
- ✅ Development coordination docs

**Current State**: ✅ Correct - Same as main, ready for integration

#### `track1-experiment` Branch (Experimentation)
**Purpose**: Fast iteration, immediate experimentation
**Should Have**:
- ✅ `experiment-backend/` - Working experimentation backend
- ✅ Experiment-specific documentation
- ✅ Quick start guides
- ✅ Prompt templates
- ✅ Test scripts
- ❌ No production code
- ❌ No full demo machine code

**Current State**: ✅ Correct - Has experiment-backend/, but code is same as other branches

#### `track2-demo-machine` Branch (Full Demo)
**Purpose**: Production-like system with proper architecture
**Should Have**:
- ✅ `backend-python/` - Full backend structure
- ✅ `docs/demo-machine/` - Complete demo machine docs
- ✅ Task breakdowns
- ✅ Architecture designs
- ✅ Setup guides
- ❌ No experiment backend code
- ❌ No legacy code (when migrated)

**Current State**: ✅ Correct - Has docs/demo-machine/, but code structure same as other branches

## Key Insight: Code vs Documentation Variance

### Current Reality
**All branches are identical in terms of CODE** - they all have:
- Same `experiment-backend/` directory
- Same `backend-python/` directory (empty structure)
- Same `src/` (legacy Angular)
- Same `backend/` (legacy Node.js)

**Branches differ only in DOCUMENTATION**:
- Different READMEs pointing to different docs
- Track-specific documentation directories
- Different quick start guides

### What Should Happen Next

#### Phase 1: Documentation Variance (✅ DONE)
- ✅ Different READMEs per branch
- ✅ Track-specific documentation
- ✅ Branch-specific guides

#### Phase 2: Code Variance (🚧 TO DO)
**Track 1 (`track1-experiment`):**
- Keep `experiment-backend/` active and evolving
- Remove or ignore `backend-python/` (not needed)
- Remove or ignore `docs/demo-machine/` (not needed)
- Focus on experimentation features

**Track 2 (`track2-demo-machine`):**
- Build out `backend-python/` with full implementation
- Remove or ignore `experiment-backend/` (or keep as reference)
- Focus on production architecture
- Follow TASKS.md implementation

**`develop` Branch:**
- Merge validated features from both tracks
- Keep both codebases until migration complete
- Integration testing

**`main` Branch:**
- Only production-ready code
- No experimental features
- Stable releases

## Implementation Plan

### Immediate (Now)
**Status**: ✅ Documentation variance complete
- Branches have different READMEs
- Branches point to different documentation
- Clear separation of concerns documented

### Short Term (Week 1-2)
**Track 1**: 
- Start developing in `experiment-backend/`
- Add features, test prompts, iterate
- Keep it simple and fast

**Track 2**:
- Start implementing `backend-python/` structure
- Follow TASKS.md Week 1 tasks
- Set up databases, basic services

### Medium Term (Week 3+)
**Track 1**:
- Continue experimentation
- Document findings
- Share learnings with Track 2

**Track 2**:
- Implement LangChain agents
- Build RAG pipeline
- Create frontend

**Develop**:
- Merge Track 1 learnings
- Merge Track 2 features as ready
- Integration testing

### Long Term (When Ready)
**Main**:
- Merge from develop when stable
- Production releases
- Tagged versions

## Answer to Question

**Q: What variances do we want and are they implemented?**

**A**: 
- **Documentation variance**: ✅ YES - Implemented
- **Code variance**: ❌ NO - Not yet implemented (all branches have same code)
- **Structure variance**: ⚠️ PARTIAL - Directories exist but content is same

**Q: Is it just README or does nothing differ until detailed design?**

**A**: 
- Currently: **Just README and documentation differ**
- Code is **identical** across all branches
- **No code differences** until we start implementing
- This is **correct** - we haven't started development yet

**Q: When will branches actually differ in code?**

**A**:
- **Track 1**: When we start modifying `experiment-backend/server.py`
- **Track 2**: When we start implementing `backend-python/app/`
- **Develop**: When we merge features from tracks
- **Main**: When we release stable versions

## Recommendation

**Current state is CORRECT**:
- ✅ Documentation is properly separated
- ✅ Structure is ready for development
- ✅ Code will diverge naturally as development starts
- ✅ No need to force code differences before development begins

**Next Steps**:
1. Start Track 1 development in `track1-experiment` branch
2. Start Track 2 development in `track2-demo-machine` branch
3. Branches will naturally diverge as code is written
4. Merge to `develop` when features are validated
