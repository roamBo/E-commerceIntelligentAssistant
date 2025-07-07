package org.randombo.orderservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.randombo.orderservice.model.Order;
import org.randombo.orderservice.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Optional;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/**
 * 测试 OrderController 的 REST API 接口
 */
@WebMvcTest(OrderController.class)
public class OrderControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private OrderService orderService;

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Test
    public void testGetOrderByOrderId_Found() throws Exception {
        // 模拟订单
        Order order = new Order();
        order.setOrderId("ORDER-1234");
        order.setUserId(1L);
        order.setTotalAmount(100.0);
        order.setStatus("PAID");
        order.setOrderTime(LocalDateTime.now());

        when(orderService.getOrderByOrderId("ORDER-1234")).thenReturn(Optional.of(order));

        mockMvc.perform(get("/api/orders/ORDER-1234"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.orderId").value("ORDER-1234"))
                .andExpect(jsonPath("$.status").value("PAID"));
    }

    @Test
    public void testGetOrderByOrderId_NotFound() throws Exception {
        // 订单不存在
        when(orderService.getOrderByOrderId("ORDER-0000")).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/orders/ORDER-0000"))
                .andExpect(status().isNotFound());
    }

    @Test
    public void testCreateOrder() throws Exception {
        Order order = new Order();
        order.setUserId(1L);
        order.setTotalAmount(199.99);
        order.setShippingAddress("Tokyo, Japan");

        Order savedOrder = new Order();
        savedOrder.setOrderId("ORDER-NEW123");
        savedOrder.setUserId(order.getUserId());
        savedOrder.setTotalAmount(order.getTotalAmount());
        savedOrder.setOrderTime(LocalDateTime.now());
        savedOrder.setStatus("PENDING_PAYMENT");

        when(orderService.createOrder(order)).thenReturn(savedOrder);

        mockMvc.perform(post("/api/orders")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(order)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.orderId").value("ORDER-NEW123"))
                .andExpect(jsonPath("$.status").value("PENDING_PAYMENT"));
    }

    @Test
    public void testGetAllOrders() throws Exception {
        Order order = new Order();
        order.setOrderId("ORDER-1");
        order.setUserId(123L);
        order.setTotalAmount(123.45);
        order.setOrderTime(LocalDateTime.now());
        order.setStatus("PAID");

        when(orderService.getAllOrders()).thenReturn(Arrays.asList(order));

        mockMvc.perform(get("/api/orders"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.length()").value(1))
                .andExpect(jsonPath("$[0].orderId").value("ORDER-1"));
    }
}
