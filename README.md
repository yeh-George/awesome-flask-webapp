# AWESOME-FLASK-WEBAPP

这是Yeh George使用flask框架以及多种FLASK扩展搭建的blog webapp。

**Demo**：[awesome-flask-webapp](http://yeh.pythonanywhere.com)
 
---

## 主要实现以下功能：

### 1. 角色与权限管理  

> Permission和Role模型 

 
### 2. 注册/登录页面
+ #### 注册  
> 使用Flask-Mail进行邮件验证，同时支持更换邮箱邮件验证、重设密码邮件验证  
> 使用Flask-Avatars生成用户头像
+ #### 登录  
> 使用Flask-Login实现用户登录管理  

+ #### 第三方登录  
> 使用Authlib实现GitHub第三方登录

### 3. 用户浏览页面
+ #### 首页、发布文章、标签、分类、文章详情、评论、收藏文章  
  > + 主要功能发布文章，展示文章详情、评论以及收藏文章，同时实现文章的标签、分类展示  
  > + 使用Bootstrap-Flask实现前端页面效果，Flask-Moment增强时间显示效果， Flask-CKEditor富文本编辑器


+ #### 用户资料弹窗、文章收藏、用户关注、用户消息提醒及定时更新消息数  
    + 用户资料弹窗：
      > 监听hover事件并使用setTimeout()实现鼠标悬停一段时间后才触发弹窗显示，鼠标离开一段时间后才触发弹窗小时
      > 使用jQuery的ajax()方法动态获取用户资料数据，关注用户  
    + 定时更新消息提醒数  
      > 使用setInterval和ajax()实现消息提醒的定时更新  
  
  
+ #### 全文搜索  
> 使用Flask-Whooshee实现对文章标题、内容、用户名、标签的内容搜索

### 4. 用户详情页面
+ #### 发布文章、收藏文章、关注者及被关注者信息展示，用户信息设置  
> 主要是展示用户的相关信息，同时可以自定义用户设置

### 5. 管理页面
+ 管理账号：锁定、封禁、协管员权限  

+ 管理文章、评论、分类、标签


## 计划进一步实现的功能：
1. ~Redis~ 使用Redis结合Flask-Caching扩展实现视图函数的缓存
2. ~Web API~ 使用api_v1蓝本加上MethodView方法视图编写了User、Post的部分Web API，为未来实现自己的Blog客户端提供响应数据服务
3. ~OAuth认证~ 基于认证将仅限在本网站的Blog客户端使用，采用Resource Owner Password Credentials认证模式，借助与Flask依赖包itrdangerous生成有过期时间的JWS access令牌，客户端在发送请求访问受认证保护的端点时，需要在首部字段Authorization中加入认证令牌
4. 使用Vue框架实现MVVM
3. 手机验证码注册账号
