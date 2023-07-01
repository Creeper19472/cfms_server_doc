权限与用户组
===================================

.. autosummary::
   :toctree: generated

.. role:: python(code)
   :language: python

权限
-----------------
.. note::
    本节所述的部分特性尚未被实现。

CFMS 的权限由一字符串命名，但有特殊用法规定用户和用户组所属的权限的更加复杂的属性。

存储在数据库中的用户权限符合以下格式：

.. code-block:: python
    :linenos:

    {
        "read": 
            {
                "expire": 0
            },
        ...
    }

如上所示，



文档权限的匹配规则
-----------------
有时候我们希望指定的权限持有者和用户组能够访问特定的文档，而这种需求在某些时候可能会显得较为复杂。
所幸的是，CFMS 提供了一套较为全面的匹配机制，这允许用户使用复杂的匹配规则来决定特定文档是否可被请求者访问。

一个匹配规则实际上被作为一个json文本储存。它看起来如下：

.. code-block:: python
   :linenos:

   [ # 列表，并列满足 与 条件
        {
            "match": "any",
            "match_groups": [ # 下级匹配组，满足 any 条件 => True
                {
                    "match": "any",
                    "rights": {
                        "match": "any",
                        "require": ["read"]
                    },
                    "groups": {
                        "match": "any",
                        "require": ["user"]
                    }
                }
            ]
        }, 
        {
            "match": "all",
            "match_groups": [
                {
                    "match": "any",
                    "rights": {
                        "match": "any",
                        "require": []
                    },
                    "groups": {
                        "match": "any",
                        "require": []
                    }
                }
            ]
        }, 
    ]

有些复杂，不是吗？

对用户是否满足规则要求的判断由 Users 类下的 :python:`ifMatchRequirements(self, rules: list)` 进行，它接受一个列表作为要处理的规则。
列表的各个元素都是字典，它们在匹配上是并列关系；出于技术考虑，只有当列表下每个作为元素的字典的要求被满足时该规则才会返回为 True，
即满足与门逻辑。

:python:`ifMatchRequirements()` 将依次检查各个作为最外层列表的元素的字典（我们称之为“首级字典”）所描述的规则是否被满足。在首级字典中，即可以通过改变 "match" 的键值来
确定匹配的规则：它接受 "any" 或 "all" 作为有效值，若出现二者以外的情况则将抛出 :python:`ValueError` 异常。

每个首级字典只接受 "match_groups"（子规则的匹配组）这个列表作为要处理的细化规则。同样地，这个列表下的元素也是字典，具有同样的 match 作为匹配模式，并（与之前不同）
接受两个字典分别作为其 rights 和 groups 的键值。这些字典，同样地，可以使用 match 来确认匹配模式。

若没有给定 match 的值，则将默认以 all 模式进行匹配。

.. warning::
    注意！请不要随意添加没有设置任一所需权限和组的子匹配规则。尽管它们可能看起来是“空”的而被认为
    应该被忽略，但在某些情况下将可能导致整个匹配规则出现意料之外的结果，并可能出现安全性问题。

.. versionchanged:: 1.0.0.20230625_alpha
   现在 :python:`ifMatchRequirements()` 仅接受 rules 作为参数。

.. versionchanged:: 1.0.0.20230628_alpha
   现在 :python:`ifMatchRequirements()` 存在一别名为 :python:`ifMatchRules()`。

我们可以从相对简单的例子开始。

.. code-block:: python
   :linenos:

   [ # 列表，并列满足 与 条件
        {
            "match": "any",
            "match_groups": [ # 下级匹配组，满足 any 条件 => True
                {
                    "match": "any",
                    "rights": {
                        "match": "any",
                        "require": ["read"]
                    },
                    "groups": {
                        "match": "any",
                        "require": []
                    }
                }
            ]
        }
    ]

以上这个示例实际上是最开始提供的示例的其中一部分。我们将它稍作改动，以便更加容易地解释功能：

- 最外层的列表 （:python:`[]`） 容纳着一个字典（当然也可以是多个），这些字典遵循一个相同的格式。
- 这个最外层的字典的 :python:`match` 键被设置为 "any"，这意味着它将在 "match_groups" 下给定的
多个规则中的任意一个被满足时返回为真。
- 在本例中的 "match_groups" 中的列表下只有一个元素，它也是一个字典，且只能是一个字典：同样地，它
依然遵照它所被规定的格式被书写。
- 在上一条所述的字典中，有两个键的内容将作为 权限 和 用户组 的匹配规则。我们仅从 "rights" 键来分析：
    1. 与之前相同，它对应的仍然是一个字典。
    2. 它对应的字典也有具有相同功能的 "match" 键。
    3. "require" 对应的是一个列表（至少通常是一个可迭代对象），它包含要匹配的权限。列表中的元素应该
    只是字符串。

上述示例将发挥以下的效用：

检查目标用户是否拥有 :python:`read` 权限，或是否拥有空用户组（groups 键下的字典规定的所需用户组为空）。

如果满足任一条件，则该规则将返回为真。

内部逻辑上，函数将把一个空的列表返回为真。同时，函数也将视 user 用户组为所有人拥有：

.. code-block:: python
   :linenos:

    def hasGroups(self, groups=[]):
        if not groups:
            return True # 没有则返回为真
        for i in groups:
            if i == "user":
                continue # user 用户组跳过
            if not i in self.groups:
                return False
        return True

因此，groups 字典 require 的空列表将在检查时被返回为真，即无论 match 为 any 或 all 时都将返回为真。

为了避免因不设置 groups 而导致有内容的 rights 规则在 any 模式下被忽略（以及不设置 rights 而导致有
内容的 groups 规则被忽略）的情况，函数将在仅设置 rights 和 groups 中的其中之一时将匹配模式调整为 all。


