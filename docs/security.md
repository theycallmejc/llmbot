# Local security posture

- API keys are read from environment variables only and never returned by the API or logged.
- Model output is rendered with DOM text nodes, not raw HTML.
- Attachments are allowlisted UTF-8 text with size and filename checks.
- Local tools are explicitly allowlisted and the calculator accepts arithmetic AST nodes only.
- No CORS policy is enabled: the local server does not grant other origins browser access.
- Security response headers block framing, MIME sniffing, cross-origin resource loading, and referrer leakage.
- The app is single-user/local; do not expose it publicly without adding authentication and revisiting this posture.
