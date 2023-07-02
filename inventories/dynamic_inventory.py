#!/usr/bin/env python3

import json
import os
import sys

from collections import defaultdict

import requests
from terrasnek.api import TFC, TFCStateVersions


def retrieve_terraform_file(api, organization: str, workspace_id: str):
    api.set_org(organization)
    current_state_information = api.state_versions.get_current(workspace_id)

    tfstate_url = current_state_information["data"]["attributes"]["hosted-state-download-url"]
    return requests.get(tfstate_url).json()


def main(token: str):
    api = TFC(token, url="https://app.terraform.io")
    tfstate = retrieve_terraform_file(api, "torbencarstens", "ws-KwnGnQoVuwnpUH1d")

    print(json.dumps(tfstate))
    out = defaultdict(dict)
    out["worker"]["hosts"] = [ip for ip in tfstate["outputs"]["agent_ipv4"]["value"]]
    out["master"]["hosts"] = [ip for ip in tfstate["outputs"]["master_ipv4"]["value"]]
    out["loadbalancer"]["hosts"] = [tfstate["outputs"]["ipv4"]["value"]]

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    token = os.getenv("TFC_TOKEN")
    main(token)
