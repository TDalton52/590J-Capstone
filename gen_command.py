import base64
import sys

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--new_url_slug", default=None)
    parser.add_argument("--file-list", action="append")
    parser.add_argument("--git-search", action="append")
    parser.add_argument("--upload", default=None)
    
    args_obj = parser.parse_args()
    cmd_actions = list()
    if args_obj.upload is not None:
        cmd_actions.append(f"upload {args_obj.upload}")
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
    print(encoded_file.decode("ascii"))

if __name__ == "__main__":
    main()
