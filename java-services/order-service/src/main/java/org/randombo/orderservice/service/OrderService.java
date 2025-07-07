package org.randombo.orderservice.service;

import org.randombo.orderservice.model.Order;
import org.randombo.orderservice.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    // 1. 获取所有订单
    public List<Order> getAllOrders() {
        return orderRepository.findAll();
    }

    // 2. 根据订单ID查询订单
    public Optional<Order> getOrderByOrderId(String orderId) {
        return orderRepository.findByOrderId(orderId);
    }

    // 3. 根据用户ID查询订单列表
    public List<Order> findOrdersByUserId(Long userId) { // 方法名改为 findOrdersByUserId 以避免与findAllById冲突
        return orderRepository.findByUserId(userId);
    }

    // 4. 创建订单
    public Order createOrder(Order newOrder) {
        newOrder.setOrderId("ORDER-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        newOrder.setOrderTime(LocalDateTime.now());
        newOrder.setStatus("PENDING_PAYMENT");
        Order savedOrder = orderRepository.save(newOrder);
        System.out.println("创建订单: " + savedOrder.getOrderId() + " 到数据库。");
        return savedOrder;
    }

    // 5. 模拟支付订单（修改订单状态并保存到数据库）
    public boolean simulatePayment(String orderId) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            Order order = orderOptional.get();
            if ("PENDING_PAYMENT".equals(order.getStatus())) {
                order.setStatus("PAID");
                orderRepository.save(order);
                System.out.println("订单 " + orderId + " 已支付并更新到数据库。");
                return true;
            }
        }
        return false;
    }

    // 6. 通用订单更新方法
    public Optional<Order> updateOrder(String orderId, Order updatedOrderData) {
        return orderRepository.findByOrderId(orderId).map(existingOrder -> {
            if (updatedOrderData.getUserId() != null) {
                existingOrder.setUserId(updatedOrderData.getUserId());
            }
            if (updatedOrderData.getTotalAmount() != null) {
                existingOrder.setTotalAmount(updatedOrderData.getTotalAmount());
            }
            if (updatedOrderData.getShippingAddress() != null) {
                existingOrder.setShippingAddress(updatedOrderData.getShippingAddress());
            }
            if (updatedOrderData.getStatus() != null) {
                existingOrder.setStatus(updatedOrderData.getStatus());
            }
            return orderRepository.save(existingOrder);
        });
    }

    // 7. 删除订单方法 (通过数据库ID)
    public boolean deleteOrder(Long id) {
        Optional<Order> orderOptional = orderRepository.findById(id); // 通过数据库ID查找订单
        if (orderOptional.isPresent()) {
            orderRepository.deleteById(id); // 从数据库删除订单
            System.out.println("订单 ID: " + id + " 已从数据库删除。");
            return true;
        }
        return false;
    }

    // 8. 根据业务orderId删除订单 (更常用，因为API通常通过业务ID操作)
    public boolean deleteOrderByOrderId(String orderId) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId); // 通过业务orderId查找订单
        if (orderOptional.isPresent()) {
            orderRepository.delete(orderOptional.get()); // 从数据库删除订单实体
            System.out.println("订单 Order ID: " + orderId + " 已从数据库删除。");
            return true;
        }
        return false;
    }

    // 9. 查找长时间未支付的订单（异常预警逻辑）
    public List<Order> findLongPendingPaymentOrders(long minutes) {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(minutes);
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold);
    }

    // 10. 异常处理示例：标记异常订单或记录日志
    public void markOrderAsAbnormal(String orderId, String anomalyReason) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            Order order = orderOptional.get();
            // 实际中可能新增一个anomalyStatus字段，或发送事件
            System.out.println("ALERT: Order " + orderId + " is abnormal. Reason: " + anomalyReason);
            // 可以在这里更新订单状态为 "ANOMALY" 或触发其他内部流程
        }
    }
    // XXXX 新增：通过API查询异常订单的方法
    public List<Order> getAbnormalPendingOrders(long minutes) {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(minutes);
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold);
    }
}