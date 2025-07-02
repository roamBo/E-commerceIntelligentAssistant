package org.randombo.productservice;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

@SpringBootApplication                 // 启动 Spring Boot 自动配置
@EnableDiscoveryClient                // 开启服务注册/发现（Nacos、Eureka 等）
@EnableFeignClients(basePackages = {  // 开启 Feign，扫描接口包
		"org.randombo.api"            // 你放 Feign Client 接口的包，可自行修改
})
public class ProductServiceApplication {

	public static void main(String[] args) {
		SpringApplication.run(ProductServiceApplication.class, args);
	}

	/**
	 * 可选：如果你还有直调 REST 接口的场景，声明一个负载均衡版 RestTemplate
	 * （Spring Cloud 2023+ 默认集成 Spring Cloud LoadBalancer）
	 */
	@Bean
	public RestTemplate restTemplate() {
		return new RestTemplate();
	}
}
