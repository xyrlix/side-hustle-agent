"""
副业雷达 - 一键启动器

同时启动后端 API 服务和前端开发服务器
"""

import subprocess
import sys
import os
import time


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    END = "\033[0m"


def print_banner():
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"{Colors.CYAN}  副业雷达 - 一键启动{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print()


def check_api_key():
    """检查 API Key 是否设置"""
    api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("LLM_API_KEY")
    if not api_key:
        print(f"{Colors.YELLOW}[提示] 未检测到 API Key{Colors.END}")
        print(f"  请在界面右上角 ⚙️ 设置或设置环境变量")
        print()
    return bool(api_key)


def start_backend():
    """启动后端服务"""
    print(f"{Colors.GREEN}[1/2] 启动后端服务...{Colors.END}")

    cmd = [sys.executable, "-m", "uvicorn", "side_hustle_agent.main:app", "--host", "0.0.0.0", "--port", "8000"]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
        text=True,
        bufsize=1,
    )

    # 等待后端启动并输出日志
    started = False
    for i in range(20):
        time.sleep(0.5)

        # 输出实时日志
        if process.stdout:
            line = process.stdout.readline()
            if line:
                print(f"  {line.rstrip()}")

        # 检查是否启动成功
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:8000/health", timeout=1)
            if response.status == 200:
                print(f"{Colors.GREEN}  ✓ 后端已启动 (http://localhost:8000){Colors.END}")
                return process
        except:
            pass

        # 检查进程是否退出
        if process.poll() is not None:
            # 读取所有输出
            output = process.stdout.read() if process.stdout else ""
            print(f"{Colors.RED}  ✗ 后端启动失败{Colors.END}")
            print(output[-500:] if output else "")
            return None

    # 启动超时，终止进程
    process.terminate()
    print(f"{Colors.RED}  ✗ 后端启动超时{Colors.END}")
    return None


def start_frontend():
    """启动前端服务"""
    print(f"{Colors.GREEN}[2/2] 启动前端服务...{Colors.END}")

    frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

    # 检查 npm - Windows 兼容
    npm_path = None
    for cmd in ["npm", "npm.cmd", "C:\\Program Files\\nodejs\\npm.cmd"]:
        try:
            result = subprocess.run([cmd, "--version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                npm_path = cmd
                break
        except:
            continue

    if not npm_path:
        print(f"{Colors.RED}  ✗ npm 未安装，请先安装 Node.js{Colors.END}")
        return None

    # 安装依赖
    node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules):
        print(f"  {Colors.YELLOW}首次运行，安装前端依赖...{Colors.END}")
        result = subprocess.run([npm_path, "install"], cwd=frontend_dir, capture_output=True)
        if result.returncode != 0:
            print(f"{Colors.RED}  ✗ 依赖安装失败{Colors.END}")
            print(result.stderr.decode("utf-8", errors="ignore")[-300:])
            return None

    # 启动开发服务器
    cmd = [npm_path, "run", "dev", "--", "--port", "1420"]
    process = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    # 等待前端启动
    for i in range(30):
        time.sleep(0.5)

        # 输出实时日志
        if process.stdout:
            line = process.stdout.readline()
            if line:
                print(f"  {line.rstrip()}")

        # 检查是否启动成功
        try:
            import urllib.request
            response = urllib.request.urlopen("http://localhost:1420", timeout=1)
            if response.status == 200:
                print(f"{Colors.GREEN}  ✓ 前端已启动 (http://localhost:1420){Colors.END}")
                return process
        except:
            pass

        # 检查进程是否退出
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            print(f"{Colors.RED}  ✗ 前端启动失败{Colors.END}")
            print(output[-500:] if output else "")
            return None

    print(f"{Colors.RED}  ✗ 前端启动超时{Colors.END}")
    process.terminate()
    return None


def main():
    print_banner()
    check_api_key()

    backend_process = start_backend()
    if not backend_process:
        print(f"\n{Colors.RED}后端启动失败，退出{Colors.END}")
        sys.exit(1)

    frontend_process = start_frontend()
    if not frontend_process:
        print(f"\n{Colors.YELLOW}前端启动失败，后端继续运行{Colors.END}")

    print()
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print(f"{Colors.CYAN}  启动完成!{Colors.END}")
    print(f"{Colors.CYAN}{'='*50}{Colors.END}")
    print()
    print(f"  后端 API: {Colors.WHITE}http://localhost:8000{Colors.END}")
    print(f"  前端页面: {Colors.WHITE}http://localhost:1420{Colors.END}")
    print(f"  API 文档: {Colors.WHITE}http://localhost:8000/docs{Colors.END}")
    print()
    print(f"  按 Ctrl+C 停止服务")
    print()

    try:
        while True:
            time.sleep(1)

            if backend_process.poll() is not None:
                print(f"\n{Colors.RED}[错误] 后端进程已退出{Colors.END}")
                break

            if frontend_process and frontend_process.poll() is not None:
                print(f"\n{Colors.RED}[错误] 前端进程已退出{Colors.END}")
                break

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}正在停止服务...{Colors.END}")

    finally:
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()

        print(f"{Colors.GREEN}已停止{Colors.END}")


if __name__ == "__main__":
    main()