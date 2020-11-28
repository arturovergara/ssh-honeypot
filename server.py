#!/usr/bin/python3

import sys
import socket
import paramiko
import threading
from datetime import datetime

LOG_FILE_NAME = "log.txt"
LOG_FILE_LOCK = threading.Lock()
KEY_FILE_NAME = "llave_rsa"
PUERTO = 22
MAX_CONEXIONES = 10

# Clase que implementa la interfaz de paramiko para un correcto manejo de una sesion ssh
class Servidor(paramiko.ServerInterface):
    def __init__(self, direccion_cliente):
        self.event = threading.Event()
        self.direccion_cliente = direccion_cliente

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    # Verifica las credenciales ingresadas
    def check_auth_password(self, username, password):
        # Bloquea o desbloquea el acceso (programacion con hilos)
        LOG_FILE_LOCK.acquire()

        try:
            # Se agrega la conexion registrada al log
            archivo = open(LOG_FILE_NAME, "a")
            print("{}\t{}\t{}\t{}".format(datetime.now(), self.direccion_cliente[0], username, password))
            archivo.write("{}\t{}\t{}\t{}\n".format(datetime.now(), self.direccion_cliente[0], username, password))
            archivo.close()
        finally:
            # Se desbloquea el acceso
            LOG_FILE_LOCK.release()    

        # Siempre retorna "Autenticación Fallida", es decir, el usuario con ninguna credencial podrá loguearse
        return paramiko.AUTH_FAILED


# Funcion diseñada para trabajar la conexion ssh mediante hilos, se debe encapsular todo el proceso de
# conexion con un cliente en una funcion para asi manejar multiples conexiones simultaneas
def ssh(conexion, direccion):
    try:
        transporte = paramiko.Transport(conexion)
        transporte.add_server_key(paramiko.RSAKey(filename = KEY_FILE_NAME))
        transporte.local_version = "SSH-2.0-OpenSSH_7.4p1 Raspbian-10+deb9u2"
        servidor = Servidor(direccion)

        try:
            transporte.start_server(server = servidor)
        except:
            sys.stderr.write("[-] Hubo un error al establecer la negociacion SSH.\n")
            return

        canal = transporte.accept(20)

        if canal is None:
            transporte.close()
            return

        # Esto esta demas, ya que el cliente nunca se va a autenticar
        servidor.event.wait()

        if not servidor.event.is_set():
            transporte.close()
            return

        canal.close()

    except:
        sys.stderr.write("[-] Hubo un error al generar la conexion\n")
        transporte.close()


def main():
    try:
        # Se crea el socket del servidor
        socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        socket_servidor.bind(('', PUERTO))
    except:
        sys.stderr.write("[-] Error al crear y bindear el socket.\n")
        sys.exit(1)

    hilos = []

    # Se queda en un loop infinito esperando conexiones entrantes
    while True:
        try:
            socket_servidor.listen(MAX_CONEXIONES)
            cliente, direccion = socket_servidor.accept()
        except:
            sys.stderr.write("[-] Error al colocar el socket a la escucha o al aceptar la conexion del cliente.\n")
    
        # Al establecer una nueva conexion, esta la maneja en un hilo para asi tratar conexiones multiples simultaneas
        nueva_conexion = threading.Thread(target = ssh, args = ((cliente, direccion)))
        nueva_conexion.start()
        hilos.append(nueva_conexion)

        for hilo in hilos:
            hilo.join()

if __name__ == "__main__":
    main()

