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
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class PaymentServiceImplTest {

    @Mock
    private PaymentRepository paymentRepository;

    @InjectMocks
    private PaymentServiceImpl paymentService;

    private Payment testPayment;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);

        testPayment = new Payment();
        testPayment.setId(UUID.randomUUID().toString());
        testPayment.setOrderId("order123");
        testPayment.setUserId("user456");
        testPayment.setAmount(new BigDecimal("100.00"));
        testPayment.setStatus("PENDING");
        testPayment.setCreateAt(LocalDateTime.now());
        testPayment.setUpdateAt(LocalDateTime.now());
    }

    @Test
    void createPayment_ShouldSavePaymentWithTimestamps() {
        Payment newPayment = new Payment();
        newPayment.setOrderId("order123");
        newPayment.setUserId("user456");
        newPayment.setAmount(new BigDecimal("100.00"));

        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);

        Payment result = paymentService.createPayment(newPayment);

        assertNotNull(result.getCreateAt());
        assertNotNull(result.getUpdateAt());
        assertEquals(testPayment.getId(), result.getId());
        verify(paymentRepository, times(1)).save(any(Payment.class));
    }

    @Test
    void getPaymentById_ShouldReturnPaymentWhenExists() {
        when(paymentRepository.findById(testPayment.getId())).thenReturn(Optional.of(testPayment));

        Payment result = paymentService.getPaymentById(testPayment.getId());

        assertNotNull(result);
        assertEquals(testPayment.getId(), result.getId());
        verify(paymentRepository, times(1)).findById(testPayment.getId());
    }

    @Test
    void getPaymentById_ShouldReturnNullWhenNotExists() {
        when(paymentRepository.findById("nonexistent")).thenReturn(Optional.empty());

        Payment result = paymentService.getPaymentById("nonexistent");

        assertNull(result);
        verify(paymentRepository, times(1)).findById("nonexistent");
    }

    @Test
    void getAllPayments_ShouldReturnAllPayments() {
        List<Payment> payments = Arrays.asList(testPayment);
        when(paymentRepository.findAll()).thenReturn(payments);

        List<Payment> result = paymentService.getAllPayments();

        assertEquals(1, result.size());
        assertEquals(testPayment.getId(), result.get(0).getId());
        verify(paymentRepository, times(1)).findAll();
    }

    @Test
    void getPaymentsByUserId_ShouldReturnUserPayments() {
        List<Payment> payments = Arrays.asList(testPayment);
        when(paymentRepository.findByUserId(testPayment.getUserId())).thenReturn(payments);

        List<Payment> result = paymentService.getPaymentsByUserId(testPayment.getUserId());

        assertEquals(1, result.size());
        assertEquals(testPayment.getUserId(), result.get(0).getUserId());
        verify(paymentRepository, times(1)).findByUserId(testPayment.getUserId());
    }

    @Test
    void updatePayment_ShouldUpdateExistingPayment() {
        Payment updatedDetails = new Payment();
        updatedDetails.setOrderId("newOrder");
        updatedDetails.setAmount(new BigDecimal("200.00"));
        updatedDetails.setStatus("SUCCESS");

        when(paymentRepository.findById(testPayment.getId())).thenReturn(Optional.of(testPayment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);

        Payment result = paymentService.updatePayment(testPayment.getId(), updatedDetails);

        assertNotNull(result);
        assertEquals("newOrder", result.getOrderId());
        assertEquals(new BigDecimal("200.00"), result.getAmount());
        assertEquals("SUCCESS", result.getStatus());
        assertNotNull(result.getUpdateAt());
        verify(paymentRepository, times(1)).findById(testPayment.getId());
        verify(paymentRepository, times(1)).save(any(Payment.class));
    }

    @Test
    void updatePayment_ShouldReturnNullWhenNotExists() {
        when(paymentRepository.findById("nonexistent")).thenReturn(Optional.empty());

        Payment result = paymentService.updatePayment("nonexistent", new Payment());

        assertNull(result);
        verify(paymentRepository, times(1)).findById("nonexistent");
        verify(paymentRepository, never()).save(any(Payment.class));
    }

    @Test
    void deletePayment_ShouldCallRepositoryDelete() {
        doNothing().when(paymentRepository).deleteById(testPayment.getId());

        paymentService.deletePayment(testPayment.getId());

        verify(paymentRepository, times(1)).deleteById(testPayment.getId());
    }

    @Test
    void updatePaymentStatus_ShouldUpdateStatusWhenValid() {
        when(paymentRepository.findById(testPayment.getId())).thenReturn(Optional.of(testPayment));
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);

        Payment result = paymentService.updatePaymentStatus(testPayment.getId(), "SUCCESS");

        assertNotNull(result);
        assertEquals("SUCCESS", result.getStatus());
        assertNotNull(result.getUpdateAt());
        verify(paymentRepository, times(1)).findById(testPayment.getId());
        verify(paymentRepository, times(1)).save(any(Payment.class));
    }

    @Test
    void updatePaymentStatus_ShouldThrowExceptionWhenInvalidStatus() {
        assertThrows(IllegalArgumentException.class, () -> {
            paymentService.updatePaymentStatus(testPayment.getId(), "INVALID");
        });

        verify(paymentRepository, never()).findById(anyString());
        verify(paymentRepository, never()).save(any(Payment.class));
    }

    @Test
    void updatePaymentStatus_ShouldReturnNullWhenNotExists() {
        when(paymentRepository.findById("nonexistent")).thenReturn(Optional.empty());

        Payment result = paymentService.updatePaymentStatus("nonexistent", "SUCCESS");

        assertNull(result);
        verify(paymentRepository, times(1)).findById("nonexistent");
        verify(paymentRepository, never()).save(any(Payment.class));
    }
}