"""
Tools for waiting for a cluster.
"""

import click

from dcos_e2e_cli.common.options import (
    existing_cluster_id_option,
    superuser_password_option,
    superuser_username_option,
    verbosity_option,
)
from dcos_e2e_cli.common.utils import check_cluster_id_exists, command_path
from dcos_e2e_cli.common.wait import wait_for_dcos

from ._common import ClusterVMs, existing_cluster_ids
from .doctor import doctor


@click.command('wait')
@existing_cluster_id_option
@superuser_username_option
@superuser_password_option
@verbosity_option
@click.pass_context
def wait(
    ctx: click.core.Context,
    cluster_id: str,
    superuser_username: str,
    superuser_password: str,
) -> None:
    """
    Wait for DC/OS to start.
    """
    check_cluster_id_exists(
        new_cluster_id=cluster_id,
        existing_cluster_ids=existing_cluster_ids(),
    )
    cluster_vms = ClusterVMs(cluster_id=cluster_id)

    doctor_command_name = command_path(sibling_ctx=ctx, command=doctor)
    wait_for_dcos(
        cluster=cluster_vms.cluster,
        superuser_username=superuser_username,
        superuser_password=superuser_password,
        http_checks=True,
        doctor_command_name=doctor_command_name,
    )
