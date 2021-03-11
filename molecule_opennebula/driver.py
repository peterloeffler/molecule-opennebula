import os
from molecule import logger
from molecule.api import Driver

from molecule import util

LOG = logger.get_logger(__name__)


class OpenNebula(Driver):
    """
    The class responsible for managing `OpenNebula`_ instances. `OpenNebula`_
    is ``not`` the default driver used in Molecule.

    Molecule leverages Ansible's one modules, by mapping variables
    from ``molecule.yml`` into ``create.yml`` and ``destroy.yml``.

    .. code-block:: yaml

        driver:
          name: opennebula
        platforms:
          - name: instance

    .. code-block:: bash

        $ pip install 'molecule-opennebula'

    Change the options passed to the ssh client.

    .. code-block:: yaml

        driver:
          name: opennebula
          ssh_connection_options:
            - '-o ControlPath=~/.ansible/cp/%r@%h-%p'

    .. important::

        Molecule does not merge lists, when overriding the developer must
        provide all options.

    Provide a list of files Molecule will preserve, relative to the scenario
    ephemeral directory, after any ``destroy`` subcommand execution.

    .. code-block:: yaml

        driver:
          name: opennebula
          safe_files:
            - foo
    """  # noqa

    def __init__(self, config=None):
        super(OpenNebula, self).__init__(config)
        self._name = "opennebula"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def login_cmd_template(self):
        connection_options = " ".join(self.ssh_connection_options)

        return (
            "ssh {{address}} "
            "{}"
        ).format(connection_options)

    @property
    def default_safe_files(self):
        return [self.instance_config]

    @property
    def default_ssh_connection_options(self):
        return self._get_ssh_connection_options()

    def login_options(self, instance_name):
        d = {"instance": instance_name}

        return util.merge_dicts(d, self._get_instance_config(instance_name))

    def ansible_connection_options(self, instance_name):
        try:
            d = self._get_instance_config(instance_name)

            return {
                "ansible_host": d["address"],
                "vm_id": d["vm_id"],
                "connection": "ssh",
                "ansible_ssh_common_args": " ".join(self.ssh_connection_options),
            }
        except StopIteration:
            return {}
        except IOError:
            # Instance has yet to be provisioned , therefore the
            # instance_config is not on disk.
            return {}

    def _get_instance_config(self, instance_name):
        instance_config_dict = util.safe_load_file(self._config.driver.instance_config)

        return next(
            item for item in instance_config_dict if item["instance"] == instance_name + "-" + item["vm_id"]
        )

    def sanity_checks(self):
        # FIXME(decentral1se): Implement sanity checks
        pass

    def template_dir(self):
        """Return path to its own cookiecutterm templates. It is used by init
        command in order to figure out where to load the templates from.
        """
        return os.path.join(os.path.dirname(__file__), "cookiecutter")
