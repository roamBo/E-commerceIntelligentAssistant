package org.randombo.paymentservice.controller;

import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.service.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@CrossOrigin(origins = "*")
@RestController
@RequestMapping("/api/payments")
public class PaymentController {
    private PaymentService paymentService;

    @Autowired
    public void setPaymentService(PaymentService paymentService) {
        this.paymentService = paymentService;
    }

    @PostMapping
    public ResponseEntity<Payment> createPayment(@RequestBody Payment payment) {
        payment.setId(UUID.randomUUID().toString());
        Payment createdPayment = paymentService.createPayment(payment);
        return new ResponseEntity<>(createdPayment, HttpStatus.CREATED);
    }

    @GetMapping
    public ResponseEntity<List<Payment>> getAllPayments() {
        List<Payment> payments = paymentService.getAllPayments();
        return ResponseEntity.ok(payments);
    }

    @GetMapping("/{id}")
    public ResponseEntity<Payment> getPaymentById(@PathVariable String id) {
        Payment payment = paymentService.getPaymentById(id);
        return payment != null ?
                ResponseEntity.ok(payment) :
                ResponseEntity.notFound().build();
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<Payment>> getPaymentsByUserId(@PathVariable String userId) {
        List<Payment> payments = paymentService.getPaymentsByUserId(userId);
        return ResponseEntity.ok(payments);
    }

    @PutMapping("/{id}")
    public ResponseEntity<Payment> updatePayment(@PathVariable String id, @RequestBody Payment payment) {
        Payment updatedPayment = paymentService.updatePayment(id, payment);
        return updatedPayment != null ?
                ResponseEntity.ok(updatedPayment) :
                ResponseEntity.notFound().build();
    }

    @PatchMapping("/{id}/{status}")
    public ResponseEntity<Payment> updatePaymentStatus(@PathVariable String id, @PathVariable String status) {
        Payment updatedPayment = paymentService.updatePaymentStatus(id, status);
        return updatedPayment != null ?
                ResponseEntity.ok(updatedPayment) :
                ResponseEntity.notFound().build();
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Payment> deletePayment(@PathVariable String id) {
        paymentService.deletePayment(id);
        return ResponseEntity.noContent().build();
    }


}
