package org.randombo.productservice.service.impl;

import org.randombo.productservice.model.Product;
import org.randombo.productservice.repository.ProductRepository;
import org.randombo.productservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.stream.StreamSupport;

@Service
public class ProductServiceImpl implements ProductService {

    @Autowired
    private ProductRepository productRepository;

    @Override
    public Product createProduct(Product product) {
        product.setId(UUID.randomUUID().toString());
        product.setCreateTime(LocalDateTime.now());
        product.setUpdateTime(LocalDateTime.now());
        if (product.getStatus() == null) {
            product.setStatus("AVAILABLE");
        }
        if (product.getRating() == null) {
            product.setRating(0.0);
        }
        if (product.getReviewCount() == null) {
            product.setReviewCount(0);
        }
        return productRepository.save(product);
    }

    @Override
    public Optional<Product> getProductById(String id) {
        return productRepository.findById(id);
    }

    @Override
    public Optional<Product> getProductBySku(String sku) {
        return Optional.ofNullable(productRepository.findBySku(sku));
    }

    @Override
    public List<Product> getAllProducts() {
        // 方法2：使用StreamSupport转换Iterable
        Iterable<Product> products = productRepository.findAll();
        return StreamSupport.stream(products.spliterator(), false)
                .collect(Collectors.toList());
//        try {
//            // 方法1：使用分页查询（推荐）
//            Pageable pageable = PageRequest.of(0, Integer.MAX_VALUE);
//            return productRepository.findAll(pageable).getContent();
//        } catch (Exception e) {
//            System.err.println("查询所有商品失败: " + e.getMessage());
//            try {
//
//            } catch (Exception ex) {
//                System.err.println("备用查询方法也失败: " + ex.getMessage());
//                return new ArrayList<>();
//            }
//        }
    }

    @Override
    public Page<Product> getAllProducts(Pageable pageable) {
        return productRepository.findAll(pageable);
    }

    @Override
    public List<Product> searchProductsByName(String name) {
//        return productRepository.findByNameContaining(name);
//        try {
//            // 首先尝试使用分析器搜索
//            List<Product> results = productRepository.searchByNameWithAnalyzer(name);
//
//            // 如果结果为空，尝试模糊搜索
//            if (results.isEmpty()) {
//                results = productRepository.searchByNameWildcard(name);
//            }
//
//            // 如果还是为空，尝试多字段搜索
//            if (results.isEmpty()) {
//                results = productRepository.searchByMultipleFields(name);
//            }
//
//            // 如果还是为空，使用原始的containing方法作为最后的备选
//            if (results.isEmpty()) {
//                results = productRepository.findByNameContaining(name);
//            }
//
//            System.out.println("搜索关键词: " + name + ", 找到 " + results.size() + " 个结果");
//            results.forEach(product ->
//                    System.out.println("  - " + product.getName() + " (¥" + product.getPrice() + ")")
//            );
//
//            return results;
//        } catch (Exception e) {
//            System.err.println("搜索商品失败: " + e.getMessage());
//            e.printStackTrace();
//            // 返回空列表而不是抛出异常
//            return new ArrayList<>();
//        }
        try {
            System.out.println("=== 开始搜索商品，关键词: " + name + " ===");

            // 首先尝试使用分析器搜索
            System.out.println("1. 尝试使用分析器搜索...");
            List<Product> results = productRepository.searchByNameWithAnalyzer(name);
            System.out.println("   分析器搜索结果数量: " + results.size());

            // 如果结果为空，尝试模糊搜索
            if (results.isEmpty()) {
                System.out.println("2. 尝试模糊搜索...");
                results = productRepository.searchByNameWildcard(name);
                System.out.println("   模糊搜索结果数量: " + results.size());
            }

            // 如果还是为空，尝试多字段搜索
            if (results.isEmpty()) {
                System.out.println("3. 尝试多字段搜索...");
                results = productRepository.searchByMultipleFields(name);
                System.out.println("   多字段搜索结果数量: " + results.size());
            }

            // 如果还是为空，使用原始的containing方法作为最后的备选
            if (results.isEmpty()) {
                System.out.println("4. 尝试原始containing搜索...");
                results = productRepository.findByNameContaining(name);
                System.out.println("   containing搜索结果数量: " + results.size());
            }

            // 如果还是为空，尝试直接查询所有商品并在内存中过滤
            if (results.isEmpty()) {
                System.out.println("5. 尝试内存中过滤...");
                List<Product> allProducts = getAllProducts();
                results = allProducts.stream()
                        .filter(product -> product.getName() != null &&
                                product.getName().toLowerCase().contains(name.toLowerCase()))
                        .collect(Collectors.toList());
                System.out.println("   内存过滤结果数量: " + results.size());
            }

            System.out.println("=== 搜索完成，关键词: " + name + ", 找到 " + results.size() + " 个结果 ===");
            results.forEach(product ->
                    System.out.println("  - " + product.getName() + " (¥" + product.getPrice() + ")")
            );

            return results;
        } catch (Exception e) {
            System.err.println("搜索商品失败: " + e.getMessage());
            System.err.println("错误类型: " + e.getClass().getSimpleName());
            e.printStackTrace();

            // 尝试从内存中搜索作为最后的备选方案
            try {
                System.out.println("尝试从内存中搜索作为备选方案...");
                List<Product> allProducts = getAllProducts();
                List<Product> fallbackResults = allProducts.stream()
                        .filter(product -> product.getName() != null &&
                                product.getName().toLowerCase().contains(name.toLowerCase()))
                        .collect(Collectors.toList());
                System.out.println("内存搜索备选方案找到 " + fallbackResults.size() + " 个结果");
                return fallbackResults;
            } catch (Exception ex) {
                System.err.println("内存搜索备选方案也失败: " + ex.getMessage());
                return new ArrayList<>();
            }
        }
    }

    @Override
    public List<Product> getProductsByCategory(String category) {
        return productRepository.findByCategory(category);
    }

    @Override
    public List<Product> getProductsByBrand(String brand) {
        return productRepository.findByBrand(brand);
    }

    @Override
    public List<Product> getProductsByPriceRange(BigDecimal minPrice, BigDecimal maxPrice) {
        return productRepository.findByPriceBetween(minPrice, maxPrice);
    }

    @Override
    public List<Product> getProductsByTag(String tag) {
        return productRepository.findByTagsContaining(tag);
    }

    @Override
    public List<Product> getAvailableProducts() {
        return productRepository.findByStockGreaterThan(0);
    }

    @Override
    public Optional<Product> updateProduct(String id, Product product) {
        return productRepository.findById(id).map(existingProduct -> {
            product.setId(id);
            product.setCreateTime(existingProduct.getCreateTime());
            product.setUpdateTime(LocalDateTime.now());
            return productRepository.save(product);
        });
    }

    @Override
    public Optional<Product> updateStock(String id, Integer newStock) {
        return productRepository.findById(id).map(product -> {
            product.setStock(newStock);
            product.setUpdateTime(LocalDateTime.now());
            if (newStock <= 0) {
                product.setStatus("OUT_OF_STOCK");
            } else if ("OUT_OF_STOCK".equals(product.getStatus())) {
                product.setStatus("AVAILABLE");
            }
            return productRepository.save(product);
        });
    }

    @Override
    public Optional<Product> updatePrice(String id, BigDecimal newPrice) {
        return productRepository.findById(id).map(product -> {
            product.setPrice(newPrice);
            product.setUpdateTime(LocalDateTime.now());
            return productRepository.save(product);
        });
    }

    @Override
    public Optional<Product> updateStatus(String id, String status) {
        return productRepository.findById(id).map(product -> {
            product.setStatus(status);
            product.setUpdateTime(LocalDateTime.now());
            return productRepository.save(product);
        });
    }

    @Override
    public boolean deleteProduct(String id) {
        if (productRepository.existsById(id)) {
            productRepository.deleteById(id);
            return true;
        }
        return false;
    }

    @Override
    public List<Product> createProducts(List<Product> products) {
        products.forEach(product -> {
            product.setId(UUID.randomUUID().toString());
            product.setCreateTime(LocalDateTime.now());
            product.setUpdateTime(LocalDateTime.now());
            if (product.getStatus() == null) {
                product.setStatus("AVAILABLE");
            }
            if (product.getRating() == null) {
                product.setRating(0.0);
            }
            if (product.getReviewCount() == null) {
                product.setReviewCount(0);
            }
        });
        return (List<Product>) productRepository.saveAll(products);
    }

    @Override
    public List<Product> getTopRatedProducts(int limit) {
        try {
            // 修复：使用非分页版本，然后在内存中排序和限制
            List<Product> allProducts = productRepository.findByRatingGreaterThanEqual(0.0);
            return allProducts.stream()
                    .sorted((p1, p2) -> Double.compare(p2.getRating(), p1.getRating()))
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            System.err.println("获取高评分商品失败: " + e.getMessage());
            return new ArrayList<>();
        }
    }

    @Override
    public List<Product> getLatestProducts(int limit) {
        try {
            // 使用JPA方式获取最新商品
            Iterable<Product> products = productRepository.findAll();
            List<Product> allProducts = StreamSupport.stream(products.spliterator(), false)
                    .collect(Collectors.toList());
            return allProducts.stream()
                    .sorted((p1, p2) -> p2.getCreateTime().compareTo(p1.getCreateTime()))
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            System.err.println("获取最新商品失败: " + e.getMessage());
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    @Override
    public List<Product> getRecommendedProducts(String category, int limit) {
        try {
            return productRepository.findByCategory(category)
                    .stream()
                    .filter(product -> product.getRating() >= 4.0)
                    .sorted((p1, p2) -> Double.compare(p2.getRating(), p1.getRating()))
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            System.err.println("获取推荐商品失败: " + e.getMessage());
            return new ArrayList<>();
        }
    }
}