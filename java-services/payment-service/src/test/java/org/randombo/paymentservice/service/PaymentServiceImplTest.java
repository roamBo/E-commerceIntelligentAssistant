package org.randombo.paymentservice.service;

import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.request.AlipayTradePagePayRequest;
import com.alipay.api.response.AlipayTradePagePayResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.repository.PaymentRepository;
import org.randombo.paymentservice.service.impl.PaymentServiceImpl;
import org.springframework.dao.DataAccessException;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class PaymentServiceImplTest {

    @Mock
    private PaymentRepository paymentRepository;

    @Mock
    private AlipayClient alipayClient;

    @InjectMocks
    private PaymentServiceImpl paymentService;

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
        when(paymentRepository.save(any(Payment.class))).thenReturn(testPayment);

        Payment created = paymentService.createPayment(testPayment);

        assertNotNull(created);
        assertEquals("pay_123", created.getId());
        verify(paymentRepository, times(1)).save(testPayment);
    }

    @Test
    void createPayment_DatabaseError() {
        when(paymentRepository.save(any(Payment.class)))
                .thenThrow(new RuntimeException("DB connection failed"));

        assertThrows(RuntimeException.class, () -> {
            paymentService.createPayment(testPayment);
        });
    }

    @Test
    void getPaymentById_Found() {
        when(paymentRepository.findById("pay_123")).thenReturn(Optional.of(testPayment));

        Payment found = paymentService.getPaymentById("pay_123");

        assertNotNull(found);
        assertEquals("order_456", found.getOrderId());
    }

    @Test
    void getPaymentById_NotFound() {
        when(paymentRepository.findById("invalid_id")).thenReturn(Optional.empty());

        Payment result = paymentService.getPaymentById("invalid_id");

        assertNull(result);
    }

    @Test
    void getAllPayments_Success() {
        when(paymentRepository.findAll()).thenReturn(Arrays.asList(testPayment));

        List<Payment> payments = paymentService.getAllPayments();

        assertEquals(1, payments.size());
        assertEquals("pay_123", payments.get(0).getId());
    }

    @Test
    void getPaymentsByUserId_Success() {
        when(paymentRepository.findByUserId("user_789")).thenReturn(Arrays.asList(testPayment));

        List<Payment> payments = paymentService.getPaymentsByUserId("user_789");

        assertEquals(1, payments.size());
        assertEquals("user_789", payments.get(0).getUserId());
    }

    @Test
    void updatePayment_Success() {
        Payment updatedDetails = new Payment();
        updatedDetails.setAmount(new BigDecimal("149.99"));
        updatedDetails.setStatus("SUCCESS");

        when(paymentRepository.findById("pay_123")).thenReturn(Optional.of(testPayment));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(inv -> inv.getArgument(0));

        Payment updated = paymentService.updatePayment("pay_123", updatedDetails);

        assertEquals(new BigDecimal("149.99"), updated.getAmount());
        assertEquals("SUCCESS", updated.getStatus());
        assertTrue(updated.getUpdateAt().isEqual(testPayment.getUpdateAt()));
    }

    @Test
    void updatePayment_NotFound() {
        when(paymentRepository.findById("invalid_id")).thenReturn(Optional.empty());

        Payment result = paymentService.updatePayment("invalid_id", testPayment);

        assertNull(result);
    }

    @Test
    void updatePaymentStatus_Success() {
        when(paymentRepository.findById("pay_123")).thenReturn(Optional.of(testPayment));
        when(paymentRepository.save(any(Payment.class))).thenAnswer(inv -> inv.getArgument(0));

        Payment updated = paymentService.updatePaymentStatus("pay_123", "SUCCESS");

        assertEquals("SUCCESS", updated.getStatus());
        assertTrue(updated.getUpdateAt().isEqual(testPayment.getUpdateAt()));
    }

    @Test
    void updatePaymentStatus_InvalidStatus() {
        when(paymentRepository.findById("pay_123")).thenReturn(Optional.of(testPayment));

        assertThrows(IllegalArgumentException.class, () -> {
            paymentService.updatePaymentStatus("pay_123", "INVALID_STATUS");
        });
    }

    @Test
    void deletePayment_Success() {
        doNothing().when(paymentRepository).deleteById("pay_123");

        paymentService.deletePayment("pay_123");

        verify(paymentRepository, times(1)).deleteById("pay_123");
    }

    @Test
    void createAlipayOrder_Success() throws AlipayApiException {
        AlipayTradePagePayResponse mockResponse = new AlipayTradePagePayResponse();
        mockResponse.setBody("alipay_form_data");

        when(alipayClient.pageExecute(any(AlipayTradePagePayRequest.class)))
                .thenReturn(mockResponse);

        String result = paymentService.createAlipayOrder("order_123", "100.00", "Test Product");

        assertNotNull(result);
        assertEquals("alipay_form_data", result);
    }

    @Test
    void createAlipayOrder_AlipayApiException() throws AlipayApiException {
        when(alipayClient.pageExecute(any(AlipayTradePagePayRequest.class)))
                .thenThrow(new AlipayApiException("API error"));

        String result = paymentService.createAlipayOrder("order_123", "100.00", "Test Product");

        assertNull(result);
    }
}