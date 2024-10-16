# WIFI-BruteForce

## A simple tool to brute force attack wifi

- Author: Sylpha (T-13ee)
- Version: BETA

Wordlist: [https://github.com/t13ee/Wifi-BruteForce/releases/download/BETA/wordlist.zip](https://github.com/t13ee/Wifi-BruteForce/releases/download/BETA/wordlist.zip)

## Requirements
- USB WIFI
- Python3


## Install and Setup
```
sudo apt update
sudo apt install aircrack-ng 
```

```
git clone https://github.com/t13ee/Wifi-BruteForce.git && cd ./Wifi-BruteForce
pip install -r requirements.txt
chmod +x ./attack

# Download wordlist
...

```


## Tutorial
```
usage: attack [-h] [--name NAME] [--timeout-mac TIMEOUT_MAC] [--timeout-packet TIMEOUT_PACKET] [--wordlist WORDLIST] [--limit LIMIT]

WIFI BruteForce

options:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  WIFI name to find MAC address
  --timeout-mac TIMEOUT_MAC, -tm TIMEOUT_MAC
                        Time to find MAC. Default: < 5s >
  --timeout-packet TIMEOUT_PACKET, -tp TIMEOUT_PACKET
                        Time to capture packet. Default: < 0s > infinite
  --wordlist WORDLIST, -w WORDLIST
                        Path to wordlist
  --limit LIMIT, -l LIMIT
                        CPU limit (1-10 = 10%-100%). Default: 10
```

## License

This software is licensed under the terms of the [MIT License](LICENSE).

