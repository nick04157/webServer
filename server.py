import socket
import os
import mimetypes
from datetime import datetime

# Impostazioni base del server
host = 'localhost'
port = 8080
root = './www'  # Cartella da cui servire i file

# Funzione per salvare le richieste nel file di log
def scrivi_log(metodo, percorso, codice):
    with open('server.log', 'a') as file:
        file.write(f"[{datetime.now()}] {metodo} {percorso} {codice}\n")

# Funzione per capire che tipo di file stiamo servendo (html, css, jpg, ecc.)
def tipo_file(percorso):
    tipo, _ = mimetypes.guess_type(percorso)
    return tipo or 'application/octet-stream'

# Funzione che gestisce la risposta al client (cioè il browser)
def gestisci_richiesta(client, percorso):
    # Costruisce il percorso del file da leggere partendo dalla cartella www
    file_richiesto = os.path.join(root, percorso.lstrip('/'))

    # Se è una cartella, prova a caricare index.html al suo interno
    if os.path.isdir(file_richiesto):
        file_richiesto = os.path.join(file_richiesto, 'index.html')

    # Se il file esiste, lo legge e lo invia
    if os.path.exists(file_richiesto) and os.path.isfile(file_richiesto):
        with open(file_richiesto, 'rb') as file:
            contenuto = file.read()
        risposta = 'HTTP/1.1 200 OK\r\n'
        tipo = tipo_file(file_richiesto)
        intestazioni = f'Content-Type: {tipo}\r\nContent-Length: {len(contenuto)}\r\n\r\n'
        client.sendall(risposta.encode() + intestazioni.encode() + contenuto)
        scrivi_log('GET', percorso, 200)
    else:
        # Se il file non esiste, manda una risposta 404
        errore = b"<h1>404 Pagina non trovata</h1>"
        risposta = 'HTTP/1.1 404 Not Found\r\n'
        intestazioni = f'Content-Type: text/html\r\nContent-Length: {len(errore)}\r\n\r\n'
        client.sendall(risposta.encode() + intestazioni.encode() + errore)
        scrivi_log('GET', percorso, 404)

# Funzione principale che avvia il server
def avvia_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(5)
        print(f"Sito attivo su http://{host}:{port}")

        # Il server resta sempre in ascolto di nuove richieste
        while True:
            client, _ = server.accept()
            with client:
                richiesta = client.recv(1024).decode()
                if not richiesta:
                    continue
                parti = richiesta.split()
                # Se è una richiesta GET, gestiscila
                if len(parti) >= 2 and parti[0] == 'GET':
                    gestisci_richiesta(client, parti[1])
                else:
                    # Risposta generica se la richiesta non è valida
                    client.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")

# Avvia il server quando il file viene eseguito
if __name__ == '__main__':
    avvia_server()
