package org.randombo.paymentservice.config;

import com.alipay.api.AlipayClient;
import com.alipay.api.DefaultAlipayClient;
import com.alipay.easysdk.factory.Factory;
import com.alipay.easysdk.kernel.Config;
import jakarta.annotation.PostConstruct;
import jdk.jfr.DataAmount;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.PostMapping;

@Data
@Component
@ConfigurationProperties(prefix = "alipay")
public class AliPayConfig {
    // 沙盒网关https://openapi.alipaydev.com/gateway.do

    private static final String GATEWAY_URL = "https://openapi-sandbox.dl.alipaydev.com/gateway.do";
    // 沙盒应用的 APPID
    private static final String APP_ID = "9021000150621526";
    // 商户私钥
    private static final String MERCHANT_PRIVATE_KEY = "MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCZBKFVxXR661PLkolmW9G3Ei81VBzJJ4LQTfBL/iCW30Ae8Y3azd5aRcchpF26LKlHZaIg6zTvg7Ef4y3EJhIhY8C08+GukxTjbzEySckNOs0CV/tM0D6Qf6vWuH6/813RK+DsvglE7B0KPWmX4D9wvmqO19Pz/q1P5jSJqPORPl/wBc6LKidpD0m4r6uDTKaJ3+UAn02208xBeV4AqBdV5uUdKl7lv2NiELyUCmeF94OTJNTNItLlL8x5zGK+hgHWRokPv3GYnI8nq6M5JE3eArpq7j9JjQWSuLkvAyDT7QTGOEABC4mLVtm3hm1wGAuW6PzOcdtRTsxT1e5yhgvrAgMBAAECggEAJNWYgK0nfO9pHHgJ2zn/IbKe6pd01ndMZhhc3+4sqiTTqp87JpCoFdL2PIL0jPxzQ1yTypjUBVQOLz7gpXcEpkT8/pI2oW+Gd7ksfo6Ed0rQTuAe/j6i0OXq16VR3aMX0mJdop+cW5r64pwl7wlsPBeaTwhlXTbRQYqI2xpwh2W6eK9nYJKYUbQm/WWhsSMFbM5DNjpa7PBv7dDVX2DKutzvqZy1nWYBc7lr6mIS7t+FtBaKXMH706cleqAacaZXPEK7YNc+zvIOLY+iyePAps1r6QtJvuKEdunAAbHhN9btL/U7eXhpIqaIzZHGzzX6HRgaM3Z2YfLF1V37JCtMAQKBgQD61x/XBPe1wtuLiNnmM97ssYdwcqxZ7lXV/MR0kAHn3YTsGOFM2BY09yC4D9d4NUPvhn9rrKzUw0itK5yxvE76DeAsXT+//4EfFKvIxhM/hX5oXUbLaWCVJ+i3hcHdSyPQsZewYEpmXS0Z2ykz4tBwLd7HJFl3q2ODf126YbrmWwKBgQCcKmSq7qsHpf/vO5LMutdKduwv8CFogCEQQp4DI/TzTjKMYhKPSwF50EdCxFyFG/SsIwkitlRcSdad+n5HTw3dKRT48IJLuIJMxST5tfI/gU+SFAc2b8/0axnj4IbMdr0tvNTSYArU2cl/qhU8IdfQEPzZkOZhLMfZDgvtaPcFsQKBgQCVYM8BSWAKygPcUJ8SzAkRg5dYi7G/zIMpb+G+WJQJ9I1X3GkvTe/Lku/VLPnwCChw1/PBt48lFTaOic5CuhV+LA033kA8onfOfozef7auuVzR4dprAFIYATBBOlJ86mZlvZzL2Ev2Mb7OCwm6cHQYmfh1N1xgO5yDjrHOcKzQyQKBgERj+HQ3U6Vk2GHPyClqxfAxhpwz4J2gR1qUohij/Zk0LMT4CkLAyWOsiBjAX/hXVt6v9UdDbEyCdb/3vKfEAkFRxYKD6bv5kO7IA7psKSwQmGVT6hi3/O2AnfUDFmWitpS6NsXvE69FtY34UZZlB9tyJRmu8IWsE9WF5klRh6TxAoGAfCIxI6VjDHjez/YoriErOofV+2HpTiNbARX7H4tAhug1+S3U7yyFUGCOvFK4sP5aDQVhAyA32SvmWlXnviF7KvkVF/Kl5bnBW3sDad78dQtCQEtZhnSglz19p+tEo+KCs8ZP/H8hpV25K13/m9bt75VRD78V5l9gjPKO+E7Pv6M=";
    // 支付宝公钥
    private static final String ALIPAY_PUBLIC_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAmMaOIumXXxb3dYISEUd3bfbtl5jeSPQrwE9VlO2sNwSco0lzLrpzJQuZzOsLZPsnfm0YFXUYANcbLfdEfgO9VC14fkoAisNn9HaCu9q+vEbzWdqzegMKDVw8g6UrJHEKpbNUa+v1yHSH4vtK2WQU9CFvcZIwKrAb8qlBYVbNw77j5aexG6fdLAPqS9kYvdg9kR52jKdXgtUqWGO4sOrn39reY6QOYVrJgpo2foup706LXBEsG1VjYMfvHJFkN7J/JR8Urv8dxegi5vfWrCVZ5ooJc+hsmLVUXz/mOK2yhjHsPyBEMtNcUbdrMft6L5GUl0q/VRvFXuR6waUaqtBkBwIDAQAB";
    // 签名类型
    private static final String SIGN_TYPE = "RSA2";
    // 字符编码格式
    private static final String CHARSET = "UTF-8";
    // 响应格式
    private static final String FORMAT = "json";

    @Bean
    public AlipayClient alipayClient() {
        return new DefaultAlipayClient(GATEWAY_URL, APP_ID, MERCHANT_PRIVATE_KEY, FORMAT, CHARSET, ALIPAY_PUBLIC_KEY, SIGN_TYPE);
    }

}

