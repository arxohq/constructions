# Часть IV. Проект и файлы

## 9. Стандартная структура проекта

```text
law.toml
law.lock
src/
  main.law
  sources/
  rules/
  definitions/
  interpretations/
cases/
  project_17.lawcase
tests/
  bvr.lawtest
resources/
  calendars/
  source-texts/
  datasets/
```

## 10. `law.toml`

```toml
[package]
name = "kz.bvr"
version = "2026.1.0"
language = "0.1"
namespace = "urn:kz:law:bvr"

[features]
profiles = ["core-executable", "core-auditable"]

[dependencies]
"law.std" = "0.1.0"
"kz.sources" = "2026.2.0"
"kz.calendar" = "2026.1.0"
```

`law.toml` является authoring manifest. Нормативное значение имеет разрешённый `law.lock`.

**Две формы записи зависимости (errata E-0160).** Значение строки `[dependencies]` — либо строка версии, либо таблица; обе формы нормативны по `schema/package-manifest.schema.json` (§0.1 п. 5), и вторая означает ровно то же плюс три необязательных поля:

```toml
[dependencies]
"kz.sources" = "2026.2.0"
"kz.calendar" = { version = "2026.1.0", registry = "arxo", features = ["holidays"] }
"kz.archive"  = { version = "2026.1.0", optional = true }
```

- `version` — та же ТОЧНАЯ версия, что и у строковой формы: с ней сверяется `import` (`LDC-E1111`, раздел 23) и она же закрепляется lockfile-ом (раздел 11). Строковая форма есть сокращение таблицы с одним `version`; смысл записи от формы не зависит;
- `registry` — издатель, у которого зависимость взята. Названный издатель обязан совпасть с `registryId` закреплённого пакета; lockfile, не называющий издателя, сверке не подлежит — он о нём молчит, а не утверждает иное;
- `features` — набор возможностей, ЗАПРОШЕННЫХ потребителем у этой зависимости. Он едет в `dependencyEdges[].features` разрешённого lockfile (раздел 11: dependency graph и feature set) и обязан содержаться в feature set закреплённого пакета: запрос возможности, которой у закреплённого пакета нет, воспроизводимой сборкой не является. Умолчание — пустой набор;
- `optional` — зависимость, которую сборка вправе не разрешать. `optional = true` освобождает её от обязательного закрепления разделом 11: отсутствие такой зависимости в `law.lock` нарушением не является. Закреплённая необязательная зависимость проверяется как всякая другая. Умолчание — `false`.

**Профиль канона (DECISION-0170).** Манифест вправе назвать ровно один
профиль §170.1 — именованный, датированный и хэшированный состав библиотеки
норм, из которой пакет импортирует:

```toml
[profile]
id = "kz.sources"
version = "2026.2.0"
registry = "arxo"   # необязателен; издатель, как у зависимости
```

Профиль — граница допустимой библиотеки, а не состав мира §168.4. При
названном профиле каждая строка `[dependencies]` ОБЯЗАНА называть пакет из
развёртки профиля B (§170.1) с той же точной версией; её `registry` обязан
равняться `registryId` элемента B, её `features` — содержаться в
`features`, предоставляемых элементом B; `optional = true` вне B границы
не расширяет. Пакет, календарный набор §85 или пакет развёрток §279.1.8,
названный вне соответствующего перечня профиля, — `LDC-E1366` (три
различимых перечня: пакеты, `calendars[]`, `expansions[]`). Исключение
названо явно: прелюдия `law.std` и её подтверждающая строка (DECISION-0166
§4.3, §4.5) профилем не ограничиваются. Секция `[profile]` читается ТОЛЬКО
у корня лока: у пакета-зависимости она описательна и в замыкание корня не
входит, как не читаются и локи зависимостей. Дело без `[profile]`
работает как прежде.

## 11. `law.lock`

Lockfile ДОЛЖЕН содержать:

- exact package version;
- package namespace;
- content hash;
- resolver URL или registry ID;
- feature set;
- dependency graph;
- language semantics version.

`law.lock` ДОЛЖЕН быть UTF-8 canonical JSON, валидным по `schema/lockfile.schema.json`. Arrays, образующие semantic sets, сортируются по canonical identity; object members сериализуются по правилам canonical JSON из раздела 208. Generated-at timestamp и compiler build в semantic lockfile не включаются.

Production evaluator НЕ ДОЛЖЕН самостоятельно обновлять lockfile. Обновление выполняется отдельной resolver-командой и сопровождается dependency/source diff.

Покрытие манифеста lockfile-ом (errata E-0160) читается по развёрнутой записи зависимости раздела 10, а не по форме её значения. Для каждой зависимости, кроме необязательной и кроме прелюдии `law.std` (раздел 23), закреплённый пакет ОБЯЗАН существовать и совпасть с манифестом по точной версии; названный манифестом издатель — с `registryId`, когда lockfile его называет; запрошенные возможности — содержаться в feature set закреплённого пакета. Ребро dependency graph несёт запрошенный набор возможностей: `features` таблицы, пустой набор — у строковой формы.

**Лок при профиле (DECISION-0170).** Лок пакета с `[profile]` несёт блок
`profile: {id, version, contentHash, registryId?}` и закрепляет ВСЮ
развёртку профиля B, а не только замыкание импортов корня: `packages` —
каждый элемент B записью исчерпывающего состава `name, version, namespace,
contentHash, features` (предоставляемые из элемента B; отсутствие — пустой
набор), а `registryId` и вычисляемый `resolverUri =
registry://<registryId>/<name>/<version>` — оба только когда поле
`registryId` есть в элементе B (единственный источник «известности»
издателя; преобразование в лок не обогащает ничем); `dependencyEdges` —
рёбра корня по ФАКТИЧЕСКИМ `import`-декларациям корня (кроме подтверждающих
импортов прелюдии `law.std.*`): `requested = resolved =` точный пин
элемента B, `features` — запрошенные строкой `[dependencies]`, а при импорте
без строки — `[]`; строка без импорта ребра не даёт; плюс ребро для каждого
`imports` CLIR каждого пакета B (`requested = resolved =` точная версия
импорта, `features = []`); в многопутевом графе пакет — одна запись, а
рёбра сохраняются все; календари профиля — записи `resources` вида
`calendar-dataset` существующей формы; `expansions` лока — записи
`LockedExpansion` дела, чьи пакеты обязаны быть в `expansions[]` профиля;
`resolutionHash` покрывает блок профиля. Граф детерминирован по полным
входам (артефакт профиля, манифест и импорты корня, ресурсы): равные
полные входы дают один `resolutionHash`. Состав сверяется как L против B
по `contentHash` профиля из лока; подмена артефакта профиля на диске —
`LDC-E1367`. Артефакт профиля у пакета в разработке материализуется
content-addressed рядом с CLIR зависимостей: `deps/profiles/<id>/<version>/profile.json`.
**Материализация (П14 DECISION-0170).** `deps/` пакета с профилем держит
CLIR ТОЛЬКО замыкания импортов корня C; остальная B закреплена локом
хэшами без файлов и читается из реестра — в авторском дереве это
`corpus/clir` ближайшего корня, в выпуске — CLIR всей B, который выпуск
несёт сам. Отсутствие файла у пакета C — отказ материализации; отсутствие
у пакета B \ C — не отказ, пока его CLIR предъявлен реестром для проверки
замкнутости.

## 12. Расширения файлов

- `.law` — обычный исходный файл;
- `.law.md` — literate law на базе Markdown с fenced blocks `law`;
- `.lawcase` — immutable case/fact snapshot;
- `.lawtest` — conformance и regression tests;
- `.lawir.json` — canonical IR;
- `.lawproof.json` — proof graph;
- `.lawresult.json` — evaluation result.


