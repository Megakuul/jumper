from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient
    from mypy_boto3_sts import STSClient


class Client:
    iam: IAMClient
    sts: STSClient

    def __init__(self):
        self.iam = boto3.client("iam")
        self.sts = boto3.client("sts")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, _):
        if exc_type and exc_type is not KeyboardInterrupt:
            print(f"ERROR: {exc_value}")
        return True

    def List(self):
        result = self.iam.list_roles()
        roles = result.get("Roles")
        for role in roles:
            print(role.get("RoleName"))
