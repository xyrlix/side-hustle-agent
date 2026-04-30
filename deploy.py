"""
副业雷达 - 一键部署脚本

用于在服务器上一键部署前后端服务
"""

import os
import sys
import subprocess


def print_step(msg):
    print(f"\n{'='*50}")
    print(f"  {msg}")
    print(f"{'='*50}")


def check_dependencies():
    """检查必要依赖"""
    print_step("检查系统依赖")

    # Python
    try:
        v = sys.version_info
        print(f"✓ Python {v.major}.{v.minor}.{v.micro}")
    except:
        print("✗ Python 未安装")
        return False

    # Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        print(f"✓ Node.js {result.stdout.strip()}")
    except:
        print("✗ Node.js 未安装")

    return True


def install_backend():
    """安装后端依赖"""
    print_step("安装后端依赖")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)


def build_frontend():
    """构建前端"""
    print_step("构建前端")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    # 检查node_modules
    if not os.path.exists(os.path.join(frontend_dir, "node_modules")):
        print("安装前端依赖...")
        subprocess.run(["npm", "install"], cwd=frontend_dir, check=True)

    print("构建前端...")
    subprocess.run(["npm", "run", "build"], cwd=frontend_dir, check=True)
    print("✓ 前端构建完成")


def start_services():
    """启动服务"""
    print_step("启动服务")

    # 创建数据目录
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)

    # 启动后端
    print("启动后端...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "side_hustle_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]
    subprocess.Popen(backend_cmd, cwd=os.path.dirname(__file__))

    print("✓ 后端已启动 (http://0.0.0.0:8000)")

    # 启动前端
    print("启动前端...")
    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
    dist_dir = os.path.join(frontend_dir, "dist")

    if os.path.exists(dist_dir):
        # 使用serve静态文件
        subprocess.Popen(["npx", "serve", dist_dir, "-l", "1420"])
        print("✓ 前端已启动 (http://0.0.0.0:1420)")
    else:
        # 开发模式
        subprocess.Popen(["npm", "run", "dev", "--", "--host"], cwd=frontend_dir)
        print("✓ 前端开发服务器已启动 (http://0.0.0.0:1420)")


def main():
    print(f"""
{'='*50}
  副业雷达 - 一键部署脚本
{'='*50}
    """)

    if not check_dependencies():
        print("\n缺少必要依赖，请先安装")
        sys.exit(1)

    try:
        install_backend()
        build_frontend()
        start_services()

        print(f"""
{'='*50}
  部署完成！
{'='*50}

  后端: http://localhost:8000
  前端: http://localhost:1420
  API文档: http://localhost:8000/docs

  默认管理员: admin / admin123

  首次使用请修改 .env 中的 JWT_SECRET 和 API Key
    """)
    except Exception as e:
        print(f"\n部署失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()