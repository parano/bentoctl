from pathlib import Path

import click
import cloup
import yaml
from cloup import Section
from rich.pretty import pprint

from bentoctl.cli.interactive import deployment_spec_builder
from bentoctl.cli.operator_management import get_operator_management_subcommands
from bentoctl.cli.utils import BentoctlCommandGroup
from bentoctl.deployment_config import DeploymentConfig
from bentoctl.exceptions import BentoctlException
from bentoctl.deployment import (
    delete_deployment,
    deploy_deployment,
    describe_deployment,
    update_deployment,
)
from bentoctl.utils import console

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


class BentoctlSections:
    OPERATIONS = Section("Deployment Operations")
    OPERATORS = Section("Operator Management")
    INTERACTIVE = Section("Interactive Mode")


def save_deployment_spec(deployment_spec, save_path, filename="deployment_spec.yaml"):
    spec_path = Path(save_path, filename)

    if spec_path.exists():
        override = click.confirm(
            "deployment spec file exists! Should I override?", default=True
        )
        if override:
            spec_path.unlink()
        else:
            return spec_path

    with open(spec_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(deployment_spec, f, default_flow_style=False, sort_keys=False)

    return spec_path


@cloup.group(
    show_subcommand_aliases=True,
    context_settings=CONTEXT_SETTINGS,
    cls=BentoctlCommandGroup,
)
def bentoctl():
    """
    Bentoctl - Manages deployment of bentos to various cloud services.

    This tool helps you deploy your bentos to any cloud service you want. To start off
    you have to install some operators that you need to deploy to the cloud
    service of your choice, check out `bentoctl operator --help` for more details.
    You can run `bentoctl generate` to start the interactive deployment spec builder or
    check out the <link to deployment_spec doc> on how to write one yourself.
    """


@bentoctl.command(section=BentoctlSections.OPERATIONS)
@click.option(
    "--name", "-n", type=click.STRING, help="The name you want to give the deployment"
)
@click.option(
    "--operator", "-o", type=click.STRING, help="The operator of choice to deploy"
)
@click.option(
    "--bento",
    "-b",
    type=click.STRING,
    help="The path to bento bundle.",
)
@click.option(
    "--display-deployment-info",
    is_flag=True,
    help="Show deployment info",
)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="The path to the deployment spec file.",
)
def deploy(name, operator, bento, display_deployment_info, file):
    """
    Deploy a bento to cloud either in interactive mode or with deployment_spec.

    1. if interactive mode. call the interactive setup manager
    2. call deploy_bento
    3. display results from deploy_bento
    """
    try:
        if file is None:
            deployment_spec = deployment_spec_builder(bento, name, operator)
            deployment_config = DeploymentConfig(deployment_spec)
            deployment_spec_path = save_deployment_spec(
                deployment_config.deployment_spec, Path.cwd()
            )
            console.print(
                "[green]deployment spec generated to: "
                f"{deployment_spec_path.relative_to(Path.cwd())}[/]"
            )
            file = deployment_spec_path
        deploy_deployment(file)
        print("Successful deployment!")
        if display_deployment_info:
            info_json = describe(file)
            pprint(info_json)
    except BentoctlException as e:
        e.show()


@bentoctl.command(section=BentoctlSections.OPERATIONS)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="The path to the deployment spec file.",
    required=True,
)
def describe(file):
    """
    Shows the properties of the deployment given a deployment_spec.
    """
    info_json = describe_deployment(deployment_spec_path=file)
    pprint(info_json)


@bentoctl.command(section=BentoctlSections.OPERATIONS)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="The path to the deployment spec file.",
    required=True,
)
@click.option(
    "--display-deployment-info",
    is_flag=True,
    help="Show deployment info.",
)
def update(file, display_deployment_info):
    """
    Update the deployment given a deployment_spec.
    """
    update_deployment(deployment_spec_path=file)
    if display_deployment_info:
        info_json = describe(file)
        pprint(info_json)


@bentoctl.command(section=BentoctlSections.OPERATIONS)
@click.option(
    "--file",
    "-f",
    type=click.Path(exists=True),
    help="The path to the deployment spec file.",
    required=True,
)
@click.option(
    "--yes",
    "-y",
    "--assume-yes",
    is_flag=True,
    help="Skip confirmation prompt when deleting the deployment.",
)
def delete(file, yes):
    """
    Delete the deployment given a deployment_spec.
    """
    if yes or click.confirm("Are you sure you want to delete the deployment?"):
        delete_deployment(deployment_spec_path=file)
        deployment_name = delete_deployment(deployment_spec_path=file)
        click.echo(f"Deleted deployment - {deployment_name}!")


@bentoctl.command(section=BentoctlSections.INTERACTIVE)
def generate():
    """
    Start the interactive deployment spec builder file.
    """
    deployment_spec = deployment_spec_builder()
    deployment_spec_filname = console.input(
        "filename for deployment_spec [[b]deployment_spec.yaml[/]]: ",
    )
    if deployment_spec_filname == "":
        deployment_spec_filname = "deployment_spec.yaml"
    spec_path = save_deployment_spec(
        deployment_spec, Path.cwd(), deployment_spec_filname
    )
    console.print(
        f"[green]deployment spec generated to: {spec_path.relative_to(Path.cwd())}[/]"
    )


# subcommands
bentoctl.add_command(
    get_operator_management_subcommands(), section=BentoctlSections.OPERATORS
)
