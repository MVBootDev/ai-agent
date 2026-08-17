# OpenRouter migration

Rebuild this repo to the **finished** Boot.dev AI Agent course (OpenRouter + OpenAI SDK), not the old Gemini end state.

Lesson dumps live in `lessons/`. Treat those as the spec. There are no official solution files.

## How to work (including new sessions)

1. Read this file and update checkboxes as you go.
2. Implement **one phase**, targeting **final** behavior for files you touch (not intermediate stubs).
3. You (human) run Boot.dev CLI submit for that chapter/lesson.
4. If tests fail, fix strings/schemas first — not architecture.
5. Git commit that phase only after CLI (or local verify) looks good.
6. Do **not** farm the whole migration to parallel subagents. Phases stack. Isolated file work inside a phase is fine.

Early-lesson CLI tests that expect a stub (e.g. `02-02` success-only `get_files_info`) may fail against the final function. Prefer final files; temporarily stub only if a specific submit requires it.

## Target tree

```
.
├── .env                      # OPENROUTER_API_KEY (gitignored)
├── .gitignore                # .venv, .env
├── pyproject.toml            # openai==2.44.0, python-dotenv==1.1.0
├── uv.lock
├── main.py
├── prompts.py
├── config.py                 # MAX_CHARS = 10000
├── call_function.py
├── functions/
│   ├── get_files_info.py     # impl + JSON schema
│   ├── get_file_content.py
│   ├── write_file.py
│   └── run_python.py         # or run_python_file.py
├── test_get_files_info.py
├── test_get_file_content.py
├── test_write_file.py
├── test_run_python_file.py
└── calculator/
    ├── main.py
    ├── tests.py
    └── pkg/
        ├── calculator.py
        └── render.py         # JSON format_json_output
```

Remove: `requirements.txt`, `google-genai`, Gemini types/client, root `tests.py` (replaced by per-tool test modules).

## Status

- [x] Phase 0 — packaging
- [ ] Phase 1 — OpenRouter client + CLI
- [ ] Phase 2 — calculator starter
- [ ] Phase 3 — tools
- [ ] Phase 4 — schemas + call_function
- [ ] Phase 5 — agent loop + bugfix demo

---

## Phase 0 — packaging (`01-02`)

- [x] `pyproject.toml` via uv (`openai==2.44.0`, `python-dotenv==1.1.0`)
- [x] `uv.lock`
- [x] `.gitignore` includes `.venv` and `.env` (not only `venv`)
- [x] Delete `requirements.txt` once uv is source of truth

**Verify:** `uv run main.py` still starts.

**CLI:** submit `01-02`.

---

## Phase 1 — OpenRouter + argparse (`01-03`–`01-07`)

Final `main.py` (no Gemini):

- [ ] `OPENROUTER_API_KEY` from `.env`; `RuntimeError` if missing
- [ ] `OpenAI(base_url="https://openrouter.ai/api/v1", api_key=...)`
- [ ] `argparse`: positional `user_prompt`, `--verbose` (`store_true`)
- [ ] Messages as dicts (`role` / `content`)
- [ ] `client.chat.completions.create(model="openrouter/free", messages=...)`
- [ ] Print `response.choices[0].message.content`
- [ ] Verbose only: `User prompt:`, `Prompt tokens:`, `Response tokens:` from `usage.prompt_tokens` / `usage.completion_tokens`
- [ ] Raise if `response.usage` is `None`

Note: `01-04` wants tokens always printed. **Final** behavior is `01-07` (verbose only). If `01-04` submit fails, temporarily always-print, then restore verbose-only.

**Verify:**

```bash
uv run main.py "hello"
uv run main.py "hello" --verbose
uv run main.py   # argparse exit 2
```

**CLI:** `01-03`, `01-04` (maybe snapshot), `01-05`, `01-06`, `01-07`.

---

## Phase 2 — calculator (`02-01`)

Replace with lesson paste:

- [ ] `calculator/pkg/render.py` → `format_json_output` (JSON, not ASCII box)
- [ ] `calculator/main.py` uses that helper; empty-expression message
- [ ] `calculator/tests.py` includes lesson cases
- [ ] Keep `+` precedence at `1` (fixed end state, not the broken `04-02` snapshot)

**Verify:**

```bash
uv run calculator/tests.py
uv run calculator/main.py "3 + 5"    # JSON result 8
uv run calculator/main.py "3 + 7 * 2"  # 17
```

**CLI:** `02-01`.

---

## Phase 3 — tools (`02-02`–`02-06`)

Shared path rule in every tool:

```text
working_abs = abspath(working_directory)
target = normpath(join(working_abs, relative_path))
ok = commonpath([working_abs, target]) == working_abs
```

Error/success strings must match `lessons/02-*.md` exactly.

- [ ] `get_files_info(working_directory, directory=".")` + `Result for ...` listing format
- [ ] `get_file_content` + `config.py` `MAX_CHARS`; truncation via extra `read(1)`
- [ ] `write_file`: `Cannot write` (not read); reject directories; `makedirs`; success count
- [ ] `run_python_file(..., args: list[str] | None = None)`; STDOUT/STDERR/exit/`No output produced`
- [ ] Add `test_get_files_info.py`, `test_get_file_content.py`, `test_write_file.py`, `test_run_python_file.py`
- [ ] Remove old root `tests.py` / `test_path_validation.py` if unused

**Verify:** `uv run test_get_files_info.py` (and the other three). One success listing + path errors; truncation on `lorem.txt`; `/tmp` write denied; `main.py` with `["3 + 5"]`.

**CLI:** `02-02` (may need temporary stub), `02-03`, `02-04`, `02-05`, `02-06`.

---

## Phase 4 — wire tools (`03-01`–`03-04`)

- [ ] `prompts.py` — helpful coding-agent system prompt (four operations). Robot prompt is not final.
- [ ] JSON schemas (`"type": "function"`) per tool; do not expose `working_directory`
- [ ] `required`: `file_path` / `content` as in `03-03`; `args` is array of strings
- [ ] `available_functions` list passed as `tools=`
- [ ] `call_function(tool_call, verbose=False) -> dict` with `role=tool`, `tool_call_id`, `content`
- [ ] Inject `working_directory="./calculator"`
- [ ] Print `- Calling function: name` (args if verbose)

**Verify:** prompts that list/read/write/run actually invoke tools.

**CLI:** `03-01`–`03-04`.

---

## Phase 5 — loop (`04-01`–`04-03`)

```text
for _ in range(20):
    response = create(...)
    message = response.choices[0].message
    messages.append(message)          # assistant first
    if not message.tool_calls:
        print final content; break
    for tool_call in message.tool_calls:
        messages.append(call_function(tool_call, verbose))
else:
    print max-iterations failure; sys.exit(1)
```

- [ ] Order: assistant message, then one tool message per call
- [ ] Agent can fix calculator if you temporarily break `+` precedence to `3`, then restore
- [ ] Push repo for `04-03`

**Verify:**

```bash
uv run main.py "how does the calculator render results to the console?"
uv run main.py "Fix the bug: 3 + 7 * 2 shouldn't be 20."
```

**CLI:** `04-01`, `04-02`, `04-03`.

---

## Pitfalls

- CLI tests are string-sensitive. Copy error formats from `lessons/`.
- Do not wrap Gemini `types.Content` around OpenRouter.
- `01-04` token prints vs `01-07` verbose-only: final = verbose-only.
- Calculator render changed from ASCII box to JSON; agent prompts about “how it renders” must still make sense.
- Never commit `.env`.
