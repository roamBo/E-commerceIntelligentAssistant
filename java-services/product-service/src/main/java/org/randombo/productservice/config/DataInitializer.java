package org.randombo.productservice.config;

import org.randombo.productservice.model.Product;
import org.randombo.productservice.service.ProductService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.List;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private ProductService productService;

    @Override
    public void run(String... args) throws Exception {
        try {
            // 等待一下让Elasticsearch完全准备好
            Thread.sleep(3000);

            System.out.println("开始检查数据库状态...");

            // 检查是否已有数据
            List<Product> existingProducts = productService.getAllProducts();
            System.out.println("当前数据库中有 " + existingProducts.size() + " 个商品");

            if (existingProducts.isEmpty()) {
                System.out.println("数据库为空，开始初始化测试数据...");
                initializeTestData();
            } else {
                // else 分支：数据库已有数据
                System.out.println("数据库中已有数据，跳过初始化");
                System.out.println("现有商品列表（最多显示 20 条）：");

                existingProducts.stream()        // 将 List 转为 Stream
                        .limit(20)               // 只保留前 20 条
                        .forEach(product ->
                                System.out.println("   - " + product.getName() +
                                        " (¥" + product.getPrice() + ")")
                        );

                // 如果商品总数 > 20，再提示省略了多少
                if (existingProducts.size() > 20) {
                    System.out.println("   ... 其余 " +
                            (existingProducts.size() - 20) +
                            " 条已省略");
                }
            }
        } catch (Exception e) {
            System.err.println("数据初始化失败: " + e.getMessage());
            System.err.println("错误详情: " + e.getClass().getSimpleName());
            e.printStackTrace();

            // 尝试直接初始化数据，不检查现有数据
            try {
                System.out.println("尝试直接初始化数据...");
                initializeTestData();
            } catch (Exception ex) {
                System.err.println("直接初始化也失败: " + ex.getMessage());
            }
        }
    }

    private void initializeTestData() {
        List<Product> testProducts = Arrays.asList(
                // 手机类商品
                createProduct("iPhone 15 Pro", "苹果最新旗舰手机，搭载A17 Pro芯片", "手机", "Apple",
                        new BigDecimal("7999.00"), 100, Arrays.asList("智能手机", "5G", "高端"),
                        "IPHONE15PRO-256GB", "256GB存储，A17 Pro芯片"),

                createProduct("Samsung Galaxy S24", "三星旗舰手机，AI功能强大", "手机", "Samsung",
                        new BigDecimal("6999.00"), 80, Arrays.asList("智能手机", "5G", "AI"),
                        "SAMSUNG-S24-256GB", "256GB存储，骁龙8 Gen 3"),

                createProduct("华为 Mate 60 Pro", "华为旗舰手机，卫星通信", "手机", "Huawei",
                        new BigDecimal("6999.00"), 60, Arrays.asList("智能手机", "5G", "卫星通信"),
                        "HUAWEI-MATE60-256GB", "256GB存储，麒麟9000S"),

                // 电脑类商品
                createProduct("MacBook Pro 14", "专业级笔记本电脑", "电脑", "Apple",
                        new BigDecimal("14999.00"), 50, Arrays.asList("笔记本电脑", "专业级", "M3芯片"),
                        "MBP14-M3-512GB", "14英寸，M3芯片，512GB存储"),

                createProduct("ThinkPad X1 Carbon", "商务轻薄笔记本", "电脑", "Lenovo",
                        new BigDecimal("12999.00"), 40, Arrays.asList("笔记本电脑", "商务", "轻薄"),
                        "THINKPAD-X1-512GB", "14英寸，Intel i7，512GB存储"),

                createProduct("Dell XPS 13", "超薄笔记本", "电脑", "Dell",
                        new BigDecimal("9999.00"), 30, Arrays.asList("笔记本电脑", "超薄", "时尚"),
                        "DELL-XPS13-512GB", "13英寸，Intel i5，512GB存储"),

                // 耳机类商品
                createProduct("AirPods Pro 2", "主动降噪耳机", "耳机", "Apple",
                        new BigDecimal("1899.00"), 200, Arrays.asList("无线耳机", "降噪", "空间音频"),
                        "AIRPODS-PRO2", "主动降噪，空间音频，USB-C充电"),

                createProduct("Sony WH-1000XM5", "顶级降噪耳机", "耳机", "Sony",
                        new BigDecimal("2899.00"), 150, Arrays.asList("无线耳机", "降噪", "Hi-Res"),
                        "SONY-WH1000XM5", "30小时续航，LDAC编码"),

                // 手表类商品
                createProduct("Apple Watch Series 9", "智能手表", "手表", "Apple",
                        new BigDecimal("2999.00"), 120, Arrays.asList("智能手表", "健康监测", "运动"),
                        "APPLE-WATCH-S9", "45mm，心率监测，血氧检测"),

                createProduct("Garmin Fenix 7", "专业运动手表", "手表", "Garmin",
                        new BigDecimal("5999.00"), 80, Arrays.asList("运动手表", "GPS", "专业"),
                        "GARMIN-FENIX7", "太阳能充电，多运动模式")
        );

        try {
            productService.createProducts(testProducts);
            System.out.println("测试数据初始化完成，共创建 " + testProducts.size() + " 个商品");
            System.out.println("创建的商品列表：");
            testProducts.forEach(product ->
                    System.out.println("   - " + product.getName() + " (¥" + product.getPrice() + ")")
            );
        } catch (Exception e) {
            System.err.println("创建商品失败: " + e.getMessage());
            throw e;
        }
    }

    private Product createProduct(String name, String description, String category, String brand,
                                  BigDecimal price, Integer stock, List<String> tags, String sku, String specifications) {
        Product product = new Product();
        product.setName(name);
        product.setDescription(description);
        product.setCategory(category);
        product.setBrand(brand);
        product.setPrice(price);
        product.setStock(stock);
        product.setStatus("AVAILABLE");
        product.setTags(tags);
        product.setImageUrl("https://picsum.photos/400/300?random=" + System.currentTimeMillis());
        product.setSku(sku);
        product.setSpecifications(specifications);
        product.setRating(4.5 + Math.random() * 0.5);
        product.setReviewCount((int)(Math.random() * 100) + 10);

        // 确保设置完整的日期时间
        LocalDateTime now = LocalDateTime.now();
        product.setCreateTime(now);
        product.setUpdateTime(now);

        return product;
    }
}
