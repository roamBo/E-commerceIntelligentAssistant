package org.randombo.orderservice.controller;

import org.randombo.orderservice.model.Order;
// import org.randombo.orderservice.model.OrderStatus; // XXXX 移除此导入
import org.randombo.orderservice.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;
import jakarta.validation.Valid;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/orders") // 定义基础路径
public class OrderController {

    @Autowired
    private OrderService orderService;

    // 1. 获取所有订单：GET /api/orders
    @GetMapping
    public List<Order> getAllOrders() {
        return orderService.getAllOrders();
    }

    // 2. 根据订单ID查询订单：GET /api/orders/{orderId}
    // 这是订单查询功能的核心API之一
    @GetMapping("/{orderId}")
    public ResponseEntity<Order> getOrderByOrderId(@PathVariable String orderId) {
        return orderService.getOrderByOrderId(orderId)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 3. 根据用户ID查询订单：GET /api/orders/user/{userId}
    // 这是订单查询功能的核心API之二
    @GetMapping("/user/{userId}")
    public List<Order> getOrdersByUserId(@PathVariable Long userId) {
        return orderService.findOrdersByUserId(userId);
    }

    // 4. 创建订单：POST /api/orders
    // 智能客服可能通过此API创建新的订单
    @PostMapping
    public Order createOrder(@Valid @RequestBody Order order) {
        return orderService.createOrder(order);
    }

    // 5. 模拟支付订单：POST /api/orders/{orderId}/pay
    // 智能客服引导用户支付后，可以调用此API更新订单状态
    @PostMapping("/{orderId}/pay")
    public ResponseEntity<String> simulatePayment(@PathVariable String orderId) {
        boolean success = orderService.simulatePayment(orderId);
        if (success) {
            return ResponseEntity.ok("订单 " + orderId + " 支付成功模拟。");
        } else {
            return ResponseEntity.badRequest().body("订单 " + orderId + " 无法支付或已支付。");
        }
    }

    // 6. 通用订单更新 API: PUT /api/orders/{orderId}
    @PutMapping("/{orderId}")
    public ResponseEntity<Order> updateOrder(@PathVariable String orderId, @Valid @RequestBody Order orderDetails) {
        return orderService.updateOrder(orderId, orderDetails)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 7. 删除订单 API (通过数据库自动生成的id)
    @DeleteMapping("/id/{id}")
    public ResponseEntity<Void> deleteOrderById(@PathVariable Long id) {
        boolean deleted = orderService.deleteOrder(id);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    // 8. 删除订单 API (通过业务orderId，更常用)
    @DeleteMapping("/{orderId}")
    public ResponseEntity<Void> deleteOrderByOrderId(@PathVariable String orderId) {
        boolean deleted = orderService.deleteOrderByOrderId(orderId);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }

    // 9. 查询异常订单的 API 接口
    @GetMapping("/abnormal")
    public List<Order> getAbnormalOrders(@RequestParam(defaultValue = "10") long minutes) {
        return orderService.getAbnormalPendingOrders(minutes);
    }

    // 10. 专门的订单状态转换 API
    @PutMapping("/{orderId}/status/{newStatus}")
    public ResponseEntity<Order> updateOrderStatus(@PathVariable String orderId, @PathVariable String newStatus) { // XXXX 接收String
        // 直接将字符串传给Service层，Service层处理业务逻辑
        return orderService.updateOrderStatus(orderId, newStatus) // XXXX 直接传入字符串
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.badRequest().build());
    }
}