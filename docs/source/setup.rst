
=====

.. _installation:

安装与配置
------------

CFMS 服务端运行在 Python 3.11 及以上版本，并因新增语法而无法向后兼容。

您的设备可能需要满足 Python 3.11 的系统要求才能完成配置。

1. 克隆

克隆并定位到代码仓库；

.. code-block:: console

   (.venv) $ git clone https://github.com/creeper19472/cfms_2.git --depth=1
   (.venv) $ cd cfms_2

2. 安装必要的模块（这需要设备已经安装 pip）

.. code-block:: console
   
   (.venv) $ pip install -r requirements.txt

3. 配置 config.toml
   
第一次启动前的服务端目录不含 config.toml 文件，为了配置和运行 CFMS 服务端，您必须
在启动服务端前于工作根目录下放置 config.toml。这通常是不困难的，只需复制一份 config.
sample.toml，而后根据您的实际情况配置即可。

可以在 ::ref:`config` 了解更多有关 config.toml 的配置说明。

4. 初次启动

.. code-block:: console

   $ python cfms_server.py

CFMS 服务端目前被设置为在初次启动时同时生成 x25519 和 RSA 的密钥对。其中 RSA 密钥的设置
需要明显较长的时间，因而可能需要等待半分钟左右来完成初始化过程。

这个过程在 initialize.py 下被定义。

一旦启动完成，您应当可以通过预先设定的地址访问 CFMS。为了调试方便，初始用户名和密码目前被
统一设置为 `admin`, `123456`。在投入生产环境前应当立即更换它们。