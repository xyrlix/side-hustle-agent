#!/usr/bin/env python3
"""
副业雷达 - 一键启动脚本

单例启动后端 API 服务和前端开发服务器
特性：
- 检测已有进程，不重复启动
- 自动检测端口占用
- Ctrl+C 优雅退出
"""

import subprocess
import sys
import os
import time
import socket
import signal
from pathlib import Path


# 全局进程管理
backend_process = None
frontend_process = None


def is_port_in_use(port: int) -> bool:
    """检查端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) == 0


def find_free_port(start_port: int = 8000) -> int:
    """查找空闲端口"""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port


def check_existing_services():
    """检查已有服务是否运行"""
    backend_running = is_port_in_use(8000)
    frontend_running = is_port_in_use(1420)
    return backend_running, frontend_running


def check_node_npm():
    """检查 Node.js 和 npm"""
    import shutil

    node_path = shutil.which("node")
    if node_path:
        try:
            result = subprocess.run([node_path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                node_version = result.stdout.strip()
                npm_path = shutil.which("npm")
                if npm_path:
                    result = subprocess.run([npm_path, "--version"], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        return True, node_version, result.stdout.strip()
        except:
            pass

    return False, None, None


def check_python():
    """检查 Python 版本"""
    version = sys.version_info
    return version.major >= 3 and version.minor >= 8


def install_frontend_deps(frontend_dir: Path) -> bool:
    """安装前端依赖"""
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        return True

    print("  [*] 首次运行，安装前端依赖...")
    print("  [*] 这可能需要几分钟")

    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            timeout=300,
            shell=True,
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("  [!] 安装超时，请手动运行 npm install")
        return False
    except Exception as e:
        print(f"  [!] 安装失败: {e}")
        return False


def wait_for_service(url: str, timeout: int = 30) -> bool:
    """等待服务启动"""
    import urllib.request
    for _ in range(timeout * 2):
        time.sleep(0.5)
        try:
            response = urllib.request.urlopen(url, timeout=2)
            return response.status == 200
        except:
            continue
    return False


def cleanup_processes():
    """清理子进程"""
    global backend_process, frontend_process

    if backend_process:
        try:
            backend_process.terminate()
            backend_process.wait(timeout=3)
        except:
            try:
                backend_process.kill()
            except:
                pass

    if frontend_process:
        try:
            frontend_process.terminate()
            frontend_process.wait(timeout=3)
        except:
            try:
                frontend_process.kill()
            except:
                pass


def signal_handler(signum, frame):
    """信号处理"""
    print("\n\n  [*] 收到退出信号，正在停止服务...")
    cleanup_processes()
    print("  [OK] 已停止")
    sys.exit(0)


def print_banner():
    """打印横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   副业雷达 - 多平台社交媒体管理系统 v1.0                  ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)


def start_backend(port: int = 8000) -> subprocess.Popen | None:
    """启动后端服务"""
    global backend_process

    print(f"\n  [1/2] 启动后端服务 (端口 {port})...")

    if is_port_in_use(port):
        # 检查是否是 uvicorn 进程
        try:
            result = subprocess.run(
                ["powershell", "-Command", f"Get-NetTCPConnection -LocalPort {port} | Select-Object -ExpandProperty OwningProcess"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.stdout.strip():
                print(f"  [WARN] 端口 {port} 已被占用，后端服务可能已在运行")
                print(f"  [OK] 跳过后端启动")
                return None
        except:
            pass

        print(f"  [*] 端口 {port} 已被占用，尝试其他端口...")
        port = find_free_port(port)
        print(f"  [*] 使用端口 {port}")

    cmd = [sys.executable, "-m", "uvicorn",
           "side_hustle_agent.main:app",
           "--host", "0.0.0.0",
           "--port", str(port),
           "--reload"]

    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    try:
        backend_process = subprocess.Popen(
            cmd,
            cwd=str(Path(__file__).parent),
            env=env,
            shell=True,
        )

        print("  [*] 等待后端启动...")
        if wait_for_service(f"http://localhost:{port}/health", timeout=20):
            print(f"  [OK] 后端已启动 (http://localhost:{port})")
            return backend_process
        else:
            print("  [FAIL] 后端启动超时")
            if backend_process:
                backend_process.terminate()
            return None
    except Exception as e:
        print(f"  [FAIL] 后端启动失败: {e}")
        return None


def start_frontend(port: int = 1420) -> subprocess.Popen | None:
    """启动前端服务"""
    global frontend_process

    print(f"\n  [2/2] 启动前端服务 (端口 {port})...")

    frontend_dir = Path(__file__).parent / "frontend"

    if is_port_in_use(port):
        print(f"  [WARN] 端口 {port} 已被占用，前端服务可能已在运行")
        print(f"  [OK] 跳过前端启动")
        return None

    # 检查 Node.js
    has_node, node_ver, npm_ver = check_node_npm()
    if not has_node:
        print("  [FAIL] Node.js 未安装，请先安装 Node.js")
        print("  [i] 下载地址: https://nodejs.org/")
        return None

    print(f"  [OK] Node.js {node_ver}, npm {npm_ver}")

    # 安装依赖
    if not install_frontend_deps(frontend_dir):
        print("  [!] 依赖安装可能有问题，但继续尝试...")

    # 启动开发服务器
    cmd = ["npm", "run", "dev", "--", "--port", str(port), "--host"]

    try:
        frontend_process = subprocess.Popen(
            cmd,
            cwd=str(frontend_dir),
            shell=True,
        )

        print("  [*] 等待前端启动...")
        if wait_for_service(f"http://localhost:{port}", timeout=30):
            print(f"  [OK] 前端已启动 (http://localhost:{port})")
            return frontend_process
        else:
            print("  [FAIL] 前端启动超时")
            if frontend_process:
                frontend_process.terminate()
            return None
    except Exception as e:
        print(f"  [FAIL] 前端启动失败: {e}")
        return None


def main():
    global backend_process, frontend_process

    print_banner()

    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 检查 Python 版本
    if not check_python():
        print("\n  [FAIL] 需要 Python 3.8+")
        sys.exit(1)

    print("\n  [*] 检查环境...")

    # 检查已有服务
    backend_running, frontend_running = check_existing_services()

    if backend_running:
        print("  [WARN] 后端服务已在端口 8000 运行")
    if frontend_running:
        print("  [WARN] 前端服务已在端口 1420 运行")

    if backend_running and frontend_running:
        print("\n  [INFO] 所有服务已在运行，无需重新启动")
        print("\n" + "=" * 60)
        print("  后端 API:  http://localhost:8000")
        print("  前端页面:  http://localhost:1420")
        print("  API 文档:  http://localhost:8000/docs")
        print("=" * 60)
        print("\n  按 Ctrl+C 退出（不会停止已有服务）")
        print()

        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n  [OK] 退出")
        return

    # 启动后端
    backend_port = 8000
    bp = start_backend(backend_port)
    if bp:
        backend_process = bp

    # 启动前端
    frontend_port = 1420
    fp = start_frontend(frontend_port)
    if fp:
        frontend_process = fp

    # 检查是否有服务启动成功
    if not backend_process and not frontend_process:
        backend_running, frontend_running = check_existing_services()
        if backend_running or frontend_running:
            print("\n  [OK] 服务已在运行")
        else:
            print("\n  [FAIL] 所有服务启动失败")
            sys.exit(1)

    # 打印完成信息
    print("\n" + "=" * 60)
    print("  [SUCCESS] 启动完成!")
    print("=" * 60 + "\n")

    # 获取实际端口
    actual_backend = 8000 if is_port_in_use(8000) else 8000
    actual_frontend = 1420 if is_port_in_use(1420) else 1420

    print(f"  后端 API:  http://localhost:{actual_backend}")
    print(f"  前端页面:  http://localhost:{actual_frontend}")
    print(f"  API 文档:  http://localhost:{actual_backend}/docs")
    print()
    print("  按 Ctrl+C 停止服务并退出")
    print()

    # 监控进程
    try:
        while True:
            time.sleep(1)

            # 检查进程状态
            backend_alive = backend_process and backend_process.poll() is None
            frontend_alive = frontend_process and frontend_process.poll() is None

            if not backend_alive and backend_process:
                print("\n  [WARN] 后端进程已退出")
                backend_process = None

            if not frontend_alive and frontend_process:
                print("\n  [WARN] 前端进程已退出")
                frontend_process = None

            # 所有进程都退出了
            if not backend_process and not frontend_process:
                # 检查是否还有服务在运行
                if is_port_in_use(8000) or is_port_in_use(1420):
                    print("\n  [INFO] 服务仍在运行，保持监控...")
                    continue
                else:
                    print("\n  [INFO] 所有服务已停止")
                    break

    except KeyboardInterrupt:
        print("\n\n  [*] 正在停止服务...")

    finally:
        cleanup_processes()
        print("  [OK] 已停止")


if __name__ == "__main__":
    main()