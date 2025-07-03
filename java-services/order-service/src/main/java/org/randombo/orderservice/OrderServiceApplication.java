package org.randombo.orderservice;

import org.randombo.orderservice.service.OrderService; // 导入OrderService
import org.springframework.beans.factory.annotation.Autowired; // 导入Autowired
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;
import org.springframework.scheduling.annotation.Scheduled;
import java.time.LocalDateTime; // 导入LocalDateTime
import java.util.List; // 导入List

@SpringBootApplication
@EnableScheduling // 启用Spring的定时任务功能
public class OrderServiceApplication {

	// XXXX 将字段注入改为构造函数注入
	private final OrderService orderService; // 声明为final

	// 构造函数注入
	@Autowired
	public OrderServiceApplication(OrderService orderService) {
		this.orderService = orderService;
	}

	public static void main(String[] args) {
		SpringApplication.run(OrderServiceApplication.class, args);
	}

	// 定时任务：每隔5分钟检查一次长时间未支付的订单
	@Scheduled(fixedRate = 300000) // 300000毫秒 = 5分钟
	public void checkPendingOrdersForAnomaly() {
		System.out.println("Checking for long pending payment orders at " + LocalDateTime.now());
		List<org.randombo.orderservice.model.Order> abnormalOrders = orderService.findLongPendingPaymentOrders(10); // 查找超过10分钟未支付的订单
		if (!abnormalOrders.isEmpty()) {
			System.out.println("Found " + abnormalOrders.size() + " abnormal pending orders:");
			for (org.randombo.orderservice.model.Order order : abnormalOrders) {
				orderService.markOrderAsAbnormal(order.getOrderId(), "Order pending payment for too long.");
			}
		} else {
			System.out.println("No long pending payment orders found.");
		}
	}
}