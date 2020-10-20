# Wireguard CLI
Simple Wireguard user manipulation CLI

## Initial setup
Create ```/etc/wireguard``` structure like in example.folder:

	wg0/
		users/
		wg_head_template.txt
		wg_user_template.txt
	wg0.conf

Fill ``wg_head_template.txt`` with server setup, fill ``wg_user_template.txt``
with peer data (<PublicKey> and <IP> expand for each user).

## List users

	./wg_cli.py list


## Add user

	./wg_cli.py add_user -n short_user_name -f "Full Name" -i <IP> -k Key


e.g.:

	./wg_cli.py add_user -n jdoe -f "John Doe" -i 192.168.130.17 -k 7oLuxhVAbJIjZrQxLEErjZ0I0cj9qt0Qcqb+3DgqqRc=


## Remove user

	./wg_cli.py del_user -n short_user_name

e.g.:

	./wg_cli.py del_user -n jdoe
