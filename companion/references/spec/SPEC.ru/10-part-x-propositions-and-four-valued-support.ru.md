# Часть X. Propositions и четырёхзначная поддержка

## 61. Literal

Positive literal:

```text
registered(company)
```

Explicit negative literal:

```text
not registered(company)
```

Они хранятся независимо.

## 62. Support pair

Для ground atom `p` evaluator хранит пару:

```text
(t, f)
```

где:

- `t = 1`, если имеется accepted positive support;
- `f = 1`, если имеется accepted negative support.

Результаты:

| t | f | TruthStatus |
|---|---|-------------|
| 1 | 0 | `TRUE_ONLY` |
| 0 | 1 | `FALSE_ONLY` |
| 1 | 1 | `BOTH` |
| 0 | 0 | `NEITHER` |

## 63. Explicit negation

```text
neg(t, f) = (f, t)
```

`not P` не является negation-as-failure.

## 63.1. Область explicit negation

Operator `not` в proposition layer применяется только к atom/predicate call. Core 0.1 не имеет implicit classical negation сложной formula:

```text
not (A and B)   // static error
```

Автор должен либо выразить нужную disjunction явных отрицательных literals, либо ввести именованный predicate с отдельными правилами. Compiler не применяет De Morgan, excluded middle или double-negation elimination, если они не следуют из явно выбранного profile. Data Boolean `!value` остаётся обычной операцией над двухзначным data value и не является legal explicit negation.

## 64. Conjunction и disjunction

Для support pairs:

```text
P and Q = (P.t and Q.t, P.f or Q.f)
P or  Q = (P.t or  Q.t, P.f and Q.f)
```

Это paraconsistent truth behavior. Однако rule applicability использует дополнительное условие, описанное ниже.

## 64.1. Lifting data Boolean в formula

Pure comparison/status test возвращает data `Boolean` и при использовании как formula lift-ится:

```text
true  -> (1, 0)
false -> (0, 1)
```

Missing input, failed partial function или unavailable snapshot не lift-ится в `false`: formula получает `(0,0)` и соответствующий `EvaluationIssue`. Conjunction/disjunction объединяют не только support pairs, но и dependency/issues sets. Поэтому `amount > 0` при неизвестном `amount` является `NEITHER + MISSING_INPUT`, а не `FALSE_ONLY`.

## 64.2. Отношение округления над сертифицированными границами (errata E-0136)

Единственная формула Core, чья опора берётся не из lifting Boolean §64.1 и не
из store §61, а из ДОКАЗАТЕЛЬСТВА:

```text
{"kind": "rounding", "bounds": <терм Bounds>, "value": <терм Integer>,
 "precision": <целое >= 0>, "mode": "HALF_UP" | "HALF_EVEN" | "HALF_DOWN"
                                  | "UP" | "DOWN" | "CEILING" | "FLOOR"}
```

Пусть `C` — ячейка округления: множество вещественных, которые округляются в
`value` при данных `precision` и `mode` (те же семь режимов §50, то же
определение); `I = [lower, upper]` — замкнутый рациональный отрезок
сертификата §259.2. Опора §62:

```text
I ⊆ C        -> (1, 0)   TRUE_ONLY
I ∩ C = ∅    -> (0, 1)   FALSE_ONLY
иначе        -> (0, 0)   NEITHER
```

`NEITHER` здесь означает НЕДОСТАТОЧНОСТЬ ГРАНИЦ, а не отсутствие данных: у
интервала, задевающего две ячейки, ответа нет ни положительного, ни
отрицательного, и норма обязана либо взять более точный профиль, либо
признать вопрос неразрешимым на этих входах. Сопутствующий `EvaluationIssue`
называет обе ячейки — иначе «не установлено» было бы неотличимо от
`MISSING_INPUT` §69.

Решение принимается на КОНЦАХ отрезка: все семь режимов §50 монотонно
неубывающие, поэтому `round(lower) = round(upper) = value` равносильно
`I ⊆ C`, а `value ∉ [round(lower), round(upper)]` равносильно `I ∩ C = ∅`.
Открытость концов ячейки и точная половина при этом решаются ровно тем же
кодом, что и `round` §50 — второго определения режима не заводится.

**`BOTH` одна такая формула не даёт НИКОГДА.** `I ⊆ C` и `I ∩ C = ∅`
несовместимы при непустом `I`, а пустой отрезок невозможен: `Bounds` строится
только термами §259.2, и `lower <= upper` у них инвариант. Это утверждение об
ОПОРЕ одной формулы, а не обо всей базе: две нормы, округлившие одно число в
разные целые, дают обычный конфликт §62.

В позиции гарда тела правила формула сворачивается к «сработало» ровно при
`TRUE_ONLY` — по rule-body default §66, как всякий конъюнкт; терм при этом
`TruthStatus` не возвращает и вычислитель гарда остаётся Boolean.

## 65. Status tests

```text
established(P)  // P == TRUE_ONLY
refuted(P)      // P == FALSE_ONLY
supported(P)    // positive support exists: TRUE_ONLY or BOTH
monotone(P)     // тот же тест, что supported(P); слой L0 (errata E-0018)
opposed(P)      // negative support exists: FALSE_ONLY or BOTH
conflicted(P)   // P == BOTH
unknown(P)      // P == NEITHER
```

`monotone(P)` (errata E-0018) вычислительно тождествен `supported(P)` — истинен при любой положительной опоре. Различие не в тесте, а в заявленном намерении и слоевой принадлежности: `monotone(P)` — ребро монотонной рекурсии §103, принадлежит слою L0; `supported(P)` — потребление конфликта, остаётся в L3. Тест сознательно НЕ `established`: тот немонотонен при достижимом `BOTH` (появление отрицательной опоры отзывало бы вывод), а гарантия §110 требует монотонного ребра; в L0 разница ненаблюдаема — политика `on_accepted_conflict = halt` (E-0001) делает `BOTH` недостижимым, поэтому обещание «в L0 совпадает с established» выполняется как следствие.

`established(P)` возвращает Boolean data value. В rule body голый `P` является сокращением для требования `P == TRUE_ONLY`. В Core 0.1 operand status-test является ground/groundable **literal**, а не произвольной составной formula; составной статус выражается Boolean-комбинацией status-tests. Это сохраняет однозначный producer barrier и closure key.

## 66. Rule-body default

```text
when registered(company)
```

эквивалентно:

```text
when established(registered(company))
```

Это означает, что конфликтный факт не активирует обычное правило.

Для сознательного использования спорного факта:

```text
when supported(registered(company))
```

Такой код СЛЕДУЕТ сопровождать rationale annotation.

## 67. `not_known`

```text
not_known(P)
```

истинно, если после завершения предыдущего stratum отсутствует positive accepted support для `P`.

`not_known(P)`:

- не выводит `not P`;
- допустимо только в rule bodies;
- является non-monotonic/status-sensitive dependency;
- требует stratification;
- не должно использоваться как замена explicit closed-world declaration.

«Завершение предыдущего stratum» читается против ВСЕХ производителей `P`,
а не только правил: эффект полномочия §127 (`effect create(P)`) — тоже
производитель позитивной опоры `P`, и материализуется он norm runtime §280.3
ПОСЛЕ всех strata §280.2 (errata E-0134). В 0.2 строгий `not_known(P)` над
предикатом, достижимым от головы эффекта строго-позитивной цепочкой,
отклоняется как поздний производитель §111 (`LDC-E4103`,
`NON_EXECUTABLE_RULE`), а не вычисляется по снимку до эффекта: такой ответ
противоречил бы этому определению внутри одного документа.

## 68. `no_evidence`

```text
no_evidence(P, policy = PolicyX)
```

проверяет evidence graph, а не logical support. Возможна ситуация:

- `P` derived без непосредственного evidence;
- evidence для `P` есть, но оно inadmissible;
- evidence отсутствует, но `P` установлено binding adjudication.

## 69. Missing data

Отсутствующий function input или unresolved external value не создаёт `not P`. Он формирует:

```text
TruthStatus = NEITHER
evaluation_status = MISSING_INPUT | EXTERNAL_UNAVAILABLE
```

и dependency report.

Держатель негатива (DECISION-0353 §2, errata E-0235). Голый отрицательный
литерал тела — `when not p(x)`, по §66 он же `established(not p(x))` — требует
от `p(x)` статуса `FALSE_ONLY`, и получить его можно ТОЛЬКО от явного
негатива: отрицательной головы правила §99, отрицательного assertion §71,
принятой `refutes`-опоры §78.2.2 либо замыкания §70 с
`derive_explicit_negative`. Отсутствие записи негативом не является — это и
сказано абзацем выше, — поэтому тело, у предиката которого нет ни одного
производителя негатива, не станет `FALSE_ONLY` ни на одном деле: правило не
сработает ни разу, а `check`, `lower` и evaluation-документ останутся чисты и
не назовут причины. Реализация ОБЯЗАНА предупреждать о такой форме
(`LDC-E4113`, warning): условие — предикат объявлен в этом пакете (у чужого
границы файлового объёма §24 делают тела владельца невидимыми), его
`relationKind` §45 не `empirical` (дело вправе утверждать `assert not p(…)`) и
не `judgment` (ответ органа §47.3 несёт обе полярности), и производителя
негатива в пакете нет. Уровень — предупреждение, а не отказ: негатив вправе
приходить из чужого пакета либо `refutes`-опорой, которую статика не читает.
Где норма читается «если иное не установлено», а держателя полноты нет,
записывается `not_known(p(x))` §67, а не `not p(x)`.

## 70. Closed-world declarations

Closed world задаётся локально:

```law
closure PermitRegistryClosure {
    predicate valid_permit;
    domain companies_in_registry_snapshot;
    snapshot PERMIT_REGISTRY_2026_08_25;
    complete_as_of @2026-08-25T00:00:00+05:00;
    derive_explicit_negative true;
}
```

Только после валидной closure policy отсутствие записи может породить explicit negative assertion. Closure scope ДОЛЖЕН быть конечным и точно определённым.

Обязательные поля (errata E-0104): `predicate`, `domain`, `snapshot`, `complete_as_of` — те же, что `required` у `ClosurePolicy` в `legal-ir.schema.json`; `complete_as_of` — момент (`Instant`), не дата (§48). Замыкание без обязательного поля — статический отказ `LDC-E1307`, и по §210.1 он ДОЛЖЕН звучать одинаково на каждом входе компилятора: `lawc check` отвергает такое замыкание так же, как `lawc lower`. До errata сторож стоял только на понижении: `check` печатал `check OK`, `lower` отказывал, и закрытие оставалось объявленным, но не действующим — признака у того, кто зовёт только `check`, не было ни одного.

Арность и окно (errata E-0087). Закрытый предикат — ЛЮБОЙ арности; `domain` —
предикат ТОЙ ЖЕ арности, чьи установленные кортежи и есть закрытая область:
explicit negative порождается для каждого кортежа домена, у которого нет
позитивной опоры закрытого предиката. Домен иной арности либо не предикат —
`NON_EXECUTABLE_CLOSURE` (warning, закрытие не применяется — громко, не
молча). Closure принимает `effective` §87 наравне с правилом: замыкание
отменённого акта вне окна `legal_time` не порождает ни одного негатива —
до errata окно у closure отсутствовало, и отменённое замыкание выводило
явный негатив на любую дату.


Evaluator НЕ ОБЯЗАН физически materialize все отрицательные tuples. Для больших closed domains СЛЕДУЕТ использовать lazy anti-membership proof: negative literal создаётся по запросу/при match только вместе с closure certificate, snapshot hash, domain membership proof и доказательством отсутствия ключа. Это сохраняет семантику и предотвращает взрыв размера facts.

Уровни замыканий (errata E-0113). Замыкание — вершина графа страт §110: `producers(P ∪ domain) → closure(P) → readers(¬P)`. Уровень замыкания на единицу выше уровней всех замыканий, чьи негативы читают — транзитивно, через любую зависимость — производители его предиката или домена; замыкания без такой зависимости стоят на уровне 1. Исполнение идёт уровнями: правила → замыкания уровня 1 → правила → замыкания уровня 2 → … Цикл (производители каждого из двух замыканий читают негатив другого) не стратифицируем: `LDC-E4102` статически, `NON_EXECUTABLE_UNSTRATIFIED` на исполнении. Одноуровневая программа — все замыкания на уровне 1 — исполняется прежним сэндвичем §231.1 байт в байт. До errata уровень был один по умолчанию реализации, и производитель закрытого предиката, читавший негатив ДРУГОГО замыкания, получал обе опоры — `BOTH` без единой issue.

Читатель над вершиной замыкания (errata E-0174). Сэндвич исполняет строгий фикспойнт до замыкания и после него, а вывод append-only. Поэтому строгое правило, чей тест опровергается негативом замыкания, в проходах до материализации этого замыкания не исполняется: оно стоит над вершиной `closure(P)`, а не рядом с производителями `P`. Негатив опровергает `unknown(P)` любой полярности, `not_known(not P)`, перечисление, чей generator зависит от опоры `not P` (агрегат §59, домен квантора §52), и условный терм головы §56 над такой опорой. Ожидание транзитивно: правило ждёт замыкание и тогда, когда его тест опровергает опора строгого производителя, не завершённого до этого замыкания; производитель завершён, когда завершены все его чтения, монотонные тоже. Правило над `not_known(barred)`, где `barred ⇐s company ∧ not licensed`, ждёт замыкание `licensed`. Тесты, которые негатив делает только истинными (голый `not P`, `established`/`supported`/`monotone` отрицательного литерала, `refuted(P)`), не ждут: их исполняет проход после замыкания. Это подъём над вершиной, а не отказ. Программа стратифицируема, `check` её принимает, правило исполняется после материализации. Замыкание, которое ничего не материализовало (вне окна §87, без явного негатива, `NON_EXECUTABLE_CLOSURE`), считается пройденным. Программа без таких чтений исполняется прежним сэндвичем байт в байт. До errata обе реализации исполняли ждущее правило уже в первом проходе и не отзывали вывод: при закрытом `licensed` над доменом `company` правило `pending ⇐s company ∧ unknown(licensed)` давало `pending(a)` TRUE_ONLY при `licensed(a)` FALSE_ONLY.



