#!/usr/bin/env python3

import argparse
import glob
import os
import json
from enum import Enum

class ServerEnvironment(Enum):
    r = 'rese'
    t = 'test'
    s = 'syst'
    p = 'prod'

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Search Ansible system inventory reports to check which servers have "
            "a specific RPM package and version installed.\n\n"
            "Example usage:\n"
            "  python3 script.py bash 5.1.8 r\n"
            "This will search for package 'bash' with version '5.1.8' in all reports "
            "from the 'rese' (R&D) environment."
        ),
        formatter_class=argparse.RawTextHelpFormatter  # Allows multiline descriptions
    )
    parser.add_argument(
        "package",
        help="Name of the RPM package to check (e.g., bash, glibc, openssl)"
    )
    parser.add_argument(
        "version",
        help="Version of the RPM package to match (e.g., 5.1.8, 2.28-227.el8)"
    )
    parser.add_argument(
        "env",
        choices=ServerEnvironment.__members__.keys(),
        help="Environment code:\n"
             "  r = rese (R&D)\n"
             "  s = syst (System)\n"
             "  t = test (Testing)\n"
             "  p = prod (Production)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    rpm = args.package
    rpm_version = args.version
    env = args.env
    server_env = ServerEnvironment[env].value

    json_files_dir = "/var/opt/ansible/reports"
    json_pattern = f"svli{env}c*.json"
    json_reports = glob.glob(os.path.join(json_files_dir, json_pattern))

    output_file = f"/tmp/{rpm}_{server_env}.txt"
    installed_servers = []

    for report in json_reports:
        if os.path.getsize(report) > 0:
            server_name = os.path.basename(report).split('.')[0]
            try:
                with open(report) as jf:
                    server_data = json.load(jf)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON file: {report}")
                continue

            packages = server_data.get('packages', {})
            if rpm in packages and isinstance(packages[rpm], list):
                if packages[rpm][0].get('version') == rpm_version:
                    installed_servers.append(server_name)

    if installed_servers:
        with open(output_file, 'w') as of:
            for server in installed_servers:
                of.write(f"{server}\n")
        print(f"✅ Found on {len(installed_servers)} servers. Saved to: {output_file}")
    else:
        print(f"❌ No servers found with package '{rpm}' version '{rpm_version}' in '{server_env}' environment.")

if __name__ == "__main__":
    main()
