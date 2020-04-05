# awesome-flask-webapp

这是Yeh George使用flask框架以及多种FLASK扩展搭建的blog webapp。

Demo：[awesome-flask-webapp]<http://yeh.pythonanywhere.com>
 
---

## 主要实现以下功能：

### 1. 角色与权限管理  

 Permission和Role模型 
 
### 2. 注册/登录页面
+ #### 注册  
> 使用FLASK-MAIL进行邮件验证  
> 使用FLASK-Avatars生成用户头像
+ #### 登录  
> 使用FLASK-LOGIN实现用户登录管理
+ #### 第三方登录  
使用Authlib实现GitHub第三方登录

### 3. 用户浏览页面
+ #### 首页、发布文章、标签、分类、文章详情、评论、收藏文章
主要功能发布文章，展示文章详情、评论以及收藏文章，同时实现文章的标签、分类展示

+ #### 用户资料弹窗、文章收藏、用户关注、用户消息提醒及轮询更新消息数  
用户资料弹窗：
  + 监听hover事件并使用setTimeout()实现鼠标悬停一段事件后才触发弹窗  
  + 使用jQuery的ajax()方法动态获取用户资料数据，关注用户  
  + 使用setInterval和ajax()实现消息提醒的定时更新  
  
+ #### 全文搜索  
使用FLASK-Whooshee实现对文章标题、内容、用户名、标签的内容搜索

### 4. 用户详情页面
+ #### 发布文章、收藏文章、关注者及被关注者信息展示，用户信息设置  
主要是展示用户的相关信息，同时可以自定义用户设置

### 5. 管理页面
+ 管理账户：锁定、封禁、协管员权限  

+ 管理文章、评论、分类、标签


