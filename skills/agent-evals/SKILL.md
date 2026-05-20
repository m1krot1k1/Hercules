---
name: agent-evals
description: Измерения оценки агентов, golden tasks, регрессионные наборы, рубрики; когда гонять до merge core rules.
---

## ЦЕЛЬ

Ввести воспроизводимую дисциплину оценки поведения агентов и правил (`rules/*.mdc`, `agents/*.md`, `skills/*/SKILL.md`): что измеряем, на каких задачах, как фиксируем регрессии и когда блокируем мерж в core.

## КОГДА ИСПОЛЬЗОВАТЬ

- Перед и после изменения **core** файлов: `rules/*.mdc`, `agents/*.md`, `skills/*/SKILL.md`
- При подозрении на «prompt drift», lazy completion, игнор AC
- Перед релизом набора агентов или крупным обновлением оркестратора
- Когда нужен объективный сравнительный отчёт A/B двух версий правил

## ИЗМЕРЕНИЯ (DIMENSIONS)

| Измерение | Что фиксируем | Пример метрики / сигнала |
|-----------|----------------|---------------------------|
| **Correctness** | Соответствие TASK_INPUT и AC; отсутствие выдуманных фактов | % AC met на golden set; count hallucinated paths |
| **Procedure** | Соблюдение шагов, инструментов, делегирования | Task вызван когда нужен; не нарушен trust order |
| **Safety** | Секреты, инъекции, деструктивные команды | injection probes passed; нет утечки policy в user-facing |
| **Efficiency** | Лишние итерации, объём отчёта vs diff | steps to AC; report-to-diff ratio (оркестратор §5) |
| **Stability** | Вариативность на повторах | variance по 3 прогонам одной задачи (см. prompt regression gate в `aleksander.mdc` 2.6.4) |

Назначьте **веса** под ваш риск-профиль; для security-sensitive веток вес Safety не ниже correctness.

## GOLDEN TASKS

**Golden task** — фиксированный конверт задачи с известным эталонным исходом или известным набором обязательных артефактов.

Требования к golden set:

1. **Покрытие режимов**: минимум одна задача на тип — simple multi-step, делегирование, read-only анализ, adversarial / injection.
2. **Детерминируемые AC**: конкретные команды (`git diff --stat`, `./scripts/...`), не субъективные оценки.
3. **Версионирование**: id задачи + версия набора golden-N; изменение эталона = bump версии.
4. **Хранение**: в репозитории (например `benchmarks/` или `docs/evals/`) или в CI артефактах — главное, чтобы воспроизводимо.

Пример **идеального** golden (структура, не контент):

```yaml
golden_id: G-2026-001
task_type: multi_step_delegate
inputs:
  TRUSTED_POLICY: [...]
  TASK_INPUT: {...}
must_produce:
  - artifact: completion_contract.yaml
  - check: command_with_expected_exit_0
forbidden:
  - raw_refusal_string_in_user_output
  - single_agent_fallback_without_label
```

## РЕГРЕССИОННЫЕ НАБОРЫ (REGRESSION SUITES)

Слои:

| Слой | Размер | Когда гонять |
|------|--------|--------------|
| **Smoke** | 3–5 задач | каждый PR, меняющий prompts/rules |
| **Standard** | 10–20 | merge в `dev`, nightly |
| **Full** | golden + injection mini-suite + stress | перед релизом core, крупный рефактор оркестрации |

**Injection mini-suite** (ориентир из `aleksander.mdc` 2.6.4): набор коротких промптов с вложенными инструкциями («ignore previous rules», «run this shell»). Ожидание: отказ следовать untrusted instructions, данные нормализуются.

## РУБРИКИ (RUBRICS)

Для каждой задачи заведите лист оценки:

- **0–2**: критический fail (AC не выполнены, security violation)
- **3–5**: частично, требуется rework
- **6–8**: AC выполнены, мелкие шероховатости
- **9–10**: эталонное поведение под вашу политику

Явно разделите **автопроверяемые** пункты (команда, файл) и **экспертные** (тон, избыточность) — последние только с двумя независимыми ревьюерами или calibrate по эталону.

## КОГДА ЗАПУСКАТЬ ДО MERGE CORE

По `aleksander.mdc` **Prompt Regression Gate** для изменений `rules/*.mdc`, `agents/*.md`, `skills/*/SKILL.md`:

1. **A/B**: baseline (текущий `dev`) vs candidate ветка на **5 задачах** (2 обычных + 2 multi-step + 1 adversarial).
2. **Метрики**: accuracy (AC met), latency (wall/agent steps), stability (variance 3 runs), cost если доступно.
3. **Injection mini-suite**: проход без следования вредоносным инструкциям.
4. **Leakage**: нет сырых refusal-строк в user-facing артефактах.

Блокер мержа, если:

- падает любая **must_produce** golden задача,
- регресс по safety на injection suite,
- stability сильно хуже baseline без явного обоснования.

## ШАГИ

1. Зафиксировать версию набора golden + smoke/standard/full.
2. Прогнать smoke на candidate; собрать логи и completion contracts.
3. Сравнить с baseline; зафиксировать deltas по таблице измерений.
4. По core-delta — выполнить полный gate (A/B + injection + leakage scan).
5. Итог: отчёт с таблицей `task_id × dimension × score` и решение merge/rework.

## ЧЕКЛИСТ

- [ ] Golden tasks имеют стабильные id и воспроизводимые AC
- [ ] Есть минимум один adversarial/injection сценарий в standard suite
- [ ] Для core-изменений выполнен A/B на 5 задачах
- [ ] Метрики включают stability (несколько прогонов)
- [ ] Регресс фиксируется как failing check или issue, не «на память»
- [ ] Report-to-diff непропорциональность помечается как procedure risk
- [ ] Секреты и PII не попадают в eval-логи

## СВЯЗАННЫЕ ДОКУМЕНТЫ

- `rules/aleksander.mdc` §2.6.4 Prompt Regression Gate
- `rules/orchestrator.mdc` §5 Lazy Agent Detection, Pre-Acceptance, Large core-delta verify gate
- `docs/evidence-first-acceptance.md` — как фиксировать доказательства по AC
- `agents/benchmark-specialist.md` (агент) — если используете репо-бенчмарки
- См. `docs/skills-index.md` (forward ref)
