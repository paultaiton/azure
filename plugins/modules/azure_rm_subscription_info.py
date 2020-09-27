#!/usr/bin/python
#
# Copyright (c) 2020 Paul Aiton, < paultaiton >
#
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: azure_rm_subscription_info

version_added: "1.2.0"

short_description: Get Azure Subscription facts

description:
    - Get facts for a specific subscription or all subscriptions.

options:
    name:
        description:
            - Limit results to a specific subscription.

extends_documentation_fragment:
    - azure.azcollection.azure

author:
    - Paul Aiton ( @paultaiton )
'''

EXAMPLES = '''
    - name: Get facts for one subscription
      azure_rm_subscription_info:
        name: mySubscription

    - name: Get facts for all subscriptions
      azure_rm_subscription_info:
'''

RETURN = '''
subscriptions:
    description:
        - List of subscription dicts.
    returned: always
    type: list
    contains:
        id:
            description:
                - subscription id.
            returned: always
            type: str
            sample: "/subscriptions/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx/"
        name:
            description:
                - Subscription name.
            returned: always
            type: str
            sample: foo
'''

try:
    from msrestazure.azure_exceptions import CloudError
except Exception:
    # This is handled in azure_rm_common
    pass

from ansible_collections.azure.azcollection.plugins.module_utils.azure_rm_common import AzureRMModuleBase


AZURE_OBJECT_CLASS = 'Subscription'


class AzureRMSubscriptionInfo(AzureRMModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(type='str'),
        )

        self.results = dict(
            changed=False,
            subscriptions=[]
        )

        self.name = None

        super(AzureRMSubscriptionInfo, self).__init__(self.module_arg_spec,
                                                       supports_tags=False,
                                                       facts_module=True)

    def exec_module(self, **kwargs):
        is_old_facts = self.module._name == 'azure_rm_resourcegroup_facts'
        if is_old_facts:
            self.module.deprecate("The 'azure_rm_resourcegroup_facts' module has been renamed to 'azure_rm_resourcegroup_info'", version=(2.9, ))

        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.name:
            result = self.get_item()
        else:
            result = self.list_items()

        if self.list_resources:
            for item in result:
                item['resources'] = self.list_by_rg(item['name'])

        if is_old_facts:
            self.results['ansible_facts']['azure_resourcegroups'] = result
        self.results['resourcegroups'] = result

        return self.results

    def get_item(self):
        self.log('Get properties for {0}'.format(self.name))
        item = None
        result = []

        try:
            item = self.rm_client.resource_groups.get(self.name)
        except CloudError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            result = [self.serialize_obj(item, AZURE_OBJECT_CLASS)]

        return result

    def list_items(self):
        self.log('List all items')
        try:
            response = self.rm_client.resource_groups.list()
        except CloudError as exc:
            self.fail("Failed to list all items - {0}".format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(self.serialize_obj(item, AZURE_OBJECT_CLASS))
        return results

    def list_by_rg(self, name):
        self.log('List resources under resource group')
        results = []
        try:
            response = self.rm_client.resources.list_by_resource_group(name)
            while True:
                results.append(response.next().as_dict())
        except StopIteration:
            pass
        except CloudError as exc:
            self.fail('Error when listing resources under resource group {0}: {1}'.format(name, exc.message or str(exc)))
        return results


def main():
    AzureRMSubscriptionInfo()


if __name__ == '__main__':
    main()
