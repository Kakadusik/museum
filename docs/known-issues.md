# Известные проблемы и обходы

Фронтенд собирается компилятором **Nue 2.0.0-beta.2** (nuekit). В этой версии есть несколько багов, которые приходится обходить в исходниках. Документировано, чтобы изменения фронтенда не сломали сборку.

## Проверка сборки

После любого изменения `frontend/ui/*.html` проверяйте, что скомпилированные JS валидны:

```powershell
cd frontend
nue build
$ok = 0; $bad = @()
Get-ChildItem ".dist" -Recurse -Include "*.js" | ForEach-Object {
  bun build "$($_.FullName)" --outdir "$env:TEMP\nue-gate" --target browser --external state --external "/@nue/*" 2>$null
  if ($LASTEXITCODE -eq 0) { $ok++ } else { $bad += $_.Name }
}
"valid: $ok, broken: $($bad -join ', ')"
```

Ожидаемый результат: **12 valid, 0 broken** (8 компонентов + index + mount.js + state.js + ещё 1).

## 1. Геттеры в скриптах компонентов

**Баг:** `convertGetters` в `nuedom` использует регекс с `[\s\S]*?`, который «съедает» последующие геттеры и теряет закрывающие `} })` — получается невалидный JS.

**Симптом:** `Object.defineProperty(this, 'q', { get() { return ... }` без закрывающих скобок.

**Обход:** не использовать `get` в скриптах компонентов. Вместо этого — метод `sync()`, который вызывает `this.update({...})`:

```js
sync() {
  this.update({ q: state.q || '', status: state.status || '' })
}
```

**Где применено:** `frontend/ui/items.html` (вместо 4 геттеров).

## 2. Смешанные кавычки в строках скрипта

**Баг:** `compileJS` в `compiler.js` извлекает скрипт из `util.inspect`-вывода регексом `([^\2]*?)\2`, который останавливается на первом символе закрывающей кавычки. Если строка содержит **оба** типа кавычек (`'` и `"`), inspect экранирует их, и регекс режет строку раньше времени — на выходе мусор вида `const labels = { gravity: \ '`.

**Обход:** в скриптах и выражениях шаблона не использовать строки с обоими типами кавычек. Плохо: `'[name="exhibition_ids"]'`. Хорошо: `'input[type=checkbox]'`.

**Где применено:** `frontend/ui/item-detail.html`, селектор в `updateItem`.

## 3. Стрелочные функции в выражениях шаблона

**Баг:** `addContext` переименовывает идентификаторы в `_.имя`. Если параметр стрелки `x => ...` переименуется в `_.x`, получится `_.x => ...` — невалидный параметр (member-выражение), синтаксическая ошибка.

**Обход:** в атрибутах `:expr` шаблона не использовать стрелочные функции с параметрами. Вместо `item.exhibitions.some(x => x.id == exh.id)` — `item.exhibition_ids.includes(exh.id)`.

**Где применено:** `frontend/ui/item-detail.html`, атрибут `:checked`.

## 4. Порядок importmap и mount.js

**Баг:** `nue build` генерирует `index.html`, где `<script src="/@nue/mount.js">` стоит **до** `<script type="importmap">`. Браузер игнорирует importmap, объявленный после начала загрузки модулей, — падает с «голый спефикатор state не переназначен».

**Обход (применён):** `backend/app.py`, функция `_fix_index_mount_order()` при отдаче `index.html` переносит тег `mount.js` после importmap. Работает для всех сборок без изменения исходников.

## 5. CRLF-окончания строк

**Проблема:** `git checkout` на Windows раскладывает файлы с CRLF (core.autocrlf). При CRLF-исходниках `nue build` генерирует невалидный JS (escape-последовательности `\r`, `\t`, `\ `).

**Обход:**
- держать исходники фронтенда с LF (Write/Edit-инструменты пишут LF; PowerShell `Set-Content` и Python `write_text` на Windows пишут CRLF — осторожно);
- перед сборкой можно нормализовать: `(Get-Content file -Raw) -replace \"`r`n\", \"`n\" | Set-Content file -NoNewline`.

В репозитории в HEAD все файлы с LF.

## Примечание по версиям

Актуальная версия nuekit на npm — `2.0.0-beta.2`, более свежих нет. При обновлении Nue в будущем проверить, что баги 1–4 исчезли, и убрать обходы.
