# server

from ssl import *
from socket import *
from threading import *

# tüm istemci bağlantılarını soketleri depolar
clients = []

# sunucu, bu ayar Yanlış olarak ayarlanana kadar çalışacak
running = True

# haberci sunucu bilgisi
HOST = 'localhost'
PORT = 50000
SERVER = (HOST, PORT)

# SSL metin kur
sslctx = SSLContext(PROTOCOL_TLS_SERVER)
#sertifika zinciri altaki bastaki certifika sondaki private key
sslctx.load_cert_chain('certificate.pem', 'private.key')

# sunucuyu kurar ve istemcinin katılmasına izin verir(server ve socket)
server = sslctx.wrap_socket(socket(AF_INET , SOCK_STREAM), server_side=True)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(SERVER)
server.listen(5)

print('Port dinleniyor ', PORT)


def listen_to_client(client):
    '''Bu işlev, bir istemci tarafından sunucuya gönderilen mesajları dinler ve
    mesajı sunucuya bağlı diğer tüm istemcilere iletir. Ne zaman
    istemci bağlantıyı kapatır, sunucudan kaldırılır. '''

    try:
        while True:
            msg = client.recv(2048).decode() # recv ile metni alır

            # İstemci bağlantıyı kapattığında istemciyi dinlemeyi bırak
            if not msg:
                break

            # diğer tüm bağlı istemcilere mesaj gönderir
            for c in clients:
                if c != client:
                    c.send(msg.encode())
    except:
        print('Client hatasi!')
    
    finally:
        # istemci bağlantısını sonlandırın ve bunları bağlı istemciler listesinden kaldırın
        client.close() # eğer burada silmezsek hem porta dolu alan olur ve kişi aktif gözükür

        clients.remove(client)
        
        print('siliniyor Client!')

        # istemci kalmamışsa sunucuyu kapat
        if len(clients) == 0:
            global running
            running = False


def listen_for_clients():
    '''Bu işlev, sunucuya bağlanmaya çalışan yeni istemcileri dinler.
    ve yeni bir başlıkta onlar tarafından gönderilen mesajları dinlemeye başlar. '''
    try:
        while True:
            client, address = server.accept()
            
            print('Yeni client katıldı: ', address)

            # farklı iş parçacığındaki istemciden gelen mesajları dinler
            Thread(target=listen_to_client, args=[client, ], daemon=True).start()
            
            clients.append(client)
    except:
        running = False

# yeni iş parçacığındaki yeni bağlantıları dinlemeye başlar Thread çoklu işleme olanak sağlar çoklu işlemcili sistemlerde çalışır
Thread(target=listen_for_clients, daemon=True).start()

try:
    # sunucu durdurulana kadar burada bekleyin (running=False)
    while running:
        pass

# kullanıcının basarak sunucuyu kapatmasına izin verir 'Ctrl-C'
except KeyboardInterrupt:
    print('Server termination requested!')
    
except:
    print('Error, terminating server!')

finally:
    # tüm istemci bağlantılarını kapatır
    for client in clients:
        client.close()

    # sunucu soketini kapatır
    server.close()

    print('Sunucu sonlandırıldı!')

