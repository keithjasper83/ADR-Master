# Offline Operation Guide

ADR-Master is designed to work completely offline without any external dependencies.

## Requirements for Offline Use

1. **Python 3.12+** installed
2. **Optional: Local LLM** (Ollama, llama.cpp, etc.)
3. **Optional: Git** (for sync features)

## Setup for Air-Gapped Environment

### 1. Prepare Dependencies

On a machine with internet:

```bash
# Download wheel files
pip download -r requirements.txt -d ./wheels

# Or if using uv
uv pip compile pyproject.toml -o requirements.txt
uv pip download -r requirements.txt -d ./wheels
```

Transfer the `wheels/` directory to your air-gapped machine.

### 2. Install Offline

```bash
# Install from local wheels
pip install --no-index --find-links=./wheels -e .
```

### 3. Configure for Offline

Create `.env`:

```env
# No MCP integration
MCP_BASE_URL=

# No GitHub integration
GITHUB_TOKEN=

# Local LLM (if available)
LLM_ENDPOINT=http://localhost:11434/api/generate

# Everything else works offline
WORKDIR=/path/to/your/project
DATABASE_URL=sqlite:///./adr_master.db
```

## Running Without LLM

If you don't have a local LLM:

1. ADR creation, editing, linting, and promotion still work
2. Only the "compile" feature will be unavailable
3. You can manually edit and improve ADRs

## Running Without Git

If you don't have Git or don't want GitHub sync:

1. All ADR operations work normally
2. Files are managed locally
3. Sync and PR features will be disabled

## Local LLM Options

### Ollama (Recommended)

```bash
# Install from https://ollama.ai
ollama pull llama2
ollama serve

# ADR-Master will connect to http://localhost:11434
```

### llama.cpp

```bash
# Build and run
./server -m models/llama-2-7b.gguf --port 11434

# Configure endpoint in .env
LLM_ENDPOINT=http://localhost:11434/v1/completions
```

### Other Options

- **GPT4All**: GUI with API mode
- **LocalAI**: OpenAI-compatible API
- **text-generation-webui**: Gradio UI with API

## Verifying Offline Operation

```bash
# 1. Disconnect from internet

# 2. Start ADR-Master
make run

# 3. Test endpoints
curl http://localhost:8000/healthz
curl -X POST http://localhost:8000/api/adr/draft \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","problem":"Test problem","context":"Test context"}'

# 4. Open browser
# Visit http://localhost:8000
```

## Data Storage

All data is stored locally:

- **ADRs**: `./ADR/` and `./ADR/Draft/`
- **Database**: `./adr_master.db` (SQLite)
- **Logs**: `./_logs/`
- **Config**: `.env`

## Backup Strategy

```bash
# Backup everything
tar -czf adr-master-backup.tar.gz ADR/ adr_master.db .env _logs/

# Restore
tar -xzf adr-master-backup.tar.gz
```

## Limitations in Offline Mode

### Without LLM
- ❌ Automatic ADR compilation/improvement
- ✅ Manual editing and refinement
- ✅ All other features work

### Without MCP
- ❌ Project/feature awareness
- ❌ Proposal submission
- ✅ All ADR operations work
- ✅ Can still link features manually

### Without GitHub
- ❌ Automatic PR creation
- ❌ Remote sync
- ✅ Local Git operations work
- ✅ Manual push/pull possible

## Network-Isolated Deployment

For organizations requiring network isolation:

1. **Docker image**: Build and transfer image file
2. **Dependencies**: Pre-downloaded wheels
3. **LLM models**: Pre-downloaded model files
4. **Documentation**: Included in repo

Example Docker deployment:

```bash
# On internet-connected machine
docker build -t adr-master:offline .
docker save adr-master:offline > adr-master-offline.tar

# Transfer to air-gapped machine
docker load < adr-master-offline.tar
docker run -p 8000:8000 -v $(pwd)/ADR:/app/ADR adr-master:offline
```

## Security Considerations

- ✅ No telemetry or phone-home
- ✅ No external API calls (except configured)
- ✅ All processing local
- ✅ No cloud dependencies
- ✅ File-based storage

## Troubleshooting

### "Network unreachable" errors

**Cause**: Application trying to reach external services

**Solution**: Check `.env` and ensure external URLs are not set:
```env
MCP_BASE_URL=
GITHUB_TOKEN=
```

### LLM compilation fails

**Cause**: LLM endpoint not reachable

**Solution**:
1. Check LLM is running: `curl $LLM_ENDPOINT`
2. Verify endpoint in `.env`
3. Skip compilation and edit manually

### Database locked

**Cause**: Another process using SQLite database

**Solution**: 
1. Check for running instances: `ps aux | grep uvicorn`
2. Stop other instances
3. Restart application

## Best Practices

1. **Regular backups**: Use automated backup script
2. **Version ADRs in Git**: Even without GitHub
3. **Document decisions**: Use clear, detailed ADRs
4. **Test offline regularly**: Ensure dependencies don't creep in
5. **Keep local LLM updated**: Download new models periodically

## Support

For offline deployment questions, see:
- GitHub Discussions (when online)
- Local documentation in `docs/`
- Example configurations in `examples/`
