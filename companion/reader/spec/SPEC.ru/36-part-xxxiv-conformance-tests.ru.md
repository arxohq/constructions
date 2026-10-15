# Часть XXXIV. Conformance tests

## 267. Test syntax

DECISION-0186: `test "group" variants (amount: Money) { "row-a" (10 KZT);
"row-b" (20 KZT); } { given { ... } evaluate ...; expect ...; }` задаёт
числовые варианты фиксированного полного given. Каждая строка становится
самостоятельным тестом с явно указанным заголовком и локальными const.
Ожидания общие и явные; отсутствующие факты, отрицания и BOTH не выводятся
из таблицы. Колонки и строки непусты; число числовых литералов в строке
равно числу колонок. Ограничения первого среза — DECISION-0186 §4.

```law
test "18-year-old is classified as adult" {
    given {
        const p: Person = entity_ref("urn:person:P1");
        assert age(p, 18 year);
    }

    evaluate truth(adult(p));
    expect truth_status == TRUE_ONLY;
}
```

Один файл `.lawtest` может содержать несколько деклараций `test` и
`property` в любом порядке, разрешённом верхней грамматикой. `lower-test`
возвращает аддитивный конверт
`{"tests": [<test-document>, …], "properties": [<property-document>, …]}` в
порядке исходника внутри каждого массива; даже один тест остаётся массивом из
одного элемента. Документ отдельного теста не получает новых ключей, поэтому
его существующие голдены и `caseHash` сохраняются.

Раннер обязан исполнить каждый элемент `tests` и каждое свойство, а отчёт —
назвать каждый тест его заголовком. Счётчики `total`, `passed` и `failed`
считают декларации, не файлы. Файл с несколькими тестами не вводит общего
`given`: у каждой декларации своё самостоятельное дело §168.

### 267.1. `given` — дело §168

Тело `given` ЕСТЬ тело `case` §168: грамматика описывает его одной продукцией `case_item`, и все ограничения §169 действуют внутри теста без изменений. Тест несёт **вход** вычисления — дело §168 и вопрос §173, — но не право: §169 прямо запрещает делу менять law rules. Ось `calendar` §168.2 доступна здесь без отдельной тестовой формы и входит в `case.options.calendarSnapshot`.

Отсюда следствие для инструмента: программа теста не объявляется в нём и предъявляется вызывающим. Форма предъявления нормативно не фиксируется; реализация ДОЛЖНА отказать с диагностикой, если программа не предъявлена, и НЕ ДОЛЖНА подставлять программу по умолчанию — тест, исполненный против неназванного права, утверждает не то, что написано.

Тем же вызывающим предъявляются внешние снимки §47.2, если право сценария их читает (DECISION-0244). Снимки — транспорт запроса §168.3, а не часть дела: `given` их не называет, и в `case.options` и caseHash они не входят. Форма предъявления нормативно не фиксируется; корпус объявляет их частью семьи сценариев в манифесте пакета — путём файла и ожидаемым `contentHash`. Реализация ДОЛЖНА передать оценщику ровно объявленные снимки, ДОЛЖНА отказать набору до исполнения, если `contentHash` файла не совпадает с объявленным, и НЕ ДОЛЖНА подставлять снимки, которых часть не объявила: сценарий «снимок не подан» законен и проверяет отказ `EXTERNAL_SNAPSHOT_MISSING`. Внутренний хэш набора раннер не пересчитывает — расхождение содержимого с собственным `contentHash` снимка есть семантический отказ оценщика `EXTERNAL_SNAPSHOT_HASH_MISMATCH`, а не отказ инструмента.

Предъявленная программа участвует и в РАЗРЕШЕНИИ ИМЁН дела §168: имя члена автомата §201.1 внутри `given` разрешается по ней — той же таблицей членов, какой его разрешает сама программа в своём файле (DECISION-0156 §8.8). Таблица однозначна по построению: имя члена уникально в пакете (§160.2, `LDC-E1351`), и вложенные состояния областей §162.1 входят в неё наравне с корневыми. Реализация НЕ ДОЛЖНА понижать такое имя в ссылку на несуществующий StableId: молчаливый `NEITHER` у сцены о ходе дела неотличим от ответа права.

### 267.2. `evaluate` — запрос §172

`evaluate` называет стандартный запрос §172 над пропозицией либо терм, чьё значение запрашивается (`DATA` §174.1). Тест допускает ровно один запрос: `expect` адресует поля ОДНОГО результата.

Реализация, не исполняющая названный вид запроса §172, ДОЛЖНА отвергнуть тест диагностикой и НЕ ДОЛЖНА подменять его соседним видом. «Спросили одно, вычислили другое» — худший ответ, какой может дать право: он неотличим от верного.

Арность атома запроса сверяется с сигнатурой §38 ПРЕДЪЯВЛЕННОЙ программы исполнением, а не статикой (§172, errata E-0168): файл теста понижается отдельно от программы (§267.1), деклараций отношений в нём нет, и компилятору сверять не с чем. Несовпадение — отказ `QUERY_INVALID` до вычисления, то есть провал теста с названной причиной; прежде тот же промах давал `NEITHER`, неотличимый от «право молчит».

Строка `evaluate <выражение>;` разбирается тем же правилом `test_item` и вне
теста — как самостоятельный вопрос к пакету-делу §168.4 (DECISION-0165):
разбор и понижение общие, различие только в том, что `expect` у такого
вопроса нет, а `queryId` предъявляется явно (§172).

### 267.3. `expect` — ожидание о поле результата §174

`expect` адресует поля документа-результата §174, а не факты программы. Словарь полей ЗАКРЫТ и расширяется аддитивно:

| Поле | Значение |
|---|---|
| `result_kind` | имя из перечня §174.1 |
| `truth_status` | имя из перечня §62 (`TRUE_ONLY`, `FALSE_ONLY`, `BOTH`, `NEITHER`) |
| `applicability_status` | имя из перечня §91 |
| `trigger_status` | имя из перечня §91.1 |
| `evaluation_status` | имя из перечня §175 |
| `normative_status` | имя из перечня §134 |
| `value` | терм: у `DATA` перечня нет |

Операторы — `==` и `!=`. Порядковые сравнения не определены: ни один из перечней не упорядочен, и `truth_status > NEITHER` не имеет смысла ни в одном из них.

Значение ожидания над **перечислимым** полем ДОЛЖНО быть именем ЕГО словаря. Имя вне словаря и значение, не являющееся именем вовсе, отвергаются статически: иначе опечатка в статусе становится падающим тестом и отправляет автора искать дефект в праве вместо буквы.

Тест без единого `expect` ДОЛЖЕН быть отвергнут: он проходит всегда, и это хуже отсутствия теста.

### 267.4. Ожидания-наблюдения — предикаты над документом

Кроме сравнений §267.3, `expect` принимает **наблюдения** — предикаты над evaluation-документом целиком, а не над полями одного результата (DECISION-0036, DECISION-0075). Каждое отрицается префиксом `not`:

```text
expect applied(MinimumWageRule);          expect not applied(ExemptionRule);
expect issue(RESOURCE_LIMIT);             expect not issue(TYPE_ERROR);
expect position(PayDuty, VIOLATED);       expect not position(PayDuty, ACTIVE);
```

| Наблюдение | Истинно, когда |
|---|---|
| `applied(R)` | в proof graph §180 есть узел `rule_application`, чей `rule` — StableId правила `R` |
| `issue(CODE)` | в `issues[]` документа есть запись с этим `code` |
| `position(T, S)` | в `positions[]` документа есть позиция, чей `template` — StableId норм-шаблона `T`, а `status` — имя `S` перечня §134 |
| `blocked_by(R)` | в значении ответа `why_not` §185 есть блокер, чей `rule` — StableId правила `R` либо перехода `P/T` §185.1 (errata E-0127) |
| `blocked_by(R, "причина")` | тот же блокер, и он — блокер перехода с причиной шага §180.2: `attempt` (попытка §164 не предъявлена), `from`, `on`, `guard`, `requires`, `join` (условие §161.1). У блокера правила причины нет, и он не совпадает ни с одной (DECISION-0156 §2.9) |
| `blockers(n)` | блокеров в значении ответа `why_not` ровно `n` (errata E-0127) |
| `judgment_request(P)` | в `judgmentRequests[]` результата есть запрос §47.3, чей `predicate` — StableId отношения суждения `P` (форма исполнялась обеими реализациями с E-0127, в прозе записана errata E-0169) |
| `judgment_request(P, A)` | тот же запрос, и его `authority` — StableId органа `A` (errata E-0169): без органа тест не отличает «вопрос суду» от «вопрос эксперту» по тому же отношению, а §47.3.1 принимает ответ только от органа декларации |
| `interpretations(R, …)` | `EvaluationInputManifest.interpretations` §168.3 равен ровно списку StableId прочтений `R, …` — локальных либо `пакет::Прочтение` (DECISION-0152 §7: та же квалификация и та же проверка вида по `exportKinds`, что у оси `interpretation` §168.2, — ожидание о чужом прочтении обязано разрешаться в тот же StableId, что и выбор) |

Словарь наблюдений ЗАКРЫТ и расширяется аддитивно — той же формулой, что словарь полей §267.3.

Причина у `blocked_by` нужна потому, что id блокера один и тот же у «переход не рассматривался» (попытки нет) и «условие не выполнено» (попытка есть): сцена, потерявшая попытку, без причины оставалась бы зелёной по совпадению id.

Три формы отвечают на вопросы, которые исход не выражает: **путь** («выведено именно этим правилом» — для акта, где два правила ведут к одному выводу, исход их не различает), **отказ** («пришла эта диагностика» — в частности, тест-сторож молчания утверждает причину `NEITHER`, а не только его наличие) и **адресный статус** (`normative_status` §267.3 — агрегат по всем позициям дела; при нескольких нормах он говорит `UNDETERMINED`, и проверить конкретную обязанность может только наблюдение).

`position` — экзистенциальный предикат намеренно: позиций одного шаблона в деле может быть много (по одной на подстановку носителя), и форма-поле заставила бы выбирать «главную». «Нарушена и не активна» выражается парой строк: `position(T, VIOLATED)` + `not position(T, ACTIVE)`.

Имена в аргументах проверяются по роду. Имя правила у `applied` и имя шаблона у `position` — StableId §14; их существование в программе проверяет ИСПОЛНЕНИЕ (программа предъявляется отдельно, §267.1), и несуществующее имя ДОЛЖНО давать отказ теста с этой причиной, а не тихое «не нашлось»: молчание читалось бы как утверждение о праве, тогда как это опечатка в букве. Имя статуса у `position` — имя перечня §134 и проверяется статически, как значения §267.3; `Issue.code` — свободная строка схемы, нормативного перечня кодов исполнения нет, поэтому `expect not issue(ОПЕЧАТКА)` проходит вакуумно — граница названа в DECISION-0036 §4.

Статический словарь не отличает исполнимое значение перечня §134 от ЗАРЕЗЕРВИРОВАННОГО: `AVAILABLE`, `EXERCISED`, `VALIDLY_EXERCISED`, `INVALIDLY_EXERCISED` синтаксически проходят у `position(T, S)` наравне с `ACTIVE`/`EXPIRED`/…, но 0.2 их не производит (errata E-0239). Положительное `expect position(T, RESERVED)` над таким значением вакуумно — красный либо мнимо-зелёный тест той же природы, что `expect not issue(ОПЕЧАТКА)` абзацем выше; форма `expect not position(T, RESERVED)` держится и годна регрессией.

### Числовая таблица с общим ожиданием

```law
test "Порог" variants (cost: Money) {
    "threshold/below" (799999 KZT);
    "threshold/exact" (800000 KZT);
} {
    given {
        assert repair_cost(cost);
    }
    evaluate truth(total_loss());
    expect truth_status == NEITHER;
}
```

## 268. Обязательные semantic tests

Conforming evaluator должен пройти как минимум:

1. explicit negative отличается от unknown;
2. positive и negative support дают `BOTH` без explosion;
3. bare body atom не срабатывает при `BOTH`;
4. `supported(P)` срабатывает при `BOTH`;
5. strict conclusion не побеждается defeasible rule;
6. два conflicting strict conclusions сохраняются;
7. stronger defeasible candidate побеждает weaker opposing candidate;
8. incomparable candidates дают conflict;
9. defeater блокирует, но не поддерживает complement;
10. exception из `unless` не равен explicit contrary conclusion;
11. default-negation cycle отклоняется executable validator-ом;
12. positive strict cycle без base не выводит facts;
13. dynamic reference записывает resolved edition;
14. rule вне effective interval не применимо;
15. retroactive governed interval работает отдельно от effective interval;
16. weak permission не выводится без closure policy;
17. maintenance violation выводится по counterexample;
18. maintenance satisfaction не выводится только из отсутствия counterexample;
19. achievement duty не violated до due time;
20. violation требует completeness/adjudication после deadline;
21. power effect возникает только при valid exercise;
22. immunity блокирует legal effect, но не стирает attempted event;
23. incomparable surviving power/immunity не создают effect без explicit policy;
24. conflicting satisfied/violated supports дают `normative_status = CONFLICTED`;
25. interpretation alternatives вычисляются отдельно;
26. priority cycle даёт `PRIORITY_CONFLICT`;
27. unit mismatch является type error;
28. currency conversion требует snapshot;
29. Date-to-Instant требует timezone/policy;
30. same EvaluationInputManifest produces same result/proof hash;
31. source formatting change не меняет semantic hash;
32. rule body change меняет semantic hash и invalidates dependent cache.
33. explicit contrary `unless C then not A` lowers to defeasible contrary + priority, not strict rule.
34. late producer после status completion barrier отклоняется независимо от file order.
35. Date legal_time не разрешает multiple same-date editions без pinned temporal resolution policy.
36. DATA result не получает фиктивный truth status; dimensions следуют result_kind/query contract.
37. necessary/exact definition lowers necessary direction to Constraint, not formula-headed rule.
38. different conforming compiler receipts leave semantic manifest/result/proof hashes unchanged.
39. CalendarSnapshot dataset hash mismatch is rejected before evaluation.
40. business-time operation outside calendar coverage returns `CALENDAR_OUT_OF_RANGE`.
41. inherited context profile and equivalent expanded context produce the same EvaluationInputManifest.
42. `let`/`match` lowering is deterministic and alpha-normalized.
43. non-exhaustive match is rejected in `core-executable`, and match-arm order is semantic.
44. source/manifest/lockfile validators agree on lowercase package-name syntax.

## 269. Differential testing

Независимые implementations должны обмениваться:

```text
.law source
.lawlock
.lawcase
expected .lawir.json hash
expected .lawresult.json
expected .lawproof.json hash
```

Допускается различие human-readable wording, но не canonical result semantics.

## 270. Property-based tests

Executable profiles могут объявлять:

```law
property NonNegativeTax {
    forall input in GeneratedTaxInputs;
    expect calculate_tax(input) >= 0 KZT;
}
```

Generator domain должен быть конечным/seeded, а seed фиксироваться в test manifest.

### 270.1. Цель акта как свойство (аддитивно, DECISION-0089)

Свойство может нести **основание** — `basis <фрагмент>;` — якорь §194 в
фрагмент того же пакета, называющий, ЗАЧЕМ акт принят (преамбула,
пояснительная записка, статья о целях). Свойство с основанием есть **цель**
акта: утверждение об исходах, которое право обязано давать на всяком деле
своего домена. Основание одно; второе основание есть вторая цель.

Цели могут быть упорядочены: `over <цель>;` в теле старшей цели называет
младшую (частичный порядок; цикл и ссылка на себя — статический отказ).
Порядок — свойство ФИЛЬТРА над вердиктами целей (какое прочтение §155 им
служит), а не семантики: ни на исполнение права, ни на вердикт отдельной
цели он не влияет.

Ожидание может быть **позицией** §134: `expect position(Шаблон, СТАТУС, x);`,
где `x` — переменная `forall`. Оно истинно для элемента домена, если в
`positions[]` evaluation-документа стоит экземпляр шаблона в названном
статусе, КАСАЮЩИЙСЯ элемента: он назван стороной (`holder`, `beneficiary`,
`counterparty`) либо любым `entity_ref` в payload (`against`, аргументы
действия, условие цели). Наблюдающих правил у такого свойства нет — позиции
телу правила недоступны; нарушения считает исполнитель свойства запросом
`positions` над тем же миром, и обе реализации обязаны сходиться на том,
кого позиция касается. Шаблон, не объявленный программой, даёт «не
проверено», а не «держится». Статус — имя перечня `NormativeStatus`
(`LDC-E1319` вне словаря).

В теле свойства допускается метка §218 (`label`); в пониженный документ
свойства уходят `basis` (StableId фрагмента), `labels` и `over` — только
при наличии, документ без них байтово прежний. В CLIR пакета цели не
понижаются: они, как и тесты §267, описывают ожидание, а не норму.

```law
property WeakerPartyRecovers {
    label ru-KZ official "слабая сторона получает возмещение";
    basis CONSUMER_PREAMBLE;
    over SupplierKeepsMargin;
    forall c in collect x: Contract where consumer_contract(x);
    expect refund_due(c);
}
```
