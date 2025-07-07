package org.randombo.productservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.randombo.productservice.model.Product;
import org.randombo.productservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureWebMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;
import org.springframework.web.context.WebApplicationContext;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureWebMvc
class ProductControllerIntegrationTest {

    @Autowired
    private WebApplicationContext webApplicationContext;

    @MockBean
    private ProductService productService;

    private MockMvc mockMvc;
    private ObjectMapper objectMapper;
    private Product testProduct;

    @BeforeEach
    void setUp() {
        mockMvc = MockMvcBuilders.webAppContextSetup(webApplicationContext).build();
        objectMapper = new ObjectMapper();
        
        testProduct = new Product();
        testProduct.setId("test-id-1");
        testProduct.setName("iPhone 15 Pro");
        testProduct.setDescription("苹果最新旗舰手机");
        testProduct.setCategory("手机");
        testProduct.setBrand("Apple");
        testProduct.setPrice(new BigDecimal("7999.00"));
        testProduct.setStock(100);
        testProduct.setStatus("AVAILABLE");
        testProduct.setTags(Arrays.asList("智能手机", "5G", "高端"));
        testProduct.setSku("IPHONE15PRO-256GB");
        testProduct.setSpecifications("256GB存储，A17 Pro芯片");
        testProduct.setCreateTime(LocalDateTime.now());
        testProduct.setUpdateTime(LocalDateTime.now());
        testProduct.setRating(4.8);
        testProduct.setReviewCount(50);
    }

    @Test
    void testCreateProduct() throws Exception {
        // Given
        when(productService.createProduct(any(Product.class))).thenReturn(testProduct);

        // When & Then
        mockMvc.perform(post("/api/products")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testProduct)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("test-id-1"))
                .andExpect(jsonPath("$.name").value("iPhone 15 Pro"))
                .andExpect(jsonPath("$.brand").value("Apple"))
                .andExpect(jsonPath("$.status").value("AVAILABLE"));
    }

    @Test
    void testGetAllProducts() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.getAllProducts()).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].id").value("test-id-1"))
                .andExpect(jsonPath("$[0].name").value("iPhone 15 Pro"))
                .andExpect(jsonPath("$[0].brand").value("Apple"));
    }

    @Test
    void testGetProductById() throws Exception {
        // Given
        when(productService.getProductById("test-id-1")).thenReturn(Optional.of(testProduct));

        // When & Then
        mockMvc.perform(get("/api/products/test-id-1"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("test-id-1"))
                .andExpect(jsonPath("$.name").value("iPhone 15 Pro"))
                .andExpect(jsonPath("$.brand").value("Apple"));
    }

    @Test
    void testGetProductByIdNotFound() throws Exception {
        // Given
        when(productService.getProductById("non-existent-id")).thenReturn(Optional.empty());

        // When & Then
        mockMvc.perform(get("/api/products/non-existent-id"))
                .andExpect(status().isNotFound());
    }

    @Test
    void testSearchProductsByName() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.searchProductsByName("iPhone")).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products/search")
                .param("name", "iPhone"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("iPhone 15 Pro"));
    }

    @Test
    void testGetProductsByCategory() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.getProductsByCategory("手机")).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products/category/手机"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].category").value("手机"));
    }

    @Test
    void testGetProductsByBrand() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.getProductsByBrand("Apple")).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products/brand/Apple"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].brand").value("Apple"));
    }

    @Test
    void testUpdateProduct() throws Exception {
        // Given
        when(productService.updateProduct(anyString(), any(Product.class)))
                .thenReturn(Optional.of(testProduct));

        // When & Then
        mockMvc.perform(put("/api/products/test-id-1")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testProduct)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("test-id-1"))
                .andExpect(jsonPath("$.name").value("iPhone 15 Pro"));
    }

    @Test
    void testUpdateProductNotFound() throws Exception {
        // Given
        when(productService.updateProduct(anyString(), any(Product.class)))
                .thenReturn(Optional.empty());

        // When & Then
        mockMvc.perform(put("/api/products/non-existent-id")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(testProduct)))
                .andExpect(status().isNotFound());
    }

    @Test
    void testUpdateStock() throws Exception {
        // Given
        when(productService.updateStock("test-id-1", 50))
                .thenReturn(Optional.of(testProduct));

        // When & Then
        mockMvc.perform(patch("/api/products/test-id-1/stock")
                .param("stock", "50"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("test-id-1"));
    }

    @Test
    void testDeleteProduct() throws Exception {
        // Given
        when(productService.deleteProduct("test-id-1")).thenReturn(true);

        // When & Then
        mockMvc.perform(delete("/api/products/test-id-1"))
                .andExpect(status().isNoContent());
    }

    @Test
    void testDeleteProductNotFound() throws Exception {
        // Given
        when(productService.deleteProduct("non-existent-id")).thenReturn(false);

        // When & Then
        mockMvc.perform(delete("/api/products/non-existent-id"))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetTopRatedProducts() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.getTopRatedProducts(5)).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products/top-rated")
                .param("limit", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("iPhone 15 Pro"));
    }

    @Test
    void testGetAvailableProducts() throws Exception {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productService.getAvailableProducts()).thenReturn(products);

        // When & Then
        mockMvc.perform(get("/api/products/available"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].status").value("AVAILABLE"));
    }
} 