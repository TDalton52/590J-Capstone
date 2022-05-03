import base64
import bwt

import time

# Dropbox components modified from https://raw.githubusercontent.com/dropbox/dropbox-sdk-python/main/example/oauth/commandline-oauth.py
import dropbox
from dropbox import DropboxOAuth2FlowNoRedirect

APP_KEY = "oi2xyrzkozto1wv"

def main():
    auth_flow = DropboxOAuth2FlowNoRedirect(APP_KEY, use_pkce=True, token_access_type="offline")

    authorize_url = auth_flow.start()
    print("1. Go to: " + authorize_url)
    print("2. Click \"Allow\" (you might have to log in first).")
    print("3. Copy the authorization code.")
    auth_code = input("Enter the authorization code here: ").strip()
    try:
        oauth_result = auth_flow.finish(auth_code)
    except Exception as e:
        print('Error obtaining token: %s' % (e,))
        exit(1)
    with dropbox.Dropbox(oauth2_refresh_token=oauth_result.refresh_token, app_key=APP_KEY) as dbx:
        while True:
            print("========")
            file_path = input("Enter file path: ")
            try:
                with open(file_path, "rb") as fil:
                    cmds = fil.read()
            except Exception as e:
                print("Unable to open file:", repr(e))
                continue
            dbx.check_and_refresh_access_token()
            # grab Dropbox token
            # XXX undocumented but eh
            access_token = dbx._oauth2_access_token

            cmds = bytes(f"token {access_token}\n", "utf8") + cmds
            encoded_file = base64.b64encode(cmds)
            print("Copy the below text into the pastebin:")
            print(bwt.bwt(encoded_file.decode("ascii")))
            input("Press enter when done")

            print("Sleeping for 120 seconds, ctrl-c once results appear")
            try:
                time.sleep(120)
            except KeyboardInterrupt:
                pass

            dbx.refresh_access_token()

if __name__ == "__main__":
    main()
