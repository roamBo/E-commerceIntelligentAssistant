package org.randombo.paymentservice;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class testController {
    @GetMapping("/offer")
    public String offerService(){
        System.out.println("offer service invoke");
        return "offer service invoke";
    }
}

