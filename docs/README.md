# PDF Concept Tagger - Documentation

> **Single source of truth for all project documentation**

## 📖 Quick Navigation

### 🚀 Getting Started
- **[Quick Start Guide](GETTING_STARTED.md)** - Get up and running in 5 minutes
- **[Setup Guide](SETUP.md)** - Complete setup instructions
- **[MVP Status](MVP_STATUS.md)** - Current MVP status and features

### 📋 Project Documentation
- **[Requirements](../REQUIREMENTS.md)** - Functional requirements
- **[Design](demo-machine/DESIGN.md)** - Complete design specification
- **[Architecture](demo-machine/DEMO_ARCHITECTURE.md)** - System architecture
- **[Tasks](demo-machine/TASKS.md)** - Implementation tasks

### 🛠️ Development
- **[Project Rules](../PROJECT_RULES.md)** - Development standards and rules
- **[Code Quality](../CODE_QUALITY_CHECKLIST.md)** - Pre-commit checklist
- **[Prototype Alignment](PROTOTYPE_ALIGNMENT.md)** - Frontend integration guide

### 🔧 Configuration
- **[Gateway Setup](backend-python/GATEWAY_SETUP.md)** - Cognizant LLM Gateway
- **[Environment Config](config/ENV_CONFIG.md)** - Environment variables
- **[Proxy Deployment](config/PROXY_DEPLOYMENT.md)** - Proxy configuration

### 📚 Reference
- **[Context](../CONTEXT.md)** - Project context and history
- **[Agents Guide](demo-machine/AGENTS_GUIDE.md)** - Agent development guide
- **[API Reference](API.md)** - API documentation (coming soon)

---

## Documentation Structure

```
docs/
├── README.md                    # This file - navigation hub
├── GETTING_STARTED.md          # Quick start guide
├── SETUP.md                    # Complete setup instructions
├── MVP_STATUS.md               # Current MVP status
├── PROTOTYPE_ALIGNMENT.md      # Frontend integration guide
├── API.md                      # API reference (coming soon)
│
├── demo-machine/               # Demo machine documentation
│   ├── DESIGN.md              # Complete design spec
│   ├── DEMO_ARCHITECTURE.md   # Architecture details
│   ├── TASKS.md               # Task breakdown
│   ├── MVP_BUILD_PLAN.md      # MVP build plan
│   └── AGENTS_GUIDE.md        # Agent development guide
│
├── backend-python/             # Backend-specific docs
│   ├── README.md              # Backend overview
│   ├── GATEWAY_SETUP.md       # Gateway setup
│   └── TESTING.md             # Testing guide
│
├── config/                     # Configuration docs
│   ├── ENV_CONFIG.md          # Environment variables
│   └── PROXY_DEPLOYMENT.md    # Proxy setup
│
└── archive/                    # Archived/reference docs
    └── ARCHITECTURE.md         # Old architecture docs
```

---

## For Different Audiences

### 👨‍💻 Developers
1. Start: [GETTING_STARTED.md](GETTING_STARTED.md)
2. Read: [PROJECT_RULES.md](../PROJECT_RULES.md)
3. Build: [demo-machine/TASKS.md](demo-machine/TASKS.md)

### 🎯 Product/Design
1. Requirements: [REQUIREMENTS.md](../REQUIREMENTS.md)
2. Design: [demo-machine/DESIGN.md](demo-machine/DESIGN.md)
3. Status: [MVP_STATUS.md](MVP_STATUS.md)

### 🔧 DevOps/Setup
1. Setup: [SETUP.md](SETUP.md)
2. Gateway: [backend-python/GATEWAY_SETUP.md](backend-python/GATEWAY_SETUP.md)
3. Config: [config/ENV_CONFIG.md](config/ENV_CONFIG.md)

### 🚀 Quick Start
1. [GETTING_STARTED.md](GETTING_STARTED.md) - 5-minute setup
2. [MVP_STATUS.md](MVP_STATUS.md) - What's working
3. [PROTOTYPE_ALIGNMENT.md](PROTOTYPE_ALIGNMENT.md) - Next steps

---

## Documentation Standards

All documentation follows these principles:
- **Single source of truth** - One place for each topic
- **Progressive disclosure** - Start simple, drill down
- **Consistent structure** - Same format across docs
- **Up-to-date** - Regular updates with code changes
- **Actionable** - Clear next steps

---

## Contributing to Docs

When adding or updating documentation:
1. Check if topic already exists
2. Update existing doc rather than creating new
3. Follow existing structure and format
4. Update this README if adding new sections
5. Link from relevant places

---

**Last Updated**: 2026-01-11  
**Maintained By**: Development Team
