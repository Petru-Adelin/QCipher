import socket as skt
import threading as thr
import time
from shared_state import e
from encrypt import Encoder

def send_back(conn: skt.socket,  encoder: Encoder):
    connected = True
    FORMAT = 'utf-8'
    DISCONNECT_SEQ = '<END>'
    print('Write down the messages (q for quit): \n')
    while connected:
        msg = input()
        if msg == 'q':
            connected = False
        else:
            encoded_msg = encoder.encrypt(msg.encode(FORMAT))
            conn.send(encoded_msg) 
    
    conn.send(encoder.encrypt(DISCONNECT_SEQ.encode(FORMAT)))
    time.sleep(1)
    print('Disconnected...')



def receive_cipher(conn: skt.socket, encoder: Encoder):
    connected = True
    DISCONNECT_SEQ = '<END>'
    while connected:
        msg = encoder.decrypt(conn.recv(1024)).decode('utf-8')
        if msg == DISCONNECT_SEQ or not msg:
            connected = False
        print(f'[~]: {msg}')


def main():
    # connecting 
    SERVER = '127.0.0.1'
    PORT = 5050
    encoder = e 
    sock = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    sock.connect((SERVER, PORT))
    t1 = thr.Thread(target=send_back, args=(sock,encoder))
    t2 = thr.Thread(target=receive_cipher, args=(sock,encoder))
    t1.start()
    t2.start()
    t1.join()
    t2.join()
   
if __name__ == "__main__":
    main()

    