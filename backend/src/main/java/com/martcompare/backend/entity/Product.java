package com.martcompare.backend.entity;

import jakarta.persistence.*;
import lombok.Getter;

@Getter
@Entity
@Table(name = "product")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "mart_id")
    private Long martId;

    private String name;

    private Integer price;

    @Column(name = "event_type")
    private String eventType;
}
