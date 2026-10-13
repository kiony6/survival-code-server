# 生存代码 - 联机服务器

## 部署到 Render（免费）

### 步骤

1. **注册 Render 账号**
   - 打开 https://render.com
   - 用 GitHub 账号注册（需要先有 GitHub 账号）

2. **上传代码到 GitHub**
   - 在 GitHub 创建一个新仓库，比如叫 `survival-code-server`
   - 把这个文件夹里的所有文件传上去：
     - app.py
     - requirements.txt
     - Dockerfile
     - admin.html

3. **在 Render 创建 Web Service**
   - 打开 https://dashboard.render.com
   - 点「New +」→「Web Service」
   - 连接你刚创建的 GitHub 仓库
   - 配置：
     - Name: 随便起个名字，比如 `survival-code`
     - Environment: 选 `Docker`
     - Region: 选靠近你的，比如 `Singapore` 或 `Tokyo`
     - Instance Type: 选 `Free`
   - 点「Create Web Service」

4. **等待部署完成**
   - 大约 2-3 分钟
   - 部署成功后会给你一个网址，比如：
     `https://survival-code.onrender.com`

5. **更新游戏客户端**
   - 打开 game_pygame.py
   - 找到 `SERVER_URL = '...'`
   - 改成你的 Render 网址

### 访问管理后台
```
https://你的网址.onrender.com/admin
```

### API 说明
- POST /create - 创建房间
- POST /join - 加入房间
- POST /sync - 同步状态
- POST /leave - 离开房间
- GET /admin - 管理后台页面
