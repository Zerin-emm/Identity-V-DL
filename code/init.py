import os
import subprocess
import ctypes
import sys

# used for colored console output
import colorama

HOSTS_FILE = r"C:\Windows\System32\drivers\etc\hosts"
DOMAIN = "service.mkey.163.com"

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
    
    # 移除末尾的 init\ 目录（如果存在）
    if SCRIPT_DIR.endswith('init\\'):
        SCRIPT_DIR = SCRIPT_DIR[:-5]  # 移除 "init\\"
    
    # 证书目录为 SCRIPT_DIR + certificate
    WORKDIR = SCRIPT_DIR + "certificate"
except Exception as e:
    # 异常情况下使用当前目录
    WORKDIR = os.path.join(os.getcwd(), "certificate")

def safe_input(prompt=""):
    try:
        return input(prompt)
    except (RuntimeError, OSError):
        return None

def ensure_console():
    try:
        # 检查并分配控制台
        if not ctypes.windll.kernel32.GetConsoleWindow():
            ctypes.windll.kernel32.AllocConsole()
            # 重定向标准输入输出
            sys.stdout = open("CONOUT$", "w", encoding="utf-8")
            sys.stderr = open("CONOUT$", "w", encoding="utf-8")
            sys.stdin = open("CONIN$", "r", encoding="utf-8")
        
        # 设置窗口标题
        ctypes.windll.kernel32.SetConsoleTitleW("初始化程序")
        
        # 设置代码页为UTF-8
        try:
            import subprocess
            subprocess.run("chcp 65001", shell=True, capture_output=True)
        except:
            pass

        # initialize colorama for ANSI support on Windows
        try:
            colorama.init()
        except Exception:
            pass
    except Exception as e:
        # 控制台设置失败不影响程序运行
        pass

def main():
    ensure_console()

    # 删除工作目录残留
    from shutil import rmtree
    if os.path.exists(WORKDIR):
        print(f"清理工作目录残留：{WORKDIR}")
        try:
            rmtree(WORKDIR)
            print("清理完成")
        except Exception as e:
            print(f"清理失败：{str(e)}")
            safe_input("回车退出...")
            sys.exit(0)
    
    # 创建工作目录
    os.mkdir(WORKDIR)
    print(f"工作目录：{WORKDIR}")
    os.chdir(WORKDIR)
    
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives.serialization import (
        Encoding,
        PrivateFormat,
        NoEncryption,
    )
    from datetime import datetime, timedelta

    # 生成密钥对
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 创建证书主题和颁发者名称
    subject = issuer = x509.Name(
        [
            x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Beijing"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "BeiJing"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Identity-V"),
            x509.NameAttribute(NameOID.COMMON_NAME, "Identity-V"),
        ]
    )

    # 创建证书
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(
            # 证书有效期为1年
            datetime.now()
            + timedelta(days=365)
        )
        .add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True,
        )
        .sign(key, hashes.SHA256())
    )

    # 证书和密钥写入文件
    with open("root_ca.pem", "wb") as f:
        f.write(cert.public_bytes(Encoding.PEM))

    # 生成域名密钥对
    domain_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # 创建CSR
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(
            x509.Name(
                [
                    x509.NameAttribute(NameOID.COUNTRY_NAME, "CN"),
                    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "BeiJing"),
                    x509.NameAttribute(NameOID.LOCALITY_NAME, "BeiJing"),
                    x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Identity-V"),
                    x509.NameAttribute(NameOID.COMMON_NAME, DOMAIN),
                ]
            )
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName(DOMAIN),
                ]
            ),
            critical=False,
        )
        .sign(domain_key, hashes.SHA256())
    )

    # 使用根证书签名CSR
    domain_cert = (
        x509.CertificateBuilder()
        .subject_name(csr.subject)
        .issuer_name(cert.subject)
        .public_key(csr.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now())
        .not_valid_after(
            # 证书有效期为1年
            datetime.now()
            + timedelta(days=365)
        )
        .add_extension(
            x509.SubjectAlternativeName(
                [
                    x509.DNSName(DOMAIN),
                ]
            ),
            critical=False,
        )
        .sign(key, hashes.SHA256())
    )

    # 证书和密钥写入文件
    with open("domain_cert.pem", "wb") as f:
        f.write(domain_cert.public_bytes(Encoding.PEM))
    with open("domain_key.pem", "wb") as f:
        f.write(
            domain_key.private_bytes(
                Encoding.PEM, PrivateFormat.TraditionalOpenSSL, NoEncryption()
            )
        )
    # 安装根证书
    print("安装根证书...")
    subprocess.check_call(["certutil", "-addstore", "-f", "Root", "root_ca.pem"])
    print("配置Hosts...")
    
    # 读取现有 hosts 文件内容
    if os.path.exists(HOSTS_FILE):
        with open(HOSTS_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        print("已存在Hosts文件")
    else:
        lines = []
        print("Hosts文件不存在，将创建新文件")
    
    # 检查是否已存在该域名配置
    domain_line = f"127.0.0.1 {DOMAIN}\n"
    if not any(DOMAIN in line for line in lines):
        lines.append(domain_line)
        print(f"已添加域名配置: {DOMAIN}")
    else:
        print(f"域名配置已存在: {DOMAIN}")
    
    # 写入文件
    with open(HOSTS_FILE, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print("初始化完成！")
    print(" ")
    # use colorama Fore for red text
    from colorama import Fore, Style
    print(Fore.RED + "请手动点击 启动登录代理" + Style.RESET_ALL)
    print(" ")
    safe_input("回车退出...")

if __name__ == "__main__":
    main()
