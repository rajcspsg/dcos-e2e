"""
Tools for running arbitrary commands on cluster nodes.
"""

from pathlib import Path
from typing import Dict, Tuple

import click

from dcos_e2e.node import Transport
from dcos_e2e_cli.common.arguments import node_args_argument
from dcos_e2e_cli.common.nodes import get_nodes
from dcos_e2e_cli.common.options import (
    dcos_login_pw_option,
    dcos_login_uname_option,
    environment_variables_option,
    existing_cluster_id_option,
    sync_dir_run_option,
    test_env_run_option,
    verbosity_option,
)
from dcos_e2e_cli.common.run_command import run_command
from dcos_e2e_cli.common.sync import sync_code_to_masters
from dcos_e2e_cli.common.utils import check_cluster_id_exists, command_path

from ._common import ClusterInstances, existing_cluster_ids
from ._nodes import node_option
from ._options import aws_region_option
from .inspect_cluster import inspect_cluster


@click.command('run', context_settings=dict(ignore_unknown_options=True))
@existing_cluster_id_option
@node_args_argument
@dcos_login_uname_option
@dcos_login_pw_option
@sync_dir_run_option
@test_env_run_option
@environment_variables_option
@aws_region_option
@verbosity_option
@node_option
@click.pass_context
def run(
    ctx: click.core.Context,
    cluster_id: str,
    node_args: Tuple[str],
    sync_dir: Tuple[Path],
    dcos_login_uname: str,
    dcos_login_pw: str,
    test_env: bool,
    env: Dict[str, str],
    aws_region: str,
    node: Tuple[str],
) -> None:
    """
    Run an arbitrary command on a node or multiple nodes.

    To use special characters such as single quotes in your command, wrap the
    whole command in double quotes.
    """
    check_cluster_id_exists(
        new_cluster_id=cluster_id,
        existing_cluster_ids=existing_cluster_ids(aws_region=aws_region),
    )
    cluster_instances = ClusterInstances(
        cluster_id=cluster_id,
        aws_region=aws_region,
    )
    cluster = cluster_instances.cluster

    for dcos_checkout_dir in sync_dir:
        sync_code_to_masters(
            cluster=cluster,
            dcos_checkout_dir=dcos_checkout_dir,
            sudo=True,
        )

    inspect_command_name = command_path(
        sibling_ctx=ctx,
        command=inspect_cluster,
    )

    hosts = get_nodes(
        cluster_id=cluster_id,
        cluster_representation=cluster_instances,
        node_references=node,
        inspect_command_name=inspect_command_name,
    )

    for host in hosts:
        run_command(
            args=list(node_args),
            cluster=cluster,
            host=host,
            use_test_env=test_env,
            dcos_login_uname=dcos_login_uname,
            dcos_login_pw=dcos_login_pw,
            env=env,
            transport=Transport.SSH,
        )
