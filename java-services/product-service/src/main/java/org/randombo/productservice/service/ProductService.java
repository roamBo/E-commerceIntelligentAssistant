package org.randombo.productservice.service;

import org.randombo.productservice.model.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;

public interface ProductService {

    // 创建商品
    Product createProduct(Product product);

    // 根据ID获取商品
    Optional<Product> getProductById(String id);

    // 根据SKU获取商品
    Optional<Product> getProductBySku(String sku);

    // 获取所有商品
    List<Product> getAllProducts();

    // 分页获取所有商品
    Page<Product> getAllProducts(Pageable pageable);

    // 根据名称搜索商品
    List<Product> searchProductsByName(String name);

    // 根据分类获取商品
    List<Product> getProductsByCategory(String category);

    // 根据品牌获取商品
    List<Product> getProductsByBrand(String brand);

    // 根据价格范围获取商品
    List<Product> getProductsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice);

    // 根据标签获取商品
    List<Product> getProductsByTag(String tag);

    // 获取有库存的商品
    List<Product> getAvailableProducts();

    // 更新商品
    Optional<Product> updateProduct(String id, Product product);

    // 更新商品库存
    Optional<Product> updateStock(String id, Integer newStock);

    // 更新商品价格
    Optional<Product> updatePrice(String id, BigDecimal newPrice);

    // 更新商品状态
    Optional<Product> updateStatus(String id, String status);

    // 删除商品
    boolean deleteProduct(String id);

    // 批量创建商品
    List<Product> createProducts(List<Product> products);

    // 获取热门商品（按评分排序）
    List<Product> getTopRatedProducts(int limit);

    // 获取最新商品
    List<Product> getLatestProducts(int limit);

    // 获取推荐商品（基于分类）
    List<Product> getRecommendedProducts(String category, int limit);
}