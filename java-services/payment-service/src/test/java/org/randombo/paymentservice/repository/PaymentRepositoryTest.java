package org.randombo.paymentservice.repository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.randombo.paymentservice.model.Payment;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.data.redis.DataRedisTest;
import org.springframework.test.context.ActiveProfiles;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataRedisTest
@ActiveProfiles("test")
public class PaymentRepositoryTest {

    @Autowired
    private PaymentRepository paymentRepository;

    private Payment savedPayment;

    @BeforeEach
    void setUp() {
        // 清理测试数据
        paymentRepository.deleteAll();

        // 准备测试数据
        Payment payment = new Payment();
        payment.setId("test123");
        payment.setOrderId("order123");
        payment.setUserId("user123");
        payment.setAmount(new BigDecimal("100.00"));
        payment.setStatus("PENDING");
        payment.setCreateAt(LocalDateTime.now());
        payment.setUpdateAt(LocalDateTime.now());

        savedPayment = paymentRepository.save(payment);
    }

    @Test
    void shouldSaveAndFindPaymentById() {
        // When
        Optional<Payment> foundPayment = paymentRepository.findById(savedPayment.getId());

        // Then
        assertThat(foundPayment).isPresent();
        assertThat(foundPayment.get().getId()).isEqualTo(savedPayment.getId());
        assertThat(foundPayment.get().getOrderId()).isEqualTo("order123");
    }

    @Test
    void shouldFindAllPayments() {
        // When
        Iterable<Payment> payments = paymentRepository.findAll();

        // Then
        assertThat(payments).hasSize(1);
        assertThat(payments.iterator().next().getUserId()).isEqualTo("user123");
    }

    @Test
    void shouldFindPaymentsByUserId() {
        // When
        Iterable<Payment> payments = paymentRepository.findByUserId("user123");

        // Then
        assertThat(payments).hasSize(1);
        assertThat(payments.iterator().next().getId()).isEqualTo("test123");
    }

    @Test
    void shouldFindPaymentsByStatus() {
        // When
        Iterable<Payment> payments = paymentRepository.findByStatus("PENDING");

        // Then
        assertThat(payments).hasSize(1);
        assertThat(payments.iterator().next().getStatus()).isEqualTo("PENDING");
    }

    @Test
    void shouldUpdatePayment() {
        // Given
        Payment paymentToUpdate = paymentRepository.findById("test123").get();
        paymentToUpdate.setStatus("SUCCESS");

        // When
        Payment updatedPayment = paymentRepository.save(paymentToUpdate);

        // Then
        assertThat(updatedPayment.getStatus()).isEqualTo("SUCCESS");
        assertThat(paymentRepository.findById("test123").get().getStatus())
                .isEqualTo("SUCCESS");
    }

    @Test
    void shouldDeletePayment() {
        // When
        paymentRepository.deleteById("test123");

        // Then
        assertThat(paymentRepository.findById("test123")).isEmpty();
    }

    @Test
    void shouldReturnEmptyWhenPaymentNotFound() {
        // When
        Optional<Payment> foundPayment = paymentRepository.findById("non-existing");

        // Then
        assertThat(foundPayment).isEmpty();
    }
}