package org.randombo.orderservice.model;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Entity // XXXX 标识这是一个JPA实体
@Table(name = "orders") // XXXX 映射到名为 'orders' 的数据库表
@Data
public class Order {

    @Id // XXXX 标识为主键
    @GeneratedValue(strategy = GenerationType.IDENTITY) // XXXX 数据库自增主键
    private Long id; // XXXX 数据库通常使用Long作为自增主增主键
    private String orderId; // 保持业务订单ID
    private Long userId;
    private Double totalAmount;
    private LocalDateTime orderTime;
    private String status;
    private String shippingAddress;

    @OneToMany(cascade = CascadeType.ALL, orphanRemoval = true) // XXXX 一对多关系，级联操作，孤儿移除
    @JoinColumn(name = "order_id_fk") // XXXX 在order_items表中添加外键列order_id_fk指向orders表的id
    private List<OrderItem> items;

    @Entity // XXXX OrderItem也是一个JPA实体
    @Table(name = "order_items") // XXXX 映射到名为 'order_items' 的数据库表
    @Data
    public static class OrderItem {
        @Id // XXXX 标识为主键
        @GeneratedValue(strategy = GenerationType.IDENTITY) // XXXX 数据库自增主键
        private Long id; // XXXX OrderItem自己的主键
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
    public Order(String orderId, Long userId, Double totalAmount, LocalDateTime orderTime, String status, String shippingAddress, List<OrderItem> items) {
        this.orderId = orderId;
        this.userId = userId;
        this.totalAmount = totalAmount;
        this.orderTime = orderTime;
        this.status = status;
        this.shippingAddress = shippingAddress;
        this.items = items;
    }
}