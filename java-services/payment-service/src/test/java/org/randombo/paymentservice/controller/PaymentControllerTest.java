package org.randombo.paymentservice.controller;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.service.PaymentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentControllerTest {

    @Mock
    private PaymentService paymentService;

    @InjectMocks
    private PaymentController paymentController;

    private Payment testPayment;

    @BeforeEach
    void setUp() {
        testPayment = new Payment();
        testPayment.setId("pay_123");
        testPayment.setOrderId("order_456");
        testPayment.setUserId("user_789");
        testPayment.setAmount(new BigDecimal("99.99"));
        testPayment.setStatus("PENDING");
        testPayment.setCreateAt(LocalDateTime.now());
        testPayment.setUpdateAt(LocalDateTime.now());
    }

    @Test
    void createPayment_Success() {
        when(paymentService.createPayment(any(Payment.class))).thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.createPayment(testPayment);

        assertEquals(HttpStatus.CREATED, response.getStatusCode());
        assertEquals("pay_123", response.getBody().getId());
    }

    @Test
    void getPaymentById_Found() {
        when(paymentService.getPaymentById("pay_123")).thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.getPaymentById("pay_123");

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("order_456", response.getBody().getOrderId());
    }

    @Test
    void getPaymentById_NotFound() {
        when(paymentService.getPaymentById("invalid_id")).thenReturn(null);

        ResponseEntity<Payment> response = paymentController.getPaymentById("invalid_id");

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }

    @Test
    void getAllPayments_Success() {
        when(paymentService.getAllPayments()).thenReturn(Arrays.asList(testPayment));

        ResponseEntity<List<Payment>> response = paymentController.getAllPayments();

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(1, response.getBody().size());
    }

    @Test
    void getAllPayments_Empty() {
        when(paymentService.getAllPayments()).thenReturn(Collections.emptyList());

        ResponseEntity<List<Payment>> response = paymentController.getAllPayments();

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertTrue(response.getBody().isEmpty());
    }

    @Test
    void getPaymentsByUserId_Success() {
        when(paymentService.getPaymentsByUserId("user_789")).thenReturn(Arrays.asList(testPayment));

        ResponseEntity<List<Payment>> response = paymentController.getPaymentsByUserId("user_789");

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals(1, response.getBody().size());
        assertEquals("user_789", response.getBody().get(0).getUserId());
    }

    @Test
    void updatePayment_Success() {
        when(paymentService.updatePayment(eq("pay_123"), any(Payment.class)))
                .thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.updatePayment("pay_123", testPayment);

        assertEquals(HttpStatus.OK, response.getStatusCode());
    }

    @Test
    void updatePayment_NotFound() {
        when(paymentService.updatePayment(eq("invalid_id"), any(Payment.class)))
                .thenReturn(null);

        ResponseEntity<Payment> response = paymentController.updatePayment("invalid_id", testPayment);

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }

    @Test
    void updatePaymentStatus_Success() {
        when(paymentService.updatePaymentStatus("pay_123", "SUCCESS")).thenReturn(testPayment);

        ResponseEntity<Payment> response = paymentController.updatePaymentStatus("pay_123", "SUCCESS");

        assertEquals(HttpStatus.OK, response.getStatusCode());
    }

    @Test
    void updatePaymentStatus_NotFound() {
        when(paymentService.updatePaymentStatus("invalid_id", "SUCCESS")).thenReturn(null);

        ResponseEntity<Payment> response = paymentController.updatePaymentStatus("invalid_id", "SUCCESS");

        assertEquals(HttpStatus.NOT_FOUND, response.getStatusCode());
    }

    @Test
    void deletePayment_Success() {
        doNothing().when(paymentService).deletePayment("pay_123");

        ResponseEntity<Payment> response = paymentController.deletePayment("pay_123");

        assertEquals(HttpStatus.NO_CONTENT, response.getStatusCode());
    }

    @Test
    void createAlipayOrder_Success() {
        when(paymentService.createAlipayOrder("order_123", "100.00", "Test Product"))
                .thenReturn("alipay_form_data");

        ResponseEntity<String> response = paymentController.createAlipayOrder(
                "order_123", "100.00", "Test Product");

        assertEquals(HttpStatus.OK, response.getStatusCode());
        assertEquals("alipay_form_data", response.getBody());
    }

    @Test
    void createAlipayOrder_Failure() {
        when(paymentService.createAlipayOrder("order_123", "100.00", "Test Product"))
                .thenReturn(null);

        ResponseEntity<String> response = paymentController.createAlipayOrder(
                "order_123", "100.00", "Test Product");

        assertEquals(HttpStatus.INTERNAL_SERVER_ERROR, response.getStatusCode());
    }
}