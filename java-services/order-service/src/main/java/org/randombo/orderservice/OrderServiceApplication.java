package org.randombo.orderservice;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling; // 保持此导入，因为全局调度在此启用
//space for merge
@SpringBootApplication
@EnableScheduling // 启用Spring的定时任务功能 (保持)
public class OrderServiceApplication {


	public static void main(String[] args) {
		SpringApplication.run(OrderServiceApplication.class, args);
	}


}