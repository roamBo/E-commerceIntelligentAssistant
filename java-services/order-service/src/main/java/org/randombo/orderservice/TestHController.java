package org.randombo.orderservice; // XXXX 修改为正确的包名，与文件实际路径匹配
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController // 标识这是一个RESTful控制器
public class TestHController { // 类名与你创建的文件名一致

    @GetMapping("/test") // 定义一个GET请求的接口路径为 /test
    public String test() {
        System.out.println("Order Service: test invoke from TestHController"); // 打印到控制台
        return "Order Service: test invoke from TestHController"; // 返回给请求者
    }
}