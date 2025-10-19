# add_user.py
from database import add_user
import sys

if len(sys.argv) != 3:
    print("Использование: python add_user.py email пароль")
    sys.exit(1)

email = sys.argv[1]
password = sys.argv[2]
add_user(email, password)
print(f"✅ Пользователь {email} добавлен в users.db")