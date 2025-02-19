import shutil

from bentoctl.deployment_config import DeploymentConfig
from bentoctl.operator import get_local_operator_registry

local_operator_registry = get_local_operator_registry()


def deploy_deployment(deployment_spec_path):
    deployment_resource = DeploymentConfig.from_file(deployment_spec_path)
    deployable_path = deployment_resource.operator.deploy(
        bento_path=deployment_resource.bento_path,
        deployment_name=deployment_resource.deployment_name,
        deployment_spec=deployment_resource.operator_spec,
    )
    # remove the deployable
    if deployable_path is not None:
        shutil.rmtree(deployable_path)


def update_deployment(deployment_spec_path):
    deployment_resource = DeploymentConfig.from_file(deployment_spec_path)
    deployable_path = deployment_resource.operator.update(
        bento_path=deployment_resource.bento_path,
        deployment_name=deployment_resource.deployment_name,
        deployment_spec=deployment_resource.operator_spec,
    )
    if deployable_path is not None:
        shutil.rmtree(deployable_path)


def describe_deployment(deployment_spec_path):
    deployment_resource = DeploymentConfig.from_file(deployment_spec_path)
    return deployment_resource.operator.describe(
        deployment_name=deployment_resource.deployment_name,
        deployment_spec=deployment_resource.operator_spec,
    )


def delete_deployment(deployment_spec_path):
    deployment_resource = DeploymentConfig.from_file(deployment_spec_path)
    deployment_resource.operator.delete(
        deployment_name=deployment_resource.deployment_name,
        deployment_spec=deployment_resource.operator_spec,
    )
    return deployment_resource.deployment_name
