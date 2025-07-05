package org.randombo.productservice.http;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.randombo.productservice.model.Product;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.test.context.TestPropertySource;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = {
    "spring.elasticsearch.uris=http://localhost:9200",
    "spring.cloud.nacos.discovery.enabled=false"
})
class ProductHttpClientTest {

    @LocalServerPort
    private int port;

    @Autowired
    private RestTemplate restTemplate;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final String baseUrl = "http://localhost:";

    @Test
    void testCreateAndGetProduct() {
        // 创建测试商品
        Product product = createTestProduct();
        
        // 发送POST请求创建商品
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Product> request = new HttpEntity<>(product, headers);
        
        ResponseEntity<Product> response = restTemplate.exchange(
            baseUrl + port + "/api/products",
            HttpMethod.POST,
            request,
            Product.class
        );
        
        // 验证响应
        assertEquals(201, response.getStatusCodeValue());
        assertNotNull(response.getBody());
        assertNotNull(response.getBody().getId());
        assertEquals("iPhone 15 Pro", response.getBody().getName());
        
        // 获取创建的商品ID
        String productId = response.getBody().getId();
        
        // 发送GET请求获取商品
        ResponseEntity<Product> getResponse = restTemplate.exchange(
            baseUrl + port + "/api/products/" + productId,
            HttpMethod.GET,
            null,
            Product.class
        );
        
        // 验证获取响应
        assertEquals(200, getResponse.getStatusCodeValue());
        assertNotNull(getResponse.getBody());
        assertEquals(productId, getResponse.getBody().getId());
        assertEquals("iPhone 15 Pro", getResponse.getBody().getName());
    }

    @Test
    void testGetAllProducts() {
        // 发送GET请求获取所有商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
        assertTrue(response.getBody().length > 0);
    }

    @Test
    void testSearchProducts() {
        // 发送GET请求搜索商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products/search?name=iPhone",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
    }

    @Test
    void testGetProductsByCategory() {
        // 发送GET请求按分类获取商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products/category/手机",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
    }

    @Test
    void testGetProductsByBrand() {
        // 发送GET请求按品牌获取商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products/brand/Apple",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
    }

    @Test
    void testUpdateProduct() {
        // 首先创建一个商品
        Product product = createTestProduct();
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Product> createRequest = new HttpEntity<>(product, headers);
        
        ResponseEntity<Product> createResponse = restTemplate.exchange(
            baseUrl + port + "/api/products",
            HttpMethod.POST,
            createRequest,
            Product.class
        );
        
        String productId = createResponse.getBody().getId();
        
        // 更新商品信息
        Product updateProduct = createResponse.getBody();
        updateProduct.setName("iPhone 15 Pro Max");
        updateProduct.setPrice(new BigDecimal("8999.00"));
        
        HttpEntity<Product> updateRequest = new HttpEntity<>(updateProduct, headers);
        
        ResponseEntity<Product> updateResponse = restTemplate.exchange(
            baseUrl + port + "/api/products/" + productId,
            HttpMethod.PUT,
            updateRequest,
            Product.class
        );
        
        // 验证更新响应
        assertEquals(200, updateResponse.getStatusCodeValue());
        assertNotNull(updateResponse.getBody());
        assertEquals("iPhone 15 Pro Max", updateResponse.getBody().getName());
        assertEquals(new BigDecimal("8999.00"), updateResponse.getBody().getPrice());
    }

    @Test
    void testUpdateStock() {
        // 首先创建一个商品
        Product product = createTestProduct();
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Product> createRequest = new HttpEntity<>(product, headers);
        
        ResponseEntity<Product> createResponse = restTemplate.exchange(
            baseUrl + port + "/api/products",
            HttpMethod.POST,
            createRequest,
            Product.class
        );
        
        String productId = createResponse.getBody().getId();
        
        // 更新库存
        ResponseEntity<Product> updateResponse = restTemplate.exchange(
            baseUrl + port + "/api/products/" + productId + "/stock?stock=50",
            HttpMethod.PATCH,
            null,
            Product.class
        );
        
        // 验证更新响应
        assertEquals(200, updateResponse.getStatusCodeValue());
        assertNotNull(updateResponse.getBody());
        assertEquals(50, updateResponse.getBody().getStock());
    }

    @Test
    void testDeleteProduct() {
        // 首先创建一个商品
        Product product = createTestProduct();
        
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Product> createRequest = new HttpEntity<>(product, headers);
        
        ResponseEntity<Product> createResponse = restTemplate.exchange(
            baseUrl + port + "/api/products",
            HttpMethod.POST,
            createRequest,
            Product.class
        );
        
        String productId = createResponse.getBody().getId();
        
        // 删除商品
        ResponseEntity<Void> deleteResponse = restTemplate.exchange(
            baseUrl + port + "/api/products/" + productId,
            HttpMethod.DELETE,
            null,
            Void.class
        );
        
        // 验证删除响应
        assertEquals(204, deleteResponse.getStatusCodeValue());
        
        // 验证商品已被删除
        ResponseEntity<Product> getResponse = restTemplate.exchange(
            baseUrl + port + "/api/products/" + productId,
            HttpMethod.GET,
            null,
            Product.class
        );
        
        assertEquals(404, getResponse.getStatusCodeValue());
    }

    @Test
    void testGetTopRatedProducts() {
        // 发送GET请求获取热门商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products/top-rated?limit=5",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
    }

    @Test
    void testGetAvailableProducts() {
        // 发送GET请求获取有库存的商品
        ResponseEntity<Product[]> response = restTemplate.exchange(
            baseUrl + port + "/api/products/available",
            HttpMethod.GET,
            null,
            Product[].class
        );
        
        // 验证响应
        assertEquals(200, response.getStatusCodeValue());
        assertNotNull(response.getBody());
    }

    private Product createTestProduct() {
        Product product = new Product();
        product.setName("iPhone 15 Pro");
        product.setDescription("苹果最新旗舰手机");
        product.setCategory("手机");
        product.setBrand("Apple");
        product.setPrice(new BigDecimal("7999.00"));
        product.setStock(100);
        product.setStatus("AVAILABLE");
        product.setTags(Arrays.asList("智能手机", "5G", "高端"));
        product.setSku("IPHONE15PRO-256GB");
        product.setSpecifications("256GB存储，A17 Pro芯片");
        product.setRating(4.8);
        product.setReviewCount(50);
        return product;
    }
} 