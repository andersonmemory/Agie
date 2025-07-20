import bcrypt

def check_password(password : bytes, author_id : int, moderators_list : list):
    for moderator_id in moderators_list:
          if author_id == moderator_id[0]:
                if bcrypt.checkpw(password, moderator_id[1]):  
                    return True
                else:
                      return False
    else:
          return False
    
def hash_password(password : str):
    
        byte_password = bytes(password, 'utf-8')

        salt = bcrypt.gensalt()

        hashed = bcrypt.hashpw(password=byte_password, salt=salt)

        return hashed