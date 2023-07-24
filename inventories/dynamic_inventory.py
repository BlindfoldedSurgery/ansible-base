#!/usr/bin/env python3

import json
import os
import sys

from collections import defaultdict

import requests
from terrasnek.api import TFC, TFCStateVersions


def flatten(l):
    return [item for sublist in l for item in sublist]


def find_server_instances(tfstate: dict) -> list[dict]:
    return flatten([
        item["instances"]
        for item
        in tfstate["resources"]
        if item["type"] == "hcloud_server"
    ])


def find_loadbalancer_resource(tfstate: dict) -> dict:
    return [
        item
        for item
        in tfstate["resources"]
        if item["type"] == "hcloud_load_balancer_network"
    ][0]


def retrieve_terraform_file(api, organization: str, workspace_id: str):
    api.set_org(organization)
    current_state_information = api.state_versions.get_current(workspace_id)

    tfstate_url = current_state_information["data"]["attributes"]["hosted-state-download-url"]
    return requests.get(tfstate_url).json()


def main(token: str):
    api = TFC(token, url="https://app.terraform.io")
    tfstate = retrieve_terraform_file(api, "torbencarstens", "ws-KwnGnQoVuwnpUH1d")

    out = defaultdict(dict)
    out["master"] = defaultdict(dict)
    out["master"]["hosts"] = []
    out["worker"] = defaultdict(dict)
    out["worker"]["hosts"] = []
    out["_meta"] = defaultdict(dict)
    out["_meta"]["hostvars"] = defaultdict(lambda: defaultdict(dict))

    for instance in find_server_instances(tfstate):
        name = instance["attributes"]["name"].split("-", maxsplit=1)[1].replace("-", "_")
        external_ipv4 = instance["attributes"]["ipv4_address"]
        is_master = instance["attributes"]["labels"].get("master", "false") == "true"

        category_key = "master" if is_master else "worker"

        out[category_key]["hosts"].append(name)
        out["_meta"]["hostvars"][name]["ansible_host"] = external_ipv4

    out["loadbalancer"]["children"] = ["loadbalancer_external", "loadbalancer_internal"]
    out["loadbalancer_external"]["hosts"] = [tfstate["outputs"]["ipv4"]["value"]]
    lb_resource = find_loadbalancer_resource(tfstate)
    out["loadbalancer_internal"]["hosts"] = [lb_resource["instances"][0]["attributes"]["ip"]]

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    token = os.getenv("TFC_TOKEN")
    main(token)
