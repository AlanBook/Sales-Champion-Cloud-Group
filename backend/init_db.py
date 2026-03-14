import sys
import os

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import text
from sales_champion_backend.db.session import SessionLocal
from sales_champion_backend.db.models import Base
from sales_champion_backend.services.seed_service import load_demo_seed

print("开始初始化数据库...")

try:
    with SessionLocal() as db:
        # 创建所有表
        print("正在创建数据库表结构...")
        Base.metadata.create_all(db.get_bind())
        print("✅ 表结构创建完成")
        
        db.execute(text("SELECT 1"))
        print("数据库连接成功")
        
        print("正在加载种子数据...")
        load_demo_seed(db)
        db.commit()
        
    print("✅ 数据库初始化完成！")
    print("内置账号:")
    print("  - boss_demo / password")
    print("  - manager_demo / password")
    print("  - admin_demo / password")
    print("  - staff_08 / password")
except Exception as e:
    print(f"❌ 初始化失败：{e}")
    import traceback
    traceback.print_exc()
