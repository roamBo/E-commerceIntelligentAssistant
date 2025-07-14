package org.randombo.orderservice.repository;

import org.randombo.orderservice.model.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository
public interface OrderRepository extends JpaRepository<Order, Long> {

    Optional<Order> findByOrderId(String orderId);

    // 参数类型已从 Long 更改为 String
    List<Order> findByUserId(String userId);


    List<Order> findByStatusAndOrderTimeBefore(String status, LocalDateTime orderTime);
}