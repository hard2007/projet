class User:
    def __init__(self, user_id, username, role, full_name, email=None, group_name=None):
        self.user_id = user_id
        self.username = username
        self.role = role
        self.full_name = full_name
        self.email = email
        self.group_name = group_name
