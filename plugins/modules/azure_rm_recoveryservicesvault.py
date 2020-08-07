#!/usr/bin/python
#
# Copyright (c) 2019 Paul Aiton, <@paultaiton>
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_recoveryservicesvault
version_added: "2.10"
short_description: Manage Azure Recovery Services Vaults
description:
    - Create, modify or delete an Azure Recovery Services Vaults
    - To create, modify or delete Recovery Services Vaults, you must have access to Microsoft.RecoveryServices/Vaults/* actions.
    - Of the built-in roles, only Contributor is granted those actions.
options:
    name:
        description:
            - Name of the Recovery Services vault.
        type: str
        required: true
    resource_group:
        description:
            - Name of the resource group to use.
        required: true
        type: str
    state:
        description:
            - State of the vault
            - Use C(present) to create or update a vault and C(absent) to delete a vault.
        type: str
        default: present
        choices:
            - absent
            - present
extends_documentation_fragment:
    - azure.azcollection.azure

author:
    - Paul Aiton (@paultaiton)

'''

EXAMPLES = '''
'''

RETURN = '''
'''

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase
try:
    from msrestazure.azure_exceptions import CloudError
except ImportError:
    # This is handled in azure_rm_common
    pass


class AzureRMRecoveryServicesVault(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str', required=True),
            state=dict(type='str', default='present', choices=['present', 'absent']),
            resource_group=dict(type='str')
        )

        self.results = dict(
            changed=False,
            id=None
        )

        required_if = [
            ('state', 'present' )
        ]

        mutually_exclusive = [['resource_group', 'managed_resource_id']]

        self.name = None
        self.state = None
        self.level = None
        self.resource_group = None
        self.managed_resource_id = None

        super(AzureRMRecoveryServicesVault, self).__init__(self.module_arg_spec,
                                          supports_check_mode=True,
                                          required_if=required_if,
                                          mutually_exclusive=mutually_exclusive,
                                          supports_tags=True)

    def exec_module(self, **kwargs):

        for key in self.module_arg_spec.keys():
            setattr(self, key, kwargs[key])

        changed = False
        # construct scope id
        scope = self.get_scope()
        lock = self.get_lock(scope)
        if self.state == 'present':
            lock_level = getattr(self.lock_models.LockLevel, self.level)
            if not lock:
                changed = True
                lock = self.lock_models.ManagementLockObject(level=lock_level)
            elif lock.level != lock_level:
                self.log('Lock level changed')
                lock.level = lock_level
                changed = True
            if not self.check_mode:
                lock = self.create_or_update_lock(scope, lock)
                self.results['id'] = lock.id
        elif lock:
            changed = True
            if not self.check_mode:
                self.delete_lock(scope)
        self.results['changed'] = changed
        return self.results

    def delete_lock(self, scope):
        try:
            return self.lock_client.management_locks.delete_by_scope(scope, self.name)
        except CloudError as exc:
            self.fail('Error when deleting lock {0} for {1}: {2}'.format(self.name, scope, exc.message))

    def create_or_update_lock(self, scope, lock):
        try:
            return self.lock_client.management_locks.create_or_update_by_scope(scope, self.name, lock)
        except CloudError as exc:
            self.fail('Error when creating or updating lock {0} for {1}: {2}'.format(self.name, scope, exc.message))

    def get_lock(self, scope):
        try:
            return self.lock_client.management_locks.get_by_scope(scope, self.name)
        except CloudError as exc:
            if exc.status_code in [404]:
                return None
            self.fail('Error when getting lock {0} for {1}: {2}'.format(self.name, scope, exc.message))

    def get_scope(self):
        '''
        Get the resource scope of the lock management.
        '/subscriptions/{subscriptionId}' for subscriptions,
        '/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}' for resource groups,
        '/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/{namespace}/{resourceType}/{resourceName}' for resources.
        '''
        if self.managed_resource_id:
            return self.managed_resource_id
        elif self.resource_group:
            return '/subscriptions/{0}/resourcegroups/{1}'.format(self.subscription_id, self.resource_group)
        else:
            return '/subscriptions/{0}'.format(self.subscription_id)


def main():
    AzureRMRecoveryServicesVault()


if __name__ == '__main__':
    main()
