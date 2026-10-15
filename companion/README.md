# Constructions: English reader companion

English edition 2026.10, 14 October 2026. For noncommercial distribution.
See THIRD-PARTY-NOTICES.md for component licences and exclusions.

## Install and run

Use Node.js 20 or newer with npm. The published CLI supports macOS ARM64
and Linux x86-64; this book was tested on macOS ARM64.

```sh
npm install -g @arxo/cli@0.2.4
law version --json
cd reader
law test corpus/laws/org/openstax/chemistry-acids
python3 packs/demo/expense-evidence/run_demo.py
python3 ../check_reader.py --bundle ..
```

Expect tool version 0.2.4. Unpack first, then use one terminal session for
each chapter's commands. Python helpers use Python 3's standard library
and need `law` on PATH. npm supplies the executable; this archive supplies
models, pinned dependencies, locks and prepared CLIR. No CLI is bundled.
For direct calls you can use `npx --yes --package @arxo/cli@0.2.4 law`.
For a global-install permission error, follow npm's user-owned setup:
<https://docs.npmjs.com/resolving-eacces-permissions-errors-when-installing-packages-globally>.

## Checked scope

All 50 printed shell blocks and all 383
selected scenarios in 119 test files passed. The printed route includes
three intentional refusals. Water replays identical result and proof hashes;
four truth states and four receipt scenes passed. Full corpus acceptance
and execution on other platforms are not claimed.

`references/` supplies the files linked by the book. They are identified
historical references; `reader/` is the adapted runnable layer. The full
private historical review archive is not included. Syzdyq's handbook and
long embedded quotations are excluded; the model uses ABSTRACT_ONLY source
references, preserving its rules and expectations. Product implementation
source, system font files, caches and private editorial materials are excluded.
Editorial and source-language checks were completed with Codex and Astra.
The human reader pilot has not been performed; its forms support optional feedback.
See MIGRATION.md and execution.json for the recorded adaptations.
