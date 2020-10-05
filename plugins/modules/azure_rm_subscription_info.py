#!/usr/bin/python
#
# Copyright (c) 2020 Paul Aiton, < @paultaiton >
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
    id:
        description:
            - Limit results to a specific subscription by id.
            - Cannot be used together with name.
        aliases:
            - id
    name:
        description:
            - Limit results to a specific subscription by name.
            - Cannot be used together with id.
        aliases:
            - subscription_name
    all:
        description:
            - If true, will show all subscriptions.
            - If false will omit disabled subscriptions (default).
        default: False

extends_documentation_fragment:
    - azure.azcollection.azure

author:
    - Paul Aiton ( @paultaiton )
'''

EXAMPLES = '''
    - name: Get facts for one subscription
      azure_rm_subscription_info:
        id: 00000000-0000-0000-0000-000000000000

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
            description: Subscription fully qualified id.
            returned: always
            type: str
            sample: "/subscriptions/00000000-0000-0000-0000-000000000000"
        subscription_id:
            description: Subscription guid.
            returned: always
            type: str
            sample: "00000000-0000-0000-0000-000000000000"
        state:
            description: Subscription state.
            returned: always
            type: str
            sample: "'Enabled' or 'Disabled'"
        display_name:
            description: Subscription display name.
            returned: always
            type: str
            sample: foo
        tags:
            description: Tags assigned to resource group.
            returned: always
            type: dict
            sample: { "tag1": "value1", "tag2": "value2" }
        tenant_id:
            description: Subscription tenant id
            returned: always
            type: str
            sample: "00000000-0000-0000-0000-000000000000"
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
            id=dict(type='str'),
            all=dict(type='bool')
        )

        self.results = dict(
            changed=False,
            subscriptions=[]
        )

        self.name = None
        self.id = None
        self.all = False

        super(AzureRMSubscriptionInfo, self).__init__(self.module_arg_spec,
                                                       supports_tags=False,
                                                       facts_module=True)

    def exec_module(self, **kwargs):
        for key in self.module_arg_spec:
            setattr(self, key, kwargs[key])

        if self.id:
            result = self.get_item()
        else:
            result = self.list_items()

        return self.results

    def get_item(self):
        self.log('Get properties for {0}'.format(self.id))
        item = None
        result = []

        try:
            item = self.rm_client.subscription_client.get(self.id)
        except CloudError:
            pass

        if item and self.has_tags(item.tags, self.tags):
            result = [self.serialize_obj(item, AZURE_OBJECT_CLASS)]

        return result

    def list_items(self):
        self.log('List all items')
        try:
            response = self.rm_client.subscription_client.list()
        except CloudError as exc:
            self.fail("Failed to list all items - {0}".format(str(exc)))

        results = []
        for item in response:
            if self.has_tags(item.tags, self.tags):
                results.append(self.serialize_obj(item, AZURE_OBJECT_CLASS))
        return results

def main():
    AzureRMSubscriptionInfo()

if __name__ == '__main__':
    main()
