import bcrypt

def hash_password(password):
    # Convert password to bytes if it's a string
    if isinstance(password, str):
        password = password.encode('utf-8')
    
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password, salt)
    return hashed.decode('utf-8')  # Convert back to string for storage

# Usage
# hashed = hash_password('myPassword123')
# print('Hashed password:', hashed)

def check_password(password, hashed):
    # Convert both to bytes if they're strings
    if isinstance(password, str):
        password = password.encode('utf-8')
    if isinstance(hashed, str):
        hashed = hashed.encode('utf-8')
    
    return bcrypt.checkpw(password, hashed)

# Usage
# stored_hash = hashed  # From the previous example
# if check_password('myPassword123', stored_hash):
#     print('Password correct!')
# else:
#     print('Password incorrect!')