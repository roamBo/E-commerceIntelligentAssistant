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
        return productRepository.findByNameContaining(name);
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
            // 修复：使用分页查询替代类型转换
            Pageable pageable = PageRequest.of(0, Integer.MAX_VALUE, Sort.by(Sort.Direction.DESC, "createTime"));
            return productRepository.findAll(pageable).getContent()
                    .stream()
                    .limit(limit)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            System.err.println("获取最新商品失败: " + e.getMessage());
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