# Docker镜像管理系统

一个基于Web的Docker镜像管理系统，提供镜像搜索、拉取、删除等功能，支持实时进度显示。


## 功能特点

- 🔍 镜像搜索：支持搜索Docker Hub上的镜像
- 📥 镜像拉取：支持选择特定标签进行拉取，实时显示进度
- 📋 本地管理：查看和管理本地Docker镜像
- 🗑️ 镜像删除：支持删除本地镜像，包括多标签镜像
- 💡 用户友好：简洁的界面设计，清晰的操作反馈

## 技术栈

### 后端
- Python Flask
- Docker SDK for Python
- Server-Sent Events (SSE)

### 前端
- Vue.js 3
- Element Plus UI
- Axios

## 项目结构

```
docker/
├── backend/                # 后端代码
│   ├── app.py             # Flask应用主文件
│   └── requirements.txt   # Python依赖
├── frontend/              # 前端代码
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── services/      # API服务
│   │   └── main.js        # 入口文件
│   ├── package.json       # NPM配置
│   └── vite.config.js     # Vite配置
└── README.md              # 项目文档
```

## API 接口文档

### 1. 获取本地镜像列表
- **接口**: `GET /api/images`
- **描述**: 获取本地所有Docker镜像
- **响应示例**:
  ```json
  [
    {
      "Id": "sha256:...",
      "RepoTags": ["nginx:latest"],
      "Size": 142862666
    }
  ]
  ```

### 2. 搜索镜像
- **接口**: `GET /api/images/search`
- **参数**: 
  - `term`: 搜索关键词
- **响应示例**:
  ```json
  [
    {
      "name": "nginx",
      "description": "Official build of Nginx",
      "stars": 15000,
      "official": true,
      "automated": false
    }
  ]
  ```

### 3. 获取镜像标签
- **接口**: `GET /api/images/tags`
- **参数**:
  - `name`: 镜像名称
- **响应示例**:
  ```json
  [
    {
      "name": "latest",
      "full_size": 142862666,
      "last_updated": "2024-12-14T10:00:00Z",
      "architectures": ["amd64", "arm64"],
      "os": "linux"
    }
  ]
  ```

### 4. 拉取镜像
- **接口**: `POST /api/images/pull`
- **请求体**:
  ```json
  {
    "name": "nginx:latest"
  }
  ```
- **响应示例**:
  ```json
  {
    "task_id": "1234567890",
    "message": "Pull task started"
  }
  ```

### 5. 获取拉取进度
- **接口**: `GET /api/images/pull/progress/<task_id>`
- **类型**: Server-Sent Events (SSE)
- **事件数据示例**:
  ```json
  {
    "status": "downloading",
    "progress": 45.5,
    "message": "正在下载层 abc123: 45.5%"
  }
  ```

### 6. 删除镜像
- **接口**: `DELETE /api/images/<image_id>`
- **响应示例**:
  ```json
  {
    "message": "镜像删除成功"
  }
  ```

## 安装说明

### 后端安装
1. 进入backend目录
2. 创建虚拟环境（推荐）：
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
4. 启动服务器：
   ```bash
   python app.py
   ```

### 前端安装
1. 进入frontend目录
2. 安装依赖：
   ```bash
   npm install
   ```
3. 启动开发服务器：
   ```bash
   npm run dev
   ```

### 前端打包部署
1. 在frontend目录下执行打包命令：
   ```bash
   npm run build
   ```
2. 打包完成后会在frontend/dist目录下生成静态文件
3. 部署方式：
   - 方式一：使用Nginx部署
     ```nginx
     server {
         listen 80;
         server_name your_domain.com;

         location / {
             root /path/to/frontend/dist;
             index index.html;
             try_files $uri $uri/ /index.html;
         }

         # 后端API代理
         location /api {
             proxy_pass http://localhost:5000;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
         }
     }
     ```
   - 方式二：使用Docker部署（推荐）
     ```dockerfile
     # 前端Dockerfile
     FROM nginx:alpine
     COPY dist/ /usr/share/nginx/html/
     COPY nginx.conf /etc/nginx/conf.d/default.conf
     EXPOSE 80
     ```
     
     ```bash
     # 构建和运行Docker容器
     docker build -t docker-manager-frontend .
     docker run -d -p 80:80 docker-manager-frontend
     ```

4. 环境配置：
   - 开发环境配置文件：`.env.development`
     ```env
     # 开发环境使用本地后端服务
     VITE_API_URL=http://localhost:5000/api
     ```
   - 生产环境配置文件：`.env.production`
     ```env
     # 生产环境使用相对路径，由Nginx配置代理
     VITE_API_URL=/api
     ```
5. 打包优化：
   - 启用生产环境优化：
     ```bash
     npm run build -- --mode production
     ```
   - 查看打包分析：
     ```bash
     npm run build -- --report
     ```

6. 注意事项：
   - 确保API地址配置正确
   - 检查跨域配置
   - 确保路由配置正确（使用history模式需要服务器配置支持）
   - 静态资源路径使用相对路径

## 使用说明

1. **搜索镜像**
   - 点击搜索框输入关键词
   - 选择需要的镜像和标签
   - 点击拉取按钮开始下载

2. **查看本地镜像**
   - 在主页面可以看到所有本地镜像
   - 显示镜像ID、标签和大小等信息

3. **删除镜像**
   - 点击镜像列表中的删除按钮
   - 确认删除操作
   - 系统会自动处理多标签镜像的删除

## 注意事项

- 确保Docker守护进程正在运行
- 后端服务需要有Docker API的访问权限
- 删除镜像时要注意是否有容器正在使用该镜像
- 拉取大型镜像时请保持耐心，进度会实时显示

## 开发计划

- [ ] 添加镜像导出功能
- [ ] 支持私有镜像仓库
- [ ] 添加镜像构建功能
- [ ] 支持容器管理
- [ ] 添加用户认证系统

## 贡献指南

欢迎提交Issue和Pull Request来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试用例
3. 更新相关文档

## 许可证

本项目采用 MIT 许可证。
