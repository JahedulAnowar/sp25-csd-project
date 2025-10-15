package com.example.sdg_app

import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Query

interface CountryApiService {
    @GET("prod")
    fun getCountryData(@Query("country") countryCode: String): Call<ApiResponse>
}