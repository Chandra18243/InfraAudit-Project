import argparse
import glob
import os
import json
import sys
from enum import Enum

class ServerEnvironment(Enum):
    r = 'rese'
    t = 'test'
    s = 'syst'
    p = 'prod'

def parse_args():
    parser = argparse.ArgumentParser(
        description="Check which servers have a specific RPM package and version installed."
    )
    parser.add_argument(
        "package",
        help="Name of the RPM package to check (e.g., bash)"
    )
    parser.add_argument(
        "version",
        help="Version of the RPM package to match (e.g., 5.1.8)"
    )
    parser.add_argument(
        "env",
        choices=ServerEnvironment.__members__.keys(),
        help="Environment code: r (rese), s (syst), t (test), p (prod)"
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
        print(f"File saved with list of servers: {output_file}")
    else:
        print(f"No servers found with package '{rpm}' version '{rpm_version}' in environment '{server_env}'.")

if __name__ == "__main__":
    main()
