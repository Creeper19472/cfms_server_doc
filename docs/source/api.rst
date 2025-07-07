API
===

本章节将介绍 CFMS 的请求与响应规范。

.. autosummary::
   :toctree: generated

.. role:: python(code)
   :language: python


通常而言，CFMS 的服务端由配置文件默认设置为在 0.0.0.0:5104 这一地址上进行监听。

CFMS 使用 Websocket 协议进行通信，因此，可以在 Python 环境下使用以下命令
连接到服务器：

.. code-block:: python
   :linenos:

   from websockets.sync.client import connect
   import ssl

   server_address = "wss://localhost:5104"

   ssl_context = ssl.create_default_context()
   ssl_context.check_hostname = False
   ssl_context.verify_mode = ssl.CERT_NONE

   client = connect(server_address, ssl=ssl_context)

需要注意上面的示例实际上直接跳过了对证书可信性的检查，因此，在生产环境中
应当使用合适的证书进行连接，以便避免被中间人攻击。

请求规范
--------------

.. note::

   CFMS 的请求规范仍在频繁变化之中，以下部分的内容可能已经过时。

一个合法的请求应当具有如下的格式：

.. code-block:: python
   :linenos:

   # 请求

   {
      "action": "",
      "data": {},
      "username": "",
      "token": ""
   }

其中，`username`和`token`的键值在执行包括登录、根据任务ID上传和下载文件在内的少数操作时可以为空（无论设置为null还是空字符串）。

一个响应根据服务端版本的不同格式可能存在变化，但大致具有以下的格式：

.. code-block:: json

   // 响应

   {
      "code": 400, 
      "msg": "bad request", 
      "trace_id": null, 
      "api_version": "v1"
   }