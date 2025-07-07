package org.randombo.productservice.repository;

import org.randombo.productservice.model.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.elasticsearch.annotations.Query; //
import org.springframework.data.elasticsearch.repository.ElasticsearchRepository;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.List;

@Repository
public interface ProductRepository extends ElasticsearchRepository<Product, String> {

    // 根据名称搜索
    List<Product> findByNameContaining(String name);

    // 新增：使用Elasticsearch查询进行更精确的中文搜索
    @Query("{\"match\": {\"name\": {\"query\": \"?0\", \"analyzer\": \"ik_smart\"}}}")
    List<Product> searchByNameWithAnalyzer(String name);

    // 新增：模糊搜索，支持部分匹配
    @Query("{\"wildcard\": {\"name\": {\"value\": \"*?0*\"}}}")
    List<Product> searchByNameWildcard(String name);

    // 新增：多字段搜索
    @Query("{\"multi_match\": {\"query\": \"?0\", \"fields\": [\"name^2\", \"description\", \"specifications\"], \"analyzer\": \"ik_smart\"}}")
    List<Product> searchByMultipleFields(String keyword);

    // 新增：OR逻辑多关键词搜索
    @Query("{\"bool\": {\"should\": [{\"multi_match\": {\"query\": \"?0\", \"fields\": [\"name^2\", \"description\", \"specifications\"], \"analyzer\": \"ik_smart\"}}]}}")
    List<Product> searchByOrLogic(String keywords);

    // 新增：AND逻辑多关键词搜索
    @Query("{\"bool\": {\"must\": [{\"multi_match\": {\"query\": \"?0\", \"fields\": [\"name^2\", \"description\", \"specifications\"], \"analyzer\": \"ik_smart\"}}]}}")
    List<Product> searchByAndLogic(String keywords);

    // 根据分类查询
    List<Product> findByCategory(String category);

    // 根据品牌查询
    List<Product> findByBrand(String brand);

    // 根据状态查询
    List<Product> findByStatus(String status);

    // 根据价格范围查询
    List<Product> findByPriceBetween(BigDecimal minPrice, BigDecimal maxPrice);

    // 根据库存查询
    List<Product> findByStockGreaterThan(Integer minStock);

    // 根据评分查询
    List<Product> findByRatingGreaterThanEqual(Double minRating);

    // 根据标签查询
    List<Product> findByTagsContaining(String tag);

    // 根据SKU查询
    Product findBySku(String sku);

    // 分页查询所有商品
    Page<Product> findAll(Pageable pageable);

    // 根据分类分页查询
    Page<Product> findByCategory(String category, Pageable pageable);

    // 根据品牌分页查询
    Page<Product> findByBrand(String brand, Pageable pageable);

    // 根据价格范围分页查询
    Page<Product> findByPriceBetween(BigDecimal minPrice, BigDecimal maxPrice, Pageable pageable);
}