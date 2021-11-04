# SSH Honeypot
```diff
- Warning: This server hasn't been tested in production
- Please consider this before running it in a real environment.
```
Small SSH Honeypot written in Python 3 using the Paramiko library. This server listens for incoming connections and logs in a file the timestamp, IP address, username and password that were used.

**NOTE:** This server is designed so that no credentials can return a TTY or a valid SSH session.

## Dependencies
No need for a `requirements.txt` file here,  because only one dependency is required.
```bash
# Install with pip3 the Paramiko library
pip3 install paramiko
```

## Usage
To run the honeypot, Python 3 must be used:
```bash
python3 ssh-honeypot.py
```
Also, you can specify different options through the CLI to change the behavior of the honeypot. The available options will be listed below.
| Option | Description |
| ----- | ---- |
| `-l`, `--list-banners` | List available banners to use. |
| `-b INDEX`, `--banner INDEX` | Specify banner index to use from the list. (default: 8) |
| `-B STRING`, `--banner-string STRING` | Specify a custom banner to use. |
| `-f RSA_FILE`, `--file RSA_FILE` | RSA Key File to use. If it's not specified, a new one is dynamically generated. |
| `-n MAX_NUMBER`, `--number MAX_NUMBER` | Number of max connections to listen. (default: 10) |
| `-o LOG_FILE`, `--output LOG_FILE` | Specify a log file to append the records. (default: ./ssh-honeypot.log) |
| `-p PORT`, `--port PORT` | Listen port. (default: 2222) |

### Example:
Run the honeypot on port 4444 and register the log in `log.txt` file.
```bash
python3 ssh-honeypot.py -p 4444 -o log.txt
```
