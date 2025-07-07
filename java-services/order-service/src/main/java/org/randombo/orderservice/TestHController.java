package org.randombo.orderservice; // 确保这个包名与TestHController.java文件所在的路径匹配

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class TestHController {

    @GetMapping("/test")
    public String test() {
        System.out.println("Order Service: test invoke from TestHController");
        return "Order Service: test invoke from TestHController";
    }
}