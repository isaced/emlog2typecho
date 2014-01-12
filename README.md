Emlog2Typecho
=============

emlog2typecho 是一个用python写的脚本，用来迁移Emlog的数据库到Typecho。

###使用方法

1. 在本地新建emlog数据库并导入需要转换的数据
2. 再安装Typecho来建立Typecho的数据库
3. 在脚本中设置两个数据库名（默认是“emlog”和“typecho”）
4. 运行emlog2typecho.py
5. 备份Typecho数据库，上传到你的博客

###注意

- 此Python代码用到了MySQLdb库来连接MySQL，没有这个包的可以用pip安装：` pip install MySQL-python `
- Typecho最好是新安装出来的空数据库，以免出现不必要的麻烦

###状态
转移数据	| 状态
------	| ----
分类		| √ 
文章		| √ 
页面		| √ 
标签		| √
评论		| √
基本设置	| ...

###作者

[isaced](http://www.isaced.com)

> 有什么问题欢迎反馈，也希望大家一起优化完善本脚本。