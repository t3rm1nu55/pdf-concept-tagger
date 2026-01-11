# Branch Alignment Check

## Status: ✅ All Branches Aligned

Last checked: $(date)

## Branch Structure

### `main` Branch (Production)
**Root Files:**
- README.md
- REQUIREMENTS.md
- CONTEXT.md
- DOCUMENTATION_INDEX.md

**Docs Structure:**
- docs/config/ - Configuration docs
- docs/archive/ - Archived docs
- docs/development/ - Development workflow (from develop)
- docs/demo-machine/ - Demo machine docs (from track2)
- docs/production/ - Production docs

### `develop` Branch (Integration)
**Root Files:** Same as main
**Additional:** Merged from main + development-specific docs

### `track1-experiment` Branch
**Root Files:** Same as main
**Additional:** 
- experiment-backend/QUICK_START.md
- experiment-backend/README.md

### `track2-demo-machine` Branch
**Root Files:** Same as main
**Additional:**
- docs/demo-machine/ - Full demo machine documentation
- backend-python/README.md

## Alignment Rules

1. **All branches** have same root structure (4 essential files)
2. **All branches** share docs/config/ and docs/archive/
3. **Track-specific** docs only in their respective branches
4. **develop** merges from main regularly
5. **Track branches** merge from develop regularly

## Verification Commands

```bash
# Check root files consistency
for branch in main develop track1-experiment track2-demo-machine; do
  git checkout $branch
  echo "$branch: $(ls -1 *.md | wc -l) root MD files"
done

# Check docs structure
git checkout main
find docs -type d | sort
```

## Sync Status

- ✅ main → develop: Synced
- ✅ develop → track1-experiment: Synced
- ✅ develop → track2-demo-machine: Synced
- ✅ All branches have consistent root structure
- ✅ All branches have organized docs structure
