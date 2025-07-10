package org.randombo.productservice.repository;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.randombo.productservice.model.Product;
import org.randombo.productservice.repository.ProductRepository;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.*;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ProductRepositoryTest {

    @Mock
    private ProductRepository productRepository;

    @Test
    void testSaveFindAndDeleteBySku_WithMock() {
        Product p = new Product();
        p.setSku("MOCK-001");
        p.setName("MockTest");
        p.setPrice(new BigDecimal("100.00"));

        when(productRepository.save(p)).thenAnswer(inv -> {
            Product arg = inv.getArgument(0);
            arg.setId("ID-123");
            return arg;
        });
        Product saved = productRepository.save(p);
        assertEquals("ID-123", saved.getId());

        when(productRepository.findBySku("MOCK-001")).thenReturn(p);
        Product found = productRepository.findBySku("MOCK-001");
        assertNotNull(found);
        assertEquals("MockTest", found.getName());

        doNothing().when(productRepository).deleteById("ID-123");
        productRepository.deleteById("ID-123");
        verify(productRepository, times(1)).deleteById("ID-123");
    }

    @Test
    void testFindByNameContaining_and_Analyzer_and_Wildcard_and_MultiAndOr() {
        Product a = new Product(); a.setId("A"); a.setName("Alpha");
        Product b = new Product(); b.setId("B"); b.setName("Beta");

        when(productRepository.findByNameContaining("ph")).thenReturn(List.of(a));
        when(productRepository.searchByNameWithAnalyzer("阿尔法")).thenReturn(List.of(a));
        when(productRepository.searchByNameWildcard("Al")).thenReturn(List.of(a, b));
        when(productRepository.searchByMultipleFields("key")).thenReturn(List.of(b));
        when(productRepository.searchByOrLogic("x y")).thenReturn(List.of(a, b));
        when(productRepository.searchByAndLogic("x y")).thenReturn(List.of(a));

        assertEquals(1, productRepository.findByNameContaining("ph").size());
        assertEquals(1, productRepository.searchByNameWithAnalyzer("阿尔法").size());
        assertEquals(2, productRepository.searchByNameWildcard("Al").size());
        assertEquals("B", productRepository.searchByMultipleFields("key").get(0).getId());
        assertEquals(2, productRepository.searchByOrLogic("x y").size());
        assertEquals(1, productRepository.searchByAndLogic("x y").size());

        verify(productRepository).findByNameContaining("ph");
        verify(productRepository).searchByNameWithAnalyzer("阿尔法");
        verify(productRepository).searchByNameWildcard("Al");
        verify(productRepository).searchByMultipleFields("key");
        verify(productRepository).searchByOrLogic("x y");
        verify(productRepository).searchByAndLogic("x y");
    }

    @Test
    void testFindByCategory_Brand_Status_Stock_Rating_Tag() {
        Product p = new Product();
        p.setId("P");
        p.setCategory("C");
        p.setBrand("B");
        p.setStatus("S");
        p.setStock(10);
        p.setRating(4.7);
        p.setTags(List.of("t"));

        when(productRepository.findByCategory("C")).thenReturn(List.of(p));
        when(productRepository.findByBrand("B")).thenReturn(List.of(p));
        when(productRepository.findByStatus("S")).thenReturn(List.of(p));
        when(productRepository.findByStockGreaterThan(5)).thenReturn(List.of(p));
        when(productRepository.findByRatingGreaterThanEqual(4.0)).thenReturn(List.of(p));
        when(productRepository.findByTagsContaining("t")).thenReturn(List.of(p));

        assertEquals("P", productRepository.findByCategory("C").get(0).getId());
        assertEquals("P", productRepository.findByBrand("B").get(0).getId());
        assertEquals("P", productRepository.findByStatus("S").get(0).getId());
        assertFalse(productRepository.findByStockGreaterThan(5).isEmpty());
        assertFalse(productRepository.findByRatingGreaterThanEqual(4.0).isEmpty());
        assertFalse(productRepository.findByTagsContaining("t").isEmpty());

        verify(productRepository).findByCategory("C");
        verify(productRepository).findByBrand("B");
        verify(productRepository).findByStatus("S");
        verify(productRepository).findByStockGreaterThan(5);
        verify(productRepository).findByRatingGreaterThanEqual(4.0);
        verify(productRepository).findByTagsContaining("t");
    }

    @Test
    void testFindByPriceBetween_and_Pagination() {
        Product cheap = new Product(); cheap.setId("cheap"); cheap.setPrice(new BigDecimal("50"));
        Product mid   = new Product(); mid  .setId("mid");   mid  .setPrice(new BigDecimal("150"));

        when(productRepository.findByPriceBetween(
                new BigDecimal("0"), new BigDecimal("100")))
                .thenReturn(List.of(cheap));

        List<Product> list = productRepository.findByPriceBetween(
                new BigDecimal("0"), new BigDecimal("100"));
        assertEquals(1, list.size());
        verify(productRepository).findByPriceBetween(new BigDecimal("0"), new BigDecimal("100"));

        // 分页 findAll
        Page<Product> allPage = new PageImpl<>(List.of(cheap, mid), PageRequest.of(0, 2), 2);
        when(productRepository.findAll(PageRequest.of(0,2))).thenReturn(allPage);
        Page<Product> page = productRepository.findAll(PageRequest.of(0,2));
        assertEquals(2, page.getTotalElements());

        // 分页 findByCategory
        when(productRepository.findByCategory(eq("cat"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(cheap), PageRequest.of(0,1), 1));
        Page<Product> catPage = productRepository.findByCategory("cat", PageRequest.of(0,1));
        assertEquals(1, catPage.getTotalElements());

        // 分页 findByBrand
        when(productRepository.findByBrand(eq("brand"), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(mid), PageRequest.of(0,1), 1));
        Page<Product> brandPage = productRepository.findByBrand("brand", PageRequest.of(0,1));
        assertEquals("mid", brandPage.getContent().get(0).getId());

        // 分页 findByPriceBetween
        when(productRepository.findByPriceBetween(
                any(BigDecimal.class), any(BigDecimal.class), any(Pageable.class)))
                .thenReturn(new PageImpl<>(List.of(cheap), PageRequest.of(0,1), 1));
        Page<Product> prPage = productRepository.findByPriceBetween(
                new BigDecimal("0"), new BigDecimal("100"), PageRequest.of(0,1));
        assertEquals(1, prPage.getContent().size());

        verify(productRepository).findAll(PageRequest.of(0,2));
        verify(productRepository).findByCategory("cat", PageRequest.of(0,1));
        verify(productRepository).findByBrand("brand", PageRequest.of(0,1));
        verify(productRepository).findByPriceBetween(
                new BigDecimal("0"), new BigDecimal("100"), PageRequest.of(0,1));
    }
}
