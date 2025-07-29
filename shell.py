import paramiko
import socket

host_key = paramiko.RSAKey.generate(2048)

class MyServer(paramiko.ServerInterface):
    def check_auth_password(self, username, password):
        if (username == "admin" and password == "12345678"):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('0.0.0.0', 2200))
sock.listen(5)

client_socket, addr = sock.accept()
print(f"[+] Connection from {addr}")

transport = paramiko.Transport(client_socket)
transport.add_server_key(host_key)

server = MyServer()
transport.start_server(server=server)

channel = transport.accept(20)

if channel is None:
    print("Failed to open channel")
    exit(1)

def shell(channel):
    prompt = "admin@server:~$ "
    channel.send(prompt)

    command = b''

    while True:
        try:
            char = channel.recv(1)
            channel.send(char)
            if not char:
                break

            if char in [b'\r', b'\n']:
                
                if command.strip() == b'exit':
                    channel.send(b'Exiting shell...\n')
                    break

                elif command.strip() == b'whoami':
                    response = b'admin\n'

                elif command.strip() == b'uname -a':
                    response = b'Linux DESKTOP-FH075I7 6.6.87.2-microsoft-standard-WSL2 #1 SMP PREEMPT_DYNAMIC Thu Jun  5 18:30:46 UTC 2025 x86_64 x86_64 x86_64 GNU/Linux\n'

                elif command.strip() == b'pwd':
                    response = b'/home/admin\n'

                elif command.strip() == b'ls':
                    response = b'file1.txt\nfile2.txt\n'

                elif command.strip() == b'cat file1.txt':
                    response = b'This is the content of file1.txt\n'

                elif command.strip() == b'cat file2.txt':
                    response = b'This is the content of file2.txt\n'

                elif command.strip() == b'exit':
                    channel.send(b'Exiting shell...\n')
                    break

                else:
                    response = b'Command not found: ' + command.strip() + b'\n'

                channel.send(response)
                channel.send(prompt)
                command = b''

            else:
                command += char

            
        except Exception as e:
            print(f"Error: {e}")
            break

    channel.close()



shell(channel)