package org.randombo.paymentservice.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.redis.core.RedisHash;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@RedisHash("Payment")
public class Payment implements Serializable {
    @Id
    private String id;
    private String orderId;
    private String userId;
    private BigDecimal amount;
    private String status; //PENDING, SUCCESS, FAILED
    private LocalDateTime createAt;
    private LocalDateTime updateAt;
}
