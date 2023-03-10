# client

from ssl import *
from socket import *
from threading import *

# istemci, bu Yanlış olarak ayarlanana kadar çalışacak
running = True

username = input('isminiz: ')

# messenger server info 
HOST = 'localhost'
PORT = 50000
SERVER = (HOST, PORT)

# SSL bağlamını kur
sslctx = SSLContext(PROTOCOL_TLS_CLIENT)
sslctx.load_verify_locations('certificate.pem')

# sunucuya bağlantı kur
client = sslctx.wrap_socket(socket(AF_INET , SOCK_STREAM), server_hostname=HOST)

# sunucuya düzgün bir şekilde bağlanır
try:
    client.connect(SERVER)
except:
    print('Sunucuyla bağlantı başarısız!')
    quit()
else:
    print('sunucuya bağlandı!')


def listen_loop():
    '''Sunucu tarafından gönderilen mesajları dinler ve bağlantı kurulana kadar yazdırır.
    sunucu veya bu müşteri tarafından kapatıldı. '''
    try:
        while True:
            msg = client.recv(2048).decode()

            # sunucu bağlantıyı kapattığında dinlemeyi bırak
            if not msg:
                break

            print(msg)
    except:
        print('Server error!')
        
    finally:
        global running
        running = False

        print('Connection terminated!')


# bağlantı kapatılana kadar sunucuyu dinlemeye başlar
Thread(target=listen_loop, daemon=True).start()

# bağlantı kapatılana kadar sunucuya mesaj gönderir
try:
    while running:
        msg = input('')

        if msg == 'exit':
            running = False
        else:
            msg = '[' + username + '] ' + msg
            client.send(msg.encode())
except:
    print('mesaj gönderilemedi')

finally:
    # closes connection to server
    client.close()

    print('sunucuyla bağlantı kesildi!')

