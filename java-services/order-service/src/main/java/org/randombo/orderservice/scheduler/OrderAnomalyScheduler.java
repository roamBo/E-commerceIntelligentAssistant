package org.randombo.orderservice.scheduler; // 确保包名与你的项目路径匹配

import org.randombo.orderservice.model.Order; // 导入Order实体
import org.randombo.orderservice.service.OrderService; // 导入OrderService
import org.springframework.beans.factory.annotation.Autowired; // 导入Autowired
import org.springframework.scheduling.annotation.Scheduled; // 导入Scheduled
import org.springframework.stereotype.Component; // 导入Component

import java.time.LocalDateTime; // 导入LocalDateTime
import java.util.List; // 导入List

@Component // 标记为Spring组件，使其能被扫描并管理定时任务
public class OrderAnomalyScheduler {

    private final OrderService orderService; // 构造函数注入

    @Autowired
    public OrderAnomalyScheduler(OrderService orderService) {
        this.orderService = orderService;
    }

    // 定时任务：每隔5分钟检查一次长时间未支付的订单
    @Scheduled(fixedRate = 300000) // 300000毫秒 = 5分钟
    public void checkPendingOrdersForAnomaly() {
        System.out.println("Checking for long pending payment orders at " + LocalDateTime.now());
        List<Order> abnormalOrders = orderService.findLongPendingPaymentOrders(10); // 查找超过10分钟未支付的订单
        if (!abnormalOrders.isEmpty()) {
            System.out.println("Found " + abnormalOrders.size() + " abnormal pending orders:");
            for (Order order : abnormalOrders) {
                orderService.markOrderAsAbnormal(order.getOrderId(), "Order pending payment for too long.");
            }
        } else {
            System.out.println("No long pending payment orders found.");
        }
    }
}