import bcrypt

print(bcrypt.hashpw(b"user31234", bcrypt.gensalt()).decode())