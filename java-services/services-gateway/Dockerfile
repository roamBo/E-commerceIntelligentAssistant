# 基础镜像
FROM openjdk:17-alpine

# 工作目录
WORKDIR /app

# 拷贝打好包的 JAR（假设已 mvn package 产出）
ADD target/services-gateway-0.0.1-SNAPSHOT.jar .

# 暴露端口，跟 application.yml 保持一致
EXPOSE 8084

# 启动命令，激活 prod 配置
ENTRYPOINT ["java","-jar","/app/services-gateway-0.0.1-SNAPSHOT.jar","--spring.profiles.active=prod"]
