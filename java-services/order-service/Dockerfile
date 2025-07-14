# 基础镜像
FROM openjdk:17-jdk-alpine

# 指定工作目录
WORKDIR /app

# 将 jar 包添加到工作目录
ADD target/order-service-0.0.1-SNAPSHOT.jar .

# 暴露端口（与 application.yml 中 server.port 保持一致）
EXPOSE 8083

# 启动命令（激活 prod 配置）
ENTRYPOINT ["java", "-jar", "/app/order-service-0.0.1-SNAPSHOT.jar", "--spring.profiles.active=prod"]
