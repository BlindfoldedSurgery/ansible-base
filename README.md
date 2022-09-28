# ansible-base

## run a playbook

`ansible-playbook plays/{{ filename }}.yml -l {{ hosts }} -i inventories/{{ inventory }} --vault-id base@prompt`

example for github-runner (with pre-existing `.vault-pass` file):

`ansible-playbook plays/github-runner.yml -l pivpn -i inventories/pi_management_inventory --vault-password-file .vault-pass`


## vault

create a new encrypted file:

`ansible-vault create --vault-id base@prompt inventories/group_vars/{{ group }}/{{ filename }}.yml`
