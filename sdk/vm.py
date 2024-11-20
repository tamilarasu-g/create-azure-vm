# Import the needed credential and management objects from the libraries.
import os

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

print(
    "Provisioning a virtual machine...some operations might take a \
minute or two."
)

# Acquire a credential object.
credential = DefaultAzureCredential()

# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]


# Step 1: Provision a resource group

# Obtain the management object for resources.
resource_client = ResourceManagementClient(credential, subscription_id)

RESOURCE_GROUP_NAME = "python-rg"
LOCATION = "centralindia"

# Provision the resource group.
rg_result = resource_client.resource_groups.create_or_update(
    RESOURCE_GROUP_NAME, {"location": LOCATION}
)

print(
    f"Provisioned resource group {rg_result.name} in the \
{rg_result.location} region"
)

# Step 2: provision a virtual network

# Network and IP address names
VNET_NAME = "python-vnet"
SUBNET_NAME = "python-subnet"
IP_NAME = "python-ip"
IP_CONFIG_NAME = "python-ip-config"
NIC_NAME = "python-nic"
NSG_NAME = "python-nsg"
SECURITY_RULE_NAME = "python-allow-ssh-rule"

# Obtain the management object for networks
network_client = NetworkManagementClient(credential, subscription_id)

# Provision the virtual network and wait for completion
poller = network_client.virtual_networks.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    {
        "location": LOCATION,
        "address_space": {"address_prefixes": ["10.0.0.0/16"]},
    },
)

vnet_result = poller.result()

print(
    f"Provisioned virtual network {vnet_result.name} with address \
prefixes {vnet_result.address_space.address_prefixes}"
)

# Step 3: Provision the subnet and wait for completion
poller = network_client.subnets.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VNET_NAME,
    SUBNET_NAME,
    {"address_prefix": "10.0.0.0/24"},
)
subnet_result = poller.result()

print(
    f"Provisioned virtual subnet {subnet_result.name} with address \
prefix {subnet_result.address_prefix}"
)

# Step 4: Provision an IP address and wait for completion
poller = network_client.public_ip_addresses.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    IP_NAME,
    {
        "location": LOCATION,
        "sku": {"name": "Standard"},
        "public_ip_allocation_method": "Static",
        "public_ip_address_version": "IPV4",
    },
)

ip_address_result = poller.result()

print(
    f"Provisioned public IP address {ip_address_result.name} \
with address {ip_address_result.ip_address}"
)

# Step 5 : Provision the Network Security Group
poller = network_client.network_security_groups.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NSG_NAME,
    {
        "location": LOCATION,
        "properties" : {
            "securityRules": [
                {
                    "name" : SECURITY_RULE_NAME,
                    "properties": {
                        "access": "Allow",
                        "destinationAddressPrefix": "*",
                        "destinationPortRange": "22",
                        "direction": "Inbound",
                        "priority": 100,
                        "protocol": "Tcp",
                        "sourceAddressPrefix": "*",
                        "sourcePortRange": "*",
                    }
                }
            ]
        }
    },
)

nsg_result = poller.result()

print(f"Provisioned network security group  {nsg_result.name}")


# Step 5: Provision the network interface client
poller = network_client.network_interfaces.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    NIC_NAME,
    {
        "location": LOCATION,
        "network_security_group": {
            "id" : nsg_result.id
        },
        "ip_configurations": [
            {
                "name": IP_CONFIG_NAME,
                "subnet": {"id": subnet_result.id},
                "public_ip_address": {"id": ip_address_result.id},
            }
        ],
    },
)

nic_result = poller.result()

print(f"Provisioned network interface client {nic_result.name}")

# Step 6: Provision the virtual machine

# Obtain the management object for virtual machines
compute_client = ComputeManagementClient(credential, subscription_id)

VM_NAME = "python-vm"
USERNAME = "azureuser"
PASSWORD = "Python@123456"

print(
    f"Provisioning virtual machine {VM_NAME}; this operation might \
take a few minutes."
)

poller = compute_client.virtual_machines.begin_create_or_update(
    RESOURCE_GROUP_NAME,
    VM_NAME,
    {
        "location": LOCATION,
        "storage_profile": {
            "image_reference": {
                "publisher": "Canonical",
                "offer": "ubuntu-24_04-lts",
                "sku": "server",
                "version": "latest",
            }
        },
        "hardware_profile": {"vm_size": "Standard_B1s"},
        "os_profile": {
            "computer_name": VM_NAME,
            "admin_username": USERNAME,
            "admin_password": PASSWORD,
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": nic_result.id,
                }
            ]
        },
    },
)

vm_result = poller.result()

print(f"Provisioned virtual machine {vm_result.name}")

