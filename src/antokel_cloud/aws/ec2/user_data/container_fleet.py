from __future__ import annotations

from typing import Optional, Literal

from .base import BaseUserData


class ContainerFleet(BaseUserData):
  """
  UserData that installs Docker + AWS CLI, logs into ECR, pulls an image,
  and runs a container in detached mode.

  Example:
    script = ec2.user_data.ContainerFleet(
      ecr='6695...amazonaws.com/penya-warmer',
      os='amazon_linux',
      env={'DEBUG': 'true'},
      cmd='python main.py --concurrency 5',
    )
  """

  def __init__(
    self,
    ecr: str,
    os: Literal[
      "amazon_linux",
      "debian",
      "ubuntu",
      "red_hat",
      "suse_linux",
      "windows",
      "macos",
    ] = "amazon_linux",
    env: Optional[dict[str, str]] = None,
    cmd: str = "",
    *,
    tag: str = "latest",
    include_aws_env: bool = True,
    ec2=None,
  ):
    super().__init__(ec2=ec2)
    self.ecr = ecr
    self.os = os
    self.env = env or {}
    self.cmd = cmd
    self.tag = tag
    self.include_aws_env = include_aws_env

  def _image(self) -> str:
    # If already includes a tag (':tag' after last '/'), keep it.
    last = self.ecr.rsplit("/", 1)[-1]
    if ":" in last:
      return self.ecr
    return f"{self.ecr}:{self.tag}"

  def render(self) -> str:
    creds = self._aws_creds()
    region = creds.region or ""
    access = creds.access_key or ""
    secret = creds.secret_key or ""

    # OS-level bootstrap
    if self.os == "amazon_linux" or self.os == "red_hat":
      install = "\n".join([
        "yum update -y",
        "yum install -y docker aws-cli",
        "service docker start",
        "usermod -a -G docker ec2-user",
      ])
    elif self.os in ("ubuntu", "debian"):
      install = "\n".join([
        "apt-get update -y",
        "apt-get install -y docker.io awscli",
        "systemctl enable docker",
        "systemctl start docker",
        "usermod -a -G docker ubuntu || true",
      ])
    else:
      raise ValueError(f"Unsupported OS for ContainerFleet user-data: {self.os}")

    image = self._image()
    registry = self._parse_ecr_registry(image)

    # docker run env flags
    run_env = dict(self.env)
    if self.include_aws_env:
      if creds.region:
        run_env.setdefault("AWS_REGION", creds.region)
      if creds.access_key:
        run_env.setdefault("AWS_ACCESS_KEY_ID", creds.access_key)
      if creds.secret_key:
        run_env.setdefault("AWS_SECRET_ACCESS_KEY", creds.secret_key)

    env_flags = ""
    if run_env:
      env_flags = " ".join([f"-e {self._shell_quote(k)}={self._shell_quote(v)}" for k, v in run_env.items()])

    # NOTE: We intentionally embed creds into the user-data per SDK requirement.
    # Users should strongly prefer IAM instance profiles in production.
    login_cmd = (
      f"AWS_REGION={self._shell_quote(region)} "
      f"AWS_ACCESS_KEY_ID={self._shell_quote(access)} "
      f"AWS_SECRET_ACCESS_KEY={self._shell_quote(secret)} "
      f"aws ecr get-login-password --region {self._shell_quote(region)}"
      f" | docker login --username AWS --password-stdin {self._shell_quote(registry)}"
    )

    # When cmd is empty we just run the image default CMD/ENTRYPOINT.
    # When cmd is provided, we clear the entrypoint to fully override the command.
    if self.cmd:
      entrypoint_flag = "--entrypoint ''"
      cmd_part = f" {self.cmd}"
    else:
      entrypoint_flag = ""
      cmd_part = ""
    docker_run = (
      f"docker run -d --restart=always {entrypoint_flag} {env_flags} {self._shell_quote(image)}{cmd_part}"
    ).strip()

    script = f"""\
#!/bin/bash
set -euo pipefail

{install}

# Authenticate to ECR and pull the image
su - ec2-user -c "{login_cmd}"
su - ec2-user -c "docker pull {self._shell_quote(image)}"

# Run the container in detached mode
su - ec2-user -c "{docker_run}"
"""
    return script