"""
数据库管理
"""

import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path


def get_db_path():
    """获取数据库路径，支持环境变量覆盖"""
    if os.getenv("TEST_DB_PATH"):
        return Path(os.getenv("TEST_DB_PATH"))
    return Path(__file__).parent.parent / "data" / "side_hustle.db"


def get_db():
    """获取数据库连接"""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_db()
    cursor = conn.cursor()

    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    """)

    # 推荐记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            input_data TEXT,
            result_data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 系统配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 内容表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT '',
            body TEXT NOT NULL DEFAULT '',
            summary TEXT DEFAULT '',
            cover_image TEXT DEFAULT '',
            platform_versions TEXT DEFAULT '{}',
            material_ids TEXT DEFAULT '[]',
            status TEXT DEFAULT 'draft',
            tags TEXT DEFAULT '[]',
            category TEXT DEFAULT '',
            scheduled_at TIMESTAMP,
            published_at TIMESTAMP,
            published_platforms TEXT DEFAULT '[]',
            ai_generated INTEGER DEFAULT 0,
            ai_prompt TEXT DEFAULT '',
            views INTEGER DEFAULT 0,
            likes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            shares INTEGER DEFAULT 0,
            revenue REAL DEFAULT 0,
            version INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 内容版本历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS content_versions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            version INTEGER NOT NULL,
            title TEXT,
            body TEXT,
            change_summary TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id)
        )
    """)

    # 运营活动表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL DEFAULT '',
            description TEXT DEFAULT '',
            content_ids TEXT DEFAULT '[]',
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            target_views INTEGER DEFAULT 0,
            target_revenue REAL DEFAULT 0,
            actual_views INTEGER DEFAULT 0,
            actual_revenue REAL DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 平台账号表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS platform_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            account_name TEXT DEFAULT '',
            account_id TEXT DEFAULT '',
            access_token TEXT DEFAULT '',
            refresh_token TEXT DEFAULT '',
            status TEXT DEFAULT 'active',
            followers INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 素材表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT DEFAULT '',
            file_size INTEGER DEFAULT 0,
            mime_type TEXT DEFAULT '',
            width INTEGER DEFAULT 0,
            height INTEGER DEFAULT 0,
            duration INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            folder TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # 发布日志表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publish_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            error_message TEXT DEFAULT '',
            published_url TEXT DEFAULT '',
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (content_id) REFERENCES content(id)
        )
    """)

    # 创建默认管理员账户 (admin/admin123)
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        password_hash = hash_password("admin123")
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            ("admin", password_hash, "admin@sidehustle.local", "admin")
        )

    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(user_id: int, username: str, role: str) -> str:
    """创建JWT token"""
    import os
    secret = os.getenv("JWT_SECRET", "side_hustle_secret_key_change_in_production")
    import time
    timestamp = int(time.time())
    random_data = secrets.token_hex(16)
    payload = f"{user_id}|{username}|{role}|{timestamp}|{random_data}"
    import hmac
    signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    import base64
    token = base64.b64encode(f"{payload}|{signature}".encode()).decode()
    return token


def verify_token(token: str) -> Optional[dict]:
    """验证token"""
    import os
    import time
    import hmac
    import hashlib
    import base64
    secret = os.getenv("JWT_SECRET", "side_hustle_secret_key_change_in_production")
    try:
        decoded = base64.b64decode(token.encode()).decode()
        # 使用 | 分隔符，避免与 base64 字符冲突
        parts = decoded.split("|")
        if len(parts) < 6:
            return None
        user_id, username, role, timestamp, random_data, signature = parts[:6]
        # 重建payload并验证签名
        payload = f"{user_id}|{username}|{role}|{timestamp}|{random_data}"
        expected_sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if signature != expected_sig:
            return None
        # 检查是否过期 (7天)
        if int(time.time()) - int(timestamp) > 7 * 24 * 3600:
            return None
        return {"user_id": int(user_id), "username": username, "role": role}
    except:
        return None


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


def get_user_by_username(username: str) -> Optional[dict]:
    """根据用户名获取用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[dict]:
    """根据ID获取用户"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, created_at, last_login FROM users WHERE id = ? AND is_active = 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username: str, password: str, email: str = "") -> dict:
    """创建新用户"""
    conn = get_db()
    cursor = conn.cursor()
    password_hash = hash_password(password)
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, email, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, email, "user")
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "username": username, "role": "user"}
    except sqlite3.IntegrityError:
        conn.close()
        return {"error": "用户名已存在"}


def save_recommendation(user_id: int, input_data: dict, result_data: dict):
    """保存推荐记录"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO recommendations (user_id, input_data, result_data) VALUES (?, ?, ?)",
        (user_id, json.dumps(input_data, ensure_ascii=False), json.dumps(result_data, ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_user_recommendations(user_id: int, limit: int = 50):
    """获取用户的推荐历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, input_data, result_data, created_at FROM recommendations WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_all_users():
    """获取所有用户（管理员用）"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, role, created_at, last_login FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_stats():
    """获取系统统计"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_users FROM users")
    total_users = cursor.fetchone()["total_users"]
    cursor.execute("SELECT COUNT(*) as total_recommendations FROM recommendations")
    total_recommendations = cursor.fetchone()["total_recommendations"]
    conn.close()
    return {"total_users": total_users, "total_recommendations": total_recommendations}


# ============================================
# 内容管理 CRUD
# ============================================

def create_content(user_id: int, title: str, body: str, summary: str = "",
                   cover_image: str = "", tags: list = None, category: str = "",
                   ai_generated: bool = False, ai_prompt: str = "") -> dict:
    """创建内容"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    tags_json = json.dumps(tags or [], ensure_ascii=False)
    try:
        cursor.execute("""
            INSERT INTO content (user_id, title, body, summary, cover_image, tags, category, ai_generated, ai_prompt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, title, body, summary, cover_image, tags_json, category, 1 if ai_generated else 0, ai_prompt))
        conn.commit()
        content_id = cursor.lastrowid
        conn.close()
        return {"id": content_id, "title": title}
    except Exception as e:
        conn.close()
        return {"error": str(e)}


def get_content_by_id(content_id: int, user_id: int = None) -> dict | None:
    """获取内容详情"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM content WHERE id = ? AND user_id = ?", (content_id, user_id))
    else:
        cursor.execute("SELECT * FROM content WHERE id = ?", (content_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        result = dict(row)
        result["tags"] = json.loads(result.get("tags", "[]"))
        result["material_ids"] = json.loads(result.get("material_ids", "[]"))
        result["published_platforms"] = json.loads(result.get("published_platforms", "[]"))
        result["platform_versions"] = json.loads(result.get("platform_versions", "{}"))
        return result
    return None


def get_user_contents(user_id: int, status: str = None, limit: int = 50, offset: int = 0) -> list:
    """获取用户的内容列表"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    if status:
        cursor.execute("""
            SELECT id, title, summary, status, tags, category, views, likes, revenue, created_at, updated_at
            FROM content WHERE user_id = ? AND status = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?
        """, (user_id, status, limit, offset))
    else:
        cursor.execute("""
            SELECT id, title, summary, status, tags, category, views, likes, revenue, created_at, updated_at
            FROM content WHERE user_id = ? ORDER BY updated_at DESC LIMIT ? OFFSET ?
        """, (user_id, limit, offset))
    rows = cursor.fetchall()
    conn.close()
    result = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item.get("tags", "[]"))
        result.append(item)
    return result


def update_content(content_id: int, user_id: int, **kwargs) -> dict:
    """更新内容"""
    import json
    conn = get_db()
    cursor = conn.cursor()

    # 获取当前版本
    cursor.execute("SELECT version, title, body FROM content WHERE id = ? AND user_id = ?", (content_id, user_id))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "内容不存在"}

    current_version = row["version"]
    old_title = row["title"]
    old_body = row["body"]

    # 保存版本历史
    change_summary = kwargs.get("change_summary", "内容更新")
    cursor.execute("""
        INSERT INTO content_versions (content_id, version, title, body, change_summary)
        VALUES (?, ?, ?, ?, ?)
    """, (content_id, current_version, old_title, old_body, change_summary))

    # 构建更新语句
    allowed_fields = ["title", "body", "summary", "cover_image", "tags", "category",
                      "status", "scheduled_at", "published_at", "platform_versions",
                      "ai_prompt", "views", "likes", "comments", "shares", "revenue"]
    update_parts = []
    values = []

    for field in allowed_fields:
        if field in kwargs:
            if field in ["tags", "platform_versions"]:
                update_parts.append(f"{field} = ?")
                values.append(json.dumps(kwargs[field], ensure_ascii=False))
            elif field == "scheduled_at" and kwargs[field]:
                update_parts.append(f"{field} = ?")
                values.append(kwargs[field].isoformat() if hasattr(kwargs[field], 'isoformat') else kwargs[field])
            elif field == "published_at" and kwargs[field]:
                update_parts.append(f"{field} = ?")
                values.append(kwargs[field].isoformat() if hasattr(kwargs[field], 'isoformat') else kwargs[field])
            else:
                update_parts.append(f"{field} = ?")
                values.append(kwargs[field])

    if update_parts:
        update_parts.append("version = version + 1")
        update_parts.append("updated_at = CURRENT_TIMESTAMP")
        sql = f"UPDATE content SET {', '.join(update_parts)} WHERE id = ? AND user_id = ?"
        values.extend([content_id, user_id])
        cursor.execute(sql, values)
        conn.commit()

    conn.close()
    return {"id": content_id, "updated": True}


def delete_content(content_id: int, user_id: int) -> dict:
    """删除内容"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM content WHERE id = ? AND user_id = ?", (content_id, user_id))
    affected = cursor.rowcount
    # 同时删除版本历史
    cursor.execute("DELETE FROM content_versions WHERE content_id = ?", (content_id,))
    conn.commit()
    conn.close()
    return {"deleted": affected > 0}


def get_content_versions(content_id: int) -> list:
    """获取内容版本历史"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, version, title, body, change_summary, created_at
        FROM content_versions WHERE content_id = ? ORDER BY version DESC
    """, (content_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============================================
# 活动管理 CRUD
# ============================================

def create_campaign(user_id: int, name: str, description: str = "",
                    start_date: str = None, end_date: str = None) -> dict:
    """创建活动"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO campaigns (user_id, name, description, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name, description, start_date, end_date))
        conn.commit()
        campaign_id = cursor.lastrowid
        conn.close()
        return {"id": campaign_id, "name": name}
    except Exception as e:
        conn.close()
        return {"error": str(e)}


def get_user_campaigns(user_id: int, limit: int = 50) -> list:
    """获取用户活动列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, description, start_date, end_date, target_views, target_revenue,
               actual_views, actual_revenue, status, created_at
        FROM campaigns WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
    """, (user_id, limit))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def add_content_to_campaign(campaign_id: int, content_id: int) -> dict:
    """添加内容到活动"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT content_ids FROM campaigns WHERE id = ?", (campaign_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "活动不存在"}

    content_ids = json.loads(row["content_ids"] or "[]")
    if content_id not in content_ids:
        content_ids.append(content_id)
        cursor.execute("UPDATE campaigns SET content_ids = ? WHERE id = ?",
                      (json.dumps(content_ids), campaign_id))
        conn.commit()
    conn.close()
    return {"added": True, "content_ids": content_ids}


# ============================================
# 平台账号管理 CRUD
# ============================================

def create_platform_account(user_id: int, platform: str, account_name: str,
                            account_id: str = "", access_token: str = "",
                            refresh_token: str = "") -> dict:
    """创建平台账号"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO platform_accounts (user_id, platform, account_name, account_id, access_token, refresh_token)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, platform, account_name, account_id, access_token, refresh_token))
        conn.commit()
        account_id_new = cursor.lastrowid
        conn.close()
        return {"id": account_id_new, "platform": platform}
    except Exception as e:
        conn.close()
        return {"error": str(e)}


def get_user_platform_accounts(user_id: int) -> list:
    """获取用户的平台账号列表"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, platform, account_name, account_id, status, followers, created_at, updated_at
        FROM platform_accounts WHERE user_id = ? ORDER BY created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def update_platform_account(account_id: int, user_id: int, **kwargs) -> dict:
    """更新平台账号"""
    conn = get_db()
    cursor = conn.cursor()
    allowed_fields = ["account_name", "access_token", "refresh_token", "status", "followers"]
    update_parts = []
    values = []

    for field in allowed_fields:
        if field in kwargs:
            update_parts.append(f"{field} = ?")
            values.append(kwargs[field])

    if update_parts:
        update_parts.append("updated_at = CURRENT_TIMESTAMP")
        sql = f"UPDATE platform_accounts SET {', '.join(update_parts)} WHERE id = ? AND user_id = ?"
        values.extend([account_id, user_id])
        cursor.execute(sql, values)
        conn.commit()

    conn.close()
    return {"id": account_id, "updated": True}


def delete_platform_account(account_id: int, user_id: int) -> dict:
    """删除平台账号"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM platform_accounts WHERE id = ? AND user_id = ?", (account_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"deleted": affected > 0}


# ============================================
# 素材管理 CRUD
# ============================================

def create_material(user_id: int, filename: str, file_path: str,
                    file_type: str = "", file_size: int = 0,
                    mime_type: str = "", **kwargs) -> dict:
    """创建素材记录"""
    import json
    conn = get_db()
    cursor = conn.cursor()
    tags = kwargs.get("tags", [])
    folder = kwargs.get("folder", "")

    try:
        cursor.execute("""
            INSERT INTO materials (user_id, filename, file_path, file_type, file_size, mime_type, tags, folder, width, height, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, filename, file_path, file_type, file_size, mime_type,
              json.dumps(tags), folder, kwargs.get("width", 0), kwargs.get("height", 0), kwargs.get("duration", 0)))
        conn.commit()
        material_id = cursor.lastrowid
        conn.close()
        return {"id": material_id, "filename": filename}
    except Exception as e:
        conn.close()
        return {"error": str(e)}


def get_user_materials(user_id: int, file_type: str = None, folder: str = None, limit: int = 100) -> list:
    """获取用户素材列表"""
    import json
    conn = get_db()
    cursor = conn.cursor()

    conditions = ["user_id = ?"]
    params = [user_id]

    if file_type:
        conditions.append("file_type = ?")
        params.append(file_type)
    if folder:
        conditions.append("folder = ?")
        params.append(folder)

    where_clause = " AND ".join(conditions) + f" ORDER BY created_at DESC LIMIT {limit}"
    cursor.execute(f"SELECT * FROM materials WHERE {where_clause}", params)
    rows = cursor.fetchall()
    conn.close()

    result = []
    for row in rows:
        item = dict(row)
        item["tags"] = json.loads(item.get("tags", "[]"))
        result.append(item)
    return result


def delete_material(material_id: int, user_id: int) -> dict:
    """删除素材记录"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ? AND user_id = ?", (material_id, user_id))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return {"deleted": affected > 0}


# ============================================
# 发布日志
# ============================================

def create_publish_log(content_id: int, platform: str) -> dict:
    """创建发布日志"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO publish_logs (content_id, platform, status)
        VALUES (?, ?, 'pending')
    """, (content_id, platform))
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()
    return {"id": log_id}


def update_publish_log(log_id: int, status: str, error_message: str = "",
                       published_url: str = "", published_at: str = None) -> dict:
    """更新发布日志"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE publish_logs SET status = ?, error_message = ?, published_url = ?, published_at = ?
        WHERE id = ?
    """, (status, error_message, published_url, published_at, log_id))
    conn.commit()
    conn.close()
    return {"updated": True}


def get_content_publish_logs(content_id: int) -> list:
    """获取内容的发布日志"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM publish_logs WHERE content_id = ? ORDER BY created_at DESC
    """, (content_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


# ============================================
# 定时发布队列处理
# ============================================

def get_pending_publish_content() -> list:
    """获取待发布的内容"""
    from datetime import datetime
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        SELECT c.*, u.id as user_id FROM content c
        JOIN users u ON c.user_id = u.id
        WHERE c.status = 'pending' AND c.scheduled_at <= ?
        ORDER BY c.scheduled_at ASC
    """, (now,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_content_published(content_id: int, platform: str) -> dict:
    """标记内容已发布"""
    import json
    from datetime import datetime
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT published_platforms FROM content WHERE id = ?", (content_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "内容不存在"}

    platforms = json.loads(row["published_platforms"] or "[]")
    if platform not in platforms:
        platforms.append(platform)

    cursor.execute("""
        UPDATE content SET status = 'published', published_at = ?, published_platforms = ?
        WHERE id = ?
    """, (datetime.now().isoformat(), json.dumps(platforms), content_id))
    conn.commit()
    conn.close()
    return {"published": True}