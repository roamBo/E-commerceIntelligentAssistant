package org.randombo.paymentservice;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class testController {
    @GetMapping("/test")
    public String test(){
        System.out.println("test invoke");
        return "test invoke";
    }
}
