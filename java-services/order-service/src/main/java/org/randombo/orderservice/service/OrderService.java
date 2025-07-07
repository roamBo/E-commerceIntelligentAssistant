package org.randombo.orderservice.service;

import org.randombo.orderservice.model.Order;
// import org.randombo.orderservice.model.OrderStatus; // XXXX 移除此导入
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
    public List<Order> findOrdersByUserId(Long userId) {
        return orderRepository.findByUserId(userId);
    }

    // 4. 创建订单
    public Order createOrder(Order newOrder) {
        newOrder.setOrderId("ORDER-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase());
        newOrder.setOrderTime(LocalDateTime.now());
        newOrder.setStatus("PENDING_PAYMENT"); // XXXX 改为字符串
        Order savedOrder = orderRepository.save(newOrder);
        System.out.println("创建订单: " + savedOrder.getOrderId() + " 到数据库。");
        return savedOrder;
    }

    // 5. 模拟支付订单（修改订单状态并保存到数据库）
    public boolean simulatePayment(String orderId) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            Order order = orderOptional.get();
            if (order.getStatus().equals("PENDING_PAYMENT")) { // XXXX 使用 .equals() 比较字符串
                order.setStatus("PAID"); // XXXX 改为字符串
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
            // updatedOrderData.getStatus() 现在是String类型
            if (updatedOrderData.getStatus() != null) {
                existingOrder.setStatus(updatedOrderData.getStatus());
            }
            return orderRepository.save(existingOrder);
        });
    }

    // 7. 删除订单方法 (通过数据库ID)
    public boolean deleteOrder(Long id) {
        Optional<Order> orderOptional = orderRepository.findById(id);
        if (orderOptional.isPresent()) {
            orderRepository.deleteById(id);
            System.out.println("订单 ID: " + id + " 已从数据库删除。");
            return true;
        }
        return false;
    }

    // 8. 根据业务orderId删除订单 (更常用)
    public boolean deleteOrderByOrderId(String orderId) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            orderRepository.delete(orderOptional.get());
            System.out.println("订单 Order ID: " + orderId + " 已从数据库删除。");
            return true;
        }
        return false;
    }

    // 9. 查找长时间未支付的订单（异常预警逻辑）
    public List<Order> findLongPendingPaymentOrders(long minutes) {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(minutes);
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold); // XXXX 改为字符串
    }

    // 10. 异常处理示例：标记异常订单或记录日志
    public void markOrderAsAbnormal(String orderId, String anomalyReason) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            Order order = orderOptional.get();
            System.out.println("ALERT: Order " + orderId + " is abnormal. Reason: " + anomalyReason);
        }
    }

    // 11. 通过API查询异常订单的方法
    public List<Order> getAbnormalPendingOrders(long minutes) {
        LocalDateTime threshold = LocalDateTime.now().minusMinutes(minutes);
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold); // XXXX 改为字符串
    }

    // 12. 专门的订单状态转换方法
    public Optional<Order> updateOrderStatus(String orderId, String newStatusString) { // XXXX 接收String
        return orderRepository.findByOrderId(orderId).map(order -> {
            // XXXX 修正逻辑：直接用字符串比较和赋值
            if (newStatusString.equals("PENDING_PAYMENT") && !order.getStatus().equals("PENDING_PAYMENT")) {
                System.out.println("WARN: Cannot revert order " + orderId + " to PENDING_PAYMENT from " + order.getStatus());
                return null;
            }
            order.setStatus(newStatusString); // XXXX 直接赋值字符串
            Order updated = orderRepository.save(order);
            System.out.println("订单 " + orderId + " 状态更新为 " + newStatusString);
            return updated;
        });
    }
}