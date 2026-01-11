# Root Documentation Cleanup Plan

## Current Root Docs Analysis

### ✅ Keep in Root (Essential)
- `README.md` - Main entry point, project overview
- `REQUIREMENTS.md` - Production requirements
- `CONTEXT.md` - Project context (shared)
- `DOCUMENTATION_INDEX.md` - Navigation guide

### 🔄 Move to Appropriate Location
- `BRANCH_STRATEGY.md` → `docs/development/` (already there, remove from root)
- `REPO_STRUCTURE.md` → `docs/development/` (already there, remove from root)
- `START_HERE.md` → `docs/development/` (or merge into README)
- `ENV_CONFIG.md` → `docs/config/` (create new location)
- `PROXY_DEPLOYMENT.md` → `docs/config/` or `docs/deployment/`

### 🗑️ Archive or Remove
- `ARCHITECTURE.md` - Old architecture, superseded by `docs/demo-machine/DEMO_ARCHITECTURE.md`
- `ARCHITECTURE_FROM_SCRATCH.md` - Reference doc, archive to `docs/archive/`
- `DOCS_ORGANIZATION.md` - Planning doc, can be removed (info in DOCUMENTATION_INDEX.md)

## Proposed Root Structure

```
Root/
├── README.md                    # Main entry point
├── REQUIREMENTS.md              # Production requirements
├── CONTEXT.md                   # Project context
├── DOCUMENTATION_INDEX.md       # Navigation guide
└── docs/
    ├── development/            # Development workflow docs
    ├── demo-machine/           # Demo machine docs
    ├── config/                 # Configuration docs
    └── archive/                # Archived/reference docs
```

## Action Plan

1. Move config docs to `docs/config/`
2. Archive old architecture docs to `docs/archive/`
3. Remove duplicates (DOCS_ORGANIZATION.md)
4. Move START_HERE content into README or docs/development/
5. Remove BRANCH_STRATEGY.md and REPO_STRUCTURE.md from root (already in docs/development/)
