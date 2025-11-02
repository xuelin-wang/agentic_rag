variable "environment" {
  type    = string
  default = "dev"
}

variable "namespace" {
  type    = string
  default = "default"
}

variable "datacenters" {
  type    = list(string)
  default = ["dc1"]
}

variable "catalog_image" {
  type    = string
  default = "agentic-rag/catalog:dev"
}

variable "datasets_image" {
  type    = string
  default = "agentic-rag/datasets:dev"
}

variable "catalog_count" {
  type    = number
  default = 1
}

variable "datasets_count" {
  type    = number
  default = 1
}

variable "catalog_config_path" {
  type    = string
  default = "/app/catalog/deploy/configs/nomad.yaml"
}

variable "datasets_config_path" {
  type    = string
  default = "/app/datasets/deploy/configs/nomad.yaml"
}

job "agentic-rag" {
  datacenters = var.datacenters
  namespace   = var.namespace
  type        = "service"

  meta {
    environment = var.environment
  }

  group "catalog" {
    count = var.catalog_count

    network {
      mode = "bridge"
      port "http" {
        to = 9000
      }
    }

    service {
      name = "catalog-${var.environment}"
      port = "http"
      tags = ["traefik.enable=false"]
      provider = "consul"

      check {
        name     = "catalog-http"
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "catalog" {
      driver = "docker"

      config {
        image = var.catalog_image
        ports = ["http"]
      }

      env {
        APP_CONFIG_PATH = var.catalog_config_path
      }

      resources {
        cpu    = 500
        memory = 512
      }

      restart {
        attempts = 10
        interval = "5m"
        delay    = "15s"
        mode     = "delay"
      }
    }
  }

  group "datasets" {
    count = var.datasets_count

    network {
      mode = "bridge"
      port "http" {
        to = 8100
      }
    }

    service {
      name = "datasets-${var.environment}"
      port = "http"
      tags = ["traefik.enable=false"]
      provider = "consul"

      check {
        name     = "datasets-http"
        type     = "http"
        path     = "/"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "datasets" {
      driver = "docker"

      config {
        image = var.datasets_image
        ports = ["http"]
      }

      env {
        APP_CONFIG_PATH = var.datasets_config_path
      }

      template {
        data = <<-EOF
          {{- $service_name := printf "catalog-%s" (meta "environment") -}}
          {{- with service $service_name }}
          {{- $instance := index . 0 -}}
          CATALOG_BASE_URL=http://{{ $instance.Address }}:{{ $instance.Port }}
          {{- else }}
          CATALOG_BASE_URL=
          {{- end }}
        EOF
        destination = "secrets/catalog.env"
        env          = true
      }

      resources {
        cpu    = 500
        memory = 512
      }

      restart {
        attempts = 10
        interval = "5m"
        delay    = "15s"
        mode     = "delay"
      }
    }
  }
}
