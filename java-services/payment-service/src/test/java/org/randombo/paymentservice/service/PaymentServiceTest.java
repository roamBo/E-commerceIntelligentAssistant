package org.randombo.paymentservice.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.repository.PaymentRepository;
import org.randombo.paymentservice.service.impl.PaymentServiceImpl;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

public class PaymentServiceTest {

    @Mock
    private PaymentRepository paymentRepository;

    @InjectMocks
    private PaymentServiceImpl paymentService;

    private Payment samplePayment;

    @BeforeEach
    void setup() {
        MockitoAnnotations.openMocks(this);
        samplePayment = new Payment("1", "order-1", "user-1", new BigDecimal("88.88"),
                "PENDING", LocalDateTime.now(), LocalDateTime.now());
    }

    @Test
    void testCreatePayment() {
        when(paymentRepository.save(any())).thenReturn(samplePayment);

        Payment created = paymentService.createPayment(samplePayment);
        assertNotNull(created);
        assertEquals("user-1", created.getUserId());
    }

    @Test
    void testGetPaymentById_found() {
        when(paymentRepository.findById("1")).thenReturn(Optional.of(samplePayment));

        Payment found = paymentService.getPaymentById("1");
        assertEquals("order-1", found.getOrderId());
    }

    @Test
    void testUpdateStatus() {
        when(paymentRepository.findById("1")).thenReturn(Optional.of(samplePayment));
        when(paymentRepository.save(any())).thenReturn(samplePayment);

        Payment updated = paymentService.updatePaymentStatus("1", "SUCCESS");
        assertNotNull(updated);
        assertEquals("SUCCESS", updated.getStatus());
    }
}
