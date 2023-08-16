job "snmp-exporter" {
    datacenters = ["th3"]
    type = "service"

    update {
        stagger = "10s"
        max_parallel = 1
    }

    group "snmp-exporter" {
        count = 1

        constraint {
            attribute = "${node.unique.name}"
            value = "labs03"
        }

        network {
            mode = "cni/bridge"
            port "snmp" {
            }
        }

        service {
            port = "snmp"
            name = "snmp-exporter"
            tags = [
                "web-prive",
                "traefik.enable=true",
                "traefik.http.routers.snmp-exporter.rule=Host(`snmp-exporter.rd.nic.fr`)",
            ]
        }

        task "app" {
            driver = "docker"

            template {
                destination = "local/snmp.yml"
                data = file("./snmp-exporter/config/snmp.yml")
            }

            config {
                image = "quay.io/prometheus/snmp-exporter:v0.22.0"
                args = [
                    "--config.file='/local/snmp.yml'",
                    "--web.listen-address=:${NOMAD_PORT_snmp}",
                ]
                ports = ["snmp"]
            }

            


            resources {
                cpu = 100 # in MHz
                memory = 64 # in MB
            }
        }
    }
}