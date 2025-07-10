package org.randombo.orderservice.service;

import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.randombo.orderservice.model.Order;
import org.randombo.orderservice.repository.OrderRepository;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDateTime;
import java.util.Optional;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

/**
 * 测试 OrderService 的业务逻辑方法
 */
@SpringBootTest
public class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @InjectMocks
    private OrderService orderService;

    @Test
    public void testCreateOrder_ShouldInitializeFields() {
        Order order = new Order();
        order.setUserId(42L);
        order.setTotalAmount(299.99);
        order.setShippingAddress("Shibuya");

        // 模拟保存直接返回原对象
        when(orderRepository.save(any())).thenAnswer(inv -> inv.getArguments()[0]);

        Order created = orderService.createOrder(order);
        assertNotNull(created.getOrderId());
        assertNotNull(created.getOrderTime());
        assertEquals("PENDING_PAYMENT", created.getStatus());
    }

    @Test
    public void testSimulatePayment_Success() {
        Order order = new Order();
        order.setOrderId("ORDER-123");
        order.setStatus("PENDING_PAYMENT");

        when(orderRepository.findByOrderId("ORDER-123")).thenReturn(Optional.of(order));

        boolean result = orderService.simulatePayment("ORDER-123");
        assertTrue(result);
        assertEquals("PAID", order.getStatus());
    }

    @Test
    public void testSimulatePayment_Failure_OrderNotFound() {
        when(orderRepository.findByOrderId("ORDER-404")).thenReturn(Optional.empty());

        boolean result = orderService.simulatePayment("ORDER-404");
        assertFalse(result);
    }

    @Test
    public void testDeleteOrderByOrderId() {
        Order order = new Order();
        order.setOrderId("ORDER-DEL");
        order.setId(1L);

        when(orderRepository.findByOrderId("ORDER-DEL")).thenReturn(Optional.of(order));
        doNothing().when(orderRepository).delete(order);

        boolean result = orderService.deleteOrderByOrderId("ORDER-DEL");
        assertTrue(result);
    }

    @Test
    public void testGetAbnormalOrders() {
        when(orderRepository.findByStatusAndOrderTimeBefore(eq("PENDING_PAYMENT"), any()))
                .thenReturn(List.of(new Order()));

        List<Order> list = orderService.findLongPendingPaymentOrders(30);
        assertFalse(list.isEmpty());
    }
}