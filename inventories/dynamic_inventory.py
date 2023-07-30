#!/usr/bin/env python3

import json
import os

from collections import defaultdict
from io import BytesIO, TextIOWrapper

import boto3
import requests
from botocore.config import Config


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


def retrieve_terraform_file(bucket_name: str, key: str, endpoint: str, region: str) -> dict:
    session = boto3.session.Session()
    s3 = session.client(
        service_name="s3",
        endpoint_url=endpoint,
        config=Config(
            region_name=region,
        ),
    )

    filename = "./terraform.tfstate"
    s3.download_file(bucket_name, key, filename)

    with open(filename) as f:
        return json.load(f)


def main():
    endpoint = "https://5487401ce26c58bc1fa7725833ede7ae.r2.cloudflarestorage.com"
    region = "us-east-1"
    bucket_name = "blindfoldedsurgery"
    key = "blindfoldedsurgery/BlindfoldedSurgery/terraform-github.state"
    tfstate = retrieve_terraform_file(bucket_name, key, endpoint, region)

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
    out["loadbalancer_external"]["hosts"] = [tfstate["outputs"]["loadbalancer_ipv4"]["value"]]
    lb_resource = find_loadbalancer_resource(tfstate)
    out["loadbalancer_internal"]["hosts"] = [lb_resource["instances"][0]["attributes"]["ip"]]

    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
