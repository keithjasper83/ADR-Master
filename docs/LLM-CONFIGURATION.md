# LLM Configuration Guide

ADR-Master supports configurable LLM endpoints and models for ADR compilation. This guide explains how to configure different LLM providers.

## Configuration Parameters

Add these environment variables to your `.env` file:

```env
LLM_ENDPOINT=<your-llm-endpoint-url>
LLM_MODEL=<model-name>
```

## Supported LLM Providers

### 1. Local Ollama

**Default configuration** - works out of the box if Ollama is running locally.

```env
LLM_ENDPOINT=http://localhost:11434/api/generate
LLM_MODEL=llama2
```

**Other popular Ollama models:**
- `llama2` - Meta's Llama 2 (default)
- `mistral` - Mistral 7B
- `codellama` - Code-focused Llama variant
- `phi` - Microsoft Phi models

**Setup:**
1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Model runs automatically when ADR-Master makes requests

### 2. LM Studio (Local/Network)

LM Studio provides an OpenAI-compatible API for locally hosted models.

**Local configuration:**
```env
LLM_ENDPOINT=http://localhost:1234/v1/chat/completions
LLM_MODEL=your-model-name
```

**Network configuration (Tailscale example from docs/LLM-Location.MD):**
```env
LLM_ENDPOINT=http://desktop.taile9300d.ts.net:1234/v1/chat/completions
LLM_MODEL=qwen/qwen3-4b-2507
```

**Setup:**
1. Install LM Studio: https://lmstudio.ai
2. Download and load a model in LM Studio
3. Enable "Local Server" in LM Studio
4. Set the endpoint URL and model name in your `.env`

### 3. OpenAI Compatible APIs

Any OpenAI-compatible API can be used (OpenAI, Azure OpenAI, local proxies, etc.).

```env
LLM_ENDPOINT=https://api.openai.com/v1/chat/completions
LLM_MODEL=gpt-3.5-turbo
```

**Note:** For OpenAI, you'll also need to set an API key (implementation may vary based on your setup).

### 4. Custom Endpoints

ADR-Master tries two endpoint formats automatically:

1. **Ollama-style** (`/api/generate`):
   ```json
   {
     "model": "llama2",
     "prompt": "...",
     "stream": false
   }
   ```

2. **OpenAI-style** (`/v1/chat/completions`):
   ```json
   {
     "model": "gpt-3.5-turbo",
     "messages": [{"role": "user", "content": "..."}]
   }
   ```

The service automatically falls back to the original content if both fail.

## Model Selection Guidelines

### For ADR Compilation

**Recommended models:**
- **Llama 2 7B/13B**: Good general-purpose model, works well for ADR refinement
- **Qwen 3-4B**: Efficient and fast, suitable for technical documentation (as used in LLM-Location.MD)
- **Mistral 7B**: Strong reasoning capabilities, good for architectural decisions
- **Code Llama**: If ADRs include code examples

**Considerations:**
- Larger models (13B+) provide better quality but are slower
- Smaller models (7B or less) are faster but may need more specific prompts
- Code-focused models are better for ADRs with technical implementation details

## Testing Your Configuration

1. Start ADR-Master with your configuration
2. Create a draft ADR via the API or UI
3. Trigger compilation: `POST /api/adr/compile`
4. Check job status: `GET /api/adr/jobs/{job_id}`
5. Review logs for any connection errors

## Troubleshooting

### LLM endpoint not responding

**Check:**
1. Is the LLM service running? (`ollama list` or check LM Studio)
2. Is the endpoint URL correct? (try curl: `curl -X POST $LLM_ENDPOINT`)
3. Is the model loaded? (check Ollama with `ollama list` or LM Studio UI)

### Wrong model format errors

**Solution:** Ensure `LLM_MODEL` matches the exact model name in your LLM provider:
- Ollama: Use short names like `llama2`, `mistral`
- LM Studio: Use the full model path shown in the UI
- OpenAI: Use API model names like `gpt-3.5-turbo`, `gpt-4`

### Timeouts

**Solutions:**
- Increase timeout in `llm_service.py` (currently 60 seconds)
- Use a smaller, faster model
- Reduce the size of ADR drafts
- Use local models instead of remote APIs

## Offline Operation

ADR-Master is designed for offline use. Recommended setup:

1. Install Ollama locally
2. Pull desired models: `ollama pull llama2`
3. Configure `.env` to use localhost endpoint
4. No internet connection required for ADR compilation

## Security Considerations

- **Local models**: No data leaves your machine
- **Network models**: Ensure you trust the endpoint (use Tailscale, VPN, or trusted networks)
- **Cloud APIs**: Be aware that ADR content is sent to third-party services
- **Sensitive data**: Use local models for ADRs containing proprietary information

## Performance Tuning

### For faster compilation:
- Use smaller models (7B or less)
- Use local models instead of API calls
- Consider streaming responses (requires code changes)

### For better quality:
- Use larger models (13B or 70B)
- Provide more context in drafts
- Use domain-specific models when available

## Example Configurations

### Development (Fast, Local)
```env
LLM_ENDPOINT=http://localhost:11434/api/generate
LLM_MODEL=llama2
```

### Production (Quality, Local)
```env
LLM_ENDPOINT=http://localhost:11434/api/generate
LLM_MODEL=llama2:13b
```

### Team (Shared, Network)
```env
LLM_ENDPOINT=http://llm-server.local:1234/v1/chat/completions
LLM_MODEL=qwen/qwen3-4b-2507
```

### Air-gapped (Completely Offline)
```env
LLM_ENDPOINT=http://localhost:11434/api/generate
LLM_MODEL=llama2
# Ensure Ollama and model are pre-installed
```

## See Also

- [LLM-Location.MD](./LLM-Location.MD) - Specific LM Studio configuration example
- [OFFLINE.md](./OFFLINE.md) - Offline operation guide
- [API.md](./API.md) - API documentation for ADR compilation
