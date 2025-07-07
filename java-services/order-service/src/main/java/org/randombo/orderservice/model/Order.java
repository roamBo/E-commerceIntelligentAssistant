package org.randombo.orderservice.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "orders")
@Data
public class Order {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String orderId;
    private Long userId;
    private Double totalAmount;
    private LocalDateTime orderTime;
    // XXXX 移除 @Enumerated 注解
    private String status; // XXXX 将类型改回 String
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
        private Integer quantity;
        private Double unitPrice;

        public OrderItem() {}
        public OrderItem(String productId, String productName, Integer quantity, Double unitPrice) {
            this.productId = productId;
            this.productName = productName;
            this.quantity = quantity;
            this.unitPrice = unitPrice;
        }
    }

    public Order() {}
    public Order(String orderId, Long userId, Double totalAmount, LocalDateTime orderTime, String status, String shippingAddress, List<OrderItem> items) { // XXXX 构造函数中status类型改为 String
        this.orderId = orderId;
        this.userId = userId;
        this.totalAmount = totalAmount;
        this.orderTime = orderTime;
        this.status = status;
        this.shippingAddress = shippingAddress;
        this.items = items;
    }
}