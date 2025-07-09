package org.randombo.orderservice.config;

import org.randombo.orderservice.filter.JwtRequestFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.core.userdetails.User;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.provisioning.InMemoryUserDetailsManager;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity // 启用Spring Security的Web安全功能
public class SecurityConfig {

    // 移除构造函数注入 JwtRequestFilter
    // private final JwtRequestFilter jwtRequestFilter;
    // public SecurityConfig(JwtRequestFilter jwtRequestFilter) {
    //     this.jwtRequestFilter = jwtRequestFilter;
    // }

    // 配置密码编码器
    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    // 配置认证管理器，用于处理用户认证
    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authenticationConfiguration) throws Exception {
        return authenticationConfiguration.getAuthenticationManager();
    }

    // 临时配置内存用户（实际项目中应替换为从数据库加载用户）
    @Bean
    public UserDetailsService userDetailsService(PasswordEncoder passwordEncoder) { // 注入PasswordEncoder
        UserDetails user = User.builder()
                .username("user") // 替换为你的测试用户名
                .password(passwordEncoder.encode("password")) // 替换为你的测试密码
                .roles("USER")
                .build();
        UserDetails admin = User.builder()
                .username("admin") // 替换为你的测试管理员用户名
                .password(passwordEncoder.encode("adminpass")) // 替换为你的测试管理员密码
                .roles("ADMIN")
                .build();
        return new InMemoryUserDetailsManager(user, admin);
    }

    // 配置安全过滤链
    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http, JwtRequestFilter jwtRequestFilter) throws Exception { // <-- 将 JwtRequestFilter 作为方法参数注入
        http.csrf(csrf -> csrf.disable()) // 禁用CSRF防护，因为我们使用JWT
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/**").permitAll() // 允许所有用户访问认证（登录）接口
                        .anyRequest().authenticated() // 其他所有请求都需要认证
                )
                .sessionManagement(session -> session
                        .sessionCreationPolicy(SessionCreationPolicy.STATELESS) // 设置会话管理为无状态
                )
                .addFilterBefore(jwtRequestFilter, UsernamePasswordAuthenticationFilter.class); // 在UsernamePasswordAuthenticationFilter之前添加JWT过滤器

        return http.build();
    }
}