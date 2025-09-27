import glob
import os
import json
import sys
from enum import Enum

def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <package> <version> <env: r,s,t,p>")
        sys.exit(1)

    class ServerEnvironment(Enum):
        r = 'rese'
        t = 'test'
        s = 'syst'
        p = 'prod'

    rpm = sys.argv[1]
    rpm_version = sys.argv[2]
    env = sys.argv[3]

    if env not in ServerEnvironment.__members__:
        print(f"Invalid environment '{env}'. Use one of: r, s, t, p")
        sys.exit(1)

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
