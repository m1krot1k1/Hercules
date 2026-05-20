# Локальные задачи с доказуемым циклом

Каталог для артефактов **repo task proof loop** (см. `skills/repo-task-proof-loop/SKILL.md`).

Для каждой крупной задачи создаётся подкаталог:

`<TASK_ID>/` с `spec.md`, опционально `shared-context.md`, `evidence.md`, `verdict.md`, `problems.md`, опционально **`learnings.md`** (операционные выводы после цикла — см. skill `repo-task-proof-loop`), каталог `raw/`.

Канонический путь **в этом репозитории конфигурации**: `agent-tasks/<TASK_ID>/`.
Если конфигурация установлена в корень другого проекта как `.cursor/`, runtime-путь будет `.cursor/agent-tasks/<TASK_ID>/`.

Не коммитить секреты. При необходимости добавьте `agent-tasks/**/raw/` в `.gitignore` в корне приложения.
