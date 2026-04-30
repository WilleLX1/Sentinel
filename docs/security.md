# Sentinel Security

Sentinel is an administrative tool. The agent can read Docker metadata and logs, which may contain sensitive values.

Default security posture:

- Bind the agent privately.
- Access the agent over Tailscale, WireGuard, or SSH tunneling.
- Require long random API keys.
- Redact sensitive environment keys before returning container metadata.
- Keep remote actions disabled unless explicitly needed.
- Use a separate action key when remote actions are enabled.
- Store dashboard API keys encrypted in SQLite.
- Use a strong dashboard session secret.

Do not expose the agent directly to the public internet without an authenticated HTTPS reverse proxy and firewall restrictions.

