from socket import socket
import time
from io import BytesIO
import ssl
from clouddrive import stats
from clouddrive import configurator


RATE = float(configurator.UPLOAD_RATE * 1024) / 8.0  # specified in kb

CHUNK_SIZE = 1000


def ssl_sendall(self, data, flags=0):
    self._checkClosed()

    if self._sslobj:
        if flags != 0:
            raise ValueError(
                "non-zero flags not allowed in calls to sendall() on %s" %
                self.__class__)
        amount = len(data)
        done = count = 0
        start = time.time()

        io = BytesIO(data)
        while True:
            count += 1

            # calc current rate
            now = time.time()
            elapsed = now - start
            rate = float(done) / elapsed
            if rate > RATE:
                time.sleep(0.5)
                continue

            chunk = io.read(CHUNK_SIZE)
            if chunk:
                self.send(chunk)
                done += len(chunk)
                if count % 15 == 0:
                    stats.record_fileprogress(done, amount)
            else:
                break
        return amount
    else:
        return socket.sendall(self, data, flags)

ssl.SSLSocket.sendall = ssl_sendall
