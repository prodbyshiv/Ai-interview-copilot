# 1. user enters email + password
# 2. find the user's row by email, get the saved 60-character hash
# 3. extract the salt (characters 8 to 29)
# 4. entered password + that salt, scramble using the same cost (12)
# 5. compare the new result with the last 31 characters
#       match     → correct password
#       no match  → wrong password

import bcrypt

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))




