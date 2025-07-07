package org.randombo.paymentservice.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.randombo.paymentservice.model.Payment;
import org.randombo.paymentservice.service.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.Arrays;

import static org.mockito.BDDMockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(PaymentController.class)
class PaymentControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PaymentService paymentService;

    @Autowired
    private ObjectMapper objectMapper;

    private Payment samplePayment;

    @BeforeEach
    void setUp() {
        samplePayment = new Payment(
                "1",
                "order123",
                "user123",
                new BigDecimal("99.99"),
                "PENDING",
                LocalDateTime.now(),
                LocalDateTime.now()
        );
    }

    @Test
    void testCreatePayment() throws Exception {
        given(paymentService.createPayment(any(Payment.class))).willReturn(samplePayment);

        mockMvc.perform(post("/api/payments")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(samplePayment)))
                .andExpect(status().isCreated())
                .andExpect(jsonPath("$.id").value("1"))
                .andExpect(jsonPath("$.orderId").value("order123"));
    }

    @Test
    void testGetAllPayments() throws Exception {
        given(paymentService.getAllPayments()).willReturn(Arrays.asList(samplePayment));

        mockMvc.perform(get("/api/payments"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].userId").value("user123"));
    }

    @Test
    void testGetPaymentById() throws Exception {
        given(paymentService.getPaymentById("1")).willReturn(samplePayment);

        mockMvc.perform(get("/api/payments/1/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value("1"));
    }

    @Test
    void testUpdatePaymentStatus() throws Exception {
        samplePayment.setStatus("SUCCESS");
        given(paymentService.updatePaymentStatus(eq("1"), eq("SUCCESS"))).willReturn(samplePayment);
        given(paymentService.getPaymentById("1")).willReturn(samplePayment);

        mockMvc.perform(get("/api/payments/1/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"));
    }

    @Test
    void testDeletePayment() throws Exception {
        willDoNothing().given(paymentService).deletePayment("1");

        mockMvc.perform(delete("/api/payments/1"))
                .andExpect(status().isNoContent());
    }
}
