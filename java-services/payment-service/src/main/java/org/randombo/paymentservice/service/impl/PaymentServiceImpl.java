package org.randombo.paymentservice.service.impl;

import com.alipay.api.AlipayApiException;
import com.alipay.api.AlipayClient;
import com.alipay.api.AlipayConfig;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.api.request.AlipayTradePagePayRequest;
import org.randombo.paymentservice.config.AliPayConfig;
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
    private AliPayConfig alipayConfig;

    @Autowired
    public PaymentServiceImpl(PaymentRepository paymentRepository, AliPayConfig alipayConfig) {
        this.paymentRepository = paymentRepository;
        this.alipayConfig = alipayConfig;
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
    @Override
    public String createAlipayOrder(String out_trade_no, String total_amount, String subject) throws AlipayApiException {
        // 创建 AlipayClient 实例
        AlipayClient alipayClient = new DefaultAlipayClient(
                alipayConfig.getGatewayUrl(),
                alipayConfig.getAppId(),
                alipayConfig.getAppPrivateKey(),
                "json",
                "UTF-8",
                alipayConfig.getAlipayPublicKey(),
                "RSA2"
        );
        // 创建 AlipayTradePagePayRequest 实例
        AlipayTradePagePayRequest alipayRequest = new AlipayTradePagePayRequest();
        alipayRequest.setReturnUrl("your_return_url"); // 设置返回 URL
        alipayRequest.setNotifyUrl(alipayConfig.getNotifyUrl()); // 设置通知 URL

        // 设置订单信息
        alipayRequest.setBizContent("{\"out_trade_no\":\"" + out_trade_no + "\","
                + "\"total_amount\":\"" + total_amount + "\","
                + "\"subject\":\"" + subject + "\","
                + "\"product_code\":\"FAST_INSTANT_TRADE_PAY\"}");
        String result = alipayClient.pageExecute(alipayRequest).getBody();
        //会收到支付宝的响应，响应的是一个页面，只要浏览器显示这个页面，就会自动来到支付宝的收银台页面
        System.out.println("支付宝的响应：" + result);

        try {
            // 调用支付宝接口获取支付页面 URL
            return alipayClient.pageExecute(alipayRequest).getBody();
        } catch (AlipayApiException e) {
            e.printStackTrace();
            return null;
        }
    }
}
