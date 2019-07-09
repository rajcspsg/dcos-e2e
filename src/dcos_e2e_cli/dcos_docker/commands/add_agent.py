import click

from pathlib import Path
from dcos_e2e.cluster import Cluster
from dcos_e2e.backends import Docker
from dcos_e2e_cli.common.options import (
    existing_cluster_id_option
)
from dcos_e2e.docker_storage_drivers import DockerStorageDriver
from ._docker_version import docker_version_option
from ._linux_distribution import linux_distribution_option

from ._common import (
    CLUSTER_ID_LABEL_KEY,
    NODE_TYPE_AGENT_LABEL_VALUE,
    NODE_TYPE_LABEL_KEY,
    NODE_TYPE_MASTER_LABEL_VALUE,
    NODE_TYPE_PUBLIC_AGENT_LABEL_VALUE,
    WORKSPACE_DIR_LABEL_KEY,
)

from dcos_e2e.node import Transport
from docker.models.networks import Network

@click.command()
@existing_cluster_id_option
@AGENT_VOLUME_OPTION
@docker_version_option
@linux_distribution_option
@docker_storage_driver_option
@workspace_dir_option
@docker_network_option
@node_transport_option
@one_master_host_port_map_option
@click.pass_context
def add_agent(custom_volume: List[Mount],
              cluster_id: str,
              custom_agent_volume: List[Mount],
              docker_version: DockerVersion,
              linux_distribution: Distribution,
              docker_storage_driver: Optional[DockerStorageDriver],
              workspace_dir: Path,
              transport: Transport,
              network: Network,
              one_master_host_port_map: Dict[str, int],
              mount_sys_fs_cgroup: bool
            ):
    
    # This is useful for some people to identify containers.
    container_name_prefix = Docker().container_name_prefix + '-' + cluster_id
     
    cluster_backend = cluster_backend = Docker(
        container_name_prefix=container_name_prefix,
        custom_container_mounts=custom_volume,
        custom_master_mounts=[],
        custom_agent_mounts=custom_agent_volume,
        custom_public_agent_mounts=[],
        linux_distribution=linux_distribution,
        docker_version=docker_version,
        storage_driver=docker_storage_driver,
        docker_container_labels={
            CLUSTER_ID_LABEL_KEY: cluster_id,
            WORKSPACE_DIR_LABEL_KEY: str(workspace_dir),
        },
        docker_master_labels={
            NODE_TYPE_LABEL_KEY: NODE_TYPE_MASTER_LABEL_VALUE,
        },
        docker_agent_labels={NODE_TYPE_LABEL_KEY: NODE_TYPE_AGENT_LABEL_VALUE},
        docker_public_agent_labels={
            NODE_TYPE_LABEL_KEY: NODE_TYPE_PUBLIC_AGENT_LABEL_VALUE,
        },
        workspace_dir=workspace_dir,
        transport=transport,
        network=network,
        one_master_host_port_map=one_master_host_port_map,
        mount_sys_fs_cgroup=mount_sys_fs_cgroup,
    )
    
    new_cluster = Cluster(cluster_backend=cluster_backend, masters=0, public_agents=0, agents=1)
    #(agent, ) = new_cluster.agents
    #agent.install_dcos_from_path(dcos_installer=dcos_installer,
    #                              dcos_config=dcos_config,
    #                              ip_detect_path=ip_detect_path,
    #                              role=role, files_to_copy_to_genconf_dir=files_to_copy_to_genconf_dir,
    #                              user=user,
    #                              output=output,
    #                              transport=transport)
    
    
    print("Hello")
    
    
# def install_dcos_from_path(
#         self,
#         dcos_installer: Path,
#         dcos_config: Dict[str, Any],
#         ip_detect_path: Path,
#         role: Role,
#         files_to_copy_to_genconf_dir: Iterable[Tuple[Path, Path]] = (),
#         user: Optional[str] = None,
#         output: Output = Output.CAPTURE,
#         transport: Optional[Transport] = None,
#     ) -> None: