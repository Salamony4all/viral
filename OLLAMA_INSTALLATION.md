# 🐳 OLLAMA INSTALLATION & SETUP GUIDE

## ⚠️ Important Notice

Ollama requires an installer that needs to run with your user interaction. Here's how to install it:

## Option 1: Direct Download & Install (Recommended)

### Step 1: Download Ollama
1. Go to: **https://ollama.ai**
2. Click "Download" (Windows version)
3. This will download `OllamaSetup.exe` (~226 MB)

### Step 2: Install Ollama
1. Run the downloaded `OllamaSetup.exe`
2. Follow the installation wizard
3. Choose your installation directory (default is fine)
4. Complete the installation

### Step 3: Verify Installation
```powershell
# Check if ollama command is available
ollama --version

# Should output something like:
# ollama version 0.1.32
```

### Step 4: Start Ollama Server
```powershell
# Start the Ollama server
ollama serve

# You should see:
# Listening on 127.0.0.1:11434
```

---

## Option 2: Using Docker (If You Prefer)

### Step 1: Start Ollama Container
```powershell
docker run -d \
  --name ollama \
  -p 11434:11434 \
  ollama/ollama:latest
```

### Step 2: Pull a Model
```powershell
docker exec ollama ollama pull mistral
```

### Step 3: Access the Server
- API: `http://localhost:11434`
- Test: `curl http://localhost:11434/api/tags`

---

## Option 3: Pre-Built Scripts

If you want automation, create a PowerShell script file `start_ollama.ps1`:

```powershell
# start_ollama.ps1

Write-Host "Starting Ollama Server..."

# Check if ollama is installed
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Ollama not installed!"
    Write-Host ""
    Write-Host "Please install Ollama first:"
    Write-Host "1. Visit: https://ollama.ai"
    Write-Host "2. Download and run OllamaSetup.exe"
    Write-Host "3. Restart this script after installation"
    exit 1
}

Write-Host "✓ Ollama found!"
Write-Host ""
Write-Host "Checking for mistral model..."

# Check if model exists
$models = ollama list 2>&1
if ($models -notmatch "mistral") {
    Write-Host "⏳ Pulling mistral model (first time only, ~4GB)..."
    ollama pull mistral
} else {
    Write-Host "✓ Mistral model already installed"
}

Write-Host ""
Write-Host "🚀 Starting Ollama server..."
Write-Host "Server will be available at: http://localhost:11434"
Write-Host ""
ollama serve
```

---

## Verification

Once Ollama is running, verify in a new PowerShell window:

```powershell
# Check API health
curl http://localhost:11434/api/tags

# Should return JSON with available models
```

---

## Troubleshooting

### "ollama: The term is not recognized"
- **Cause**: Ollama not installed or not in PATH
- **Fix**: Download and run the installer from https://ollama.ai

### "Port 11434 already in use"
- **Cause**: Another Ollama instance is running
- **Fix**: Kill the process or use a different port

### "Installation takes a long time"
- **Cause**: First-time setup downloads models
- **Fix**: Be patient, especially for large models like mistral (~4GB)

### "Model pull fails"
- **Cause**: Network issues or storage space
- **Fix**: Check internet connection and available disk space (>10GB recommended)

---

## Next Steps

Once Ollama is installed and running:

1. ✓ Ollama server is running on `localhost:11434`
2. ✓ Models are available via the API
3. ✓ You're ready to use the Viral Engine!

Then run:
```bash
python main.py "your topic"
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start server | `ollama serve` |
| Pull model | `ollama pull mistral` |
| List models | `ollama list` |
| Test API | `curl http://localhost:11434/api/tags` |
| Stop server | `Ctrl+C` |

---

**Note**: The Ollama installer needs interactive mode. Please download from https://ollama.ai and run it directly on your Windows machine.
