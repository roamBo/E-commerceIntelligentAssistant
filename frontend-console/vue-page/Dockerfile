# 使用 Node.js 20 LTS 版本，避免 crypto.hash 报错
FROM node:20.12.2

# 设置工作目录
WORKDIR /app

# 拷贝依赖清单并安装
COPY package*.json ./
RUN npm install

# 拷贝完整项目代码
COPY . .

# 暴露开发端口（vite 默认是 5173，但你也可以映射为 80）
EXPOSE 5173

# 启动开发服务器
CMD ["npm", "run", "dev"]
