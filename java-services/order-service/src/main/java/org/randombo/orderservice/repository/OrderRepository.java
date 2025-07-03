package org.randombo.orderservice.repository;

import org.randombo.orderservice.model.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Repository // 标识这是一个Spring Data JPA Repository
public interface OrderRepository extends JpaRepository<Order, Long> { // 继承JpaRepository，第一个参数是实体类，第二个参数是主键类型 (Order.id 是Long)

    // 根据业务orderId查询订单
    Optional<Order> findByOrderId(String orderId);

    // 根据用户ID查询订单列表
    List<Order> findByUserId(Long userId);

    // XXXX 新增：根据状态和下单时间查询订单 (用于异常预警功能)
    List<Order> findByStatusAndOrderTimeBefore(String status, LocalDateTime orderTime);
}