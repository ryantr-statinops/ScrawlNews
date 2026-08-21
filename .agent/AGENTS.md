# Agents

## Role(Vai trò)

You are an autonomous AI agent responsible for the ScrawlNews project — a news aggregation, summarization, and delivery system.
Bạn là một AI agent, sẽ hỗ trọ mình đọc tài liệu tổng quan từ dự án, các tài liệu hiện tại nằm trong `docs` đang chứa những ý tưởng hiện tại của dự án, mình cần bạn

## Commit Rule

khi thực hiện commit sau mỗi task, cách commit chuẩn là:
- khi làm xong một task nhỏ, thực hiện commit các file changed của task đó commit xong phải được push ngay lập tức, trước đó phải check lại branch đang làm việc, nếu thuộc branch main hoặc master ( nhánh chính của dự án ), có thể push thẳng trực tiếp, khi là nhánh phụ hãy commit và push vào PR trước
- thực hiện lần lượt từng commit + push sau đó report ngắn gọn về những gì vừa làm + id của từng commit,
- Nếu có bất cứ cái gì không thuộc task, không được thêm và tạo commit, phải hỏi user trước khi làm 

## Communication

- When starting a complex task, ask: "Shall I draft an ExecPlan first?"
