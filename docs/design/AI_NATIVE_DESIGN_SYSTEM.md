# AI-Native Design System

## Visual language

Local Chat uses a restrained, typography-led interface: system sans-serif text, a neutral off-white canvas, white message surfaces, graphite text, and one blue interactive accent. It deliberately avoids gradients, mascots, neon effects, and ornamental “AI” decoration. Reading content is constrained to a comfortable maximum width.

## Interaction and state

The interface communicates only real application state. While a request is active, the status chip says “Replying…” and the send control is disabled; errors appear in the conversation at the point they occur. Future streaming responses use the existing short content-entry transition and a cursor, not fabricated typing delays. No tool, retrieval, or agent activity is shown until those capabilities exist.

## Layout and accessibility

Desktop uses a narrow utility sidebar and a reading-focused conversation panel. On small screens the sidebar becomes a compact top bar. The composer is keyboard-first: Enter sends and Shift+Enter creates a line break. Focus styles, visible labels for assistive technology, sufficient contrast, and text-only model rendering are required.

## Message actions

Assistant responses expose Copy only on hover or keyboard focus, avoiding persistent visual clutter. Model output is inserted through text nodes, never as raw HTML. Markdown rendering is deferred until it can preserve this safety guarantee.
