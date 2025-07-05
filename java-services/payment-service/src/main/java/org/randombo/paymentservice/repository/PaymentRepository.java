package org.randombo.paymentservice.repository;

import org.randombo.paymentservice.model.Payment;
import org.springframework.data.repository.CrudRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface PaymentRepository extends CrudRepository<Payment,String> {
    Iterable<Payment> findByUserId(String userId);
    Iterable<Payment> findByStatus(String status);
}
