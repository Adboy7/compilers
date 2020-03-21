# VSOPC Makefile

.PHONY: all clean install-tools

clean:
	rm -rf __pycache__ parser.out parsetab.py

install-tools:
	sudo apt install -y python3 python3-pip
	sudo pip3 install ply

vsopc:
	sudo chmod +x vsopc.py
