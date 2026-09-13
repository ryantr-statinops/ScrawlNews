# CI Hardening — 2026-09-13

## Mandatory gates

| Gate | Verification |
|---|---|
| Backend lint | `ruff check src/ tests/` passed |
| Backend typecheck | `mypy src/` passed, 55 source files |
| Backend tests/coverage | 251 passed, 6 skipped; 87% total coverage; threshold 85% |
| Frontend install | `npm ci` passed |
| Frontend lint/typecheck | ESLint và `tsc --noEmit` passed |
| Frontend tests | 4 files / 11 tests passed |
| Docker build | API, worker, beat, bot và web images passed |

Tất cả gate trên đã bỏ `|| true`. Frontend tests là mandatory nhưng coverage chưa là gate: baseline hiện tại chỉ 11.12%, cần tăng test theo feature trước khi đặt threshold.

## Docker reproducibility

- Frontend image dùng `package-lock.json` + `npm ci`.
- `frontend/.dockerignore` loại `node_modules`, `dist` và coverage artifacts.
- Frontend Docker context giảm từ khoảng 237 MB xuống 481.8 KB trong local verification.

## Dependency audit follow-up

`npm audit` còn 4 findings: 2 moderate, 1 high và 1 critical trong Vite/Vitest toolchain. Automated fix đề xuất major upgrades (Vite 8, Vitest 5), nên không chạy `npm audit fix --force`; migration có kiểm soát được đưa vào reliability backlog.
