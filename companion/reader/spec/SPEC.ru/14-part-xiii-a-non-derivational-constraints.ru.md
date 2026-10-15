# Часть XIII-A. Non-derivational constraints

## 93.1. Назначение

DECISION-0187 разрешает `constraint C(x: T) { … }` вместо `for x: T;`
в теле. Доступны те же группы типов, что у rule. Заголовок и `for` тела
взаимоисключающие; семантика ограничения и порядок связывателей сохраняются.

Constraint выражает обязательное отношение между уже определяемыми facts/positions, но не выводит consequent как новый факт:

```law
@source(CIVIL_CODE_MINOR_DEF)
constraint MinorOnlyIfAge(p: Person) {
    when Minor(p);
    require age(p) < 18 year;
    severity error;
}
```

Для каждой finite grounding:

- antecedent `when` не `TRUE_ONLY` → constraint не triggered либо имеет conflicted/undetermined trigger;
- antecedent `TRUE_ONLY`, requirement `TRUE_ONLY` → `SATISFIED`;
- antecedent `TRUE_ONLY`, requirement `FALSE_ONLY` → `VIOLATED`;
- requirement `BOTH` → `CONFLICTED`;
- requirement `NEITHER`/missing → `UNDETERMINED`.

Constraint:

- не добавляет logical support;
- не участвует в defeat/priority как rule;
- не создаёт автоматически legal violation/sanction;
- может иметь source, scope, lifecycle, interpretation и proof;
- должен быть range-restricted/finite в executable profile;
- вычисляется после producer strata, от которых зависит, и не может быть producer для них в 0.1.

Юридическое нарушение по-прежнему выводится из `PositionInstance`; constraint failure — validation/compliance finding. Если source прямо связывает failure с legal consequence, consequence кодируется отдельным обычным rule на соответствующие установленные facts/position status, а не hidden side effect constraint evaluator-а.

## 93.2. Constraint identity и result

Ground constraint application получает stable runtime ID из canonical constraint ID, substitution и manifest hash. Result содержит antecedent/requirement support, source anchors, missing inputs и proof. Несколько failures агрегируются query policy (`all`, `first`, `count`, severity threshold), но не скрываются.

## 93.3. Исполнение и место результата (errata E-0086)

До errata §93.1–§93.2 называли исходы, но не говорили, КОГДА constraint
вычисляется и ГДЕ в evaluation-документе живёт его результат; ни одна
реализация его не вычисляла вовсе (замер 01.09.2026: `kz.tuystyq`, оба движка
байтово — ни статуса, ни узла). Настоящая подсекция закрывает пробел; всё в
ней аддитивно к §93.1–§93.2 и §280.2.

**Момент.** Constraint вычисляется при КАЖДОМ evaluation, независимо от вида
запроса §172, — после всех strata §111 и norm runtime §280.3, перед ответом на
запрос (§280.2: «after their producer barriers»). Constraint с `effective`
(§87) вне `legal_time` не применяется. Constraint, чьи формулы выходят за
исполняемое подмножество либо нарушают range restriction §190, не
вычисляется и объявляет об этом issue `NON_EXECUTABLE_CONSTRAINT`
(warning, `relatedNodes` — сам constraint) — по образцу `NON_EXECUTABLE_RULE`.

**Grounding.** Подстановки переменных перечисляются по позитивным
связывающим литералам `scope ∧ when` (§190). Перечисление включает атомы со
статусом `BOTH`: противоречивый antecedent есть находка, а не повод её
скрыть. Подстановка, при которой antecedent имеет пару §62 `(t, f)` с
`t = false`, не triggered — результата у неё нет.

**Trigger и вердикт.** Для каждой triggered подстановки:

| antecedent `(t, f)` | trigger_status | requirement `(t, f)` | вердикт |
|---|---|---|---|
| `(T, F)` | `SATISFIED` | `(T, F)` | `SATISFIED` |
| `(T, F)` | `SATISFIED` | `(F, T)` | `VIOLATED` |
| `(T, F)` | `SATISFIED` | `(T, T)` | `CONFLICTED` |
| `(T, F)` | `SATISFIED` | `(F, F)` | `UNDETERMINED` |
| `(T, T)` | `CONFLICTED` | любая | `CONFLICTED` |

Requirement вычисляется четырёхзначно (§62) над готовым состоянием — тем же
правилом, что квантор §52 и запрос-формула: один conflicted элемент доезжает
до `BOTH`. Implicit-established обёртка §204 (`require age(p)` понижается в
`established(age(p))`, как литерал тела правила §66) читается в antecedent и
requirement как САМ ЛИТЕРАЛ — четырёхзначно; иначе исходов `BOTH`/`NEITHER` не
существовало бы. Прочие статусные тесты (`not_known`, `supported`, `refuted`,
`unknown`) остаются булевыми.

**Результат.** Ground constraint application — элемент `results[]` с
`result_kind = CONSTRAINT` (§174.1): `applicability_status = APPLICABLE`,
`trigger_status` и `truth_status` requirement по таблице, `normative_status` —
вердикт, `target` — stable ID constraint-а, `query` — запрос этого evaluation,
`evaluation_status = COMPUTED`. Stable runtime ID §93.2 —
`urn:result:constraint:<хвост id после '#'>:<h>`, где `h` — первые 16
шестнадцатеричных знаков `sha256` канонических байтов §208 объекта
`{"constraint", "substitution", "manifest"}` (`manifest` — `semanticHash`
манифеста §170). Элементы `CONSTRAINT` стоят ПОСЛЕ ответов на запрос в
порядке (stable ID constraint-а, канонические байты подстановки). Для
`UNDETERMINED` `missing_inputs` называет литералы requirement со статусом
`NEITHER` (`kind = fact`, `related_node` — предикат).

**Proof.** Узел вида `constraint_check` (§179, аддитивно):
`id = urn:proof:constraint:<хвост>:<h>`, `substitution` — подстановка,
`conclusion = {constraint, status, triggerStatus, requirementStatus}`,
`premises` — опоры, прочитанные antecedent и requirement (§180 для формул);
узел — корень графа (`roots`). Ядро проверяет структуру узла (constraint
объявлен программой, подстановка связывает каждую переменную); сам вердикт —
пересчёт четырёхзначной формулы — вне ядра v1, как у `query_evaluation` со
статусом, отличным от `TRUE_ONLY`.

**Issues.** `VIOLATED` даёт issue `CONSTRAINT_VIOLATED`, `CONFLICTED` —
`CONSTRAINT_CONFLICTED`; `severity` — объявленная у constraint-а, причём
`critical` записывается как `error` с `details.severity = "critical"`
(`fatal` схемы зарезервирован за остановкой вычисления §238); `message` —
`constraint <id> <вердикт>: <message constraint-а>` (без `message` — `требование
не выполнено (§93.1)` / `antecedent или requirement противоречивы (§93.1)`);
`relatedNodes` — constraint; `details.result` — ID результата. `SATISFIED` и
`UNDETERMINED` issue не порождают. Query policy агрегации §93.2 в v1 одна —
`all`: находки не скрываются и не сворачиваются.

Область блокировки такой issue — §181.2 (errata E-0236): с семантики 0.2
`error` гасит только результат, зависящий от предикатов клауз `scope`, `when` и
`require` этого ограничения по замыканию §110; в документе независимого
результата issue сохраняется дословно с `severity: warning`. Сам вердикт §93.1
и результат `CONSTRAINT` от этого не меняются.

## 93.4. Состав тела constraint (errata E-0132)

Тело `constraint` — неупорядоченное множество `constraint_item`
(`grammar.ebnf`): биндеры `for` законны в любом месте, `scope` и `effective`
— не более одной клаузы на блок (повтор — `LDC-E1329`, как у правила §94).
`effective` — интервал `legal_time` §87 в том же смысле, что у правила, и
ложится в поле `effective` узла `constraint` CLIR; §93.3 определяет его
действие (вне `legal_time` constraint не применяется). Каждый написанный
элемент либо разбирается, либо отвергается статически (`LDC-E0201`);
молчаливый пропуск запрещён — constraint, понижённый без написанной клаузы,
применяется шире написанного (класс E-0114). Формы `constraint_item`, для
которых развёртка не определена, — `source_anchor_item`, `interpretation`,
`metadata_item` — в 0.1 отвергаются тем же кодом.
