# Ejemplo-SSH-Server
Pequeño servidor SSH creado en Python utilizando la librería Paramiko, puede ser un ejemplo de Honeypot ya que nunca va a retornar una conexión establecida.

Este servidor está configurado para que con ninguna credencial pueda retornar una pseudo-terminal o conexión.

## Dependencias
```pip3 install paramiko```

## Uso
Se debe agregar una llave privada con el nombre ``llave_rsa``, esta puede ser generada con ``ssh-keygen``.

**NOTA:** Puede especficar otro nombre de archivo a la llave, pero debe cambiar el contenido de la constante ``KEY_FILE_NAME``

Para iniciar el servidor, debe utilizar Python 3:

```python3 server.py```
