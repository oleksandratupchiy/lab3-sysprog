# Фактичні перевірки

Перевірено 6 листопада 2026 року у Windows PowerShell; Python `.venv` — 3.14.2, PLY — 3.11, pytest — 9.2.0. Наявні `AGENTS.md` і `requirements.txt` збережено; нових сторонніх Python-залежностей не додано.

## Автоматизований набір

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Останній повний запуск після виправлення Windows cp1251: **30 passed in 67.45s**. Попередній повний запуск: 30 passed in 27.48s. Час залежить від навантаження та запуску дочірніх процесів. Для CLI help окремо перевіряється `PYTHONIOENCODING=cp1251`, а основні subprocess-перевірки працюють у UTF-8.

Виконано також:

```powershell
.\.venv\Scripts\python.exe main.py --help
.\.venv\Scripts\python.exe main.py examples/arithmetic.c --run
.\.venv\Scripts\python.exe main.py examples/conditions.c --run
.\.venv\Scripts\python.exe main.py examples/loops.c --run
.\.venv\Scripts\python.exe main.py examples/complex.c --tokens
.\.venv\Scripts\python.exe main.py examples/complex.c --ast
.\.venv\Scripts\python.exe main.py examples/complex.c --run --emit-python output/program.py --emit-ast output/ast.json --parser-report output/parser.out
.\.venv\Scripts\python.exe output/program.py
node --check web/app.js
git diff --check
git status --short
```

Команди успішні; `--tokens` і `--ast` додатково зберігалися перенаправленням у `output/tokens.txt` та `output/ast-preview.txt`. Очікувані stdout прикладів збіглися з README. `complex.c` та автономний Python друкують `-2` і `35`; інтерпретатор повертає 35. Тести окремо отримують значення `main` із згенерованого модуля й порівнюють його з інтерпретатором.

Діагностика PLY містить `Parsing method: LALR`; невирішених конфліктів не виявлено. Звіт `output/parser.out` справді згенеровано, а не написано вручну. AST JSON розібрано стандартним `json`: 49 вузлів, стабільні унікальні ID та координати. Додатково перевірено відсутність кінцевих пробілів у вихідних файлах; `git diff --check` сам по собі не охоплює ще не додані до Git файли.

## Браузер

Виконано локальну перевірку **реального headless Google Chrome** через Chrome DevTools Protocol, без backend застосунку. Одноразовий допоміжний скрипт — `output/check-viewer.cjs`, команда:

```powershell
node output/check-viewer.cjs
```

Скрипт не є залежністю проєкту чи частиною pytest; для звичайного використання достатньо відкрити HTML і вибрати JSON. Браузерна перевірка потребувала запуску поза пісочницею. Після перезапуску середовища її завершено з окремим тимчасовим профілем Chrome.

Підтверджено:

- Відкриття локального `web/index.html`, завантаження d3.js 7.9.0 з CDN.
- Вибір справжнього `output/ast.json` через file input і відображення 49 вузлів.
- Згортання кореня до одного видимого вузла кліком.
- Відновлення всіх 49 вузлів клавішею Enter.
- Зміна масштабу коліщатком.
- Кнопка reset вміщує дерево у видиму область SVG.
- Вузли мають tooltip із подробицями та ID.
- Знімок `output/viewer.png` збережено та візуально переглянуто.

Підсумок браузерного скрипта: `fileInput=true`, `collapse=true`, `keyboardExpand=true`, `zoom=true`, `reset=true`, `tooltips=true`. Перетягування реалізоване стандартним d3.zoom; окремого автоматизованого жесту pan у цій перевірці не було. Інші браузери й мобільні пристрої окремо не перевірялися. Початкова перевірка reset порівнювала transform як точний рядок; її замінено перевіркою реального вміщення дерева у viewport, щоб не залежати від округлення та метрик тексту.

## Стан вимог і файли

Обов'язкові функціональні частини реалізовано: PLY lexer/LALR parser, AST, статичні перевірки, інтерпретатор, генератор автономного Python, JSON, інтерактивна d3.js-сторінка, CLI, приклади, 30 тестів, README й теорія для очного захисту. Відомих невиправлених збоїв у перевірених випадках немає. Обмеження підмножини й розбіжність часткового stdout за помилок виконання явно описано в README. Формального доказу еквівалентності та перевірки всіх можливих програм немає.

Не реалізовано необов'язкові розширення: for, ++/--, інші типи, масиви/вказівники, функції користувача та довільний printf. Не готувалися відео або слайди — вони не потрібні за завданням.

Для коміту: `.gitignore`, `AGENTS.md`, `requirements.txt`, `main.py`, `README.md`, `compiler/`, `examples/`, `tests/`, `web/`, `docs/`. Початкові `AGENTS.md` і `requirements.txt` також були untracked, тому їх треба включити. `.venv/`, `output/`, кеші pytest/Python і тимчасові браузерні профілі ігноруються. Коміт автоматично не створювався.