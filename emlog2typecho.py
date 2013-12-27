#! /usr/bin/env python
# -*- coding: utf-8 -*- 
#
# Descrption:emlog2typecho 是一个用python写的脚本，用来迁移Emlog的数据库到Typecho。
#
# Github: https://github.com/isaced/emlog2typecho
# Author: isaced@163.com

# 一些设置项

# Emlog 数据库名
emlog_database_name = 'emlog'
# Typecho 数据库名
typecho_database_name = 'typecho'
# 数据库地址
database_host = 'localhost'
# 数据库用户名
database_port = 3306
# 数据库用户名
database_user_name = 'root'
# 数据库用户名
database_user_password = 'root'
# 字符集
database_charset = 'utf8'

#################################################################################

import MySQLdb

# 连接数据库...
conn=MySQLdb.connect(host    =   database_host,
                     user    =   database_user_name,
                     passwd  =   database_user_password,
                     port    =   database_port,
                     charset =   database_charset)

# 切换emlog数据库...
conn.select_db(emlog_database_name)
cur=conn.cursor()

# 读取emlog所有分类
cur.execute('select sid, sortname, alias, ( select count( * ) from emlog_blog where sortid = sid ) AS count FROM emlog_sort')
emlog_sort_list = cur.fetchall()

# 读取Emlog所有Tag
cur.execute('select tid,tagname,gid from emlog_tag')
emlog_tag_list = []
for row in cur.fetchall():
    tagname = row[1]
    gid_list = row[2].split(',')

    # 移除列表中为空字符串的项
    for gid in gid_list:
        if gid == '':
            gid_list.remove(gid)
    # 组装
    tag = {'tagname':tagname,'gidlist':gid_list}
    emlog_tag_list.append(tag)


# 读取emlog blog表...
cur.execute('select gid,title,date,content,excerpt,alias,sortid,type  from emlog_blog')
emlog_blog_list = cur.fetchall()

# 切换Typecho数据库...
conn.select_db(typecho_database_name)   
cur=conn.cursor()

# 删除Typecho 所有分类和标签...
cur.execute('delete from typecho_metas')

# 插入emlog所有分类
for sort in emlog_sort_list:
    sort_id = sort[0]
    sort_name = sort[1]
    sort_sulg = sort[2] # sort[0] if sort[1] == '' else sort[1]
    sort_count = sort[3]
    cur.execute("insert into typecho_metas (mid, name, slug, type, description, `count`, `order`) VALUES (%s, %s, %s, 'category', NULL, %s, 0)" , (sort_id,sort_name, sort_sulg,sort_count))

# 删除Typecho 所有文章...
cur.execute('delete from typecho_contents')
# 删除文章所有关系
cur.execute('delete from typecho_relationships')

# 转移所有文章
for blog in emlog_blog_list:
    blog_id = blog[0]
    blog_title = blog[1]
    blog_create_date = blog[2]
    blog_content = blog[3]
    blog_excerpt = blog[4]

    # 不能为空字符串
    blog_alias = blog[5]
    if blog_alias == '':
        blog_alias = None

    # emlog     --> blog page
    # typecho   --> post page
    if blog[7] == 'blog':
        blog_type = 'post'
    else:
        blog_type = 'page'

    params = (blog_id,blog_title,blog_alias,blog_create_date,blog_content,blog_type)
    cur.execute("insert into `typecho_contents` (`cid`, `title`, `slug`, `created`, `modified`, `text`, `order`, `authorId`, `template`, `type`, `status`, `password`, `commentsNum`, `allowComment`, `allowPing`, `allowFeed`, `parent`) VALUES (%s, %s, %s, %s, NULL, %s, '0', '1', NULL, %s, 'publish', NULL, '0', '0', '0', '0', '0')",params)

    # 添加文章的relationships
    blog_sortid = blog[6]

    # emlog 中 分类id -1 为页面
    if blog_sortid == -1:
        continue
    cur.execute('insert into `typecho_relationships` (`cid`, `mid`) VALUES (%s, %s)',(blog_id,blog_sortid))

# 插入所有Tag（和关系）
cur.execute("select MAX( mid ) FROM `typecho_metas`")
sort_max_id = cur.fetchall()[0][0] + 1 
# 从刚插入的分类最后一个ID+1作为ID开始循环插入
for tag in emlog_tag_list:
    cur.execute("insert into `typecho_metas` (`mid`, `name`, `slug`, `type`, `description`, `count`, `order`) VALUES (%s, %s, NULL, 'tag', NULL, %s, '0');",(sort_max_id,tag['tagname'],len(tag['gidlist'])))
    for gid in tag['gidlist']:
        params = (int(gid),sort_max_id)
        # ！有时会遇到重复项插入失败跳过
        try:
            cur.execute('insert into `typecho_relationships` (`cid`, `mid`) VALUES (%s, %s)',params)
        except:
            print '失败一条Tag:%s,%s' % (params)
    sort_max_id = sort_max_id + 1

cur.close()
conn.close()

print '转移完成...'