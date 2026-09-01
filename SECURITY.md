# Security Policy

## Scope

AdaptiveRAG-X includes prompt-injection detection, optional API-key authentication, rate limiting and tenant metadata. These controls are defensive layers, not a substitute for network security or application-level authorization.

## Reporting

Do not publish exploitable vulnerabilities in public issues. Report security problems privately to the repository owner through GitHub's private security reporting facilities when available.

## Production checklist

- Set `ADAPTIVE_RAG_API_KEY`.
- Run behind TLS and a trusted reverse proxy.
- Restrict CORS origins.
- Use a managed database/vector store with access controls.
- Never commit `.env` or provider keys.
- Treat retrieved documents as untrusted input.
- Add provider-specific content moderation where required.
- Monitor authentication failures, latency and unusual retrieval patterns.
