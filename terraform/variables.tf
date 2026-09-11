variable "tenancy_ocid" {
  description = "OCID of your Oracle Cloud Tenancy"
  type        = string
}

variable "user_ocid" {
  description = "OCID of your Oracle Cloud User"
  type        = string
}

variable "compartment_ocid" {
  description = "OCID of your Oracle Cloud Compartment"
  type        = string
}

variable "region" {
  description = "Oracle Cloud region (e.g. us-ashburn-1, us-phoenix-1, ap-singapore-1)"
  type        = string
  default     = "us-ashburn-1"
}

variable "fingerprint" {
  description = "Fingerprint of your OCI API Signing Key"
  type        = string
}

variable "private_key_path" {
  description = "Local path to your OCI API private key (e.g. ~/.oci/oci_api_key.pem)"
  type        = string
}

variable "ssh_public_key" {
  description = "Your SSH public key (e.g. ~/.ssh/id_rsa.pub or ~/.ssh/id_ed25519.pub)"
  type        = string
}
