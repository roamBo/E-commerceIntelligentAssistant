package org.randombo.paymentservice.service.impl;

import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.AlipayConfig;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.request.AlipayTradePagePayRequest;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.repository.PaymentRepository;
import org.randombo.paymentservice.service.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class PaymentServiceImpl implements PaymentService {
    private final PaymentRepository paymentRepository;



    @Autowired
    public PaymentServiceImpl(PaymentRepository paymentRepository) {
        this.paymentRepository = paymentRepository;
    }

    @Override
    public Payment createPayment(Payment payment) {
        payment.setCreateAt(LocalDateTime.now());
        payment.setUpdateAt(LocalDateTime.now());
        return paymentRepository.save(payment);
    }

    @Override
    public Payment getPaymentById(String id) {
        return paymentRepository.findById(id).orElse(null);
    }

    @Override
    public List<Payment> getAllPayments() {
        return (List<Payment>) paymentRepository.findAll();
    }

    @Override
    public List<Payment> getPaymentsByUserId(String userId) {
        return (List<Payment>) paymentRepository.findByUserId(userId);
    }

    @Override
    public Payment updatePayment(String id, Payment paymentDetails) {
        return paymentRepository.findById(id)
                .map(payment -> {
                    payment.setOrderId(paymentDetails.getOrderId());
                    payment.setAmount(paymentDetails.getAmount());
                    payment.setStatus(paymentDetails.getStatus());
                    payment.setUpdateAt(LocalDateTime.now());
                    return paymentRepository.save(payment);
                }).orElse(null);
    }

    @Override
    public void deletePayment(String id) {
        paymentRepository.deleteById(id);
    }

    @Override
    public Payment updatePaymentStatus(String id, String status) {
        // 定义合法的状态列表
        List<String> validStatuses = List.of("PENDING", "SUCCESS", "FAILED");

        // 验证传入的状态是否合法
        if (!validStatuses.contains(status)) {
            throw new IllegalArgumentException("Invalid payment status: " + status);
        }

        return paymentRepository.findById(id)
                .map(payment -> {
                    payment.setStatus(status);
                    payment.setUpdateAt(LocalDateTime.now());
                    return paymentRepository.save(payment);
                })
                .orElse(null);
    }

}
