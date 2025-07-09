package org.randombo.paymentservice.service;

import com.alipay.api.AlipayApiException;
import org.randombo.paymentservice.model.Payment;

import java.util.List;

public interface PaymentService {
    Payment createPayment(Payment payment);
    Payment getPaymentById(String id);
    List<Payment> getAllPayments();
    List<Payment> getPaymentsByUserId(String userId);
    Payment updatePayment(String id, Payment payment);
    void deletePayment(String id);
    Payment updatePaymentStatus(String id, String status);
}
