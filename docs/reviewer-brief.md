# Translation reviewer brief - Ginga Sengoku Gunyuuden Rai (SNES)

You review one or more batches of a JP->English fan translation. Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, encodable characters, width, stub last lines) is already enforced by the
check tool - judge translation quality. Return the report as your final message: subagents cannot write files, so the
controller saves it.

## Inputs (paths in your dispatch)
- Pairs files `work/qa/review/bNNN.txt`: every entry as `>> id | box | JP` / `EN`, in ROM order (neighbours are the
  context). Read ALL of each, in passes if large.
- `glossary.md`: rulings, register/voice (its "Register / flavour" line is the style reference), names and terms.
- Codes: `{br}` line break, `{n}` padded line break, `{skip:..}` indent, `{c5}`/`{c6}` typewriter on/off, `{FFFE}`
  officer name, `{FFFD}` planet name, `{end}`. English lines are short because boxes are tight (labels 8-10
  letters, dialogue ~28 letters a line): terse is expected, but lost meaning is not.
- `専` in the JP is the game's 夢 (dream) misread by the table. Strings like `雷の同意の台詞(エラ〜)` are the
  developers' placeholders; a literal English placeholder is correct.

## Judge
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (a one-letter slip like "Bran" for "Plan" is what players notice); honorific relationships stable
  within a scene; voice matches the style reference.
- Things players and users caught that reviewers missed: jokes/wordplay losing their punch; ordinal suffix after a
  variable ("1th"); abbreviated names or terms (unless the glossary rulings allow them); stock phrases that read awkwardly in English ("... GET!").
- Voice: each speaker against their row in the style reference. Speech quirks (〜っス, 〜ぞい, 〜ニャ, ござる, drawn-out
  〜ぉ/〜ぅ endings, katakana robot speech), register (a king's formality, a thug's swagger, a child's cuteness) and
  emotional intensity (rage, fear, comic timing) must come through in English, not be normalised into neutral prose.
  Register markers flatten most often, more than quirks: old-man じゃ/のう/わし, rough ぜ/ねぇ/っス, feminine
  かしら/わよ/のね. Audits of two patches found about 9 in 10 old-man lines and nearly every かしら line turned neutral.
- Naturalness: would a fan-translation reader stumble? Against the glossary's Style rules: register and voice per
  scene, calques of an earlier translation (a second-language pass copies English phrasing).

## Report
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, a character's voice flattened: quirk, register or emotional beat lost, joke dead)
#### Minor (style - these are deferred to one polish pass)
Each: `id - JP gist - problem - suggested EN`.
### Assessment
Approved | Needs fixes - one sentence why.
