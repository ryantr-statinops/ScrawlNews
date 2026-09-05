# Reports

Thư mục lưu **test reports** và **verification results** của các lần chạy.

## Quy ước

- Lưu output của `pytest --cov`, `ruff`, `mypy`, `npm run test` vào đây khi cần archive (vd: `reports/2026-08-28-stage4.txt`).
- Mỗi report đặt tên theo ngày + mục đích để dễ tìm.
- Không commit artifact lớn (coverage HTML, logs); chỉ commit tóm tắt text nếu cần tham chiếu lâu dài.

## Latest verification (2026-08-28, Stage 4)

```
pytest tests/unit -q        → 77 passed
pytest tests/integration -q → 10 passed
ruff check                 → passed
web lint (eslint flat)     → fixed
docker compose config      → passed (với .env)
go run ./cmd/newsctl --help → ok
```

> Chi tiết hơn trong [changelog.md](../changelog.md).
