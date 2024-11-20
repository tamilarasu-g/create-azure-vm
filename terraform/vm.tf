resource "azurerm_virtual_network" "terraform_vnet" {
  name                = "terraform_vnet"
  address_space       = ["10.0.0.0/16"]
  location            = azurerm_resource_group.testing-group.location
  resource_group_name = azurerm_resource_group.testing-group.name
}

resource "azurerm_subnet" "terraform_subnet" {
  name                 = "terraform_subnet"
  resource_group_name  = azurerm_resource_group.testing-group.name
  virtual_network_name = azurerm_virtual_network.terraform_vnet.name
  address_prefixes     = ["10.0.2.0/24"]
}

resource "azurerm_public_ip" "terraform_pip" {
  name                = "terraform_public_ip"
  resource_group_name = azurerm_resource_group.testing-group.name
  location            = azurerm_resource_group.testing-group.location
  allocation_method   = "Static"
}



resource "azurerm_network_interface" "terraform_nic" {
  name                = "terraform_nic"
  location            = azurerm_resource_group.testing-group.location
  resource_group_name = azurerm_resource_group.testing-group.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.terraform_subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.terraform_pip.id
  }
}

resource "azurerm_network_security_group" "terraform-nsg" {
  name                = "terraform-nsg"
  location            = azurerm_resource_group.testing-group.location
  resource_group_name = azurerm_resource_group.testing-group.name

  security_rule {
    name                       = "allow-ssh"
    priority                   = "100"
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_subnet_network_security_group_association" "terraform-subnet-nsg-assoc" {
  subnet_id                 = azurerm_subnet.terraform_subnet.id
  network_security_group_id = azurerm_network_security_group.terraform-nsg.id
}


resource "azurerm_linux_virtual_machine" "terraform_vm" {
  name                  = "terraform-vm"
  resource_group_name   = azurerm_resource_group.testing-group.name
  location              = azurerm_resource_group.testing-group.location
  size                  = "Standard_B1s"
  admin_username        = "my-admin-user"
  network_interface_ids = [azurerm_network_interface.terraform_nic.id]

  admin_ssh_key {
    username   = "my-admin-user"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts"
    version   = "latest"
  }

}








