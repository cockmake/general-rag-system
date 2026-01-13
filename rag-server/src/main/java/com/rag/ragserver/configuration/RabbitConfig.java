package com.rag.ragserver.configuration;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.amqp.support.converter.Jackson2JsonMessageConverter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.amqp.support.converter.MessageConverter;
import org.springframework.amqp.rabbit.connection.ConnectionFactory;

@Configuration
public class RabbitConfig {
    @Bean
    public MessageConverter jackson2JsonMessageConverter() {
        return new Jackson2JsonMessageConverter();
    }

    @Bean
    public RabbitTemplate rabbitTemplate(ConnectionFactory connectionFactory, MessageConverter messageConverter) {
        final RabbitTemplate rabbitTemplate = new RabbitTemplate(connectionFactory);
        //设置Json转换器
        rabbitTemplate.setMessageConverter(messageConverter);
        return rabbitTemplate;
    }

    // --- 声明生产者相关的交换机、队列以及绑定 ---
    // --- 消费者相关的使用注解生成 ---
    @Bean
    public DirectExchange serverInteractLLMExchange() {
        return new DirectExchange("server.interact.llm.exchange", true, false);
    }

    @Bean
    public Queue sessionNameGenerateQueue() {
        return QueueBuilder.durable("session.name.generate.producer.queue").build();
    }

    @Bean
    public Binding sessionNameGenerateBinding(DirectExchange serverInteractLLMExchange, Queue sessionNameGenerateQueue) {
        return BindingBuilder.bind(sessionNameGenerateQueue)
                .to(serverInteractLLMExchange)
                .with("session.name.generate.producer.key");
    }

    @Bean
    public Queue documentEmbeddingQueue() {
        return QueueBuilder.durable("rag.document.process.queue").build();
    }

    @Bean
    public Binding documentEmbeddingBinding(DirectExchange serverInteractLLMExchange, Queue documentEmbeddingQueue) {
        return BindingBuilder.bind(documentEmbeddingQueue)
                .to(serverInteractLLMExchange)
                .with("rag.document.process.key");
    }
}
