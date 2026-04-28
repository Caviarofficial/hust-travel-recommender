"""数据库路径管理 - 兼容本地和 Streamlit Cloud"""
import os
import sqlite3


def _on_streamlit_cloud():
    """检测是否运行在 Streamlit Cloud 上"""
    return os.path.exists("/mount/src")


def get_db_path():
    """返回可写的数据库路径"""
    if _on_streamlit_cloud():
        return "/tmp/survey.db"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "survey.db")


def _init_at(db_path):
    """在指定路径创建并初始化数据库（不依赖 init_db.py）"""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS items (
            item_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            distance TEXT,
            energy TEXT,
            category TEXT,
            cost TEXT,
            tags TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            q1 TEXT, q2 TEXT, q3 TEXT, q4 TEXT, q5 TEXT,
            path_code TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS item_path_mapping (
            path_code TEXT,
            item_id INTEGER,
            priority INTEGER,
            PRIMARY KEY (path_code, item_id)
        )
    """)

    # 只在 items 表为空时插入数据
    if c.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0:
        ITEMS = [
            (1,"东湖绿道（磨山段）骑行","near","high","自然运动","free",'["自然","运动","免费"]'),
            (2,"东湖落雁景区散步","near","low","自然休闲","free",'["自然","安静","免费"]'),
            (3,"华科校内喻家湖环湖","near","low","自然休闲","free",'["自然","安静","免费"]'),
            (4,"华科森林公园徒步","near","high","自然运动","free",'["自然","运动","免费"]'),
            (5,"光谷步行街逛街","near","high","购物社交","mid",'["购物","社交","中消费"]'),
            (6,"光谷天地探店","near","low","美食文艺","mid",'["美食","文艺","中消费"]'),
            (7,"K11购物艺术中心","near","low","文艺展览","mid",'["看展","购物","中消费"]'),
            (8,"关山大道咖啡馆","near","low","休闲消费","low",'["安静","独处","低消费"]'),
            (9,"光谷书房/独立书店","near","low","文艺休闲","free",'["文艺","安静","免费"]'),
            (10,"藏龙岛湿地公园","near","low","自然休闲","free",'["自然","安静","免费"]'),
            (11,"光谷周边密室逃脱","near","high","娱乐社交","mid",'["刺激","社交","中消费"]'),
            (12,"光谷周边剧本杀","near","high","娱乐社交","mid",'["刺激","社交","中消费"]'),
            (13,"光谷国际网球中心","near","high","体育运动","low",'["运动","社交","低消费"]'),
            (14,"花山生态城绿道骑行","near","high","自然运动","free",'["自然","运动","免费"]'),
            (15,"鲁巷广场/光谷广场聚餐","near","high","美食社交","mid",'["美食","社交","中消费"]'),
            (16,"黄鹤楼","far","high","历史风景","mid",'["历史","风景","中消费"]'),
            (17,"昙华林文艺街区","far","low","文艺拍照","free",'["文艺","拍照","免费"]'),
            (18,"粮道街美食探店","far","low","美食小吃","low",'["美食","小吃","低消费"]'),
            (19,"汉口江滩散步","far","low","自然江景","free",'["自然","江景","免费"]'),
            (20,"武昌江滩/长江大桥","far","low","自然江景","free",'["自然","江景","免费"]'),
            (21,"湖北省博物馆","far","low","文化展览","free",'["文化","看展","免费"]'),
            (22,"武汉美术馆","far","low","艺术展览","free",'["艺术","安静","免费"]'),
            (23,"楚河汉街","far","high","购物美食","mid",'["购物","美食","中消费"]'),
            (24,"万松园美食街","far","low","美食小吃","low",'["美食","小吃","低消费"]'),
            (25,"江汉路步行街","far","high","购物逛街","mid",'["购物","逛街","中消费"]'),
            (26,"武汉天地","far","low","文艺美食","high",'["文艺","美食","高消费"]'),
            (27,"武汉欢乐谷","far","high","游乐刺激","high",'["刺激","游乐","高消费"]'),
            (28,"东湖樱花园","far","low","自然拍照","low",'["自然","拍照","低消费"]'),
            (29,"武汉大学（建筑/樱花）","far","low","文化拍照","free",'["文化","拍照","免费"]'),
            (30,"龟山公园/汉阳江滩","far","low","自然江景","free",'["自然","江景","免费"]'),
        ]
        c.executemany("INSERT INTO items VALUES (?,?,?,?,?,?,?)", ITEMS)

        PATH_MAPPING = {
            "A-A-A-A":[2,3,10],"A-A-A-B":[1,14,4],"A-A-B-A":[9,7],"A-A-B-B":[8,6],
            "A-B-A-A":[1,14],"A-B-A-B":[4,13],"A-B-B-A":[11,12],"A-B-B-B":[5,15,6],
            "B-A-A-A":[19,20],"B-A-A-B":[28,30],
            "B-A-B-A":[17,29],"B-A-B-B":[21,22],
            "B-B-A-A":[18,24],"B-B-A-B":[23,26],
            "B-B-B-A":[25,23],"B-B-B-B":[16,27],
        }
        for path_code, item_ids in PATH_MAPPING.items():
            for priority, item_id in enumerate(item_ids):
                c.execute("INSERT INTO item_path_mapping VALUES (?,?,?)",
                          (path_code, item_id, priority))

    conn.commit()
    conn.close()


def get_connection():
    """获取数据库连接，如果数据库不存在则自动初始化"""
    db_path = get_db_path()
    if not os.path.exists(db_path):
        _init_at(db_path)
    return sqlite3.connect(db_path)
