#! /usr/bin/env python
# -*- coding: utf-8 -*- 
# By isaced - https://github.com/isaced/emlog2typecho

import MySQLdb

# 连接数据库...
conn=MySQLdb.connect(host='localhost',user='root',passwd='root',port=3306,charset='utf8')

# 切换emlog数据库...
conn.select_db('emlog')
cur=conn.cursor()

# 读取emlog所有分类
cur.execute('select sid, sortname, alias, ( select count( * ) from emlog_blog where sortid = sid ) AS count FROM emlog_sort')
emlog_sort_list = cur.fetchall()


# 读取Emlog所有Tag
cur.execute('select tid,tagname from emlog_tag')
emlog_tag_list = cur.fetchall()

# 读取emlog blog表...
cur.execute('select gid,title,date,content,excerpt,alias,sortid,type  from emlog_blog')
emlog_blog_list = cur.fetchall()

# 切换Typecho数据库...
conn.select_db('typecho')   
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

cur.close()
conn.close()

print '转移完成...'