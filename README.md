# ansible-base

## run a playbook

example to run everything (`plays/main.yml`) (with pre-existing `.vault-pass` file):

`ansible-playbook -i inventories/dynamic_inventory.py -i inventories/server_inventory plays/main.yml --vault-password-file .vault-pass`


## vault

create a new encrypted file:

`ansible-vault create --vault-id base@prompt inventories/group_vars/{{ group }}/{{ filename }}.yml`
