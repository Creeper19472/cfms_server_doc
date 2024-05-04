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

客户端与服务端的数据传输目前采用 AES 进行对称加密传输，而可采取多种密钥交换模式建立加密。

客户端使用何种加密由服务端指定，该指定存在于服务器握手过程的响应之中，示例如下：

.. code-block:: json
   :linenos:
   
   {
      "msg": "enableEncryption", 
      "method": "x25519", 
      "public_key": "0e3435c51b72b(...)", 
      "code": 0
   }

服务端支持的密钥交换模式请参考 `config.sample.toml`相关字段的注释。建议使用 x25519
作为密钥交换机制以获得更好的安全性与性能。

以下提供实现对应过程的部分代码供参考。

(L255, in _setup_handshake())

.. code-block:: python
   :linenos:

   ...

   if self.recv() != "enableEncryption":
      self.send("Unknown request")
      raise ProgrammedSystemExit

   available_key_exchange_methods = ["rsa", "x25519"] # 预先定义可用的方法

   if (ukem:=self.config["security"]["use_key_exchange_method"]) in available_key_exchange_methods:
      if ukem == "rsa":
         self.send(
            json.dumps(
               {
                     "msg": "enableEncryption",
                     "method": "rsa",
                     "public_key": self.public_key.export_key("PEM").decode(),
                     "code": 0,
               }
            )
         )

         receive_encrypted = self.request.recv(
            self.server.BUFFER_SIZE
         )  # 这里还不能用 self.recv() 方法：是加密的, 无法decode()

         decrypted_data = self.pri_cipher.decrypt(receive_encrypted)  # 得到AES密钥

         # self.logger.debug(f"AES Key: {decrypted_data}")

         self.aes_key = decrypted_data
         self.encrypted_connection = True
            
      elif ukem == "x25519":
         # It is recommended that a client generates a randomized private key when connecting
         # to the server in order to ensure safety. 

         from cryptography.hazmat.primitives import hashes
         from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
         from cryptography.hazmat.primitives.kdf.hkdf import HKDF
         
         with open(f"{self.server.root_abspath}/content/auth/x25519_pri", "rb") as x_pri_file:
            x_pri_bytes = x_pri_file.read()

         x_private_key = X25519PrivateKey.from_private_bytes(x_pri_bytes)
         x_public_key = x_private_key.public_key()
         x_pub_raw = x_public_key.public_bytes_raw()

         self.send(
            json.dumps(
               {
                     "msg": "enableEncryption",
                     "method": "x25519",
                     "public_key": x_pub_raw.hex(), # json 格式只能使用 str 模式发送
                     "code": 0,
               }
            )
         )

         receive_encrypted = self.request.recv(
            self.server.BUFFER_SIZE
         )  

         peer_public_key = X25519PublicKey.from_public_bytes(receive_encrypted)

         shared_key: bytes = x_private_key.exchange(peer_public_key)

         # TODO: 实现对多种对称加密模式的支持
         
         self.aes_key = shared_key # 先用协商密钥为双向加密密钥发送新密钥
         self.encrypted_connection = True

         # # self.x25519_shared_
         derived_key = HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=secrets.token_bytes(16),
            info=b'handshake data',
         ).derive(shared_key)

         self.send(derived_key.hex()) # 发送导出密钥
         self.aes_key = derived_key

         try: self.recv() # 要求客户端发送有效回执
         except: raise ProgrammedSystemExit

   ...

服务器与客户端的通信遵循特定的握手过程。有关更多详情，请参阅相关源代码。

请求规范
--------------

.. note::

   CFMS 的请求规范仍在频繁变化之中，以下部分的内容可能已经过时。

一个合法的请求应当具有如下的格式：

.. code-block:: python
   :linenos:

   # 请求

   {
   "version": 1,
   "request": "", # 请求名（类型），如 getDocument
   "X-Ca-Timestamp": ..., # -> int or float, usually time.time(), required
   "trace_id": ..., # required, str
   "data": { # 包含请求所需的应提交的信息
      ...
   },
   "auth": { # 大多数请求所必须附带的身份认证标头
      "username": "example",
      "token": "example_token"
      }
   }

X-Ca-Timestamp 和 trace_id 是必须包含于请求中的，否则服务器将返回状态码 400.

X-Ca-Timestamp 应当被设置为客户端发出请求的当前时间， trace_id 应当根据需要设置为
一个唯一的字符串。它们被需求以防止重放攻击。

目前 CFMS 的 API 版本应当仅为 1.

一个响应根据服务端版本的不同格式可能存在变化，但大致具有以下的格式：

.. code-block:: json

   // 响应

   {
      "code": 400, 
      "msg": "bad request", 
      "trace_id": null, 
      "api_version": "v1"
   }