from os import getlogin
from socket import gethostname
from win32security import LookupAccountName, ConvertSidToStringSid

class GetSID:
    def __init__(self):
        self.username = getlogin()
        self.domain_name = gethostname()

    def get_user_sid(self):
        try:
            sid, domain, account_type = LookupAccountName(self.domain_name, self.username)
            sid_string = ConvertSidToStringSid(sid)
            return sid_string

        except Exception as e:
            print(f"Error retrieving SID for {self.username}: {e}")