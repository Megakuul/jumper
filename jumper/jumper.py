from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from mypy_boto3_iam import IAMClient
    from mypy_boto3_sts import STSClient


class Client:
    stack: list[tuple[IAMClient, STSClient]]

    def __init__(self):
        self.stack = []
        self.stack = [(boto3.client("iam"), boto3.client("sts"))]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, _):
        self.stack[-1][0].close()
        self.stack[-1][1].close()
        if exc_type and exc_type is not KeyboardInterrupt:
            print(f"ERROR: {exc_value}")
        return True

    def Top(self) -> str:
        result = self.stack[-1][1].get_caller_identity()
        blocks = result["Arn"].split("/")
        return blocks[len(blocks) - 1]

    def Autocomplete(self) -> list[str]:
        result = self.stack[-1][0].list_roles()
        roles = result.get("Roles")
        output = []
        for role in roles:
            output.append(role["RoleName"])
        return output

    def List(self) -> str:
        result = self.stack[-1][0].list_roles()
        roles = result.get("Roles")
        output = ""
        for role in roles:
            output += f"- {role.get('RoleName')}\n"
        return output

    def Pop(self) -> str:
        if len(self.stack) > 1:
            self.stack.pop()
        return ""

    def Push(self, role: str) -> str:
        role_result = self.stack[-1][0].get_role(RoleName=role)
        assume_result = self.stack[-1][1].assume_role(
            RoleArn=role_result["Role"]["Arn"],
            RoleSessionName="jumper",
        )
        assume_credentials = assume_result["Credentials"]
        self.stack.append(
            (
                boto3.client(
                    "iam",
                    aws_access_key_id=assume_credentials["AccessKeyId"],
                    aws_secret_access_key=assume_credentials["SecretAccessKey"],
                    aws_session_token=assume_credentials["SessionToken"],
                ),
                boto3.client(
                    "sts",
                    aws_access_key_id=assume_credentials["AccessKeyId"],
                    aws_secret_access_key=assume_credentials["SecretAccessKey"],
                    aws_session_token=assume_credentials["SessionToken"],
                ),
            )
        )
        return ""

    def Info(self) -> str:
        identity_result = self.stack[-1][1].get_caller_identity()
        blocks = identity_result["Arn"].split(":")
        segments = blocks[len(blocks) - 1].split("/")

        output = ""
        if segments[0] == "assumed-role":
            role_result = self.stack[-1][0].get_role(RoleName=segments[1])
            role = role_result["Role"]
            output = ">> Assumed Role <<\n"
            output += f"Session: {segments[2]}\n"
            output += f"Role: {role['RoleName']}\n"

            allowed = []
            denied = []
            # using cascading statements like a real sysadmin ⚰️
            trustPolicy = role.get("AssumeRolePolicyDocument")
            if trustPolicy:
                stmts = trustPolicy["Statement"]
                for stmt in stmts:
                    actions = stmt["Action"]
                    match actions:
                        case str():
                            if "sts:AssumeRole" not in actions:
                                break
                        case list():
                            found = False
                            for action in actions:
                                if "sts:AssumeRole" in action:
                                    found = True
                            if not found:
                                break

                    if stmt["Effect"].lower() == "allow":
                        for typ, principals in stmt["Principal"].items():
                            match principals:
                                case str():
                                    allowed.append(f"{typ}: {principals} ✔️")
                                case list():
                                    for principal in principals:
                                        allowed.append(f"{typ}: {principal} ✔️")

                    elif stmt["Effect"].lower() == "deny":
                        for typ, principals in stmt["Principal"].items():
                            match principals:
                                case str():
                                    allowed.append(f"{typ}: {principals} ✖️")
                                case list():
                                    for principal in principals:
                                        allowed.append(f"{typ}: {principal} ✖️")

            if len(allowed) > 0:
                output += "Allowed:\n"
            for allow in allowed:
                output += f" - {allow}\n"
            if len(denied) > 0:
                output += "Denied:\n"
            for deny in denied:
                output += f" - {deny}\n"

            tags = role.get("Tags")
            if tags:
                output += "Tags:\n"
                for tag in tags:
                    output += f" - {tag['Key']}: {tag['Value']}\n"
        else:
            output = f">> [{segments[0]}] <<\n"

            output += f"UserId={identity_result['UserId']}\n"
            output += f"Account={identity_result['Account']}\n"
            output += f"Arn={identity_result['Arn']}\n"

        return output
