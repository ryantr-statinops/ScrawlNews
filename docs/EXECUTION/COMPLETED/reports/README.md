# Reports

Thư mục lưu **test reports** và **verification results** của các lần chạy.

## Quy ước

- Lưu output của `pytest --cov`, `ruff`, `mypy`, `npm run test` và `npm run test:coverage` vào đây khi cần archive (vd: `reports/2026-08-28-stage4.txt`).
- Mỗi report đặt tên theo ngày + mục đích để dễ tìm.
- Không commit artifact lớn (coverage HTML, logs); chỉ commit tóm tắt text nếu cần tham chiếu lâu dài.

## Latest verification (2026-10-04, Release 1.1)

```
npm ci (Node 20.19.0 / npm 10.8.2)              → passed
npm audit --audit-level=high                    → passed (0 high/critical; 3 moderate)
npm run lint / npm run typecheck                → passed
npm run test:coverage                           → 22 files / 106 tests passed
V8 coverage                                    → lines 99.87%, statements 99.87%, branches 92.20%, functions 84.23%
npm run build:client / npm run build:ops        → passed
ruff check src/ tests/ → passed; `.venv311/bin/mypy src/` → passed
.venv311/bin/pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=85 → 333 passed, 6 skipped; 87.35%
```

- [Release 1.1 integration report](2026-10-04-release-1.1-integration.md) contains runtime and UI evidence.
- Automated tests do not replace live RSS/LLM/Telegram checks; the Release 1.1 smoke kept Telegram disabled.

## Historical verification (2026-09-14, Local Release 1.0 baseline)

```
pytest -q                         → 251 passed, 6 skipped
ruff check src/                   → passed
mypy src/                         → passed
cd frontend && npm test           → 4 files / 11 tests passed
cd frontend && npm run typecheck  → passed
cd frontend && npm run lint       → passed
```

The Release 1.0 baseline is retained for history; Release 1.1 evidence is linked above.

## Historical verification (2026-08-28, Stage 4)

```
pytest tests/unit -q        → 77 passed
pytest tests/integration -q → 10 passed
ruff check                 → passed
web lint (eslint flat)     → fixed
docker compose config      → passed (với .env)
go run ./cmd/newsctl --help → ok
```

> Chi tiết hơn trong [changelog.md](../changelog.md).

## Operational reports

- [2026-09-13 operational validation](2026-09-13-operational-validation.md) — RSS/fallback và RSS/OpenRouter pass; Telegram test delivery chờ credentials.
- [2026-09-13 CI hardening](2026-09-13-ci-hardening.md) — mandatory gates, coverage baselines và Docker build verification.
