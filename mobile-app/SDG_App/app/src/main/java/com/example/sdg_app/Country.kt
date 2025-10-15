package com.example.sdg_app

// Main response wrapper
data class ApiResponse(
    val country: CountryInfo?,
    val poverty_data: List<PovertyData>?,
    val nonprofits: List<Nonprofit>?,
    val summary: Summary?
)

// Country information
data class CountryInfo(
    val name: String?,
    val code: String?
)

// Poverty data for each year
data class PovertyData(
    val reporting_year: Int?,
    val country_name: String?,
    val headcount: Double?,
    val poverty_gap: Double?,
    val mean: Double?,
    val median: Double?,
    val gini: Double?,
    val reporting_pop: Double?,
    val poverty_line: Double?,
    val survey_acronym: String?,
    val welfare_type: String?
)

// Non-profit organization
data class Nonprofit(
    val name: String?,
    val description: String?,
    val website: String?,
    val location: String?,
    val tags: List<String>?
)

// Summary information
data class Summary(
    val total_nonprofits_found: Int?,
    val total_poverty_data_years: Int?
)