package org.randombo.productservice.controller;

import org.randombo.productservice.model.Product;
import org.randombo.productservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/products")
public class ProductController {

    @Autowired
    private ProductService productService;

    // 1. 创建商品：POST /api/products
    @PostMapping
    public ResponseEntity<Product> createProduct(@RequestBody Product product) {
        Product createdProduct = productService.createProduct(product);
        return new ResponseEntity<>(createdProduct, HttpStatus.CREATED);
    }

    // 2. 批量创建商品：POST /api/products/batch
    @PostMapping("/batch")
    public ResponseEntity<List<Product>> createProducts(@RequestBody List<Product> products) {
        List<Product> createdProducts = productService.createProducts(products);
        return new ResponseEntity<>(createdProducts, HttpStatus.CREATED);
    }

    // 3. 获取所有商品：GET /api/products
    @GetMapping
    public ResponseEntity<List<Product>> getAllProducts() {
        List<Product> products = productService.getAllProducts();
        return ResponseEntity.ok(products);
    }

    // 4. 分页获取所有商品：GET /api/products?page=0&size=10
    @GetMapping(params = {"page", "size"})
    public ResponseEntity<Page<Product>> getAllProductsPaginated(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        Pageable pageable = PageRequest.of(page, size);
        Page<Product> products = productService.getAllProducts(pageable);
        return ResponseEntity.ok(products);
    }

    // 5. 根据ID获取商品：GET /api/products/{id}
    @GetMapping("/{id}")
    public ResponseEntity<Product> getProductById(@PathVariable String id) {
        Optional<Product> product = productService.getProductById(id);
        return product.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 6. 根据SKU获取商品：GET /api/products/sku/{sku}
    @GetMapping("/sku/{sku}")
    public ResponseEntity<Product> getProductBySku(@PathVariable String sku) {
        Optional<Product> product = productService.getProductBySku(sku);
        return product.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 7. 根据名称搜索商品：GET /api/products/search?name=手机
    @GetMapping("/search")
    public ResponseEntity<List<Product>> searchProductsByName(@RequestParam String name) {
        List<Product> products = productService.searchProductsByName(name);
        return ResponseEntity.ok(products);
    }

    // 8. 根据分类获取商品：GET /api/products/category/{category}
    @GetMapping("/category/{category}")
    public ResponseEntity<List<Product>> getProductsByCategory(@PathVariable String category) {
        List<Product> products = productService.getProductsByCategory(category);
        return ResponseEntity.ok(products);
    }

    // 9. 根据品牌获取商品：GET /api/products/brand/{brand}
    @GetMapping("/brand/{brand}")
    public ResponseEntity<List<Product>> getProductsByBrand(@PathVariable String brand) {
        List<Product> products = productService.getProductsByBrand(brand);
        return ResponseEntity.ok(products);
    }

    // 10. 根据价格范围获取商品：GET /api/products/price-range?minPrice=100&maxPrice=1000
    @GetMapping("/price-range")
    public ResponseEntity<List<Product>> getProductsByPriceRange(
            @RequestParam BigDecimal minPrice,
            @RequestParam BigDecimal maxPrice) {
        List<Product> products = productService.getProductsByPriceRange(minPrice, maxPrice);
        return ResponseEntity.ok(products);
    }

    // 11. 根据标签获取商品：GET /api/products/tag/{tag}
    @GetMapping("/tag/{tag}")
    public ResponseEntity<List<Product>> getProductsByTag(@PathVariable String tag) {
        List<Product> products = productService.getProductsByTag(tag);
        return ResponseEntity.ok(products);
    }

    // 12. 获取有库存的商品：GET /api/products/available
    @GetMapping("/available")
    public ResponseEntity<List<Product>> getAvailableProducts() {
        List<Product> products = productService.getAvailableProducts();
        return ResponseEntity.ok(products);
    }

    // 13. 获取热门商品：GET /api/products/top-rated?limit=10
    @GetMapping("/top-rated")
    public ResponseEntity<List<Product>> getTopRatedProducts(@RequestParam(defaultValue = "10") int limit) {
        List<Product> products = productService.getTopRatedProducts(limit);
        return ResponseEntity.ok(products);
    }

    // 14. 获取最新商品：GET /api/products/latest?limit=10
    @GetMapping("/latest")
    public ResponseEntity<List<Product>> getLatestProducts(@RequestParam(defaultValue = "10") int limit) {
        List<Product> products = productService.getLatestProducts(limit);
        return ResponseEntity.ok(products);
    }

    // 15. 获取推荐商品：GET /api/products/recommended/{category}?limit=10
    @GetMapping("/recommended/{category}")
    public ResponseEntity<List<Product>> getRecommendedProducts(
            @PathVariable String category,
            @RequestParam(defaultValue = "10") int limit) {
        List<Product> products = productService.getRecommendedProducts(category, limit);
        return ResponseEntity.ok(products);
    }

    // 16. 更新商品：PUT /api/products/{id}
    @PutMapping("/{id}")
    public ResponseEntity<Product> updateProduct(@PathVariable String id, @RequestBody Product product) {
        Optional<Product> updatedProduct = productService.updateProduct(id, product);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 17. 更新商品库存：PATCH /api/products/{id}/stock
    @PatchMapping("/{id}/stock")
    public ResponseEntity<Product> updateStock(@PathVariable String id, @RequestParam Integer stock) {
        Optional<Product> updatedProduct = productService.updateStock(id, stock);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 18. 更新商品价格：PATCH /api/products/{id}/price
    @PatchMapping("/{id}/price")
    public ResponseEntity<Product> updatePrice(@PathVariable String id, @RequestParam BigDecimal price) {
        Optional<Product> updatedProduct = productService.updatePrice(id, price);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 19. 更新商品状态：PATCH /api/products/{id}/status
    @PatchMapping("/{id}/status")
    public ResponseEntity<Product> updateStatus(@PathVariable String id, @RequestParam String status) {
        Optional<Product> updatedProduct = productService.updateStatus(id, status);
        return updatedProduct.map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }

    // 20. 删除商品：DELETE /api/products/{id}
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteProduct(@PathVariable String id) {
        boolean deleted = productService.deleteProduct(id);
        if (deleted) {
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}