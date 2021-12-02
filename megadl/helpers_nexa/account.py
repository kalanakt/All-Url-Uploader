from mega import Mega
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config
from .mega_help import send_errors

# Mega user account credentials
email = Config.MEGA_EMAIL
password = Config.MEGA_PASSWORD

mega = Mega()

# Mega Account Login
def login_to_mega():
  try:
    if email and password is not None:
      # Login as Mega user account
      login_to_mega.m = mega.login(email, password)
      print(LOGGED_AS_USER)
    else:
      print(LOGIN_ERROR_TEXT)
      # Login as anonymous account
      login_to_mega.m = mega.login()
  except Exception as e:
    send_errors(e)
    exit()

# Mega client
print(PROCESS_TEXT.format("Trying to Log Into Mega.nz ..."))
login_to_mega()
m = login_to_mega.m
