package org.randombo.paymentservice.repository;

import org.junit.jupiter.api.Test;
import org.randombo.paymentservice.model.Payment;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.redis.DataRedisTest;

import java.math.BigDecimal;
import java.time.LocalDateTime;

import static org.junit.jupiter.api.Assertions.*;

// 用于 Redis 数据测试
@DataRedisTest
public class PaymentRepositoryTest {

    @Autowired
    private PaymentRepository paymentRepository;

    @Test
    void testSaveAndFindById() {
        Payment payment = new Payment("101", "order-101", "user-101", new BigDecimal("20.00"),
                "PENDING", LocalDateTime.now(), LocalDateTime.now());

        paymentRepository.save(payment);
        Payment result = paymentRepository.findById("101").orElse(null);

        assertNotNull(result);
        assertEquals("order-101", result.getOrderId());
    }

    @Test
    void testFindByUserId() {
        Payment payment = new Payment("102", "order-102", "user-102", new BigDecimal("50.00"),
                "SUCCESS", LocalDateTime.now(), LocalDateTime.now());

        paymentRepository.save(payment);

        Iterable<Payment> results = paymentRepository.findByUserId("user-102");
        assertTrue(results.iterator().hasNext());
    }
}
