# Start Here: Parallel Development Setup

## 🚀 Quick Start (Choose Your Track)

### Track 1: Experimentation Backend (10 minutes)
**For immediate experimentation with prompts, models, techniques**

```bash
cd experiment-backend
./setup.sh
# Edit .env with API keys
source venv/bin/activate
python server.py
```

**Test it:**
```bash
python test_experiment.py
```

**What you can do:**
- ✅ Experiment with prompts via API
- ✅ Switch between OpenAI/Claude/Gemini
- ✅ Test extraction techniques
- ✅ Try different model configurations
- ✅ See results immediately

### Track 2: Full Demo Machine (Follow TASKS.md)
**For production-like system with proper architecture**

**Week 1 Setup:**
```bash
# Start databases
docker-compose up -d

# Set up backend (when ready)
cd backend-python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Follow TASKS.md for implementation
```

## 📋 Development Plan

### This Week: Both Tracks Start

**Track 1 (Experiment)** - Immediate:
- ✅ Backend running (10 min setup)
- Day 1: Test with real PDFs
- Day 2: Experiment with prompts
- Day 3: Try different models
- Day 4: Document findings
- Day 5: Share learnings with Track 2

**Track 2 (Full Demo)** - Foundation:
- Day 1-2: Set up databases (T1.1-T1.7)
- Day 3-4: Create service layers (T2.1-T2.4)
- Day 5: Set up FastAPI structure (T1.5)

### Next Week: Agent Development

**Track 1**: Add basic LangChain agents (simplified)
**Track 2**: Implement full LangChain/LangGraph agents (T3.1-T3.8)

### Week 3+: Integration

**Track 1 learnings** → **Track 2 implementation**
- Validated prompts → Use in production
- Working techniques → Implement properly
- Model preferences → Configure

## 🗂️ Project Structure

```
pdf-concept-tagger/
├── experiment-backend/     # Track 1: Quick experimentation
│   ├── server.py          # FastAPI server
│   ├── prompts/           # Prompt templates
│   └── requirements.txt
│
├── backend-python/        # Track 2: Full demo machine
│   ├── app/               # (To be created)
│   └── requirements.txt
│
├── shared/                # Shared between tracks
│   └── models.py         # Shared data models
│
├── frontend-react/        # Track 2: React frontend (To be created)
│
├── src/                   # Current Angular frontend (keep for now)
│
├── TASKS.md              # Detailed task breakdown
├── DEMO_ARCHITECTURE.md  # Full architecture
├── PARALLEL_DEVELOPMENT.md # This plan
└── QUICK_START.md        # Quick reference
```

## 🔄 Coordination

### Daily Standup (15 min)
- Track 1: What worked, what didn't, findings
- Track 2: Architecture decisions, blockers
- Both: Coordinate on shared interfaces

### Weekly Review (1 hour)
- Review Track 1 learnings
- Incorporate into Track 2
- Update shared components
- Plan next week

### Shared Components
- **Models**: `shared/models.py` (both tracks use)
- **Prompts**: `shared/prompts/` (both tracks contribute)
- **API Contract**: Same endpoints (both tracks compatible)

## 📊 Progress Tracking

### Track 1 Milestones
- [x] Backend running
- [ ] First PDF processed
- [ ] Prompt experimentation working
- [ ] Model switching working
- [ ] Findings documented

### Track 2 Milestones
- [ ] Databases set up
- [ ] Basic services created
- [ ] LangChain agents working
- [ ] RAG pipeline integrated
- [ ] Frontend connected

## 🎯 Success Criteria

**Track 1 Success:**
- Can experiment with prompts/models immediately
- Findings documented and shared
- Validated approaches ready for Track 2

**Track 2 Success:**
- Production-like system running
- All features from requirements implemented
- Ready for demo/presentation

## 🚦 Getting Started Right Now

1. **Start Track 1** (10 minutes):
   ```bash
   cd experiment-backend && ./setup.sh
   ```

2. **Test it**:
   ```bash
   python test_experiment.py
   ```

3. **Experiment**:
   - Edit prompts in `experiment-backend/prompts/`
   - Test via API: `POST /api/v1/prompts/experiment`
   - Switch models: `POST /api/v1/models/switch`

4. **Start Track 2** (when ready):
   - Follow TASKS.md Week 1 tasks
   - Set up databases
   - Create service layers

## 📚 Documentation

- **TASKS.md**: Detailed task breakdown with dependencies
- **DEMO_ARCHITECTURE.md**: Full architecture design
- **PARALLEL_DEVELOPMENT.md**: This parallel development plan
- **QUICK_START.md**: Quick reference guide
- **DEMO_SETUP.md**: Detailed setup instructions

## 💡 Tips

1. **Track 1 First**: Get experimentation backend running immediately
2. **Share Learnings**: Document what works in Track 1
3. **Parallel Work**: Track 2 can start while Track 1 experiments
4. **Merge Later**: Track 1 learnings inform Track 2 design
5. **Keep Simple**: Track 1 stays simple, Track 2 is comprehensive
