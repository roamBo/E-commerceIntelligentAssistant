# service_launcher.py
import threading
import time
import logging
from agent_service import NacosService
from api_service import run_fastapi

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ServiceLauncher")


def run_nacos_service():
    """运行Nacos服务"""
    logger.info("Starting Nacos service")
    service = NacosService(
        service_name="agents-service",
        ip="10.172.66.224",
        port=8085
    )
    service.run()


def main():
    """主函数，启动两个服务线程"""
    # 创建并启动Nacos线程
    nacos_thread = threading.Thread(
        target=run_nacos_service,
        name="NacosServiceThread",
        daemon=True
    )
    nacos_thread.start()
    logger.info("Nacos service thread started")

    # 创建并启动FastAPI线程
    fastapi_thread = threading.Thread(
        target=run_fastapi,
        name="FastAPIThread",
        daemon=True
    )
    fastapi_thread.start()
    logger.info("FastAPI service thread started")

    # 主线程等待所有服务线程结束
    try:
        while True:
            # 检查线程状态
            if not nacos_thread.is_alive():
                logger.error("Nacos service thread has stopped")

            if not fastapi_thread.is_alive():
                logger.error("FastAPI service thread has stopped")

            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down services")
        # 这里可以添加更优雅的关闭逻辑
        # 例如调用服务的stop方法

if __name__ == "__main__":
    main()