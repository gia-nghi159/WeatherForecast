output "public_ip" {
  description = "Public IP address of the K3s server"
  value       = oci_core_instance.k3s_server.public_ip
}

output "ssh_command" {
  description = "Command to SSH into the K3s instance"
  value       = "ssh ubuntu@${oci_core_instance.k3s_server.public_ip}"
}

output "get_kubeconfig_command" {
  description = "Command to download kubeconfig to your local machine"
  value       = "scp ubuntu@${oci_core_instance.k3s_server.public_ip}:/etc/rancher/k3s/k3s.yaml ~/.kube/config-oci && sed -i '' 's/127.0.0.1/${oci_core_instance.k3s_server.public_ip}/g' ~/.kube/config-oci"
}
