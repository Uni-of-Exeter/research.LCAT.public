# LCAT Architecture Diagram — Visualisation Guide

The system architecture is defined in [`lcat-architecture.puml`](lcat-architecture.puml)
using [PlantUML](https://plantuml.com/). That `.puml` file is the **single source of
truth** — there is no separate drawing tool, so you edit the text directly and re-export
the PNG ([`lcat-architecture.png`](lcat-architecture.png)) that the README embeds.

## View and edit in VS Code (recommended)

1. Install the **PlantUML** extension by _jebbs_ (extension id `jebbs.plantuml`):
   open the Extensions view (`Cmd/Ctrl+Shift+X`), search for "PlantUML", and install it.
   - For local rendering it needs **Java** on your `PATH` (and **Graphviz** for some
     diagram types). Alternatively the extension can render against the public
     PlantUML server with no local setup.
2. Open `lcat-architecture.puml`.
3. Preview with `Alt+D` (`Option ⌥ + D` on macOS), or right-click the file →
   _Preview Current Diagram_, or run _PlantUML: Preview Current Diagram_ from the
   Command Palette (`Cmd/Ctrl+Shift+P`). The preview updates live as you type.

## Changing the diagram

- Edit `lcat-architecture.puml` directly — the diagram is generated from this text.
- Keep it in sync with the codebase: whenever the architecture changes, update the
  `.puml` and re-export the PNG (this is also noted in the repository `AGENTS.md`).

## Re-export the PNG

After editing the `.puml`, regenerate `lcat-architecture.png`:

- **From VS Code:** open the preview, then right-click → _Export Current Diagram_ → `png`.
- **From the command line** (needs PlantUML + Java, e.g. `brew install plantuml`):

  ```bash
  cd docs/software-architecture-diagrams
  plantuml -tpng lcat-architecture.puml
  ```

## No-install option

Paste the contents of `lcat-architecture.puml` into an online renderer such as
[plantuml.com](https://www.plantuml.com/plantuml/uml/) or
[planttext.com](https://www.planttext.com/) to preview it in the browser.
