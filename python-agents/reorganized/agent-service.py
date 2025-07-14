import time
from nacos import NacosClient

# 配置Nacos服务器信息
SERVER_ADDRESSES = "10.172.131.142"
NAMESPACE = "public"

# 创建Nacos客户端实例
client = NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE)


# 服务注册函数
def register_service(service_name, ip, port, weight=1.0, cluster_name="DEFAULT"):
    """
    注册服务到Nacos

    参数:
    service_name (str): 服务名称
    ip (str): 服务IP地址
    port (int): 服务端口
    weight (float): 服务权重，默认为1.0
    cluster_name (str): 集群名称，默认为"DEFAULT"

    返回:
    bool: 注册成功返回True，失败返回False
    """
    try:
        # 注册服务实例
        result = client.add_naming_instance(
            service_name=service_name,
            ip=ip,
            port=port,
            weight=weight,
            cluster_name=cluster_name
        )
        print(f"服务 {service_name} 注册结果: {result}")
        return True
    except Exception as e:
        print(f"服务注册失败: {e}")
        return False


# 服务心跳维持函数
def send_heartbeat(service_name, ip, port, cluster_name="DEFAULT"):
    """
    向Nacos发送服务心跳

    参数:
    service_name (str): 服务名称
    ip (str): 服务IP地址
    port (int): 服务端口
    cluster_name (str): 集群名称，默认为"DEFAULT"
    """
    try:
        # 发送心跳
        result = client.send_heartbeat(
            service_name=service_name,
            ip=ip,
            port=port,
            cluster_name=cluster_name
        )
        print(f"服务 {service_name} 心跳发送结果: {result}")
    except Exception as e:
        print(f"心跳发送失败: {e}")


# 主函数
def main():
    # 配置服务信息
    SERVICE_NAME = "agents-service"
    IP = "10.172.131.142"  # 请修改为实际服务IP
    PORT = 8085  # 请修改为实际服务端口

    # 注册服务
    if register_service(SERVICE_NAME, IP, PORT):
        print(f"服务 {SERVICE_NAME} 注册成功")

        # 模拟服务运行，定期发送心跳
        try:
            while True:
                send_heartbeat(SERVICE_NAME, IP, PORT)
                time.sleep(5)  # 每5秒发送一次心跳
        except KeyboardInterrupt:
            # 取消注册服务
            client.remove_naming_instance(
                service_name=SERVICE_NAME,
                ip=IP,
                port=PORT
            )
            print(f"服务 {SERVICE_NAME} 已注销")


if __name__ == "__main__":
    main()