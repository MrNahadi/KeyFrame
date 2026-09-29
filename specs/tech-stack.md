# Tech stack

Derived from `specs/brief.md` sections 8, 9 and 11. Versions are pinned in `pyproject.toml` and locked in `uv.lock`.

## Stack

| Layer | Choice | Version |
|---|---|---|
| Python | CPython via uv | 3.12 (`>=3.12,<3.13`) |
| Environment | uv (`uv sync`, `uv run`) | lockfile `uv.lock` |
| Data | pandas, NumPy, pyarrow (Parquet) | 3.0.6, 2.5.3, 25.0.1 |
| Modelling | scikit-learn, LightGBM, XGBoost (CPU wheel `xgboost-cpu`), Optuna | 1.9.1, 4.7.0, 3.4.1, 5.0.0 |
| Explainability | shap, lime (one comparison only) | 0.52.0, 0.2.0.1 |
| Plots | matplotlib (notebooks, static figures), plotly (only where interaction matters) | 3.11.2, 7.1.0 |
| Notebooks | JupyterLab, jupytext (percent format), nbconvert, ipykernel | 4.6.4, 1.19.5, 7.17.1, 7.3.0 |
| Model files | joblib | 1.6.0 |
| API | FastAPI, Uvicorn, pydantic | 0.141.1, 0.54.0, 2.13.5 |
| Tests and quality | pytest, ruff, mypy, pandas-stubs, httpx | 9.1.1, 0.16.9, 2.3.1 |
| Front end | React 19 + Vite 8 + TypeScript 6 (strict), Recharts 3, lucide-react, Vitest 4 + Testing Library + jsdom; plain CSS tokens with CSS Modules (ADR 0010) | Node 22, npm with `legacy-peer-deps` (web/.npmrc) |

The autoencoder in anomaly detection uses scikit-learn's `MLPRegressor`, so no deep-learning framework is needed. A 1D CNN is a stretch goal and would need a new dependency, installed by the human-present planning phase, never by the loop.

## Project layout

```
keyframe/
├── data/                 not committed
│   ├── raw/              the 15 release CSVs + docs, as extracted from the Zenodo zip
│   ├── lockbox/          Clogged_Injector_Nozzle2_LoadProgram.csv, used once at the end
│   └── processed/        Parquet tables written by notebooks
├── notebooks/            NN_name.py (jupytext source) + NN_name.ipynb (executed copy)
├── keyframe/             the shared package: download, load, splits, features, explain, ...
├── tests/                pytest; unit tests use small synthetic frames
├── models/               saved model, preprocessing and explainer (committed only at export)
├── reports/
│   ├── figures/          PNG figures referenced by notebooks and the README
│   ├── results/          one CSV per experiment (the results log)
│   ├── engineering_checklist.md
│   ├── targets.md
│   └── model_card.md
├── api/                  FastAPI app
├── web/                  TypeScript front end
├── specs/, docs/, questions/, .ralph/, .claude/   spec-driven build files
└── README.md
```

## Conventions

### Python

- Type hints on every public function; short docstrings that say what, in engine terms where it helps.
- Paths come from `keyframe.paths` (repo-relative), never hard-coded absolute paths.
- Random seed 42 everywhere a seed exists (`keyframe.SEED`).
- No logic that the notebooks share lives in a notebook: it goes in the package, with a test.
- Column names: the dataset's full variable names (row 1 of the header) are the canonical keys. `keyframe.load` also exposes snake_case short aliases where needed; never use the shorthand symbols as keys, because several repeat (`Pmax`, `Pmin`, `We`, `Wi`).

### Data and leakage

- Every CSV has a three-row header: full name, shorthand symbol, unit. Data start on row 4.
- The reference file has 70 columns (`Time`, no `Anomaly State`); scenario files have 73 (`Time_abs`, `Time_rel`, `Anomaly State`).
- Sampling is not a fixed 2 s: time stamps step alternately 1 s and 2 s (about 1.6 s on average). Rolling windows are defined in seconds using the time column, computed within one run, and never cross a file boundary.
- Excluded from model inputs, always: `Compressor Filter Loss`, `Turbine Back Pressure`, `Engine room Temp.`, `Time`, `Time_abs`, `Time_rel`, `Anomaly State`, and any run or file identifier. `keyframe.features.EXCLUDED_COLUMNS` is the single source of this list and a test enforces it.
- Load bins by shaft power (`Shaft Power`, kW): below 130 → 40%, 130 to 175 → 60%, 175 to 207 → 75%, 207 and above → 85%.
- No random row splits anywhere. Any fitted step (scaler, healthy-engine model, feature selection, calibration) is fitted inside the training fold only.
- The lockbox file is never read except by the final evaluation ticket.

### Notebooks

- The source of truth is `notebooks/NN_name.py` in jupytext percent format (`# %%` cells, `# %% [markdown]` for prose). Edit that file, never the `.ipynb`.
- Build the executed copy with `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/NN_name.py`, and commit both files so reviewers see outputs on GitHub.
- Each notebook opens with a markdown cell that says, for the primary user, what question it answers and what it found. Headings are questions or findings, not "Section 2".
- Static matplotlib figures, saved to `reports/figures/NN_*.png` at 150 dpi. Keep the executed notebook under about 5 MB.
- **Heavy experiments run outside the notebook.** Any computation over about 3 minutes (LOLO over several models or feature sets, tuning, SHAP over many rows) lives in `keyframe/experiments.py` as a named experiment, run with `uv run python -m keyframe.experiments <name> [options]`. Each invocation must finish in under 9 minutes (split by feature set, model or fold if needed), writes its per-row predictions to `data/processed/experiments/<name>.parquet` and its summary via `log_results`, and skips work whose output already exists unless `--force`. Notebooks read those outputs and only call an experiment if its output is missing. This keeps every loop command under the 10-minute tool limit and keeps notebook execution fast.
- Results tables go to `reports/results/*.csv` with the fold, class and metric columns needed to show spread across folds.

### Front end

- The design rules are `docs/design/manifesto.md`: Part 14 (rules sheet) for tokens, spacing, type, radius, colour, icons (Lucide), motion and states, and Part 15 (screen audit) as the checklist every screen must pass.
- Stack per ADR 0010. Every colour, size, radius and duration comes from `web/src/styles/tokens.css` (a test fails on raw colours elsewhere); icons only through `web/src/ui/Icon.tsx` (sizes 16/20/24).
- Hash routes (`#/replay/<run>`, `#/what-if`, `#/model-card`); replay reads static JSON in `web/public/replays/` (copied by `npm --prefix web run sync-replays`); what-if calls the API through the dev proxy `/api`.
- Charts: Recharts with `isAnimationActive={false}`; data colours `--data-*` only; text labels on every bar (light-mode contrast relief).
- Install dependencies with `npm --prefix web ci` (the loop never installs).

### Git

- One feature per branch (`feature/NN-slug`), one ticket per commit.
- Commit messages: `feat(T-NNN): ...`, `fix(...)`, `docs(...)`, `chore(...)`.

## Feedback commands

Run from the repo root. All must pass before any ticket is marked done.

| Check | Command |
|---|---|
| Lint | `uv run ruff check .` |
| Format | `uv run ruff format --check .` |
| Typecheck | `uv run mypy` |
| Test | `uv run pytest` (API latency: `tests/test_api_latency.py`; run the API: `uv run uvicorn api.main:app --port 8000`) |
| Build | Python: none. Front end: `npm --prefix web run build` (also type-checks) |
| E2E | Notebooks: `uv run jupytext --set-kernel python3 --to ipynb --execute notebooks/<name>.py` for each notebook the ticket touched. Front end: `npm --prefix web test` |

Data setup (one command, needs network): `uv run python -m keyframe.download`.
