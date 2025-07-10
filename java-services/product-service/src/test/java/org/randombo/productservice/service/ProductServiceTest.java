package org.randombo.productservice.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.randombo.productservice.model.Product;
import org.randombo.productservice.repository.ProductRepository;
import org.randombo.productservice.service.impl.ProductServiceImpl;
import org.springframework.dao.EmptyResultDataAccessException;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.*;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
public class ProductServiceTest {

    @Mock
    private ProductRepository productRepository;

    @InjectMocks
    private ProductServiceImpl productService;

    // ====================
    // 创建产品测试
    // ====================
    @Test
    public void testCreateProduct_ShouldSetDefaults() {
        Product input = new Product();
        input.setName("TestProduct");
        input.setSku("SKU-123");
        input.setPrice(new BigDecimal("9.99"));

        when(productRepository.save(any(Product.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        Product created = productService.createProduct(input);

        assertNotNull(created.getId(), "应该自动生成 ID");
        assertNotNull(created.getCreateTime(), "应该设置创建时间");
        assertEquals("AVAILABLE", created.getStatus(), "默认状态应为 AVAILABLE");
        verify(productRepository, times(1)).save(created);
    }

    @Test
    public void testCreateProduct_ShouldSetRatingAndReviewCountDefaults() {
        Product input = new Product();
        input.setName("NoRatingProduct");
        input.setSku("SKU-456");

        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        Product created = productService.createProduct(input);

        assertEquals(0.0, created.getRating(), "评分应默认为0.0");
        assertEquals(0, created.getReviewCount(), "评论数应默认为0");
        assertNotNull(created.getUpdateTime(), "应设置更新时间");
    }

    @Test
    public void testCreateProducts_BatchDefaults() {
        List<Product> products = new ArrayList<>();

        Product p1 = new Product();
        p1.setName("Batch1");
        Product p2 = new Product();
        p2.setName("Batch2");
        p2.setStatus(null);
        products.add(p1);
        products.add(p2);

        when(productRepository.saveAll(anyList())).thenAnswer(inv -> inv.getArgument(0));

        List<Product> created = productService.createProducts(products);

        assertEquals(2, created.size());
        created.forEach(product -> {
            assertNotNull(product.getId(), "应自动生成ID");
            assertEquals("AVAILABLE", product.getStatus(), "批量创建应设置默认状态");
            assertEquals(0.0, product.getRating(), "评分应默认为0.0");
            assertNotNull(product.getCreateTime(), "应设置创建时间");
        });
        verify(productRepository, times(1)).saveAll(anyList());
    }

    // ====================
    // 查询产品测试
    // ====================
    @Test
    public void testGetProductById_Found() {
        Product p = new Product();
        p.setId("1");
        when(productRepository.findById("1")).thenReturn(Optional.of(p));

        Optional<Product> result = productService.getProductById("1");
        assertTrue(result.isPresent(), "应该找到产品");
        assertEquals("1", result.get().getId());
    }

    @Test
    public void testGetProductById_NotFound() {
        when(productRepository.findById("unknown")).thenReturn(Optional.empty());

        Optional<Product> result = productService.getProductById("unknown");

        assertTrue(result.isEmpty(), "不存在的ID应返回空Optional");
    }

    @Test
    public void testGetProductBySku_Found() {
        Product p = createFullProduct("1", "TestProduct", "SKU-789");
        when(productRepository.findBySku("SKU-789")).thenReturn(p);

        Optional<Product> result = productService.getProductBySku("SKU-789");
        assertTrue(result.isPresent(), "应该通过SKU找到产品");
        assertEquals("SKU-789", result.get().getSku());
    }

    @Test
    public void testGetAllProducts() {
        List<Product> mockProducts = Arrays.asList(
                createFullProduct("1", "ProductA", "SKU-A"),
                createFullProduct("2", "ProductB", "SKU-B")
        );
        when(productRepository.findAll()).thenReturn(mockProducts);

        List<Product> results = productService.getAllProducts();
        assertEquals(2, results.size());
    }

    @Test
    public void testGetProductsByCategory() {
        List<Product> mockProducts = Arrays.asList(
                createProductWithCategory("1", "Laptop", "CAT-IT"),
                createProductWithCategory("2", "Tablet", "CAT-IT")
        );

        when(productRepository.findByCategory("CAT-IT")).thenReturn(mockProducts);

        List<Product> results = productService.getProductsByCategory("CAT-IT");

        assertEquals(2, results.size());
        assertTrue(results.stream().allMatch(p -> "CAT-IT".equals(p.getCategory())));
    }

    @Test
    public void testGetProductsByBrand() {
        List<Product> mockProducts = Arrays.asList(
                createProductWithBrand("1", "Laptop", "BrandA"),
                createProductWithBrand("2", "Tablet", "BrandA")
        );

        when(productRepository.findByBrand("BrandA")).thenReturn(mockProducts);

        List<Product> results = productService.getProductsByBrand("BrandA");
        assertEquals(2, results.size());
        assertTrue(results.stream().allMatch(p -> "BrandA".equals(p.getBrand())));
    }

    @Test
    public void testGetProductsByPriceRange() {
        List<Product> mockProducts = Arrays.asList(
                createProductWithPrice("1", "Product1", new BigDecimal("50.00")),
                createProductWithPrice("2", "Product2", new BigDecimal("75.00"))
        );

        when(productRepository.findByPriceBetween(
                new BigDecimal("40.00"), new BigDecimal("80.00"))
        ).thenReturn(mockProducts);

        List<Product> results = productService.getProductsByPriceRange(
                new BigDecimal("40.00"), new BigDecimal("80.00"));

        assertEquals(2, results.size());
        assertTrue(results.stream().allMatch(p ->
                p.getPrice().compareTo(new BigDecimal("40.00")) >= 0 &&
                        p.getPrice().compareTo(new BigDecimal("80.00")) <= 0
        ));
    }

    @Test
    public void testGetAvailableProducts() {
        Product available = createProductWithStock("1", "Available", 5);
        Product outOfStock = createProductWithStock("2", "OutOfStock", 0);

        when(productRepository.findByStockGreaterThan(0)).thenReturn(Collections.singletonList(available));

        List<Product> results = productService.getAvailableProducts();

        assertEquals(1, results.size());
        assertEquals(5, results.get(0).getStock());
    }

    // ====================
    // 更新产品测试
    // ====================
    @Test
    public void testUpdateStock_ToZero_ChangesStatus() {
        Product p = createFullProduct("42", "TestProduct", "SKU-001");
        p.setStock(5);
        p.setStatus("AVAILABLE");

        when(productRepository.findById("42")).thenReturn(Optional.of(p));
        when(productRepository.save(any(Product.class)))
                .thenAnswer(inv -> inv.getArgument(0));

        Optional<Product> updated = productService.updateStock("42", 0);
        assertTrue(updated.isPresent());
        assertEquals(0, updated.get().getStock());
        assertEquals("OUT_OF_STOCK", updated.get().getStatus());
        assertNotNull(updated.get().getUpdateTime(), "应更新修改时间");
    }

    @Test
    public void testUpdateStock_FromZeroToPositive_ChangesStatus() {
        Product p = createFullProduct("99", "TestProduct", "SKU-002");
        p.setStock(0);
        p.setStatus("OUT_OF_STOCK");

        when(productRepository.findById("99")).thenReturn(Optional.of(p));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        Optional<Product> updated = productService.updateStock("99", 10);

        assertTrue(updated.isPresent());
        assertEquals(10, updated.get().getStock());
        assertEquals("AVAILABLE", updated.get().getStatus(), "库存恢复时应变更为AVAILABLE");
    }

    @Test
    public void testUpdateStock_NotFound() {
        when(productRepository.findById("missing")).thenReturn(Optional.empty());

        Optional<Product> updated = productService.updateStock("missing", 10);

        assertTrue(updated.isEmpty(), "不存在的产品应返回空Optional");
    }

    @Test
    public void testUpdatePrice_PositiveValue() {
        Product p = createFullProduct("price-1", "TestProduct", "SKU-003");
        p.setPrice(new BigDecimal("19.99"));

        when(productRepository.findById("price-1")).thenReturn(Optional.of(p));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        BigDecimal newPrice = new BigDecimal("15.99");
        Optional<Product> updated = productService.updatePrice("price-1", newPrice);

        assertTrue(updated.isPresent());
        assertEquals(0, newPrice.compareTo(updated.get().getPrice()));
        assertNotNull(updated.get().getUpdateTime(), "应更新修改时间");
    }

    @Test
    public void testUpdatePrice_NegativeValue_ShouldNotUpdate() {
        Product p = createFullProduct("price-2", "TestProduct", "SKU-004");
        p.setPrice(new BigDecimal("10.00"));

        when(productRepository.findById("price-2")).thenReturn(Optional.of(p));

        // 尝试设置负价格
        Optional<Product> updated = productService.updatePrice("price-2", new BigDecimal("-5.00"));

        assertTrue(updated.isPresent());
        // 验证价格未被修改（保持原价）
        assertEquals(0, new BigDecimal("10.00").compareTo(updated.get().getPrice()));
        // 验证没有保存操作发生
        verify(productRepository, never()).save(any());
    }

    @Test
    public void testUpdateStatus() {
        Product p = createFullProduct("status-1", "TestProduct", "SKU-005");
        p.setStatus("AVAILABLE");

        when(productRepository.findById("status-1")).thenReturn(Optional.of(p));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        Optional<Product> updated = productService.updateStatus("status-1", "DISCONTINUED");

        assertTrue(updated.isPresent());
        assertEquals("DISCONTINUED", updated.get().getStatus());
    }

    @Test
    public void testUpdateProduct_FullUpdate() {
        Product existing = createFullProduct("update-1", "OldName", "SKU-OLD");
        existing.setCreateTime(LocalDateTime.now().minusDays(1));

        Product updateData = new Product();
        updateData.setName("NewName");
        updateData.setPrice(new BigDecimal("99.99"));

        when(productRepository.findById("update-1")).thenReturn(Optional.of(existing));
        when(productRepository.save(any(Product.class))).thenAnswer(inv -> inv.getArgument(0));

        Optional<Product> updated = productService.updateProduct("update-1", updateData);

        assertTrue(updated.isPresent());
        assertEquals("NewName", updated.get().getName());
        assertEquals(0, new BigDecimal("99.99").compareTo(updated.get().getPrice()));
        assertEquals(existing.getCreateTime(), updated.get().getCreateTime(), "创建时间不应改变");
        assertNotEquals(existing.getUpdateTime(), updated.get().getUpdateTime(), "更新时间应改变");
    }

    // ====================
    // 删除产品测试
    // ====================
    @Test
    public void testDeleteProduct_Exists() {
        when(productRepository.existsById("foo")).thenReturn(true);

        boolean deleted = productService.deleteProduct("foo");
        assertTrue(deleted, "存在时应删除并返回 true");
        verify(productRepository, times(1)).deleteById("foo");
    }

    @Test
    public void testDeleteProduct_NotExists() {
        when(productRepository.existsById("bar")).thenReturn(false);

        boolean deleted = productService.deleteProduct("bar");
        assertFalse(deleted, "不存在时应返回 false");
        verify(productRepository, never()).deleteById(anyString());
    }

    @Test
    public void testDeleteProduct_ConcurrentDeletion() {
        // 第一次检查存在
        when(productRepository.existsById("concurrent")).thenReturn(true);
        // 模拟在删除前其他线程已删除
        doThrow(new EmptyResultDataAccessException(1)).when(productRepository).deleteById("concurrent");

        boolean result = productService.deleteProduct("concurrent");

        assertFalse(result, "并发删除时应返回false");
        verify(productRepository, times(1)).deleteById("concurrent");
    }

    // ====================
    // 其他功能测试
    // ====================
    @Test
    public void testGetTopRatedProducts() {
        List<Product> mockProducts = Arrays.asList(
                createProductWithRating("1", "ProductA", 4.8),
                createProductWithRating("2", "ProductB", 4.5),
                createProductWithRating("3", "ProductC", 3.9)
        );

        when(productRepository.findByRatingGreaterThanEqual(0.0)).thenReturn(mockProducts);

        List<Product> results = productService.getTopRatedProducts(2);

        assertEquals(2, results.size());
        assertEquals("ProductA", results.get(0).getName()); // 最高评分
        assertEquals("ProductB", results.get(1).getName()); // 次高评分
    }

    @Test
    public void testGetLatestProducts() {
        Product oldProduct = createFullProduct("old", "OldProduct", "SKU-OLD");
        oldProduct.setCreateTime(LocalDateTime.now().minusDays(2));

        Product newProduct = createFullProduct("new", "NewProduct", "SKU-NEW");
        newProduct.setCreateTime(LocalDateTime.now());

        when(productRepository.findAll()).thenReturn(Arrays.asList(oldProduct, newProduct));

        List<Product> results = productService.getLatestProducts(1);

        assertEquals(1, results.size());
        assertEquals("NewProduct", results.get(0).getName());
    }

    @Test
    public void testGetRecommendedProducts() {
        List<Product> mockProducts = Arrays.asList(
                createProductWithCategoryAndRating("1", "Laptop", "CAT-IT", 4.2),
                createProductWithCategoryAndRating("2", "Tablet", "CAT-IT", 4.8),
                createProductWithCategoryAndRating("3", "Phone", "CAT-IT", 3.9)
        );

        when(productRepository.findByCategory("CAT-IT")).thenReturn(mockProducts);

        List<Product> results = productService.getRecommendedProducts("CAT-IT", 2);

        assertEquals(2, results.size());
        assertEquals("Tablet", results.get(0).getName()); // 最高评分
        assertEquals("Laptop", results.get(1).getName()); // 次高评分
    }

    @Test
    public void testSearchProductsByName_FallbackLogic() {
        // 模拟所有搜索方法都返回空
        when(productRepository.searchByNameWithAnalyzer(anyString())).thenReturn(Collections.emptyList());
        when(productRepository.searchByNameWildcard(anyString())).thenReturn(Collections.emptyList());
        when(productRepository.searchByMultipleFields(anyString())).thenReturn(Collections.emptyList());
        when(productRepository.findByNameContaining(anyString())).thenReturn(Collections.emptyList());

        // 设置内存中有产品
        Product memoryProduct = createFullProduct("memory", "MemoryProduct", "SKU-MEM");
        when(productRepository.findAll()).thenReturn(Collections.singletonList(memoryProduct));

        List<Product> results = productService.searchProductsByName("Memory");

        assertEquals(1, results.size());
        assertEquals("MemoryProduct", results.get(0).getName());
        assertNotNull(results.get(0).getPrice(), "产品价格不应为空");
    }

    // ====================
    // 辅助方法 - 创建完整产品数据
    // ====================
    private Product createFullProduct(String id, String name, String sku) {
        Product p = new Product();
        p.setId(id);
        p.setName(name);
        p.setSku(sku);
        p.setPrice(new BigDecimal("99.99"));
        p.setStock(10);
        p.setRating(4.5);
        p.setReviewCount(100);
        p.setStatus("AVAILABLE");
        p.setCreateTime(LocalDateTime.now());
        p.setUpdateTime(LocalDateTime.now());
        return p;
    }

    private Product createProductWithCategory(String id, String name, String category) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setCategory(category);
        return p;
    }

    private Product createProductWithBrand(String id, String name, String brand) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setBrand(brand);
        return p;
    }

    private Product createProductWithPrice(String id, String name, BigDecimal price) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setPrice(price);
        return p;
    }

    private Product createProductWithStock(String id, String name, int stock) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setStock(stock);
        return p;
    }

    private Product createProductWithRating(String id, String name, double rating) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setRating(rating);
        return p;
    }

    private Product createProductWithCategoryAndRating(String id, String name, String category, double rating) {
        Product p = createFullProduct(id, name, "SKU-" + id);
        p.setCategory(category);
        p.setRating(rating);
        return p;
    }
}