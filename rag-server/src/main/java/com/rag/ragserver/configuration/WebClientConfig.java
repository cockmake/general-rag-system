package com.rag.ragserver.configuration;

import lombok.Data;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.reactive.function.client.WebClient;

@Data
@Configuration
@ConfigurationProperties(prefix = "llm")
public class WebClientConfig {
    private String host;
    private String port;

    @Bean
    public WebClient webClient(WebClient.Builder builder) {
        // 这里可以配置全局的 BaseUrl，或者超时策略

        return builder
                .baseUrl("http://" + host + ":" + port)
                .build();
    }
}
