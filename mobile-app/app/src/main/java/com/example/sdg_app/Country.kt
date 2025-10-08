package com.example.sdg_app

data class Country(
    val name: Name,
    val capital: List<String>?,
    val population: Long,
    val region: String,
    val subregion: String?
)

data class Name(
    val common: String,
    val official: String
)