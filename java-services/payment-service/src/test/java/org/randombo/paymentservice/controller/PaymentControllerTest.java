package org.randombo.paymentservice.controller;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.service.PaymentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class PaymentControllerTest {

    @Mock
    private PaymentService paymentService;

    @InjectMocks
    private PaymentController paymentController;

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
    void createPayment_ShouldReturnCreatedPayment() {
        when(paymentService.createPayment(any(Payment.class))).thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.createPayment(testPayment);

        assertEquals(HttpStatus.CREATED, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(testPayment.getId(), response.getBody().getId());
        verify(paymentService, times(1)).createPayment(any(Payment.class));
    }

    @Test
    void getAllPayments_ShouldReturnAllPayments() {
        List<Payment> payments = Arrays.asList(testPayment);
        when(paymentService.getAllPayments()).thenReturn(payments);

        ResponseEntity<List<Payment>> response = paymentController.getAllPayments();

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(1, response.getBody().size());
        verify(paymentService, times(1)).getAllPayments();
    }

    @Test
    void getPaymentById_ShouldReturnPaymentWhenExists() {
        when(paymentService.getPaymentById(testPayment.getId())).thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.getPaymentById(testPayment.getId());

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals(testPayment.getId(), response.getBody().getId());
        verify(paymentService, times(1)).getPaymentById(testPayment.getId());
    }

    @Test
    void getPaymentById_ShouldReturnNotFoundWhenNotExists() {
        when(paymentService.getPaymentById("nonexistent")).thenReturn(null);

        ResponseEntity<Payment> response = paymentController.getPaymentById("nonexistent");

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        verify(paymentService, times(1)).getPaymentById("nonexistent");
    }

    @Test
    void getPaymentsByUserId_ShouldReturnUserPayments() {
        List<Payment> payments = Arrays.asList(testPayment);
        when(paymentService.getPaymentsByUserId(testPayment.getUserId())).thenReturn(payments);

        ResponseEntity<List<Payment>> response = paymentController.getPaymentsByUserId(testPayment.getUserId());

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(1, response.getBody().size());
        assertEquals(testPayment.getUserId(), response.getBody().get(0).getUserId());
        verify(paymentService, times(1)).getPaymentsByUserId(testPayment.getUserId());
    }

    @Test
    void updatePayment_ShouldReturnUpdatedPayment() {
        Payment updatedPayment = new Payment();
        updatedPayment.setStatus("SUCCESS");

        when(paymentService.updatePayment(eq(testPayment.getId()), any(Payment.class)))
                .thenReturn(updatedPayment);

        ResponseEntity<Payment> response = paymentController.updatePayment(testPayment.getId(), updatedPayment);

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("SUCCESS", response.getBody().getStatus());
        verify(paymentService, times(1)).updatePayment(eq(testPayment.getId()), any(Payment.class));
    }

    @Test
    void updatePayment_ShouldReturnNotFoundWhenNotExists() {
        when(paymentService.updatePayment(eq("nonexistent"), any(Payment.class))).thenReturn(null);

        ResponseEntity<Payment> response = paymentController.updatePayment("nonexistent", new Payment());

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        verify(paymentService, times(1)).updatePayment(eq("nonexistent"), any(Payment.class));
    }

    @Test
    void updatePaymentStatus_ShouldReturnUpdatedPayment() {
        Payment updatedPayment = new Payment();
        updatedPayment.setStatus("SUCCESS");

        when(paymentService.updatePaymentStatus(testPayment.getId(), "SUCCESS"))
                .thenReturn(updatedPayment);

        ResponseEntity<Payment> response = paymentController.updatePaymentStatus(testPayment.getId(), "SUCCESS");

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertNotNull(response.getBody());
        assertEquals("SUCCESS", response.getBody().getStatus());
        verify(paymentService, times(1)).updatePaymentStatus(testPayment.getId(), "SUCCESS");
    }

    @Test
    void updatePaymentStatus_ShouldReturnNotFoundWhenNotExists() {
        when(paymentService.updatePaymentStatus("nonexistent", "SUCCESS")).thenReturn(null);

        ResponseEntity<Payment> response = paymentController.updatePaymentStatus("nonexistent", "SUCCESS");

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
        verify(paymentService, times(1)).updatePaymentStatus("nonexistent", "SUCCESS");
    }

    @Test
    void deletePayment_ShouldReturnNoContent() {
        doNothing().when(paymentService).deletePayment(testPayment.getId());

        ResponseEntity<Payment> response = paymentController.deletePayment(testPayment.getId());

        assertEquals(HttpStatus.NO_CONTENT, response.getStatusCode());
        verify(paymentService, times(1)).deletePayment(testPayment.getId());
    }
}