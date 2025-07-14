package org.randombo.orderservice.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;
import jakarta.validation.constraints.Min;

@Entity
@Table(name = "orders")
@Data
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String orderId;
    private String userId; // 已将 userId 类型从 Long 改为 String
    @Min(0) // totalAmount 不能为负数 (已存在, 确认)
    private Double totalAmount; // 此字段将由商品价格总和计算得到
    private LocalDateTime orderTime;
    private String status;
    private String shippingAddress;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true)
    @JoinColumn(name = "order_id_fk")
    private List<OrderItem> items;

    @Entity
    @Table(name = "order_items")
    @Data
    public static class OrderItem {
        @Id
        @GeneratedValue(strategy = GenerationType.IDENTITY)
        private Long id;
        private String productId;
        private String productName;
        @Min(0) // 数量不能为负数
        private Integer quantity;
        @Min(0) // 单价不能为负数
        private Double unitPrice;

        public OrderItem() {}
        public OrderItem(String productId, String productName, Integer quantity, Double unitPrice) {
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }

        public Double calculateItemTotal() {
            return this.quantity * this.unitPrice;
        }
    }

    public Order() {}
    // 构造函数已更新，现在接受 String 类型的 userId
    public Order(String orderId, String userId, LocalDateTime orderTime, String status, String shippingAddress, List<OrderItem> items) {
        this.orderId = orderId;
        this.userId = userId; // 参数类型已更改
        this.orderTime = orderTime;
        this.status = status;
        this.shippingAddress = shippingAddress;
        this.items = items;
    }

    public Double calculateTotalAmount() {
        if (this.items == null || this.items.isEmpty()) {
            return 0.0;
        }
        return this.items.stream()
                .mapToDouble(OrderItem::calculateItemTotal) // 使用 OrderItem 的 calculateItemTotal 方法
                .sum();
    }
}