#!/usr/bin/env python3
"""
API服务器启动脚本

启动Nof1 Trading API服务
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from api.main import app
    import uvicorn
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("请确保已安装所需依赖:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def main():
    """启动API服务器"""
    print("\n" + "=" * 80)
    print("🚀 启动 Nof1 Trading API 服务")
    print("=" * 80)
    print()
    print("📖 API文档:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc: http://localhost:8000/redoc")
    print("  - 健康检查: http://localhost:8000/api/v1/health")
    print()
    print("📊 主要端点:")
    print("  - GET /api/v1/decisions - 获取决策记录")
    print("  - GET /api/v1/models/profit - 获取盈利数据")
    print("  - GET /api/v1/models/performance - 获取性能摘要")
    print("  - GET /api/v1/stats/summary - 获取系统统计")
    print()
    print("💡 使用示例:")
    print("  python3 examples/api_example.py")
    print()
    print("=" * 80)
    print()

    # 启动服务器
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()
