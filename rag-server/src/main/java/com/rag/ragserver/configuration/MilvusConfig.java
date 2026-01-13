package com.rag.ragserver.configuration;

import io.milvus.v2.client.ConnectConfig;
import io.milvus.v2.client.MilvusClientV2;
import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
@ConfigurationProperties(prefix = "milvus")
public class MilvusConfig {
    private String uri;
    private String token;

    @Bean
    public MilvusClientV2 milvusClientV2() {
        ConnectConfig config = ConnectConfig.builder()
                .uri(uri)
                .token(token)
                .build();
        return new MilvusClientV2(config);
    }
}
