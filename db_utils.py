"""数据库路径管理 - 兼容本地和 Streamlit Cloud"""
import os
import sys
import sqlite3

def get_db_path():
    """返回可写的数据库路径"""
    # 本地开发：直接用当前目录
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "survey.db")
    if _is_writable(os.path.dirname(local_path)):
        return local_path
    # Streamlit Cloud：用 /tmp/
    return "/tmp/survey.db"

def _is_writable(path):
    """检测目录是否可写"""
    test_file = os.path.join(path, ".write_test")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        return True
    except OSError:
        return False

def get_connection():
    """获取数据库连接，如果数据库不存在则自动初始化"""
    db_path = get_db_path()
    need_init = not os.path.exists(db_path)
    if need_init:
        from init_db import init_database, DB_PATH as _
        # 临时修改 init_db 的路径
        import init_db
        original_path = init_db.DB_PATH
        init_db.DB_PATH = db_path
        init_database()
        init_db.DB_PATH = original_path
    return sqlite3.connect(db_path)
