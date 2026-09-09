import sqlite3
from pathlib import Path

SCHEMA_VERSION = 7

MIGRATIONS = {
    1: """
    CREATE TABLE IF NOT EXISTS schema_migrations (
        version INTEGER PRIMARY KEY,
        applied_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """,
    2: """
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS config_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT NOT NULL,
        old_value TEXT,
        new_value TEXT NOT NULL,
        changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_config_history_key ON config_history(key);
    CREATE INDEX IF NOT EXISTS idx_config_history_changed_at ON config_history(changed_at DESC)
    """,
    4: """
    CREATE TABLE IF NOT EXISTS agent_audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        correlation_id TEXT NOT NULL,
        phase TEXT NOT NULL,
        status TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_agent_audit_correlation
        ON agent_audit_events(correlation_id, created_at DESC);
    """,
    5: """
    """,
    6: """
    CREATE TABLE IF NOT EXISTS sources (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        url TEXT UNIQUE NOT NULL,
        category TEXT,
        country TEXT NOT NULL DEFAULT 'VN',
        city TEXT,
        enabled INTEGER NOT NULL DEFAULT 1,
        last_status TEXT,
        last_error TEXT,
        last_checked_at DATETIME,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_sources_enabled ON sources(enabled);
    CREATE INDEX IF NOT EXISTS idx_sources_category ON sources(category)
    """
    ,
    7: """
    CREATE TABLE IF NOT EXISTS digests (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        title TEXT NOT NULL,
        digest_text TEXT NOT NULL,
        article_count INTEGER NOT NULL DEFAULT 0,
        model_used TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'ready',
        error TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_digests_category_created
        ON digests(category, created_at DESC);
    CREATE TABLE IF NOT EXISTS digest_articles (
        digest_id TEXT NOT NULL,
        article_id TEXT NOT NULL,
        PRIMARY KEY (digest_id, article_id),
        FOREIGN KEY(digest_id) REFERENCES digests(id),
        FOREIGN KEY(article_id) REFERENCES articles(id)
    )
    """
    # v3 is applied in Python (see run_migrations): add category column
    # only when the articles table already exists (fresh DBs get it via _init_db)
}


def run_migrations(db_path: str):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version INTEGER PRIMARY KEY, applied_at DATETIME DEFAULT CURRENT_TIMESTAMP)"
        )
        row = conn.execute("SELECT MAX(version) FROM schema_migrations").fetchone()
        current_version = row[0] if row and row[0] is not None else 0
        for version in range(current_version + 1, SCHEMA_VERSION + 1):
            if version == 3:
                _migrate_v3_add_category(conn)
            elif version == 5:
                _migrate_v5_add_published_at(conn)
            elif version in MIGRATIONS:
                conn.executescript(MIGRATIONS[version])
            else:
                continue
            conn.execute("INSERT INTO schema_migrations (version) VALUES (?)", (version,))
            conn.commit()


def _migrate_v3_add_category(conn):
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    if "articles" not in tables:
        return
    cols = [r[1] for r in conn.execute("PRAGMA table_info(articles)")]
    if "category" not in cols:
        conn.execute("ALTER TABLE articles ADD COLUMN category TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category)")


def _migrate_v5_add_published_at(conn):
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    if "articles" not in tables:
        return
    cols = [r[1] for r in conn.execute("PRAGMA table_info(articles)")]
    if "published_at" not in cols:
        conn.execute("ALTER TABLE articles ADD COLUMN published_at DATETIME")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at DESC)")
