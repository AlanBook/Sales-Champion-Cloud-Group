import os
import sys
import uvicorn

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == '__main__':
    uvicorn.run(
        "sales_champion_backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
