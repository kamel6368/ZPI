"""Communication with agents"""
import socket
import numpy as np
from threading import Thread
from time import sleep
from resources import res
from cStringIO import StringIO
import Tkinter as tk
import cv2
from PIL import Image, ImageTk
import errno
from object import Shape, CombinedObject
import enums
from ImageProcessing import objects_detection as od
from aruco_detector import MarkerDetector


class TCPServer(Thread):
    """Base server class"""

    def __init__(self, address):
        super(TCPServer, self).__init__()
        self._stop = False
        self.address = address
        self.receive_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._overflow = None

    def stop(self):
        self._stop = True

    def run(self):
        """Main loop of server. Never start server using run, use start instead"""
        while not self._stop:
            sleep(1)
        self.send_socket.close()
        self.receive_socket.close()

    def _send(self, message):
        """Send message to connected server"""
        message = '%d|%s' % (len(message), message)
        self.send_socket.sendall(message)
        if len(message) > 60:
            message = message[:20] + '...' + message[-20:]
        print '%s:%d -> %s' % (self.send_socket.getsockname()[0], self.send_socket.getsockname()[1], message)

    def _receive(self, connection):
        """Receive message from connected server"""
        chunks = ''
        command = ''
        if self._overflow is not None:
            chunks = self._overflow
            self._overflow = None
        buffer_size = res('tcp_server\\buffer_size')
        timeouts = 0
        connection.settimeout(0.1)
        while True:
            try:
                chunk = connection.recv(buffer_size)
            except socket.timeout:
                timeouts += 1
                if timeouts == 5:
                    break
            except socket.error, e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    break
                else:
                    break
            else:
                if not chunk:
                    break
                chunks += chunk
                timeouts = 0
        if chunks:
            length = int(chunks.split('|')[0])
            command = chunks[len(str(length)) + 1:len(str(length)) + 1 + length]
            if len(chunks) > len(str(length)) + 1+ length:
                self._overflow = chunks[len(str(length)) + 1 + length:]
            if len(chunks) > 60:
                message = chunks[:20] + '...' + chunks[-20:]
            else:
                message = chunks
            print '%s:%d <- %s' % (self.receive_socket.getsockname()[0], self.receive_socket.getsockname()[1], message)
        return command


class TCPServerManager(TCPServer):
    """Server managing connections with agents"""

    def __init__(self, context):
        super(TCPServerManager, self).__init__((res('tcp_server\\ip'), res('tcp_server\\server_port')))
        self.agents = []
        self.name = 'Manager'
        self.context = context

    def stop(self):
        for agent in self.agents:
            agent.stop()
        sleep(2)
        super(TCPServerManager, self).stop()

    def run(self):
        """Main loop of server. Never start server using run, use start instead

        Listen for registration requests from agents and create threads for them
        """
        self.receive_socket.bind(self.address)
        self.receive_socket.settimeout(0.5)
        self.receive_socket.listen(1)
        print 'manager server started on: %s' % self.address[1]
        while not self._stop:
            try:
                connection, client_address = self.receive_socket.accept()
            except socket.timeout:
                sleep(1)
            except socket.error:
                print 'manager server error'
                self.stop()
            else:
                try:
                    message = self._receive(connection)
                except socket.timeout:
                    pass
                except socket.error:
                    pass
                else:
                    if message:
                        if message.split('|')[0] == 'REGISTER':
                            agent = TCPServerAgent(self.context,
                                                   (message.split('|')[1].split(':')[0],
                                                    int(message.split('|')[1].split(':')[1])),
                                                   message.split('|')[2])
                            self.agents.append(agent)
                            agent.start()
                connection.close()
        self.send_socket.close()
        self.receive_socket.close()
        print 'manager server stopped'


class TCPServerAgent(TCPServer):
    """Server maintaining connection with specific agent"""

    def __init__(self, context, send_address, name):
        super(TCPServerAgent, self).__init__(('', 0))
        self.send_address = send_address
        self.name = 'Agent Server'
        self.agent_name = name
        self.context = context
        self.context.agents_list.insert(tk.END, self.agent_name)
        self.autonomous = True
        self.feed = False

    def run(self):
        """Main loop of server. Never start server using run, use start instead

        Establish communication with agent on new port and start listening for messages
        """
        self.receive_socket.bind(self.address)
        self.send_socket.connect(self.send_address)
        self.address = (res('tcp_server\\ip'), self.receive_socket.getsockname()[1])
        self._send('REGISTER|%s:%s' % (self.address[0], self.address[1]))
        self.receive_socket.settimeout(0.5)
        self.receive_socket.listen(1)
        print 'agent server started'
        while not self._stop:
            try:
                connection, client_address = self.receive_socket.accept()
            except socket.timeout:
                sleep(1)
            except socket.error:
                print 'agent server error'
                self.stop()
            else:
                while not self._stop:
                    try:
                        message = self._receive(connection)
                    except socket.timeout:
                        print 'agent server timeout'
                    except socket.error:
                        print 'agent server error'
                        self.stop()
                    else:
                        self.process_request(message)
        self.send_socket.close()
        self.receive_socket.close()
        print 'agent server stopped'

    def process_request(self, message):
        """Process messages from agent"""
        if message == 'LOGIC_ON':
            # Acknowledge agent logic change
            self.autonomous = True
            self.context.update_info()
        elif message == 'LOGIC_OFF':
            # Acknowledge agent logic change
            self.autonomous = False
            self.context.update_info()
        elif message.split('|')[0] == 'ARUCO':
            # Extract and send aruco data in received image, display image
            image = np.load(StringIO(message[6:]))['frame']
            b, g, r = cv2.split(image)
            tk_image = cv2.merge((r, g, b))
            tk_image = Image.fromarray(tk_image)
            tk_image = ImageTk.PhotoImage(image=tk_image)
            self.context.video_feed.create_image(0, 0, image=tk_image)
            self.context.video_feed.frame = tk_image
            adet = MarkerDetector()
            rvec, tvec = adet.detect(image)
            if rvec is None or tvec is None:
                self._send('ARUCO|None')
            else:
                send = 'ARUCO'
                for sc in rvec[0]:
                    send += '|%f' % sc
                for sc in tvec[0]:
                    send += '|%f' % sc
                self._send(send)
        elif message.split('|')[0] == 'PROCESS':
            # Detect and send objects in received image, display image
            image = np.load(StringIO(message[8:]))['frame']
            b, g, r = cv2.split(image)
            tk_image = cv2.merge((r, g, b))
            tk_image = Image.fromarray(tk_image)
            tk_image = ImageTk.PhotoImage(image=tk_image)
            self.context.video_feed.create_image(0, 0, image=tk_image)
            self.context.video_feed.frame = tk_image
            det = od.ObjectDetector()
            objects = det.detect_objects(image, 50)
            message = 'PROCESS|%d' % len(objects)
            for obj in objects:
                message += '|%s' % repr(obj)
            self._send(message)

    def shutdown(self):
        """Send shutdown command to agent"""
        self._send('SHUTDOWN')
        for i in range(self.context.agents_list.size()):
            if self.context.agents_list.get(i) == self.agent_name:
                self.context.agents_list.delete(i)
                break
        self.stop()

    def switch_logic(self):
        """Send logic switch command to agent"""
        if self.autonomous:
            self._send('LOGIC_OFF')
        else:
            self._send('LOGIC_ON')

    def __str__(self):
        return self.agent_name
