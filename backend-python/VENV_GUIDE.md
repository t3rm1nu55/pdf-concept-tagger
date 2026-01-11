# Virtual Environment Management Guide

## Quick Setup

### Automated Setup (Recommended)

```bash
cd backend-python
./setup.sh
source venv/bin/activate
```

This will:
- ✅ Create virtual environment (`venv/`)
- ✅ Upgrade pip
- ✅ Install all dependencies from `requirements.txt`
- ✅ Create `.env.example` and `.env` files
- ✅ Check Python version

### Manual Setup

```bash
cd backend-python

# Create virtual environment
python3 -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

## Daily Usage

### Activate Virtual Environment

**Linux/Mac:**
```bash
cd backend-python
source venv/bin/activate
```

**Windows:**
```bash
cd backend-python
venv\Scripts\activate
```

**Verify it's activated:**
```bash
which python  # Should show: .../backend-python/venv/bin/python
pip list      # Should show installed packages
```

### Deactivate

```bash
deactivate
```

## Managing Dependencies

### Install New Package

```bash
# Make sure venv is activated
source venv/bin/activate

# Install package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

### Update All Packages

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Remove Package

```bash
source venv/bin/activate
pip uninstall package_name
pip freeze > requirements.txt
```

## Troubleshooting

### Virtual Environment Not Found

```bash
# Recreate venv
rm -rf venv
./setup.sh
```

### Wrong Python Version

```bash
# Use specific Python version
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Package Installation Fails

```bash
# Upgrade pip first
source venv/bin/activate
pip install --upgrade pip setuptools wheel

# Try again
pip install -r requirements.txt
```

### Permission Errors (Linux/Mac)

```bash
# Make sure you own the venv directory
sudo chown -R $USER:$USER venv/
```

## Best Practices

1. **Always activate venv before working**
   ```bash
   source venv/bin/activate
   ```

2. **Check if activated**
   - Your prompt should show `(venv)`
   - `which python` should point to venv

3. **Keep requirements.txt updated**
   ```bash
   pip freeze > requirements.txt
   ```

4. **Don't commit venv/**
   - Already in `.gitignore`
   - Each developer creates their own

5. **Use .env for secrets**
   - `.env` is in `.gitignore`
   - Copy from `.env.example`
   - Never commit `.env`

## IDE Integration

### VS Code

VS Code should auto-detect the venv. If not:

1. Open Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Type "Python: Select Interpreter"
3. Choose `./venv/bin/python`

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Click gear icon → Add
3. Select "Existing environment"
4. Choose `./venv/bin/python`

## Production Deployment

For production, you typically:
- Use Docker with a virtual environment
- Or install directly to system Python (not recommended)
- Or use a tool like `pipenv` or `poetry`

For this project, Docker is recommended (see `docker-compose.yml`).

## Common Commands Reference

```bash
# Setup
./setup.sh                          # Initial setup
source venv/bin/activate            # Activate
deactivate                          # Deactivate

# Dependencies
pip install package                 # Install
pip uninstall package               # Remove
pip list                           # List installed
pip freeze > requirements.txt      # Update requirements

# Verification
which python                        # Check Python path
python --version                    # Check version
pip --version                       # Check pip version
```
