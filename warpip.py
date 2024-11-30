import ipaddress
import platform
import subprocess
import os
import datetime

# رنج‌های IPv4 و IPv6
warp_cidr_ipv4 = [
    '162.159.192.0/24',
    '162.159.193.0/24',
    '162.159.195.0/24',
    '162.159.204.0/24',
    '188.114.96.0/24',
    '188.114.97.0/24',
    '188.114.98.0/24',
    '188.114.99.0/24'
]

warp_cidr_ipv6 = [
    '2606:4700:d1::/64',
    '2606:4700:d0::/64'
]

script_directory = os.path.dirname(__file__)
ip_txt_path = os.path.join(script_directory, 'ip.txt')
result_path = os.path.join(script_directory, 'result.csv')
export_directory = os.path.join(script_directory, 'export')

# تابع ایجاد IP برای IPv4
def create_ips_ipv4():
    total_ips_needed = 10
    c = 0
    with open(ip_txt_path, 'w') as file:
        for cidr in warp_cidr_ipv4:
            ip_addresses = list(ipaddress.IPv4Network(cidr).hosts())
            for addr in ip_addresses:
                c += 1
                file.write(str(addr))
                if c != total_ips_needed:
                    file.write('\n')
                else:
                    return

# تابع ایجاد IP برای IPv6
def create_ips_ipv6():
    total_ips_needed = 10
    c = 0
    with open(ip_txt_path, 'w') as file:
        for cidr in warp_cidr_ipv6:
            ip_addresses = list(ipaddress.IPv6Network(cidr).hosts())
            for addr in ip_addresses:
                c += 1
                file.write(str(addr))
                if c != total_ips_needed:
                    file.write('\n')
                else:
                    return

# بررسی وجود فایل ip.txt
if os.path.isfile(ip_txt_path):
    print("ip.txt exists.")
else:
    print('Creating ip.txt File.')
    create_ips_ipv4()
    create_ips_ipv6()
    print('ip.txt File Created Successfully!')

# تابع شناسایی معماری سیستم
def arch_suffix():
    machine = platform.machine().lower()
    if machine.startswith('i386') or machine.startswith('i686'):
        return '386'
    elif machine.startswith(('x86_64', 'amd64')):
        return 'amd64'
    elif machine.startswith(('armv8', 'arm64', 'aarch64')):
        return 'arm64'
    elif machine.startswith('s390x'):
        return 's390x'
    else:
        raise ValueError("Unsupported CPU architecture")

arch = arch_suffix()

print("Fetch warp program...")
url = f"https://gitlab.com/Misaka-blog/warp-script/-/raw/main/files/warp-yxip/warp-linux-{arch}"

# دانلود و نصب warp
subprocess.run(["wget", url, "-O", "warp"])
os.chmod("warp", 0o755)

# اجرای warp برای اسکن IPها
command = ["./warp"]
print("Scanning ips...")
process = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# بررسی نتیجه اجرای برنامه warp
if process.returncode != 0:
    print(f"Error: Warp execution failed. {process.stderr.decode()}")
else:
    print("Warp executed successfully.")

    # ذخیره خروجی اسکن در result.csv
    with open(result_path, 'wb') as f:
        f.write(process.stdout)

# تابع پردازش فایل result.csv
def warp_ip():
    creation_time = os.path.getctime(result_path)
    formatted_time = datetime.datetime.fromtimestamp(creation_time).strftime("%Y-%m-%d %H:%M:%S")
    config_prefixes = ''  
    with open(result_path, 'r') as csv_file:
        next(csv_file)  # Skip header
        for line in csv_file:
            ip = line.split(',')[0]
            config_prefixes += f'{ip}\n'
    return config_prefixes, formatted_time

# استخراج آدرس‌ها از result.csv
configs = warp_ip()[0]

# ذخیره آدرس‌ها در فایل export
os.makedirs(export_directory, exist_ok=True)
export_file_path = os.path.join(export_directory, 'warp-ip')
with open(export_file_path, 'w') as op:
    op.write(configs)

# حذف فایل‌های موقت
os.remove(ip_txt_path)
os.remove(result_path)
os.remove("warp")
