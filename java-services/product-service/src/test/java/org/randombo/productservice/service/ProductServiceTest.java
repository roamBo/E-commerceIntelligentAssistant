package org.randombo.productservice.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.randombo.productservice.model.Product;
import org.randombo.productservice.repository.ProductRepository;
import org.randombo.productservice.service.impl.ProductServiceImpl;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductServiceImpl productService;

    private Product testProduct;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        
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
    void testCreateProduct() {
        // Given
        when(productRepository.save(any(Product.class))).thenReturn(testProduct);

        // When
        Product createdProduct = productService.createProduct(testProduct);

        // Then
        assertNotNull(createdProduct);
        assertEquals("iPhone 15 Pro", createdProduct.getName());
        assertEquals("Apple", createdProduct.getBrand());
        assertEquals("AVAILABLE", createdProduct.getStatus());
        verify(productRepository, times(1)).save(any(Product.class));
    }

    @Test
    void testGetProductById() {
        // Given
        when(productRepository.findById("test-id-1")).thenReturn(Optional.of(testProduct));

        // When
        Optional<Product> foundProduct = productService.getProductById("test-id-1");

        // Then
        assertTrue(foundProduct.isPresent());
        assertEquals("iPhone 15 Pro", foundProduct.get().getName());
        verify(productRepository, times(1)).findById("test-id-1");
    }

    @Test
    void testGetProductByIdNotFound() {
        // Given
        when(productRepository.findById("non-existent-id")).thenReturn(Optional.empty());

        // When
        Optional<Product> foundProduct = productService.getProductById("non-existent-id");

        // Then
        assertFalse(foundProduct.isPresent());
        verify(productRepository, times(1)).findById("non-existent-id");
    }

    @Test
    void testGetAllProducts() {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productRepository.findAll()).thenReturn(products);

        // When
        List<Product> allProducts = productService.getAllProducts();

        // Then
        assertNotNull(allProducts);
        assertEquals(1, allProducts.size());
        assertEquals("iPhone 15 Pro", allProducts.get(0).getName());
        verify(productRepository, times(1)).findAll();
    }

    @Test
    void testSearchProductsByName() {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productRepository.findByNameContaining("iPhone")).thenReturn(products);

        // When
        List<Product> searchResults = productService.searchProductsByName("iPhone");

        // Then
        assertNotNull(searchResults);
        assertEquals(1, searchResults.size());
        assertEquals("iPhone 15 Pro", searchResults.get(0).getName());
        verify(productRepository, times(1)).findByNameContaining("iPhone");
    }

    @Test
    void testGetProductsByCategory() {
        // Given
        List<Product> products = Arrays.asList(testProduct);
        when(productRepository.findByCategory("手机")).thenReturn(products);

        // When
        List<Product> categoryProducts = productService.getProductsByCategory("手机");

        // Then
        assertNotNull(categoryProducts);
        assertEquals(1, categoryProducts.size());
        assertEquals("手机", categoryProducts.get(0).getCategory());
        verify(productRepository, times(1)).findByCategory("手机");
    }

    @Test
    void testUpdateStock() {
        // Given
        when(productRepository.findById("test-id-1")).thenReturn(Optional.of(testProduct));
        when(productRepository.save(any(Product.class))).thenReturn(testProduct);

        // When
        Optional<Product> updatedProduct = productService.updateStock("test-id-1", 50);

        // Then
        assertTrue(updatedProduct.isPresent());
        assertEquals(50, updatedProduct.get().getStock());
        verify(productRepository, times(1)).findById("test-id-1");
        verify(productRepository, times(1)).save(any(Product.class));
    }

    @Test
    void testUpdateStockToZero() {
        // Given
        when(productRepository.findById("test-id-1")).thenReturn(Optional.of(testProduct));
        when(productRepository.save(any(Product.class))).thenReturn(testProduct);

        // When
        Optional<Product> updatedProduct = productService.updateStock("test-id-1", 0);

        // Then
        assertTrue(updatedProduct.isPresent());
        assertEquals(0, updatedProduct.get().getStock());
        assertEquals("OUT_OF_STOCK", updatedProduct.get().getStatus());
        verify(productRepository, times(1)).save(any(Product.class));
    }

    @Test
    void testDeleteProduct() {
        // Given
        when(productRepository.existsById("test-id-1")).thenReturn(true);
        doNothing().when(productRepository).deleteById("test-id-1");

        // When
        boolean deleted = productService.deleteProduct("test-id-1");

        // Then
        assertTrue(deleted);
        verify(productRepository, times(1)).existsById("test-id-1");
        verify(productRepository, times(1)).deleteById("test-id-1");
    }

    @Test
    void testDeleteProductNotFound() {
        // Given
        when(productRepository.existsById("non-existent-id")).thenReturn(false);

        // When
        boolean deleted = productService.deleteProduct("non-existent-id");

        // Then
        assertFalse(deleted);
        verify(productRepository, times(1)).existsById("non-existent-id");
        verify(productRepository, never()).deleteById(any());
    }
} 