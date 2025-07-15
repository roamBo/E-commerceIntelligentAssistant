import time
from nacos import NacosClient
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NacosService")


class NacosService:
    def __init__(self, service_name, ip, port):
        self.service_name = service_name
        self.ip = ip
        self.port = port
        self.running = False

        # 创建Nacos客户端
        self.client = NacosClient(
            server_addresses="10.172.66.224",
            namespace="public"
        )

    def register(self):
        """注册服务到Nacos"""
        try:
            result = self.client.add_naming_instance(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                cluster_name="DEFAULT"
            )
            logger.info(f"服务 {self.service_name} 注册结果: {result}")
            return True
        except Exception as e:
            logger.error(f"服务注册失败: {e}")
            return False

    def send_heartbeat(self):
        """发送心跳"""
        try:
            result = self.client.send_heartbeat(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port,
                cluster_name="INFO"
            )
            logger.debug(f"心跳发送结果: {result}")
        except Exception as e:
            logger.error(f"心跳发送失败: {e}")

    def run(self):
        """运行服务"""
        if self.register():
            logger.info(f"服务 {self.service_name} 注册成功")
            self.running = True

            try:
                while self.running:
                    self.send_heartbeat()
                    time.sleep(5)  # 每5秒发送一次心跳
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        """停止服务"""
        if self.running:
            self.running = False
            self.client.remove_naming_instance(
                service_name=self.service_name,
                ip=self.ip,
                port=self.port
            )
            logger.info(f"服务 {self.service_name} 已注销")


def nacos_main():
    """Nacos服务主函数"""
    service = NacosService(
        service_name="agents-service",
        ip="10.172.66.224",
        port=8085
    )
    service.run()


if __name__ == "__main__":
    nacos_main()