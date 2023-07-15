
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

3. 初次启动

.. code-block:: console

   $ python cfms_server.py

由于数据库和RSA密钥的设置需要一些时间，您可能需要等待半分钟左右来完成初始化过程。