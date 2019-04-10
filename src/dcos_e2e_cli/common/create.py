"""
Tools for creating DC/OS clusters.
"""

import sys
import textwrap
from pathlib import Path
from subprocess import CalledProcessError
from typing import Any, Dict, Optional

import click
import halo
from passlib.hash import sha512_crypt

from dcos_e2e.base_classes import ClusterBackend
from dcos_e2e.cluster import Cluster
from dcos_e2e_cli._vendor.dcos_installer_tools import DCOSVariant

from .credentials import DEFAULT_SUPERUSER_PASSWORD, DEFAULT_SUPERUSER_USERNAME


def create_cluster(
    cluster_backend: ClusterBackend,
    masters: int,
    agents: int,
    public_agents: int,
    doctor_message: str,
) -> Cluster:
    """
    Create a cluster.
    """
    spinner = halo.Halo(enabled=sys.stdout.isatty())
    spinner.start(text='Creating cluster')
    try:
        cluster = Cluster(
            cluster_backend=cluster_backend,
            masters=masters,
            agents=agents,
            public_agents=public_agents,
        )
    except CalledProcessError as exc:
        spinner.stop()
        click.echo('Error creating cluster.', err=True)
        click.echo(click.style('Full error:', fg='yellow'))
        click.echo(click.style(textwrap.indent(str(exc), '  '), fg='yellow'))
        click.echo(doctor_message, err=True)

        sys.exit(exc.returncode)

    spinner.succeed()
    return cluster


def get_config(
    cluster: Cluster,
    extra_config: Dict[str, Any],
    dcos_variant: DCOSVariant,
    security_mode: Optional[str],
    license_key: Optional[str],
) -> Dict[str, Any]:
    """
    Get a DC/OS configuration to use for the given cluster.
    """
    is_enterprise = bool(dcos_variant == DCOSVariant.ENTERPRISE)

    if is_enterprise:
        superuser_username = DEFAULT_SUPERUSER_USERNAME
        superuser_password = DEFAULT_SUPERUSER_PASSWORD

        enterprise_extra_config = {
            'superuser_username': superuser_username,
            'superuser_password_hash': sha512_crypt.hash(superuser_password),
            'fault_domain_enabled': False,
        }
        if license_key is not None:
            key_contents = Path(license_key).read_text()
            enterprise_extra_config['license_key_contents'] = key_contents

        extra_config = {**enterprise_extra_config, **extra_config}
        if security_mode is not None:
            extra_config['security'] = security_mode

    dcos_config = {
        **cluster.base_config,
        **extra_config,
    }

    return dcos_config
