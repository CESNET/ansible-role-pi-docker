# cesnet.pi_docker

Ansible role cesnet.pi_docker run and configure docker with privaciIDEA(https://www.privacyidea.org) and may run one or more instances of OAuth2 Proxies (https://oauth2-proxy.github.io/oauth2-proxy/).

## Role Variables
- **privacyidea_path** - Path to the main folder, where all files will be stored. Default value: `/opt/privacyidea`
- **privacyidea_dirs** - List of directories to be created.
- **privacyidea_files** - List of files to be copied to the machine. By default, no files will be copied to the machine.
- **privacyidea_templates** - List of templates to be created at the machine. By default, no files will be created from templates.
- **privacyidea_docker_compose_template** - Name of the docker-compose template to be used. By default, the default compose file will be used.
- **privacyidea_docker_image** - Docker image for privacyIDEA. Default value: `registry.gitlab.ics.muni.cz:443/perun-proxy-aai/containers/docker-privacyidea:latest`
- **privacyidea_oauthproxy_docker_image** - Docker image for OAuth2Proxy. Default value: `bitnami/oauth2-proxy:latest`
- **privacyidea_docker_network** - Docker network. Default value: `docker_network`
- **privacy_idea_config** - Configuration of privacyIDEA
- **privacyidea_oauthproxy_instances** - Configuration of OAuth2Proxy instances
- **privacyidea_cronjobs** - List of cronjobs to be added to the machine.

## Example playbook
```yaml
- hosts: all
  roles:
    - role: cesnet.pi_docker
      vars:
        privacyidea_path: "/opt/privacyidea"
        privacyidea_dirs:
          - { path: "{{ privacyidea_path }}" }
        privacyidea_files: []
        #Example: - {src: "example_file", dest: "example_file", mode: "0755", owner: "root", user: "group"}
        privacyidea_templates: []
        #Example: - {src: "example_file", dest: "example_file", mode: "0755", owner: "root", user: "group"}
        privacyidea_docker_compose_template: "default-docker-compose.yml"
        privacyidea_docker_image: "registry.gitlab.ics.muni.cz:443/perun-proxy-aai/containers/docker-privacyidea:latest"
        privacyidea_oauthproxy_docker_image: "bitnami/oauth2-proxy:latest"
        privacyidea_docker_network: "network"
        privacyidea_cronjobs: []
        #Example:
        #  - {
        #    name: "clear PI cache",
        #    job: "/usr/bin/docker exec privacy_idea /usr/local/bin/privacyidea-usercache-cleanup delete >> /dev/null 2>&1",
        #   minute: "10",
        #    hour: "10",
        #    }
        privacy_idea_config:
            environments: [] # https://privacyidea.readthedocs.io/en/latest/installation/system/inifile.html
            #Example: - "PI_LOGO=logo.svg"
            ports: []
            #Example: - "1234:1234"
            volumes: []
            #Example: - "/opt/privacyidea:/opt/privacyidea"
            log_tag: "privacy_idea"
            extra_hosts: []
            #Example: - "example_hostname:172.0.0.1"
        privacyidea_oauthproxy_instances:
            oauthproxy_name: # Docker will be started with this name
                environments: [] # https://oauth2-proxy.github.io/oauth2-proxy/docs/configuration/overview/
                #Example: - "OAUTH2_PROXY_PROVIDER=oidc"
                ports: []
                #Example: - "6432:6432"
                volumes: []
                #Example: - "/opt/privacyidea:/opt/privacyidea"
                log_tag: "oauthproxy_name"
                extra_hosts: []
                #Example: - "example_hostname:172.0.0.1"
```