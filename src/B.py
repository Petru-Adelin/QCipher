import socket as skt
import threading as thr
from shared_state import e
from encrypt import Encoder


def read_msg(conn: skt.socket, encoder: Encoder):
    FORMAT = 'utf-8'
    DISCONNECT_SEQ = '<END>'
    print(f'[NEW CONNECTION]')
    try:
        connected = True
        while connected:
            msg = encoder.decrypt(conn.recv(1024)).decode(FORMAT)
            if msg == DISCONNECT_SEQ:
                print('[~]: disconnecting...')
                connected = False

            print(f'[~]: {msg}')
    finally:
        conn.close()

def send_msg(conn: skt.socket, encoder: Encoder):
    connected = True
    while connected:

        FORMAT = 'utf-8'
        msg = input()
        conn.send(encoder.encrypt(msg.encode(FORMAT)))

def main():
    SERVER, PORT = '127.0.0.1', 5050
    server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    server.bind((SERVER, PORT))
    print('[ACTIVE SERVER]')
    encoder = e

    server.listen()
    
    conn, addr = server.accept()
    receiver = thr.Thread(target=read_msg, args=(conn, encoder))
    sender = thr.Thread(target=send_msg, args=(conn,encoder))
    receiver.start()
    sender.start()
    print(f"[CONNECTION ESTABLISHED] {thr.active_count()}")

    receiver.join()
    sender.join()
    

main()