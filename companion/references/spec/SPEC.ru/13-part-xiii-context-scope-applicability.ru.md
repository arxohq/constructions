# Часть XIII. Context, scope и applicability

## 89. Evaluation Context

Canonical context содержит:

*Описательная схема, а не объявление поверхности 0.1 (`Option<…>`, запись `A | B` в типе поля и поле с именем hard keyword `calendar`): блок не компилируется намеренно и остаётся `text`; см. errata E-0130.*

```text
record EvaluationContext {
    jurisdiction: Jurisdiction;
    territory: Option<Territory>;
    legal_time: LegalTime; // Date | Instant
    event_time: Option<Interval<Instant>>;
    decision_time: Instant;
    knowledge_time: Instant;
    timezone: Timezone;
    timezone_db_snapshot: SnapshotRef;

    source_resolver: SourceResolverRef;
    interpretation_selection: InterpretationSelection;
    evidence_policy: EvidencePolicyRef;
    calendar: CalendarRef;
    deadline_policy: DeadlinePolicyRef;
    temporal_resolution_policy: Option<TemporalResolutionPolicyRef>;

    fact_snapshot: SnapshotRef;
    evidence_snapshot: SnapshotRef;
    external_snapshots: Map<Capability, SnapshotRef>;

    mode: advisory | compliance | regulatory | simulation | audit;
}
```

Profiles могут добавлять поля через namespaced extensions.

### 89.1. Named context profiles

Чтобы `no hidden defaults` не превращал authoring в повторение десятков полей, 0.1 поддерживает явные, версионированные context profiles:

```law
context profile KZ_COMPLIANCE_2026 {
    jurisdiction KZ;
    timezone "Asia/Qyzylorda";
    timezone_db_snapshot TZDB_2026A;
    source_resolver KZ_OFFICIAL_RESOLVER_2026;
    evidence_policy OFFICIAL_RECORDS_POLICY;
    calendar KZ_2026;
    deadline_policy KZ_DEFAULT_DEADLINES_2026;
    mode compliance;
}

case Project17 {
    context extends KZ_COMPLIANCE_2026 {
        legal_time @2026-08-25;
        decision_time @2026-08-25T14:30:00+05:00;
        knowledge_time @2026-08-25T14:00:00+05:00;
        interpretation OfficialBvrReading;
    }
}
```

Profile inheritance в 0.1 является single, acyclic и field-wise. Child может override поле; duplicate assignment внутри одного level является error. Profile и все его dependencies обязаны быть pinned по version/hash. Перед evaluation compiler materialize-ит полный context в `EvaluationInputManifest`; runtime не выполняет наследование. Команда `lawc context show <case> --expanded` и LSP hover обязаны показывать effective value, origin profile и override chain каждого поля. Поэтому удобные inherited values остаются явными и аудируемыми, а не ambient defaults.

### 89.2. Статус типов полей контекста

Типы полей `EvaluationContext` (§89) закрытого перечня не образуют и в §257–§266 не входят — кроме одного (errata E-0039). Различие проходит по вопросу, на который отвечают §257–§266: «что даёт импорт package», то есть какое имя автор вправе написать в `.law`-файле, не объявив его.

- `Jurisdiction` автор пишет: §54 печатает `const KZ: Jurisdiction = Jurisdiction { code: "KZ" };`, `spec/examples/kz/social-code-art175.law` объявляет им параметр institutional relation. Поэтому он экспортируется `law.std.data` (§257) и разрешается в `urn:law:std#Jurisdiction`.
- `LegalTime` (§2.15: `Date | Instant`), `InterpretationSelection` (§155/§156), `EvidencePolicyRef` (§78.1), `CalendarRef` (§85), `DeadlinePolicyRef` (§86), `TemporalResolutionPolicyRef` (§2.15), `Capability` (§242), а также `Territory`, `SnapshotRef` и `SourceResolverRef`, определённые только этой записью, — **структурные типы самой записи контекста**, а не экспорт package. `EvaluationContext` не пишется автором в `.law` и не импортируется, поэтому и экспортировать эти имена некому. Ни одно из них, кроме `Territory`, не встречается ни в одном `.law` спецификации, корпуса или векторов; `Territory` встречается — но именно как собственная `entity` пакета, что и разбирается ниже.

Различие не косметическое, и цена ошибки в нём измерена. Имя типа, попавшее в std-словарь, перекрывает одноимённую сущность пакета молча (Часть XXXIII, абзац о типах): объявление остаётся в namespace пакета, употребления адресуют `urn:law:std#N`, диагностики нет. `Territory` объявлен собственной `entity` в двух живых пакетах корпуса (`kz.corpus.legal_acts`, `kz.corpus.healthcode`); признай его спецификация std-типом — шесть употреблений в них отцепились бы от своих объявлений, и `lawc check` остался бы зелёным. Ровно поэтому список полей §89 **не** переносится в §257–§266 целиком: он описывает структуру контекста, а не словарь имён, отнимаемых у пакетов.

Для `DeadlinePolicy` это отношение закрыто в 0.2: именованная декларация §86
понижается в узел CLIR, а `DeadlinePolicyRef` есть его StableId. Ссылка должна
разрешиться в том же закреплённом пакете при lowering дела или профиля;
необъявленное имя — `LDC-E1332`, не поздний `MISSING_POLICY`. `CalendarRef`
по-прежнему адресует закреплённый `CalendarSnapshot` §85.

### 89.3. Вычисление без временного контекста (0.2+)

В `.lawtest` блок `context` в `given` необязателен, если вычисление не
использует временной срез. Например, тест арифметического или химического
правила может содержать только утверждения. Понижение записывает пустой
объект `case.context`; особого тестового режима у оценщиков нет.

При отсутствии `legal_time` не подставляются ни текущая, ни фиксированная
дата, ни технические значения `decision_time`, `knowledge_time`, `timezone`.
Отсутствующие оси представлены как `null` в манифесте результата и входят
в его хэш. Явно заданные оси по-прежнему проверяются на корректность.

Потребитель временного среза требует соответствующее поле с диагностикой
`CONTEXT_FIELD_MISSING`, называющей причину. До отбора узлов проверяются
`effective` правил, ограничений и замыканий, `valid_time` утверждений,
применимость датирующих редакций и динамические ссылки. Проверка программы
идёт после выбора интерпретаций. При исполнении дата также требуется для
временного статуса нормативной позиции, выбора прецедента и неявного
чтения значения параметра на дату права; политика доказательств требует
даты права и среза знания. Дата в литерале, время события или метаданные
публикации сами по себе не требуют временного контекста вычисления.

Для дел с явно заданным (в том числе унаследованным) `legal_time` сохраняются
прежние технические defaults с предупреждениями. Замороженная семантика
0.1 сохраняет безусловную обязательность `legal_time`.

## 90. Scope formula

```text
rule ImportTaxRule defeasible {
    scope context.jurisdiction == KZ
      and context.domain == Tax
      and transaction.type == Import;
    ...
}
```

`scope` семантически объединяется с `when`, но сохраняется отдельно в IR для indexing, analysis и объяснений.

Статический граф зависимостей §110 также строится по `scope ∧ when`
(errata E-0181). Место записи условия не меняет вид ребра, проверку цикла
§191, барьер полноты §111, зависимость от замыкания §70 или позднего
эффекта §127. Это относится и к агрегатам, кванторам и status-условиям
вложенных условных термов §56; разрешённые монотонные чтения сохраняют
свои изъятия. Фикции §147 и классификации §148 подчиняются тому же правилу.


## 91. Applicability status

Applicability выводится как proposition `applicable(rule_application, context)` и затем проецируется в:

```text
APPLICABLE       // positive only
NOT_APPLICABLE   // negative only
CONFLICTED       // positive and negative support
UNDETERMINED     // neither / missing dependency
```

Причины `UNDETERMINED`:

- missing context;
- unresolved source edition;
- interpretation not selected;
- external judgment, необходимый именно для scope;
- temporal ambiguity scope/lifecycle.

`NOT_APPLICABLE` не означает false conclusion. Rule просто не участвует в evaluation. `CONFLICTED` также не активирует rule в conservative executable profile; обе стороны и причины сохраняются в applicability proof.

## 91.1. Trigger status

Applicability не включает substantive `when` body. Trigger formula имеет отдельный paraconsistent summary:

```text
SATISFIED       // TRUE_ONLY
NOT_SATISFIED   // FALSE_ONLY
CONFLICTED      // BOTH
UNDETERMINED    // NEITHER / missing dependency
```

Например, действующее правило в надлежащей юрисдикции может быть `APPLICABLE`, но не сработать, потому что `when` имеет `NOT_SATISFIED`. Только `SATISFIED` создаёт ordinary candidate. Использование одной стороны конфликтного prerequisite требует явного `supported(...)` в самой trigger formula; без этого trigger получает `CONFLICTED`.

## 92. Edition applicability

Edition может участвовать в evaluation только если:

1. dynamic/static reference разрешён;
2. edition соответствует language/source policy;
3. lifecycle/profile считает его действующим на legal time;
4. rule effective interval включает legal time;
5. governed event входит в temporal scope;
6. interpretation включена selection policy.

Каждый шаг появляется в proof/explanation.

Условие 3 `evaluate` применяет ко всякому нормативному узлу с якорями (`rule`, `norm_template`, `constraint`, `priority_rule`, `assertion`; errata E-0095): узел, ВСЕ датирующие якоря которого ведут на редакции, неприменимые на legal time по машине lifecycle §31 (`closed` | `suspended` | `not_yet`), в evaluation не участвует — так же, как правило вне `effective` §87 (условие 4). Якорь датирует узел редакцией своего фрагмента §28 либо самой редакцией; якорь, не разрешившийся ни в то, ни в другое, узел не датирует. Редакция без единого события применимости §31 (`in_force`, `restored`, `suspended`, `repealed`, `expired`, `invalidated`) и без `applicability: timeless` считается ВНЕ ДАТИРОВКИ и узел не исключает: обычай, доктрину и памятник в действие датой не вводили, и «право не датировано» есть ответ, а не «право не действует». Исключение сообщается issue `EDITION_NOT_APPLICABLE` (severity `info`, одна на редакцию, узлы перечислены) и в `why_not(P)` §185 статусом `NOT_APPLICABLE` кандидата. Событие lifecycle, несравнимое с legal time по §82 (`Date` против `Instant`), применимости не устанавливает: узел остаётся, документ несёт предупреждение `EDITION_APPLICABILITY_AMBIGUOUS`. Ex tunc (`invalidated` с момента принятия) §31 не выражает, и проекция его не подразумевает.

**Состав редакций, предъявленный вызывающим (errata E-0167).** Запрос §168.3 может нести transport-поле `editions_as_presented: LegalTime` — утверждение вызывающего, что состав нормативных узлов программы УЖЕ спроецирован им по машине применимости §31 на названную дату. При нём условие 3 по legal time ДЕЛА не перепроверяется: узел, оставленный вызывающим, участвует в вычислении, даже если его датирующие редакции на дату права дела неприменимы. Заменяется ровно условие 3 и ничего больше: условия 1, 2, 4–6, окно `effective` §87, ось `governs` §87, чтение датированного параметра на дату права и временной статус нормативной позиции §133 читают legal time дела как обычно. Движок предъявленную проекцию НЕ проверяет — проверить её значило бы вновь исполнить условие 3 по дате дела, то есть исполнить пересечение двух проекций; вместо этого он её НАЗЫВАЕТ: дата входит в `EvaluationInputManifest` полем `editions_as_presented` §170 (и, значит, в `semantic_hash`), а документ несёт одну issue `EDITIONS_AS_PRESENTED` (severity `info`), где сказано, на какую дату предъявлен состав и что условие 3 по дате права дела не проверялось. Без поля документ не меняется ни байтом. Ответ такого вычисления есть контрфактический ответ «то же дело при предъявленном составе редакций», а не право на дату дела; им и только им строится сторона отчёта по оси редакций (L6/О-2): проекция §31 применяется ВМЕСТО условия 3, а не поверх него. Значение не вида `LegalTime` §2.15 — отказ `EVALUATION_REQUEST_INVALID` до всякого вывода.

## 93. Material и personal scope

Высокоуровневые forms:

```text
applies_to Residents;
domain Mining;
region KyzylordaRegion;
```

являются sugar над `scope` predicates, определёнными jurisdiction/domain packages.

---
