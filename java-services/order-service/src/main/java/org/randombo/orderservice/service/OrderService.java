package org.randombo.orderservice.service;

import org.randombo.orderservice.model.Order;
// import org.randombo.orderservice.model.OrderStatus; // 确保此导入已移除或注释掉
import org.randombo.orderservice.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map; // 确保导入Map
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors; // 确保导入Collectors

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
    // 参数类型已从 Long 更改为 String
    public List<Order> findOrdersByUserId(String userId) {
        return orderRepository.findByUserId(userId);
    }

    // 4. 创建订单
    public Order createOrder(Order newOrder) {
        // 修正：如果传入的newOrder已经有orderId，则直接使用它 (为了测试重复订单号)
        if (newOrder.getOrderId() == null || newOrder.getOrderId().isEmpty()) {
            newOrder.setOrderId("ORDER-" + UUID.randomUUID().toString().substring(0, 8).toUpperCase()); // 正常情况下自动生成
        }

        // 新增：在保存前检查orderId的唯一性（程序层面检查）
        // 如果orderId已经存在，抛出异常，这将导致HTTP 400 Bad Request
        if (orderRepository.findByOrderId(newOrder.getOrderId()).isPresent()) {
            throw new IllegalArgumentException("Order ID " + newOrder.getOrderId() + " already exists. Please try again or use a different ID.");
        }

        newOrder.setOrderTime(LocalDateTime.now());
        newOrder.setStatus("PENDING_PAYMENT"); // 改为字符串
        newOrder.setTotalAmount(newOrder.calculateTotalAmount()); // 总金额由items计算
        Order savedOrder = orderRepository.save(newOrder);
        System.out.println("创建订单: " + savedOrder.getOrderId() + " 到数据库。");
        return savedOrder;
    }

    // 5. 模拟支付订单（修改订单状态并保存到数据库）
    public boolean simulatePayment(String orderId) {
        Optional<Order> orderOptional = orderRepository.findByOrderId(orderId);
        if (orderOptional.isPresent()) {
            Order order = orderOptional.get();
            if (order.getStatus().equals("PENDING_PAYMENT")) { // 使用 .equals() 比较字符串
                order.setStatus("PAID"); // 改为字符串
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
            // userId 字段现在是 String 类型，这里保持不变，因为它是直接从 updatedOrderData 获取 String 类型的值
            if (updatedOrderData.getUserId() != null) {
                existingOrder.setUserId(updatedOrderData.getUserId());
            }
            if (updatedOrderData.getShippingAddress() != null) {
                existingOrder.setShippingAddress(updatedOrderData.getShippingAddress());
            }
            if (updatedOrderData.getStatus() != null) {
                existingOrder.setStatus(updatedOrderData.getStatus());
            }

            // 修正：更安全地更新items集合 for @OneToMany with orphanRemoval=true
            if (updatedOrderData.getItems() != null) {
                // 创建一个Map，用于快速查找传入的订单项（以ID为键）
                Map<Long, Order.OrderItem> incomingItemsMap = updatedOrderData.getItems().stream()
                        .filter(item -> item.getId() != null) // 只处理有ID的（即已存在的或传入ID的）
                        .collect(Collectors.toMap(Order.OrderItem::getId, item -> item));

                // 1. 识别并移除不再存在于传入列表的旧订单项 (触发orphanRemoval)
                existingOrder.getItems().removeIf(existingItem ->
                        !incomingItemsMap.containsKey(existingItem.getId()) // 如果旧项的ID不在新项的Map中
                );

                // 2. 遍历传入的订单项，执行添加或更新操作
                updatedOrderData.getItems().forEach(incomingItem -> {
                    if (incomingItem.getId() == null) { // 这是新添加的订单项 (ID为null)
                        existingOrder.getItems().add(incomingItem); // 直接添加到集合，JPA会新增
                    } else { // 这是更新现有订单项 (ID不为null)
                        // 在现有集合中查找该订单项
                        existingOrder.getItems().stream()
                                .filter(existingItem -> existingItem.getId().equals(incomingItem.getId()))
                                .findFirst()
                                .ifPresentOrElse( // 如果找到了，则更新其属性
                                        foundItem -> {
                                            foundItem.setProductId(incomingItem.getProductId());
                                            foundItem.setProductName(incomingItem.getProductName());
                                            foundItem.setQuantity(incomingItem.getQuantity());
                                            foundItem.setUnitPrice(incomingItem.getUnitPrice());
                                        },
                                        // 如果没有找到 (可能在之前被清除了又加回来，或者原本就不在集合中)
                                        // 此时我们认为它是一个需要重新关联的项，直接添加即可。
                                        () -> existingOrder.getItems().add(incomingItem)
                                );
                    }
                });

                // items更新后，重新计算totalAmount
                existingOrder.setTotalAmount(existingOrder.calculateTotalAmount());
            } else {
                // 如果 updatedOrderData.getItems() 是 null，totalAmount 保持由现有items计算
                existingOrder.setTotalAmount(existingOrder.calculateTotalAmount());
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
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold); // 改为字符串
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
        return orderRepository.findByStatusAndOrderTimeBefore("PENDING_PAYMENT", threshold); // 改为字符串
    }

    // 12. 专门的订单状态转换方法
    public Optional<Order> updateOrderStatus(String orderId, String newStatusString) {
        return orderRepository.findByOrderId(orderId).map(order -> {
            if (newStatusString.equals("PENDING_PAYMENT") && !order.getStatus().equals("PENDING_PAYMENT")) {
                System.out.println("WARN: Cannot revert order " + orderId + " to PENDING_PAYMENT from " + order.getStatus());
                return null;
            }
            order.setStatus(newStatusString);
            Order updated = orderRepository.save(order);
            System.out.println("订单 " + orderId + " 状态更新为 " + newStatusString);
            return updated;
        });
    }
}