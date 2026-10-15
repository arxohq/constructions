# Working on the Constructions companion

- Preserve the edition's original files under `companion/`. They are checked
  against its immutable manifest and the digest in `provenance.json`.
- Do not change model semantics or expected results as part of packaging or CI.
  A new edition needs a separate, explicit source and acceptance decision.
- Keep instructions and new documentation in English.
- Use the exact npm CLI dependency and committed lockfile. Run `npm ci` and
  `npm test` from an ordinary clone. Only the selected book examples are in scope.
- Retain all component licences and distribution exclusions. Never import
  engine implementation, private review archives, credentials or caches.
- Preserve unrelated edits. Do not use git stash, reset --hard, git restore,
  git clean or checkout to discard someone else's work.
- The original book has 50 accepted printed command blocks. CI separately
  checks 383 scenarios, Water replay, four support states and expense evidence;
  do not describe this as a new execution of all printed commands.
