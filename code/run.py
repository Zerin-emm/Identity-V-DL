import os
import socket
import subprocess
import sys
import logging
import time

# 记录程序开始时间
start_time = time.time()

# 禁用 urllib3 安全警告
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入Flask相关模块
from flask import request, Response

# 导入其他必要模块
import requests
import json
import traceback

# 初始化Flask应用
from flask import Flask
app = Flask(__name__)

# 禁用 Flask 的默认日志输出
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.ERROR)

# 重定向stderr，屏蔽系统级权限错误输出
class DisableStderr:
    def __enter__(self):
        self.old_stderr = sys.stderr
        sys.stderr = open(os.devnull, 'w')  # 将stderr输出到空设备
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stderr.close()
        sys.stderr = self.old_stderr  # 恢复stderr

# 日志配置（启动清空，退出保留）
try:
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        SCRIPT_DIR = sys._MEIPASS
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
except:
    SCRIPT_DIR = os.getcwd()
LOG_PATH = os.path.join(SCRIPT_DIR, "log.txt")

def write_log(content):
    """将日志写入log.txt（优化版）"""
    try:
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {content}\n"
        
        # 使用缓冲写入，减少I/O操作
        with open(LOG_PATH, "a", encoding="utf-8", buffering=1) as f:
            f.write(log_entry)
            # 行缓冲模式，换行时自动刷新
    except Exception as e:
        pass  # 静默模式不输出错误

def clear_log():
    """清空log.txt文件"""
    try:
        open(LOG_PATH, "w", encoding="utf-8").close()
    except Exception as e:
        pass  # 静默模式不输出错误

loginMethod = [
    {
        "name": "手机账号",
        "icon_url": "",
        "text_color": "",
        "hot": True,
        "type": 7,
        "icon_url_large": "",
    },
    {
        "login_url": "",
        "name": "网易邮箱",
        "icon_url": "",
        "text_color": "",
        "hot": True,
        "type": 1,
        "icon_url_large": "",
    },
    {
        "login_url": "",
        "name": "扫码登录",
        "icon_url": "",
        "text_color": "",
        "hot": True,
        "type": 17,
        "icon_url_large": "",
    },
]
pcInfo = {
    "extra_unisdk_data": "",
    "from_game_id": "h55",
    "src_app_channel": "netease",
    "src_client_ip": "",
    "src_client_type": 1,
    "src_jf_game_id": "h55",
    "src_pay_channel": "netease",
    "src_sdk_version": "3.15.0",
    "src_udid": "",
}

DOMAIN = "service.mkey.163.com"
TRUSTED_DNS = "114.114.114.114"

# 获取证书目录
try:
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径，使用可执行文件所在目录
        SCRIPT_DIR = os.path.dirname(os.path.abspath(sys.executable))
    else:
        SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # 确保路径以反斜杠结尾
    if not SCRIPT_DIR.endswith('\\'):
        SCRIPT_DIR += '\\'
    
    # 移除末尾的 run\ 目录（如果存在）
    if SCRIPT_DIR.endswith('run\\'):
        SCRIPT_DIR = SCRIPT_DIR[:-4]  # 移除 "run\\"
    
    # 证书目录为 SCRIPT_DIR + certificate（使用字符串拼接，不使用 os.path.join）
    WORKDIR = SCRIPT_DIR + "certificate"
except Exception as e:
    # 异常情况下使用当前目录
    WORKDIR = os.path.join(os.getcwd(), "certificate")

# 全局变量
TARGET_URL = ""

def requestGetAsCv(request, cv):
    global TARGET_URL
    query = request.args.copy()
    if cv:
        query["cv"] = cv
    resp = requests.request(
        method=request.method,
        url=TARGET_URL + request.path,
        params=query,
        headers=request.headers,
        cookies=request.cookies,
        allow_redirects=False,
        verify=False,
    )
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    return Response(resp.text, resp.status_code, headers)

def proxy(request):
    global TARGET_URL
    query = request.args.copy()
    new_body = request.get_data(as_text=True)
    resp = requests.request(
        method=request.method,
        url=TARGET_URL + request.path,
        params=query,
        headers=request.headers,
        data=new_body,
        cookies=request.cookies,
        allow_redirects=False,
        verify=False,
    )
    app.logger.info(resp.url)
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    response = Response(resp.content, resp.status_code, headers)
    return response

def requestPostAsCv(request, cv):
    query = request.args.copy()
    if cv:
        query["cv"] = cv
    try:
        new_body = request.get_json()
        new_body["cv"] = cv
        new_body.pop("arch", None)
    except:
        new_body = dict(x.split("=") for x in request.get_data(as_text=True).split("&"))
        new_body["cv"] = cv
        new_body.pop("arch", None)
        new_body = "&".join([f"{k}={v}" for k, v in new_body.items()])

    app.logger.info(new_body)
    resp = requests.request(
        method=request.method,
        url=TARGET_URL + request.path,
        params=query,
        data=new_body,
        headers=request.headers,
        cookies=request.cookies,
        allow_redirects=False,
        verify=False,
    )
    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]
    return Response(resp.text, resp.status_code, headers)

@app.route("/mpay/games/<game_id>/login_methods", methods=["GET"])
def handle_login_methods(game_id):
    try:
        resp: Response = requestGetAsCv(request, "i4.7.0")
        new_login_methods = resp.get_json()
        new_login_methods["entrance"] = [(loginMethod)]
        new_login_methods["select_platform"] = True
        new_login_methods["qrcode_select_platform"] = True
        for i in new_login_methods["config"]:
            new_login_methods["config"][i]["select_platforms"] = [0, 1, 2, 3, 4]
        resp.set_data(json.dumps(new_login_methods))
        write_log("登录界面劫持成功")  # 修改日志内容
        return resp
    except Exception as e:
        error_msg = f"处理登录入口请求异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/user_info", methods=["POST"])
def handle_user_info():
    try:
        write_log("[验证码登录] 获取用户信息")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"[验证码登录] 获取用户信息异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/get_sms", methods=["POST"])
def handle_get_sms():
    try:
        write_log("[验证码登录] 获取短信验证码")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"[验证码登录] 获取短信验证码异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/verify_sms", methods=["POST"])
def handle_verify_sms():
    try:
        write_log("[验证码登录] 验证短信验证码")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"[验证码登录] 验证短信验证码异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/finish", methods=["POST"])
def handle_finish():
    try:
        write_log("[验证码登录] 完成登录")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"[验证码登录] 完成登录异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/guide", methods=["POST"])
def handle_guide():
    try:
        write_log("登录成功")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"登录成功异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/users/login/mobile/verify_pwd", methods=["POST"])
def handle_verify_pwd():
    try:
        write_log("[密码登录] 验证密码")
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"[密码登录] 验证密码异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/games/<game_id>/devices/<device_id>/users", methods=["POST"])
def handle_first_login(game_id=None, device_id=None):
    try:
        return requestPostAsCv(request, "i4.7.0")
    except Exception as e:
        error_msg = f"处理首次登录请求异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/games/<game_id>/devices/<device_id>/users/<user_id>", methods=["GET"])
def handle_login(game_id, device_id, user_id):
    try:
        write_log("[本地登录] 获取用户信息")
        resp: Response = requestGetAsCv(request, "i4.7.0")
        new_devices = resp.get_json()
        new_devices["user"]["pc_ext_info"] = pcInfo
        resp.set_data(json.dumps(new_devices))
        return resp
    except Exception as e:
        error_msg = f"[本地登录] 获取用户信息异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/games/pc_config", methods=["GET"])
def handle_pc_config():
    try:
        resp: Response = requestGetAsCv(request, "i4.7.0")
        new_config = resp.get_json()
        new_config["game"]["config"]["cv_review_status"] = 1
        resp.set_data(json.dumps(new_config))
        write_log("请求转发成功")  # 修改日志内容
        return resp
    except Exception as e:
        error_msg = f"处理PC配置请求异常: {traceback.format_exc()}"
        write_log(error_msg)
        return proxy(request)

@app.route("/mpay/api/qrcode/<path>", methods=["GET"])
def handle_qrcode(path):
    # 屏蔽二维码请求的日志打印
    return proxy(request)

@app.route("/<path:path>", methods=["GET", "POST"])
def globalProxy(path):
    # 根据不同路径修改日志内容
    if path == "mpay/config/common.json":
        write_log("客户端连接正常")
    else:
        # 其他全局代理请求默认不打印（如需保留可调整）
        pass
    if request.method == "GET":
        return requestGetAsCv(request, "i4.7.0")
    else:
        return requestPostAsCv(request, "i4.7.0")

# ========== 修复核心:正确的端口检测函数 ==========
def check_port_occupied(port):
    """检查指定端口是否被占用（修复误判逻辑）"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # 关键修复:connect_ex返回0表示能连上（端口被占用），非0表示未被占用
        is_occupied = s.connect_ex(('127.0.0.1', port)) == 0
        return is_occupied

def get_port_process(port):
    """获取占用指定端口的进程信息"""
    try:
        result = subprocess.check_output(
            f"netstat -ano | findstr :{port}",
            shell=True,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        result = result.decode("cp437")
        if result:
            for line in result.splitlines():
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    try:
                        process_info = subprocess.check_output(
                            f"tasklist /FI \"PID eq {pid}\" /FO CSV /NH",
                            shell=True,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NO_WINDOW
                        )
                        process_info = process_info.decode("cp437")
                        if process_info:
                            process_name = process_info.split(",")[0].replace('"', '')
                            return f"{process_name}={pid}"
                    except:
                        pass
        return "未知进程"
    except:
        return "未知进程"

def main():
    # 启动时清空日志
    clear_log()
    
    # 多DNS服务器并行查询
    global TARGET_URL
    try:
        import threading
        DOMAIN = "service.mkey.163.com"
        DNS_SERVERS = ["8.8.8.8", "114.114.114.114", "223.5.5.5"]  # 多个DNS服务器
        result_event = threading.Event()
        
        def query_dns(dns_server):
            global TARGET_URL
            try:
                # 使用 CREATE_NO_WINDOW 隐藏 nslookup 窗口
                result = subprocess.check_output(
                    ["nslookup", DOMAIN, dns_server], 
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    timeout=2  # 设置2秒超时
                )
                result = result.decode("cp437")
                IP = ""
                for line in result.splitlines():
                    if "Addresses" in line or "Address" in line:
                        ip_address = line.split()[-1]
                        if ip_address != dns_server:
                            IP = ip_address
                            break
                if IP:
                    TARGET_URL = f"https://{IP}"
                    result_event.set()  # 触发事件，通知主线程
            except Exception as e:
                pass  # 忽略单个DNS服务器的错误
        
        # 启动多个线程查询DNS
        threads = []
        for dns in DNS_SERVERS:
            t = threading.Thread(target=query_dns, args=(dns,))
            threads.append(t)
            t.start()
        
        # 等待任一DNS服务器返回结果，最多等待3秒
        result_event.wait(3)
        
        # 检查是否有结果
        if not TARGET_URL:
            error_msg = "DNS解析失败，请检查网络环境！"
            write_log(error_msg)
            return
    except Exception as e:
        error_msg = f"DNS查询异常: {traceback.format_exc()}"
        write_log(error_msg)
        return
    
    # 并行执行检查操作
    import threading
    
    # 检查结果变量
    workdir_exists = False
    cert_files_exist = False
    port_occupied = False
    port_process = ""
    hosts_valid = False
    
    # 线程事件
    workdir_event = threading.Event()
    cert_event = threading.Event()
    port_event = threading.Event()
    hosts_event = threading.Event()
    
    # 检查工作目录
    def check_workdir():
        nonlocal workdir_exists
        workdir_exists = os.path.exists(WORKDIR)
        workdir_event.set()
    
    # 检查证书文件
    def check_cert_files():
        nonlocal cert_files_exist
        if os.path.exists(WORKDIR):
            try:
                os.chdir(WORKDIR)
                cert_files_exist = os.path.exists("domain_cert.pem") and os.path.exists("domain_key.pem")
            except:
                pass
        cert_event.set()
    
    # 检查端口占用
    def check_port():
        nonlocal port_occupied, port_process
        port_occupied = check_port_occupied(443)
        if port_occupied:
            port_process = get_port_process(443)
        port_event.set()
    
    # 检查hosts配置
    def check_hosts():
        nonlocal hosts_valid
        try:
            hosts_valid = socket.gethostbyname(DOMAIN) == "127.0.0.1"
        except:
            pass
        hosts_event.set()
    
    # 启动并行线程
    threads = [
        threading.Thread(target=check_workdir),
        threading.Thread(target=check_cert_files),
        threading.Thread(target=check_port),
        threading.Thread(target=check_hosts)
    ]
    
    for t in threads:
        t.start()
    
    # 等待所有检查完成
    workdir_event.wait()
    cert_event.wait()
    port_event.wait()
    hosts_event.wait()
    
    # 检查结果处理
    if not workdir_exists:
        error_msg = "未初始化！请先运行初始化程序"
        write_log(error_msg)
        return
    
    if not cert_files_exist:
        error_msg = "未初始化！请先运行初始化程序"
        write_log(error_msg)
        return
    
    if port_occupied:
        write_log(f"443 端口被占用=>{port_process}")
        os._exit(0)
    
    if not hosts_valid:
        error_msg = "Hosts 状态异常！请重新运行初始化程序"
        write_log(error_msg)
        return
    
    # 进入工作目录
    try:
        os.chdir(WORKDIR)
    except Exception as e:
        error_msg = f"进入工作目录异常: {str(e)}"
        write_log(error_msg)
        return
    
    # 启动时输出常规日志
    write_log("第五人格登录代理")
    write_log(f"目标域名: service.mkey.163.com")
    write_log("本地绑定: 127.0.0.1:443")
    write_log(f"工作目录: {WORKDIR}")
    write_log("代理服务运行中")
    # 计算并输出耗时
    elapsed_time = time.time() - start_time
    write_log(f"耗费时间: {elapsed_time:.1f}秒")
    
    # 2. 启动服务器（完全静默模式）
    try:
        # 完全重定向 stdout 和 stderr 到空设备
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        
        app.run(host="127.0.0.1", port=443, ssl_context=("domain_cert.pem", "domain_key.pem"), threaded=False, use_reloader=False)
    except OSError as e:
        error_msg = f"服务器启动失败:{str(e)}"
        write_log(error_msg)
    except Exception as e:
        error_msg = f"未知错误:{traceback.format_exc()}"
        write_log(f"服务器启动出错:{error_msg}")
    finally:
        # 确保恢复 stdout 和 stderr
        try:
            sys.stdout.close()
            sys.stderr.close()
        except:
            pass

if __name__ == "__main__":
    main()