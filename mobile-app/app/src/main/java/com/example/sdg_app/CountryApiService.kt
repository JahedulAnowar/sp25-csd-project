package com.example.sdg_app

import retrofit2.Call
import retrofit2.http.GET
import retrofit2.http.Path

interface CountryApiService {
    @GET("name/{country}")
    fun getCountryByName(@Path("country") countryName: String): Call<List<Country>>
}