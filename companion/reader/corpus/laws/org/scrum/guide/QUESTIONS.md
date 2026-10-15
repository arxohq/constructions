# Вопросы к пакету `scrum.guide`

<!-- Порождено из analysis/questions.json: python3 verify/ci/gates/coverage/check_package_questions.py --emit. Не править руками. -->

Каталог **предусмотренных** запросов §172 и того, чем каждый проверен (DECISION-0190). Карточка не означает положительного ответа по делу: ответ даёт только evaluation-документ с доказательством. Отсутствие карточки означает «не описано каталогом», а не «право молчит».

## SG_S1

Единицы источника: SG_S1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-createincrementeverysprint` | Какие позиции действуют по делу и в каком статусе стоит «CreateIncrementEverySprint»? | positions | нормы `CreateIncrementEverySprint` | `evaluate positions(); — ожидаемая форма position(CreateIncrementEverySprint, <статус>)` | — | тестов 1 |
| `poziciya-ensureattendeesprepared` | Какие позиции действуют по делу и в каком статусе стоит «EnsureAttendeesPrepared»? | positions | нормы `EnsureAttendeesPrepared` | `evaluate positions(); — ожидаемая форма position(EnsureAttendeesPrepared, <статус>)` | — | тестов 1 |
| `poziciya-finalizesprintgoal` | Какие позиции действуют по делу и в каком статусе стоит «FinalizeSprintGoal»? | positions | нормы `FinalizeSprintGoal` | `evaluate positions(); — ожидаемая форма position(FinalizeSprintGoal, <статус>)` | — | тестов 1 |
| `poziciya-keepsprintgoalsafe` | Какие позиции действуют по делу и в каком статусе стоит «KeepSprintGoalSafe»? | positions | нормы `KeepSprintGoalSafe` | `evaluate positions(); — ожидаемая форма position(KeepSprintGoalSafe, <статус>)` | — | тестов 1 |
| `poziciya-maintainquality` | Какие позиции действуют по делу и в каком статусе стоит «MaintainQuality»? | positions | нормы `MaintainQuality` | `evaluate positions(); — ожидаемая форма position(MaintainQuality, <статус>)` | — | тестов 1 |
| `poziciya-sharedefinitionofdone` | Какие позиции действуют по делу и в каком статусе стоит «ShareDefinitionOfDone»? | positions | нормы `ShareDefinitionOfDone` | `evaluate positions(); — ожидаемая форма position(ShareDefinitionOfDone, <статус>)` | — | тестов 1 |

- **Не отвечает:** Покрывает ли пакет весь акт — значит ли отсутствие карточки, что право молчит? — норма есть в тексте, правил ещё нет (SG_S1). Правила заведены у 25 закреплённых фрагментов из 28: остальные закреплены байтами публикации, но исполняемых норм не несут. Отсутствие карточки означает «в модели нормы нет», а не «право молчит».
- **Не отвечает:** Можно ли спросить вывод, у которого нет порождённого сценария? — ограничение языка или движка (SG_S1). 9 выводов пакета остались без исполнимого свидетельства: их посылки содержат дизъюнкцию, текстовое значение или вызов терма, либо голова вычисляемая. Такие выводы записаны в internal и станут карточками вместе со сценариями, написанными руками.
- **Не отвечает:** Все ли позиции пакета подтверждены положительным сценарием? — норма есть в тексте, правил ещё нет (SG_S1). 6 норм пакета подтверждены только отрицательным сценарием («на этих фактах позиция не возникает»): построить мир, который их активирует, порождающий проход не смог. Положительное свидетельство — долг.

## SG_S2

Единицы источника: SG_S2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `accountable-for-fostering-environment` | Установлено ли по делу: accountable_for_fostering_environment? | truth | `accountable_for_fostering_environment(p: Person, t: Team)` | `evaluate truth(accountable_for_fostering_environment(<p>, <t>));` | — | тестов 1 |

## SG_S3_1

Единицы источника: SG_S3_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-keepworkvisible` | Какие позиции действуют по делу и в каком статусе стоит «KeepWorkVisible»? | positions | нормы `KeepWorkVisible` | `evaluate positions(); — ожидаемая форма position(KeepWorkVisible, <статус>)` | — | тестов 1 |

## SG_S3_2

Единицы источника: SG_S3_2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-inspectartifactsandprogress` | Какие позиции действуют по делу и в каком статусе стоит «InspectArtifactsAndProgress»? | positions | нормы `InspectArtifactsAndProgress` | `evaluate positions(); — ожидаемая форма position(InspectArtifactsAndProgress, <статус>)` | — | тестов 1 |

## SG_S3_3

Единицы источника: SG_S3_3.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-adjustprocessormaterials` | Какие позиции действуют по делу и в каком статусе стоит «AdjustProcessOrMaterials»? | positions | нормы `AdjustProcessOrMaterials` | `evaluate positions(); — ожидаемая форма position(AdjustProcessOrMaterials, <статус>)` | — | тестов 1 |

## SG_S5_1

Единицы источника: SG_S5_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `committed-to-creating-increment` | Установлено ли по делу: committed_to_creating_increment? | truth | `committed_to_creating_increment(p: Person, t: Team)` | `evaluate truth(committed_to_creating_increment(<p>, <t>));` | — | тестов 1 |
| `developers-accountable-for` | Установлено ли по делу: developers_accountable_for? | truth | `developers_accountable_for(t: Team, a: DeveloperAccountability)` | `evaluate truth(developers_accountable_for(<t>, <a>));` | — | тестов 1 |

## SG_S5_2

Единицы источника: SG_S5_2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `product-owner-accountable-for` | Установлено ли по делу: product_owner_accountable_for? | truth | `product_owner_accountable_for(p: Person, t: Team, a: ProductOwnerAccountability)` | `evaluate truth(product_owner_accountable_for(<p>, <t>, <a>));` | — | тестов 1 |
| `product-owner-is-a-committee` | Установлено ли по делу: product_owner_is_a_committee? | truth | `product_owner_is_a_committee(t: Team)` | `evaluate truth(product_owner_is_a_committee(<t>));` | — | тестов 1 |
| `remains-accountable-for-backlog` | Установлено ли по делу: remains_accountable_for_backlog? | truth | `remains_accountable_for_backlog(p: Person, t: Team)` | `evaluate truth(remains_accountable_for_backlog(<p>, <t>));` | — | тестов 1 |
| `poziciya-respectproductownerdecisions` | Какие позиции действуют по делу и в каком статусе стоит «RespectProductOwnerDecisions»? | positions | нормы `RespectProductOwnerDecisions` | `evaluate positions(); — ожидаемая форма position(RespectProductOwnerDecisions, <статус>)` | — | тестов 1 |

## SG_S5_3

Единицы источника: SG_S5_3.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `scrum-master-accountable-for` | Установлено ли по делу: scrum_master_accountable_for? | truth | `scrum_master_accountable_for(p: Person, t: Team, a: ScrumMasterAccountability)` | `evaluate truth(scrum_master_accountable_for(<p>, <t>, <a>));` | — | тестов 1 |
| `scrum-master-serves-organization-by` | Установлено ли по делу: scrum_master_serves_organization_by? | truth | `scrum_master_serves_organization_by(p: Person, t: Team, s: ScrumMasterService)` | `evaluate truth(scrum_master_serves_organization_by(<p>, <t>, <s>));` | — | тестов 1 |
| `scrum-master-serves-product-owner-by` | Установлено ли по делу: scrum_master_serves_product_owner_by? | truth | `scrum_master_serves_product_owner_by(p: Person, t: Team, s: ScrumMasterService)` | `evaluate truth(scrum_master_serves_product_owner_by(<p>, <t>, <s>));` | — | тестов 1 |
| `scrum-master-serves-team-by` | Установлено ли по делу: scrum_master_serves_team_by? | truth | `scrum_master_serves_team_by(p: Person, t: Team, s: ScrumMasterService)` | `evaluate truth(scrum_master_serves_team_by(<p>, <t>, <s>));` | — | тестов 1 |
| `poziciya-ensureeventswithintimebox` | Какие позиции действуют по делу и в каком статусе стоит «EnsureEventsWithinTimebox»? | positions | нормы `EnsureEventsWithinTimebox` | `evaluate positions(); — ожидаемая форма position(EnsureEventsWithinTimebox, <статус>)` | — | тестов 1 |

## SG_S6

Единицы источника: SG_S6.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `formal-inspection-opportunity` | Установлено ли по делу: formal_inspection_opportunity? | truth | `formal_inspection_opportunity(e: ScrumEvent)` | `evaluate truth(formal_inspection_opportunity(<e>));` | — | тестов 1 |
| `inspection-opportunity-lost` | Установлено ли по делу: inspection_opportunity_lost? | truth | `inspection_opportunity_lost(s: Sprint, k: EventKind)` | `evaluate truth(inspection_opportunity_lost(<s>, <k>));` | — | тестов 1 |

## SG_S6_1

Единицы источника: SG_S6_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `cancellation-declared-by-product-owner` | Установлено ли по делу: cancellation_declared_by_product_owner? | truth | `cancellation_declared_by_product_owner(s: Sprint)` | `evaluate truth(cancellation_declared_by_product_owner(<s>));` | — | тестов 1 |
| `next-sprint-start-due` | Установлено ли по делу: next_sprint_start_due? | truth | `next_sprint_start_due(next: Sprint, d: Date)` | `evaluate truth(next_sprint_start_due(<next>, <d>));` | — | тестов 1 |
| `sprint-length-conforms` | Установлено ли по делу: sprint_length_conforms? | truth | `sprint_length_conforms(s: Sprint)` | `evaluate truth(sprint_length_conforms(<s>));` | — | тестов 1 |
| `poziciya-productownercancelssprint` | Какие позиции действуют по делу и в каком статусе стоит «ProductOwnerCancelsSprint»? | positions | нормы `ProductOwnerCancelsSprint` | `evaluate positions(); — ожидаемая форма position(ProductOwnerCancelsSprint, <статус>)` | — | тестов 1 |
| `poziciya-renegotiatescope` | Какие позиции действуют по делу и в каком статусе стоит «RenegotiateScope»? | positions | нормы `RenegotiateScope` | `evaluate positions(); — ожидаемая форма position(RenegotiateScope, <статус>)` | — | тестов 1 |

## SG_S6_2

Единицы источника: SG_S6_2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `adviser-admitted` | Установлено ли по делу: adviser_admitted? | truth | `adviser_admitted(p: Person, e: ScrumEvent)` | `evaluate truth(adviser_admitted(<p>, <e>));` | — | тестов 1 |

## SG_S6_2_2

Единицы источника: SG_S6_2_2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-selectbacklogitems` | Какие позиции действуют по делу и в каком статусе стоит «SelectBacklogItems»? | positions | нормы `SelectBacklogItems` | `evaluate positions(); — ожидаемая форма position(SelectBacklogItems, <статус>)` | — | тестов 1 |

## SG_S6_2_3

Единицы источника: SG_S6_2_3.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `work-planning-at-developers-discretion` | Установлено ли по делу: work_planning_at_developers_discretion? | truth | `work_planning_at_developers_discretion(s: Sprint)` | `evaluate truth(work_planning_at_developers_discretion(<s>));` | — | тестов 1 |

## SG_S6_3

Единицы источника: SG_S6_3.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `daily-scrum-participant` | Установлено ли по делу: daily_scrum_participant? | truth | `daily_scrum_participant(p: Person, e: ScrumEvent)` | `evaluate truth(daily_scrum_participant(<p>, <e>));` | — | тестов 1 |

## SG_S7

Единицы источника: SG_S7.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `commitment-of` | Установлено ли по делу: commitment_of? | truth | `commitment_of(a: Artifact, c: Commitment)` | `evaluate truth(commitment_of(<a>, <c>));` | — | тестов 1 |

## SG_S7_1

Единицы источника: SG_S7_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `ready-for-selection` | Установлено ли по делу: ready_for_selection? | truth | `ready_for_selection(item: BacklogItem)` | `evaluate truth(ready_for_selection(<item>));` | — | тестов 1 |
| `responsible-for-sizing` | Установлено ли по делу: responsible_for_sizing? | truth | `responsible_for_sizing(p: Person, item: BacklogItem)` | `evaluate truth(responsible_for_sizing(<p>, <item>));` | — | тестов 1 |

## SG_S7_1_1

Единицы источника: SG_S7_1_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-oneobjectiveatatime` | Какие позиции действуют по делу и в каком статусе стоит «OneObjectiveAtATime»? | positions | нормы `OneObjectiveAtATime` | `evaluate positions(); — ожидаемая форма position(OneObjectiveAtATime, <статус>)` | — | тестов 1 |

## SG_S7_2

Единицы источника: SG_S7_2.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `sprint-backlog-complete` | Установлено ли по делу: sprint_backlog_complete? | truth | `sprint_backlog_complete(s: Sprint)` | `evaluate truth(sprint_backlog_complete(<s>));` | — | тестов 1 |

## SG_S7_2_1

Единицы источника: SG_S7_2_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `scope-negotiation-within-sprint-permitted` | Установлено ли по делу: scope_negotiation_within_sprint_permitted? | truth | `scope_negotiation_within_sprint_permitted(s: Sprint)` | `evaluate truth(scope_negotiation_within_sprint_permitted(<s>));` | — | тестов 1 |
| `sprint-goal-in-sprint-backlog` | Установлено ли по делу: sprint_goal_in_sprint_backlog? | truth | `sprint_goal_in_sprint_backlog(s: Sprint)` | `evaluate truth(sprint_goal_in_sprint_backlog(<s>));` | — | тестов 1 |

## SG_S7_3

Единицы источника: SG_S7_3.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `may-be-delivered-before-sprint-end` | Установлено ли по делу: may_be_delivered_before_sprint_end? | truth | `may_be_delivered_before_sprint_end(item: BacklogItem)` | `evaluate truth(may_be_delivered_before_sprint_end(<item>));` | — | тестов 1 |
| `usable-increment-created` | Установлено ли по делу: usable_increment_created? | truth | `usable_increment_created(s: Sprint)` | `evaluate truth(usable_increment_created(<s>));` | — | тестов 1 |

## SG_S7_3_1

Единицы источника: SG_S7_3_1.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `poziciya-conformtodefinitionofdone` | Какие позиции действуют по делу и в каком статусе стоит «ConformToDefinitionOfDone»? | positions | нормы `ConformToDefinitionOfDone` | `evaluate positions(); — ожидаемая форма position(ConformToDefinitionOfDone, <статус>)` | — | тестов 1 |
| `poziciya-createowndefinitionofdone` | Какие позиции действуют по делу и в каком статусе стоит «CreateOwnDefinitionOfDone»? | positions | нормы `CreateOwnDefinitionOfDone` | `evaluate positions(); — ожидаемая форма position(CreateOwnDefinitionOfDone, <статус>)` | — | тестов 1 |
| `poziciya-followorganizationalstandard` | Какие позиции действуют по делу и в каком статусе стоит «FollowOrganizationalStandard»? | positions | нормы `FollowOrganizationalStandard` | `evaluate positions(); — ожидаемая форма position(FollowOrganizationalStandard, <статус>)` | — | тестов 1 |

## SG_S8

Единицы источника: SG_S8.

| id | вопрос | форма | цель | шаблон | ветви | проверено |
|---|---|---|---|---|---|---|
| `is-scrum` | Установлено ли по делу: is_scrum? | truth | `is_scrum(i: ScrumImplementation)` | `evaluate truth(is_scrum(<i>));` | — | тестов 1 |

## Выводимое без собственной карточки

Звенья вывода: спрашиваются через карточки выше, названы здесь ради полноты поверхности в обе стороны.

| предикат | почему без карточки |
|---|---|
| `cannot_be_released_or_presented` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `not_part_of_increment` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `product_owner_is_one_person` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `retrospective_concluded` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `returns_to_product_backlog` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `review_precedes_retrospective` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `sprint_exceeds_one_month` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `sprint_planning_started` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `team_composition_conforms` | Вывод без исполнимого свидетельства: посылки правила содержат формы, которых порождённый сценарий не строит (дизъюнкция, текстовое значение или вызов терма), либо голова вычисляемая. Карточка появится вместе со сценарием, написанным руками. |
| `artifacts_inspected` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `conforms_to_definition_of_done` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `event_minutes` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (DailyScrumTimebox, SprintPlanningTimebox, SprintRetrospectiveTimebox…); самостоятельным вопросом к пакету он не является. |
| `events_kept_within_timebox` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `one_objective_at_a_time` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `part_of_increment` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (IncrementMayBeDeliveredEarly, UsableIncrementCreated); самостоятельным вопросом к пакету он не является. |
| `quality_maintained` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `respects_product_owner_decisions` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `scope_renegotiated` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `scope_renegotiation_valid` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `selected_for_sprint` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (SprintBacklogComposition, UsableIncrementCreated); самостоятельным вопросом к пакету он не является. |
| `sprint_cancelled` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `sprint_goal_kept_safe` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |
| `timebox_exceeded` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (OverrunBreaksTimeboxKeeping); самостоятельным вопросом к пакету он не является. |
| `work_visible` | Промежуточное звено: предикат выводится правилом пакета и читается телами других правил (); самостоятельным вопросом к пакету он не является. |

## Итог

Карточек 45, границ 3, внутренних звеньев 24; выводимых предикатов в CLIR 51, норм 18 — поверхность закрыта в обе стороны. Причины по конкретному делу берутся не из каталога, а из issues и why_not ответа.
