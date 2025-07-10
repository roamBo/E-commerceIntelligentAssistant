package org.randombo.productservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;
import org.randombo.productservice.model.Product;
import org.randombo.productservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders;
import org.springframework.test.web.servlet.result.MockMvcResultMatchers;

import java.math.BigDecimal;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Optional;

@WebMvcTest(ProductController.class)
public class ProductControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ProductService productService;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private Product createTestProduct() {
        Product product = new Product();
        product.setId("prod-123");
        product.setName("Test Product");
        product.setSku("SKU-001");
        product.setPrice(BigDecimal.valueOf(99.99));
        product.setStock(10);
        product.setCategory("Electronics");
        product.setBrand("TestBrand");
        return product;
    }

    @Test
    public void testCreateProduct() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.createProduct(Mockito.any(Product.class)))
                .thenReturn(product);

        mockMvc.perform(MockMvcRequestBuilders.post("/api/products")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(product)))
                .andExpect(MockMvcResultMatchers.status().isCreated())
                .andExpect(MockMvcResultMatchers.jsonPath("$.id").value("prod-123"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.name").value("Test Product"));
    }

    @Test
    public void testBatchCreateProducts() throws Exception {
        Product product1 = createTestProduct();
        Product product2 = createTestProduct();
        product2.setId("prod-456");
        product2.setSku("SKU-002");

        List<Product> products = Arrays.asList(product1, product2);

        Mockito.when(productService.createProducts(Mockito.anyList()))
                .thenReturn(products);

        mockMvc.perform(MockMvcRequestBuilders.post("/api/products/batch")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(products)))
                .andExpect(MockMvcResultMatchers.status().isCreated())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(2))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].id").value("prod-123"))
                .andExpect(MockMvcResultMatchers.jsonPath("$[1].id").value("prod-456"));
    }

    @Test
    public void testGetAllProducts() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getAllProducts())
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].name").value("Test Product"));
    }

    @Test
    public void testGetAllProductsPaginated() throws Exception {
        Product product = createTestProduct();
        Pageable pageable = PageRequest.of(0, 10);
        Page<Product> page = new PageImpl<>(Collections.singletonList(product), pageable, 1);

        Mockito.when(productService.getAllProducts(Mockito.any(Pageable.class)))
                .thenReturn(page);

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products?page=0&size=10"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.content.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$.content[0].sku").value("SKU-001"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.totalElements").value(1));
    }

    @Test
    public void testGetProductById_Found() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getProductById("prod-123"))
                .thenReturn(Optional.of(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/prod-123"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.id").value("prod-123"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.price").value(99.99));
    }

    @Test
    public void testGetProductById_NotFound() throws Exception {
        Mockito.when(productService.getProductById("unknown-id"))
                .thenReturn(Optional.empty());

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/unknown-id"))
                .andExpect(MockMvcResultMatchers.status().isNotFound());
    }

    @Test
    public void testGetProductBySku() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getProductBySku("SKU-001"))
                .thenReturn(Optional.of(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/sku/SKU-001"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.sku").value("SKU-001"));
    }

    @Test
    public void testSearchProductsByName() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.searchProductsByName("Test"))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/search?name=Test"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].name").value("Test Product"));
    }

    @Test
    public void testUpdateProduct() throws Exception {
        Product existingProduct = createTestProduct();
        Product updatedProduct = createTestProduct();
        updatedProduct.setName("Updated Product");
        updatedProduct.setPrice(BigDecimal.valueOf(129.99));

        Mockito.when(productService.updateProduct("prod-123", updatedProduct))
                .thenReturn(Optional.of(updatedProduct));

        mockMvc.perform(MockMvcRequestBuilders.put("/api/products/prod-123")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updatedProduct)))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.name").value("Updated Product"))
                .andExpect(MockMvcResultMatchers.jsonPath("$.price").value(129.99));
    }

    @Test
    public void testUpdateStock() throws Exception {
        Product product = createTestProduct();
        product.setStock(20);

        Mockito.when(productService.updateStock("prod-123", 20))
                .thenReturn(Optional.of(product));

        mockMvc.perform(MockMvcRequestBuilders.patch("/api/products/prod-123/stock?stock=20"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.stock").value(20));
    }

    @Test
    public void testDeleteProduct_Success() throws Exception {
        Mockito.when(productService.deleteProduct("prod-123"))
                .thenReturn(true);

        mockMvc.perform(MockMvcRequestBuilders.delete("/api/products/prod-123"))
                .andExpect(MockMvcResultMatchers.status().isNoContent());
    }

    @Test
    public void testDeleteProduct_NotFound() throws Exception {
        Mockito.when(productService.deleteProduct("unknown-id"))
                .thenReturn(false);

        mockMvc.perform(MockMvcRequestBuilders.delete("/api/products/unknown-id"))
                .andExpect(MockMvcResultMatchers.status().isNotFound());
    }

    @Test
    public void testGetProductsByPriceRange() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getProductsByPriceRange(
                        Mockito.any(BigDecimal.class),
                        Mockito.any(BigDecimal.class)))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/price-range?minPrice=50&maxPrice=100"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].price").value(99.99));
    }

    @Test
    public void testGetAvailableProducts() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getAvailableProducts())
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/available"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].stock").value(10));
    }
    @Test
    public void testGetProductsByCategory() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getProductsByCategory("Electronics"))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/category/Electronics"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].category").value("Electronics"));
    }

    @Test
    public void testGetProductsByBrand() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getProductsByBrand("TestBrand"))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/brand/TestBrand"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].brand").value("TestBrand"));
    }

    @Test
    public void testGetProductsByTag() throws Exception {
        Product product = createTestProduct();
        product.setTags(Arrays.asList("new", "sale"));

        Mockito.when(productService.getProductsByTag("sale"))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/tag/sale"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].tags").isArray())
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].tags[1]").value("sale"));
    }

    @Test
    public void testGetTopRatedProducts() throws Exception {
        Product product = createTestProduct();
        product.setRating(4.8);

        Mockito.when(productService.getTopRatedProducts(5))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/top-rated?limit=5"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].rating").value(4.8));
    }

    @Test
    public void testGetLatestProducts() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getLatestProducts(3))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/latest?limit=3"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].name").value("Test Product"));
    }

    @Test
    public void testGetRecommendedProducts() throws Exception {
        Product product = createTestProduct();

        Mockito.when(productService.getRecommendedProducts("Electronics", 5))
                .thenReturn(Collections.singletonList(product));

        mockMvc.perform(MockMvcRequestBuilders.get("/api/products/recommended/Electronics?limit=5"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.length()").value(1))
                .andExpect(MockMvcResultMatchers.jsonPath("$[0].category").value("Electronics"));
    }

    @Test
    public void testUpdatePrice() throws Exception {
        Product product = createTestProduct();
        product.setPrice(BigDecimal.valueOf(149.99));

        Mockito.when(productService.updatePrice("prod-123", BigDecimal.valueOf(149.99)))
                .thenReturn(Optional.of(product));

        mockMvc.perform(MockMvcRequestBuilders.patch("/api/products/prod-123/price?price=149.99"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.price").value(149.99));
    }

    @Test
    public void testUpdateStatus() throws Exception {
        Product product = createTestProduct();
        product.setStatus("DISCONTINUED");

        Mockito.when(productService.updateStatus("prod-123", "DISCONTINUED"))
                .thenReturn(Optional.of(product));

        mockMvc.perform(MockMvcRequestBuilders.patch("/api/products/prod-123/status?status=DISCONTINUED"))
                .andExpect(MockMvcResultMatchers.status().isOk())
                .andExpect(MockMvcResultMatchers.jsonPath("$.status").value("DISCONTINUED"));
    }
}