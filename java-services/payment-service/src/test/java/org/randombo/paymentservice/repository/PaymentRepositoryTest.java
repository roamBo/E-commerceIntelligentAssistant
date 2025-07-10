package org.randombo.paymentservice.repository;

import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.*;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.service.PaymentService;
import org.randombo.paymentservice.service.impl.PaymentServiceImpl;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class PaymentRepositoryTest {

    @Mock
    private PaymentRepository paymentRepository;

    @InjectMocks
    private PaymentServiceImpl paymentService;

    private AutoCloseable closeable;

    private Payment samplePayment;

    @BeforeEach
    void setUp() {
        closeable = MockitoAnnotations.openMocks(this);

        samplePayment = new Payment();
        samplePayment.setId("mock-id");
        samplePayment.setOrderId("order-999");
        samplePayment.setUserId("user-abc");
        samplePayment.setAmount(new BigDecimal("123.45"));
        samplePayment.setStatus("PENDING");
        samplePayment.setCreateAt(LocalDateTime.now());
        samplePayment.setUpdateAt(LocalDateTime.now());
    }

    @Test
    @DisplayName("createPayment should save and return a payment")
    void testCreatePayment() {
        when(paymentRepository.save(any(Payment.class))).thenReturn(samplePayment);

        Payment saved = paymentService.createPayment(samplePayment);

        assertThat(saved).isNotNull();
        assertThat(saved.getId()).isEqualTo("mock-id");
        verify(paymentRepository, times(1)).save(any(Payment.class));
    }

    @Test
    @DisplayName("getPaymentById should return payment if exists")
    void testGetPaymentById() {
        when(paymentRepository.findById("mock-id")).thenReturn(Optional.of(samplePayment));

        Payment result = paymentService.getPaymentById("mock-id");

        assertThat(result).isNotNull();
        assertThat(result.getUserId()).isEqualTo("user-abc");
        verify(paymentRepository, times(1)).findById("mock-id");
    }

    @Test
    @DisplayName("getAllPayments should return list of payments")
    void testGetAllPayments() {
        when(paymentRepository.findAll()).thenReturn(List.of(samplePayment));

        List<Payment> results = paymentService.getAllPayments();

        assertThat(results).hasSize(1);
        verify(paymentRepository).findAll();
    }

    @Test
    @DisplayName("getPaymentsByUserId should call repository")
    void testGetPaymentsByUserId() {
        when(paymentRepository.findByUserId("user-abc")).thenReturn(List.of(samplePayment));

        List<Payment> results = paymentService.getPaymentsByUserId("user-abc");

        assertThat(results).hasSize(1);
        verify(paymentRepository).findByUserId("user-abc");
    }

    @Test
    @DisplayName("updatePayment should update and return modified payment")
    void testUpdatePayment() {
        when(paymentRepository.findById("mock-id")).thenReturn(Optional.of(samplePayment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(samplePayment);

        Payment update = new Payment();
        update.setOrderId("order-updated");
        update.setAmount(new BigDecimal("999.99"));
        update.setStatus("SUCCESS");

        Payment result = paymentService.updatePayment("mock-id", update);

        assertThat(result).isNotNull();
        assertThat(result.getOrderId()).isEqualTo("order-updated");
        assertThat(result.getStatus()).isEqualTo("SUCCESS");
        verify(paymentRepository).save(any(Payment.class));
    }

    @Test
    @DisplayName("deletePayment should call repository deleteById")
    void testDeletePayment() {
        doNothing().when(paymentRepository).deleteById("mock-id");

        paymentService.deletePayment("mock-id");

        verify(paymentRepository).deleteById("mock-id");
    }

    @Test
    @DisplayName("updatePaymentStatus should update payment status")
    void testUpdatePaymentStatus() {
        when(paymentRepository.findById("mock-id")).thenReturn(Optional.of(samplePayment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(samplePayment);

        Payment result = paymentService.updatePaymentStatus("mock-id", "FAILED");

        assertThat(result).isNotNull();
        assertThat(result.getStatus()).isEqualTo("FAILED");
        verify(paymentRepository).save(any(Payment.class));
    }

    @Test
    @DisplayName("updatePaymentStatus should throw if status is invalid")
    void testUpdatePaymentStatus_invalid() {
        when(paymentRepository.findById("mock-id")).thenReturn(Optional.of(samplePayment));

        // 使用 lambda 表达式断言抛出异常
        org.junit.jupiter.api.Assertions.assertThrows(IllegalArgumentException.class, () -> {
            paymentService.updatePaymentStatus("mock-id", "INVALID_STATUS");
        });
    }

    @AfterEach
    void tearDown() throws Exception {
        closeable.close(); // 清理 mock
    }
}