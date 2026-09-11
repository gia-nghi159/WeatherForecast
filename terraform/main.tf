data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

data "oci_core_images" "ubuntu_arm64" {
  compartment_id           = var.compartment_ocid
  operating_system         = "Canonical Ubuntu"
  operating_system_version = "24.04"
  shape                    = "VM.Standard.A1.Flex"
  sort_by                  = "TIMECREATED"
  sort_order               = "DESC"
}

# 1. Virtual Cloud Network (VCN)
resource "oci_core_vcn" "weather_vcn" {
  compartment_id = var.compartment_ocid
  cidr_blocks    = ["10.0.0.0/16"]
  display_name   = "weather-vcn"
  dns_label      = "weathervcn"
}

# 2. Internet Gateway
resource "oci_core_internet_gateway" "weather_ig" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.weather_vcn.id
  display_name   = "weather-ig"
  enabled        = true
}

# 3. Route Table
resource "oci_core_route_table" "weather_rt" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.weather_vcn.id
  display_name   = "weather-route-table"

  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.weather_ig.id
  }
}

# 4. Security List
resource "oci_core_security_list" "weather_sl" {
  compartment_id = var.compartment_ocid
  vcn_id         = oci_core_vcn.weather_vcn.id
  display_name   = "weather-security-list"

  # SSH (Port 22)
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 22
      max = 22
    }
  }

  # HTTP (Port 80)
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 80
      max = 80
    }
  }

  # HTTPS (Port 443)
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 443
      max = 443
    }
  }

  # Kubernetes API Server (Port 6443)
  ingress_security_rules {
    protocol = "6"
    source   = "0.0.0.0/0"
    tcp_options {
      min = 6443
      max = 6443
    }
  }

  # Allow all outbound traffic
  egress_security_rules {
    protocol    = "all"
    destination = "0.0.0.0/0"
  }
}

# 5. Public Subnet
resource "oci_core_subnet" "weather_subnet" {
  compartment_id    = var.compartment_ocid
  vcn_id            = oci_core_vcn.weather_vcn.id
  cidr_block        = "10.0.1.0/24"
  display_name      = "weather-public-subnet"
  route_table_id    = oci_core_route_table.weather_rt.id
  security_list_ids = [oci_core_security_list.weather_sl.id]
}

# 6. Always-Free Ampere A1 Compute Instance (4 OCPUs, 24 GB RAM)
resource "oci_core_instance" "k3s_server" {
  compartment_id      = var.compartment_ocid
  availability_domain = data.oci_identity_availability_domains.ads.availability_domains[0].name
  display_name        = "weather-k3s-server"
  shape               = "VM.Standard.A1.Flex"

  shape_config {
    ocpus         = 4
    memory_in_gbs = 24
  }

  source_details {
    source_type             = "image"
    source_id               = data.oci_core_images.ubuntu_arm64.images[0].id
    boot_volume_size_in_gbs = 100 # Within 200 GB Always Free limit
  }

  create_vnic_details {
    subnet_id        = oci_core_subnet.weather_subnet.id
    assign_public_ip = true
    display_name     = "weather-k3s-vnic"
  }

  metadata = {
    ssh_authorized_keys = var.ssh_public_key
    user_data = base64encode(<<-EOF
      #!/bin/bash
      set -e

      # 1. Disable Oracle Ubuntu OS-level iptables blocking to allow ingress
      iptables -F
      netfilter-persistent save || true

      # 2. Update packages and install curl
      apt-get update && apt-get install -y curl git

      # 3. Retrieve public IP
      PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com)

      # 4. Install K3s with external IP registered in TLS cert
      curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644 --tls-san $PUBLIC_IP" sh -

      # 5. Wait for K3s readiness
      until kubectl get nodes; do
        sleep 3
      done
    EOF
    )
  }
}
