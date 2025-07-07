package org.randombo.orderservice.repository;

import org.junit.jupiter.api.Test;
import org.randombo.orderservice.model.Order;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;

import java.time.LocalDateTime;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Repository 层单元测试，只针对 JPA Repository 的 CRUD 行为进行验证。
 * 使用 @DataJpaTest 会仅加载与 JPA 有关的 Bean（Entity、Repository），不会加载完整应用上下文。
 */
@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE) // 如果你使用的是真实数据库连接（例如本地MySQL）
public class OrderRepositoryTest {

    @Autowired
    private OrderRepository orderRepository;

    /**
     * 测试 OrderRepository 的保存与根据 orderId 查询功能
     */
    @Test
    public void testSaveAndFindByOrderId() {
        // 构造订单实体
        Order order = new Order();
        order.setOrderId("ORDER-XYZ123");
        order.setUserId(100L);
        order.setTotalAmount(888.88);
        order.setOrderTime(LocalDateTime.now());
        order.setStatus("PENDING_PAYMENT");
        order.setShippingAddress("Tokyo");

        // 保存到数据库
        orderRepository.save(order);

        // 验证是否能通过 orderId 查询到刚才插入的订单
        assertTrue(orderRepository.findByOrderId("ORDER-XYZ123").isPresent(), "通过订单号应能查询到订单");
    }

    /**
     * 测试按状态和订单时间筛选订单的功能（适用于超时订单检测）
     */
    @Test
    public void testFindByStatusAndOrderTimeBefore() {
        // 创建一个15分钟前的待支付订单
        Order order = new Order();
        order.setOrderId("ORDER-AB1234");
        order.setUserId(100L);
        order.setTotalAmount(555.55);
        order.setOrderTime(LocalDateTime.now().minusMinutes(15));
        order.setStatus("PENDING_PAYMENT");
        order.setShippingAddress("Kyoto");

        orderRepository.save(order);

        // 查找10分钟前仍为未支付状态的订单（应能查到刚才插入的这条）
        List<Order> abnormalOrders = orderRepository.findByStatusAndOrderTimeBefore(
                "PENDING_PAYMENT", LocalDateTime.now().minusMinutes(10));

        assertFalse(abnormalOrders.isEmpty(), "应能查到一条超时未支付订单");
    }
}
