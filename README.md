# Constructions: the reader's materials

[Read the book](https://books.arxo.io/constructions/) · [Versioned downloads](https://github.com/arxohq/constructions/releases/tag/v2026.10.1) · [CI](https://github.com/arxohq/constructions/actions/workflows/ci.yml)

The executable examples and reference files for **Constructions. The Craft of
Formalization**, English edition 2026.10, by Rifat Jumagulov, published by Arxo.
This repository release is **v2026.10.1**. The book was published on 14 October
2026; the repository packages its existing curated companion without changing
the models or their expected answers.

## Start from a clean clone

Use Node.js 20 or newer, npm, Python 3.10 or newer and Git. The pinned CLI
supports Linux x86-64 and macOS ARM64.

```sh
git clone https://github.com/arxohq/constructions.git
cd constructions
npm ci
npm test
```

`npm test` checks every companion file against the edition's manifest, runs
the 119 selected test files (383 scenarios), replays the Water answer and its
proof, checks all four support states, and runs the expense-evidence example.
It uses temporary working copies and does not edit the supplied companion.
GitHub Actions runs the same command on Linux x86-64. The book's original
macOS ARM64 acceptance is preserved in `companion/execution.json`.

To work through the book's commands interactively:

```sh
npm install -g @arxo/cli@0.2.4
cd companion/reader
law version --json
law test corpus/laws/org/openstax/chemistry-acids
python3 packs/demo/expense-evidence/run_demo.py
python3 ../check_reader.py --bundle ..
```

See [the companion instructions](companion/README.md) and the recorded
[50 printed command blocks](companion/reader-commands.json). Three printed
study edits intentionally cause a refusal; their original acceptance is
documented in [reader-command-checks.json](companion/reader-command-checks.json).
The CI test described above does not re-execute those 50 blocks.

## What is included

- `companion/reader/`: the adapted runnable models, selected tests, pinned
  dependencies, prepared CLIR, Water project and helper scripts.
- `companion/references/`: the selected historical files linked by the book.
- `companion/execution.json` and `companion/MIGRATION.md`: provenance, recorded
  results and the adaptations for CLI 0.2.4. Equivalence to a retired semantic
  version is not claimed.
- `provenance.json`: the original download and its digest. Every file in
  `companion/` is preserved byte for byte from that published archive.
- The [release](https://github.com/arxohq/constructions/releases/tag/v2026.10.1):
  the original PDF, EPUB and companion ZIP, component notices and checksums.

The engine implementation, CLI executables, full private review archive,
Syzdyq's handbook, long embedded quotations and system fonts are excluded.
Editorial and source-language checks were AI reviews with Codex and Astra;
a human reader pilot has not been performed.

## Licences and scope

This is the curated **noncommercial** collection. Original Arxo program code
is Apache 2.0; selected specification documents and original book prose retain
their own stated licences. OpenStax excerpts and adaptations are CC BY-NC-SA
4.0, and Scrum Guide adaptations are CC BY-SA 4.0. The author's CC BY licence
does not relicense third-party material. See [LICENSE.md](LICENSE.md) and
[all component notices](companion/THIRD-PARTY-NOTICES.md).

Checks cover the selected book examples. They do not establish source truth,
full subject coverage, equivalence to earlier engines or full corpus acceptance.
