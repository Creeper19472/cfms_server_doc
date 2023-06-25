权限与用户组
===================================

.. autosummary::
   :toctree: generated

.. role:: python(code)
   :language: python

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

:python:`ifMatchRequirements()` 将依次检查各个作为列表元素的字典（我们称之为“首级字典”）所描述的规则是否被满足。在首级字典中，即可以通过改变 "match" 的键值来
确定匹配的规则：它接受 "any" 或 "all" 作为有效值，若出现二者以外的情况则将抛出 :python:`ValueError` 异常。

每个首级字典只接受 "match_groups"（子规则的匹配组）这个列表作为要处理的细化规则。同样地，这个列表下的元素也是字典，具有同样的 match 作为匹配模式，并（与之前不同）
接受两个字典分别作为其 rights 和 groups 的键值。这些字典，同样地，可以使用 match 来确认匹配模式。

若没有给定 match 的值，则将默认以 all 模式进行匹配。

.. warning::
    注意！请不要随意添加没有设置任一所需权限和组的子匹配规则。尽管它们可能看起来是“空”的而被认为
    应该被忽略，但在某些情况下将可能导致整个匹配规则出现意料之外的结果。

.. versionchanged:: 1.0.0.20230625_alpha
   现在 :python:`ifMatchRequirements()` 仅接受 rules 作为参数。
