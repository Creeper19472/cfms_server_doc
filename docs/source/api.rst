API
===

本章节将介绍 CFMS 的请求与响应规范。

.. autosummary::
   :toctree: generated

.. role:: python(code)
   :language: python


通常而言，CFMS 的服务端被默认设置为在 0.0.0.0:5103 端口上进行监听，
受技术所限尚不支持 IPv6 协议。

CFMS 使用 TCP 协议进行通信，因此，可以在 Python 环境下使用以下命令
连接到服务器：

.. code-block:: python
   :linenos:

   import socket

   host = "localhost"
   port = 5103

   client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   client.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1) # 在客户端开启心跳维护
   client.connect((host, port))

客户端与服务端的数据传输目前采用 AES 进行对称加密传输，并使用 RSA 传输对称加密所需的密钥。

为了实现这一约定过程，服务端将在 :python:`_doFirstCommunication(self, conn)` 下执行对应的过程：

.. code-block:: python
   :linenos:

   ...

   receive = self.__recv()
   
   if receive == "hello":
      self.__send("hello")
   else:
      print(receive)
      self.__send("Unknown request")
      return False
   
   if self.__recv() != "enableEncryption":
         self.__send("Unknown request")
         return False
   
   self.__send(json.dumps({
      "msg": "enableEncryption",
      "public_key": self.public_key.export_key("PEM").decode(),
      "code": 0
   }))
   
   return True

   ...

这段代码的意义是，首先等待客户端发送一内容为 "hello" 的明文请求；如果收到的内容并非这一明文，则服务端将断开与客户端的连接。

.. note::
   有效的通信过程可在 CFMS 服务端的 cli 文件夹下找到。

请求规范
--------------
一个合法的请求应当具有如下的格式：

.. code-block:: python
   :linenos:

   # 请求

   {
   "version": 1,
   "request": "", # 请求名（类型），如 getDocument
   "data": { # 包含请求所需的应提交的信息
      ...
   },
   "auth": { # 大多数请求所必须附带的身份认证标头
      "username": "example",
      "token": "example_token"
      }
   }

目前 CFMS 的 API 版本应当仅为 1.

一个响应应该会具有以下的格式：

.. code-block:: python

   # 响应

   {
      "code": 0,
      "msg": "",
      "data": {},
      "__notes__": []
   }