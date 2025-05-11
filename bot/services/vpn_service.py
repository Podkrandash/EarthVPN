import os
import random
import string
import base64
import hashlib
from typing import Dict, Any, Tuple


class VPNService:
    """Сервис для генерации VPN конфигураций"""
    
    @staticmethod
    def generate_openvpn_config(user_id: int) -> Dict[str, Any]:
        """Генерирует OpenVPN конфигурацию для пользователя"""
        username = f"user_{user_id}"
        password = VPNService._generate_password(16)
        
        config = {
            "server": "vpn.earthvpn.com",
            "port": 1194,
            "protocol": "udp",
            "cipher": "AES-256-GCM",
            "username": username,
            "password": password
        }
        
        return config
    
    @staticmethod
    def generate_wireguard_config(user_id: int) -> Dict[str, Any]:
        """Генерирует WireGuard конфигурацию для пользователя"""
        # В реальном проекте здесь должна быть настоящая генерация ключей WireGuard
        # Это просто имитация для примера
        private_key, public_key = VPNService._generate_wireguard_keypair()
        
        config = {
            "private_key": private_key,
            "public_key": public_key,
            "endpoint": "wg.earthvpn.com:51820",
            "allowed_ips": "0.0.0.0/0, ::/0",
            "dns": "1.1.1.1, 8.8.8.8",
            "address": f"10.10.10.{random.randint(2, 254)}/24"
        }
        
        return config
    
    @staticmethod
    def _generate_password(length: int = 16) -> str:
        """Генерирует случайный пароль"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def _generate_wireguard_keypair() -> Tuple[str, str]:
        """Генерирует пару ключей WireGuard (приватный и публичный)"""
        # В реальном проекте нужно использовать библиотеку wireguard для генерации настоящих ключей
        # Это просто имитация для примера
        random_bytes = os.urandom(32)
        private_key = base64.b64encode(random_bytes).decode('utf-8')
        
        # Имитация генерации публичного ключа (не использовать в реальном проекте)
        hash_obj = hashlib.sha256(random_bytes)
        public_key_bytes = hash_obj.digest()
        public_key = base64.b64encode(public_key_bytes).decode('utf-8')
        
        return private_key, public_key
    
    @staticmethod
    def format_openvpn_config(config: Dict[str, Any]) -> str:
        """Форматирует конфигурационный файл OpenVPN"""
        return f"""client
dev tun
proto {config.get('protocol', 'udp')}
remote {config.get('server', 'vpn.earthvpn.com')} {config.get('port', 1194)}
resolv-retry infinite
nobind
persist-key
persist-tun
cipher {config.get('cipher', 'AES-256-GCM')}
auth SHA256
verb 3
remote-cert-tls server

<ca>
-----BEGIN CERTIFICATE-----
MIIEjzCCA3egAwIBAgIJAMRDmws0U7kEMA0GCSqGSIb3DQEBCwUAMIGLMQswCQYD
VQQGEwJVUzELMAkGA1UECBMCQ0ExFTATBgNVBAcTDFNhbkZyYW5jaXNjbzETMBEG
A1UEChMKRm9ydC1GdW5zdG9uMRgwFgYDVQQDEw9Gb3J0LUZ1bnN0b24gQ0ExDzAN
BgNVBCkTBnNlcnZlcjEYMBYGCSqGSIb3DQEJARYJbWVAZWFydGh2cG4wHhcNMTkw
NjA4MTQ0NTM4WhcNMjkwNjA1MTQ0NTM4WjCBizELMAkGA1UEBhMCVVMxCzAJBgNV
BAgTAkNBMRUwEwYDVQQHEwxTYW5GcmFuY2lzY28xEzARBgNVBAoTCkZvcnQtRnVu
c3RvbjEYMBYGA1UEAxMPRm9ydC1GdW5zdG9uIENBMQ8wDQYDVQQpEwZzZXJ2ZXIx
GDAWBgkqhkiG9w0BCQEWCWVhcnRodnBuQGFiY2RlZmcuY29tMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAxTcUXhd1IfnZ/9QwA/YdKawl9I8jn5qt3JGq
NK4iqwrSEO0FUNAe1Ug1RMc0QTvn4JLlG3oVj3BoQa4uRKNN4Jk4XFfXB9CyTckF
o6P4KLIrYMJ5i8n+EYL9GXQjzOJGE2R6HpZQvrQJKNpXnk31TZ4QAhq1K0qL5LD9
WHE1bZsd8m5m5QTjlYOzrD6X/Uo3/XqUa32+MnNpQI3lPS+MGJvxtTwtSebrjbyd
G0uz4JhEXZFT+9Ec5QVR+QgnLy0NVaXTe0nEm7FpR+0ooEXkBrHnmj2nhKJccEfC
A0jqsPx8iCo7FnwriSXxH2bIPEP9bJVcv9LFmLFTuBZI0eMeBQIDAQABo4H0MIHx
MB0GA1UdDgQWBBQw4Oc/5WkJpj8tYiI4oLcTWcb/ZDCBwQYDVR0jBIG5MIG2gBQw
4Oc/5WkJpj8tYiI4oLcTWcb/ZKGBkaSBjjCBizELMAkGA1UEBhMCVVMxCzAJBgNV
BAgTAkNBMRUwEwYDVQQHEwxTYW5GcmFuY2lzY28xEzARBgNVBAoTCkZvcnQtRnVu
c3RvbjEYMBYGA1UEAxMPRm9ydC1GdW5zdG9uIENBMQ8wDQYDVQQpEwZzZXJ2ZXIx
GDAWBgkqhkiG9w0BCQEWCWVhcnRodnBuQGFiY2RlZmcuY29tggkAxEObCzRTuQQw
DAYDVR0TBAUwAwEB/zANBgkqhkiG9w0BAQsFAAOCAQEAm+tHZ4GmapHs7K5TgFTh
jxYF0zRUBDG3cJGRe05Bk3H7Zupgwr4jYs8GtNY4YnvLRvsEJW+/MfJ0bV+CRsxI
DRzF3RJJpZ5J3tErP1yHXjb90UZlKmtLNiHxN8qU5bLEKGZBxFxKuwfE4QK1vnNA
I+fFuvwnG3oAXmQrzOXU/mjzYB7SQUPV9lrX5JBfVfUNuY0LMcCS0paGfRRCRyJd
M81kDmhdPy3HRqzIsTzHm0DB6F7+Kn+tx9UqQQJ0G7HD/A0SeX+YXVe+LFrM5Q7d
yDPgOB4BoI0N6WlUxYWYzA5w3RQZcb6ZXCUcm/S9h271f/TpeJRXTLQcHbJZx/4E
BQ==
-----END CERTIFICATE-----
</ca>

<auth-user-pass>
{config.get('username', 'user')}
{config.get('password', 'pass')}
</auth-user-pass>
"""
    
    @staticmethod
    def format_wireguard_config(config: Dict[str, Any]) -> str:
        """Форматирует конфигурационный файл WireGuard"""
        return f"""[Interface]
PrivateKey = {config.get('private_key', '')}
Address = {config.get('address', '10.10.10.2/24')}
DNS = {config.get('dns', '1.1.1.1, 8.8.8.8')}

[Peer]
PublicKey = {config.get('public_key', '')}
Endpoint = {config.get('endpoint', 'wg.earthvpn.com:51820')}
AllowedIPs = {config.get('allowed_ips', '0.0.0.0/0, ::/0')}
PersistentKeepalive = 25
""" 