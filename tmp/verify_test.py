import bcrypt
from werkzeug.security import check_password_hash

def verify_password(password: str, password_hash: str) -> bool:
    if not password or not password_hash:
        return False
    if password_hash.startswith('$2'):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        except Exception:
            return False
    try:
        return check_password_hash(password_hash, password)
    except Exception as e:
        print(f"Werkzeug Error: {e}")
        return False

# From full JSON
admin_hash = "scrypt:32768:8:1$PsdsKfZ89cdlhnJA$6d0e40e8f2bb949de249b69fb019e4bfc072cfbe37d74943babe94cfb8b94a0c54e35e1ee26d40e13efddc55eb84f503684a26ece505c279ad1e2135b7cb0a2f"
jdoe_hash = "scrypt:32768:8:1$FKHoYbYNPkqltpAM$b6a51c7799d3ed26e1a5e7d1e07ed86029fd12cb773fc9083aefb42cb89d0f1245c1ab47d7ae730af2c627b56e7c40e567c901304a0a3e5bf21959cfb69a769d"

print(f"Admin Correct (AdminPass123!): {verify_password('AdminPass123!', admin_hash)}")
print(f"Admin Correct (admin): {verify_password('admin', admin_hash)}")
print(f"Jdoe Correct (Password123!): {verify_password('Password123!', jdoe_hash)}")
print(f"Jdoe Correct (jdoe): {verify_password('jdoe', jdoe_hash)}")
