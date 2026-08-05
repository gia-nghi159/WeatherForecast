terraform {
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# 1. Tell Terraform to talk to local Minikube cluster
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "minikube"
}

provider "helm" {
  kubernetes {
    config_path    = "~/.kube/config"
    config_context = "minikube"
  }
}

# 2. Deploy Weather App using local Helm Chart
resource "helm_release" "weather_app" {
  name      = "my-weather-app"
  chart     = "../weather-chart"
  namespace = "default"
  
  # Ensure Redis is fully deployed before booting the API so the API can connect to it!
  depends_on = [helm_release.redis]
  
  set {
    name  = "resources.requests.cpu"
    value = "500m"
  }
  set {
    name  = "resources.limits.cpu"
    value = "1000m"
  }
  set {
    name  = "resources.limits.memory"
    value = "1024Mi"
  }
  set {
    name  = "resources.requests.memory"
    value = "256Mi"
  }
  set {
    name  = "autoscaling.targetCPUUtilizationPercentage"
    value = "70"
  }
}

# 3. Deploy Prometheus and Grafana (This downloads automatically from the web)
resource "helm_release" "prometheus" {
  name             = "prometheus"
  repository       = "https://prometheus-community.github.io/helm-charts"
  chart            = "kube-prometheus-stack"
  namespace        = "monitoring"
  create_namespace = true
  timeout          = 600

  set {
    name  = "alertmanager.enabled"
    value = "false"
  }
  set {
    name  = "kubeStateMetrics.enabled"
    value = "true"
  }
  set {
    name  = "nodeExporter.enabled"
    value = "true"
  }
  set {
    name  = "prometheus.prometheusSpec.resources.requests.memory"
    value = "256Mi"
  }
  set {
    name  = "grafana.ingress.enabled"
    value = "true"
  }
  set {
    name  = "grafana.ingress.hosts[0]"
    value = "grafana.local"
  }
}
resource "helm_release" "redis" {
  name       = "my-redis"
  repository = "oci://registry-1.docker.io/bitnamicharts"
  chart      = "redis"
  version    = "19.6.1"
  
  set {
    name  = "architecture"
    value = "standalone"
  }
  set {
    name  = "auth.enabled"
    value = "false"
  }
  set {
    name  = "image.tag"
    value = "latest"
  }
  set {
    name  = "master.resources.limits.cpu"
    value = "500m"
  }
  set {
    name  = "master.resources.limits.memory"
    value = "512Mi"
  }
}
