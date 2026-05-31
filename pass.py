import getpass

from passlib.hash import sha512_crypt

# Enter your desired password at the prompt
password = getpass.getpass()
# Generates the SHA-512 hash
hashed_password = sha512_crypt.hash(password)
print(f"username:{hashed_password}")
