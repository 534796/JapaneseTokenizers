#! -*- coding: utf-8 -*-
import six
import subprocess
from subprocess import Popen, PIPE, STDOUT
import multiprocessing
# socket object
import socket
# logger
from JapaneseTokenizer import init_logger
import logging
logger = init_logger.init_logger(logging.getLogger(init_logger.LOGGER_NAME))
# else
import time
import shutil

'''
class BaseServerHandler(object):
    """Base handler to use UNIX process as server process"""
    def __init__(self):
        # メンバ変数を定義しておく
        self._sock = None  # type: socket
        self._address = None  # type: str

    def __call__(self, serversocket):
        """"""
        # type: (socket)->None
        while True:
            # 接続を受ける
            (self._sock, self._address) = serversocket.accept()
            # with ステートメントは後始末のため
            with self:
                # ハンドラを起動する
                self.handle()

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, traceback):
        """"""
        # type: ()->None
        # ソケットの後始末
        self._sock.shutdown(socket.SHUT_RDWR)
        self._sock.close()

    # 中身はサブクラスで定義してもらう
    def handle(self):
        raise NotImplementedError()


class MultiprocessingSocketStreamServer(object):
    """This class provides abstracted server function.
    """
    # 待ち受けポートとワーカープロセスの数を指定する
    def __init__(self, port, processes, max_queue_size=5):
        """* Parameters
        - port: Port number where the server process works
        - processes: The number of process
        - max_queue_size: The number of size which server can accept request
        """
        # type: (int,int,int)->None
        # IPv4 / TCP のソケットを用意する
        self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # localhost / port ポートで待ち受ける
        self._serversocket.bind(('localhost', port))
        # 接続待ちのキューのサイズ
        self._serversocket.listen(max_queue_size)
        # ワーカープロセスの数
        self.processes = processes

    # 接続を処理するハンドラを指定する
    def start(self, handler):
        """* What you can do
        - It starts server process as Multiprocess process.
        
        * Parameters
        - handler: Any instance object which can process data.
        """
        # type: (BaseServerHandler)->None
        for i in range(self.processes):
            # ワーカープロセスを生成する
            p = multiprocessing.Process(target=handler,
                                        args=(self._serversocket, ))
            # 子プロセスはデーモンにする
            p.daemon = True
            # プロセスを開始する
            p.start()
        # メインループに入る
        self._parent_main_loop()

    # 親プロセスのメインループ
    def _parent_main_loop(self):
        """* What you can do
        - Nothing.
        """
        # type: ()->None
        while True:
            # 親プロセスは特に何もしない
            time.sleep(1)



if six.PY2:
    from daemons import daemonizer

    class JumanppServerHandler(BaseServerHandler):
        def __init__(self, host, port, command):
            """* What you can do
            - You start juman++ server mode
            """
            # type: (str,int,str)->None
            self.command = command
            self.host = host
            if isinstance(port, str):
                port = int(port)
            self.port = port

        def launch_jumanpp_process(self):
            """* What you can do
            - It starts jumanpp process and keep it.
            """
            logger.debug(msg='Juman++ process is waiting with command = {}'.format(self.command))
            self.jumanpp_process = Popen(self.command, stdin=PIPE, stdout=PIPE)

        def restart_jumanpp_process(self):
            """* What you can do"""
            pass

        def __del__(self):
            if hasattr(self, 'jumanpp_process'):
                self.jumanpp_process.stdin.close()
                self.jumanpp_process.wait()

        @daemonizer.run(pidfile="/tmp/sleepy.pid")
        def start_server(self, max_queue=50):
            """"""
            # type: (int)->None
            ### it starts jumann++ process ###
            self.launch_jumanpp_process()

            ### it starts server ###
            serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversock.bind((self.host, self.port))  # IPとPORTを指定してバインドします
            serversock.listen(max_queue)
            logger.debug('Waiting for connections at host={} port={}...'.format(self.host, self.port))
            self.clientsock, self.client_address = serversock.accept()  # 接続されればデータを格納
            # todo たぶん、この処理をBaseに記述しないといけないと思う
            while True:
                input_string = self.clientsock.recv(1024)
                logger.debug('Received -> %s' % (input_string))
                if (buffer != "/^##JUMAN++\t.*/"): # 動的オプション
                    res = repr(self.process.stdout.readline(input_string))
                    self.clientsock.sendall() # 動的オプションの戻り値(必ず1行)
                elif (buffer != "/^#.*/"): # コメント行
                    res = self.process.stdout.readline(input_string)
                    self.clientsock.sendall()
                else:
                    responce = ""
                    responce += input_string
                    while True:
                        self.process.stdout.readline(input_string)
                        f = self.clientsock.recv(1024)
                        responce += f.to_s
                        if f.to_s == "EOS\n":
                            break
                        self.clientsock.sendall(input_string)  # メッセージを返します

        def shutdown_server(self):
            pass

        def call_server(self):
            """* What you can do
            """
            # type: ()->None
            if not hasattr(self, 'clientsock') or not hasattr(self, 'client_address') or not hasattr(self, 'process'):
                raise Exception('You must call start_server() first.')
            while True:
                input_string = self.clientsock.recv(1024)
                logger.debug('Received -> %s' % (input_string))
                if (buffer != "/^##JUMAN++\t.*/"): # 動的オプション
                    res = repr(self.process.stdout.readline(input_string))
                    self.clientsock.sendall() # 動的オプションの戻り値(必ず1行)
                elif (buffer != "/^#.*/"): # コメント行
                    res = self.process.stdout.readline(input_string)
                    self.clientsock.sendall()
                else:
                    responce = ""
                    responce += input_string
                    while True:
                        self.process.stdout.readline(input_string)
                        f = self.clientsock.recv(1024)
                        responce += f.to_s
                        if f.to_s == "EOS\n":
                            break
                        self.clientsock.sendall(input_string)  # メッセージを返します


    class JumanServerHandler(BaseServerHandler):
        pass

else:
    class JumanppServerHandler(BaseServerHandler):
        """* What you can do
        """
        def __init__(self, command="jumanpp"):
            """* What you can do
            - You start juman++ server mode
            
            * Parameters
            - command: UNIX command to launch Juman++ process
                - Example: "usr/bin/jumanpp"
            """
            # type: (str,int,str)->None
            super().__init__()
            self.command = command
            self.launch_jumanpp_process()

        # todo このメソッドは消すかもしれない。ベースメソッドで十分
        def __call__(self, serversocket):
            """* What you can do
            - This method is called inside Multiprocess
            - This method starts server process of Juman++ process.
            """
            # type: (socket)->None
            while True:
                # 接続を受ける
                (self._sock, self._address) = serversocket.accept()
                # with ステートメントは後始末のため
                with self:
                    # ハンドラを起動する
                    self.handle()

        def launch_jumanpp_process(self):
            """* What you can do
            - It starts jumanpp process and keep it running.
            """
            if shutil.which(self.command) is None:
                raise Exception("No Juman++ command at given path={}".format(self.command))
            else:
                logger.debug(msg='Juman++ process with command = {}'.format(self.command))
                self.jumanpp_process = Popen(self.command, stdin=PIPE, stdout=PIPE)

        def handler(self):
            """* What you can do
            - 
            """
            buffer = ""  # type: str
            # todo これクロージャにできんかな？
            while True:
                input_string = self._sock.recv(1024)
                logger.debug('Received -> %s' % (input_string))
                if (buffer != "/^##JUMAN++\t.*/"): # 動的オプション
                    res = repr(self.jumanpp_process.stdout.readline(input_string))
                    logger.debug(res)  # todo
                    self._sock.sendall() # 動的オプションの戻り値(必ず1行)
                elif (buffer != "/^#.*/"): # コメント行
                    res = self.jumanpp_process.stdout.readline(input_string)
                    logger.debug(res)  # todo
                    self._sock.sendall()
                else:
                    # todo これクロージャにできんかな？
                    responce = ""
                    responce += input_string
                    while True:
                        self.jumanpp_process.stdout.readline(input_string)
                        f = self._sock.recv(1024)
                        responce += f.to_s
                        if f.to_s == "EOS\n":
                            break
                        self._sock.sendall(input_string)  # メッセージを返します
                        '''


import pexpect
import shutil
from functools import wraps



# todo サーバー化したいならば、このクラスを複数たてればいいんじゃない？
class JumanppHnadler(object):
    def __init__(self, jumanpp_command):
        """"""
        # type: (str)->None
        self.jumanpp_command = jumanpp_command
        self.launch_jumanpp_process(jumanpp_command)

    def __del__(self):
        self.process_analyzer.kill(sig=9)

    def launch_jumanpp_process(self, command):
        """* What you can do
        - It starts jumanpp process and keep it.
        """
        # type: (str)->None
        if shutil.which(command) is None:
            raise Exception("No command at {}".format(command))
        else:
            self.process_analyzer = pexpect.spawnu(command)
            self.process_id = self.process_analyzer.pid

    def restart_process(self, message=None):
        self.process_analyzer.kill(sig=9)
        self.process_analyzer = pexpect.spawnu(self.jumanpp_command)
        self.process_id = self.process_analyzer.pid


    def __query_python3(self, input_string):
        """"""
        # type: (str)->str
        self.process_analyzer.sendline(input_string)
        buffer = ""
        while True:
            line_string = self.process_analyzer.readline()  # type: bytes
            if line_string.strip() == "EOS":
                buffer += line_string
                return buffer
            else:
                buffer += line_string

    def query(self, input_string):
        """* What you can do
        """
        # type: (str)->str
        if six.PY3:
            return self.__query_python3(input_string)
        else:
            pass


if __name__ == "__main__":
    jumanpp_handler = JumanppHnadler('/usr/local/bin/jumanpp')
    for i in range(0, 100):
        a = jumanpp_handler.query('紗倉 まな（さくらまな、1993年3月23日 - ）は、日本のAV女優。'*10)
        print(a)