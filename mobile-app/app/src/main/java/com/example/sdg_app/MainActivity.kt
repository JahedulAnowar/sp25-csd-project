package com.example.sdg_app  // Your package name will be here

import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import retrofit2.Call
import retrofit2.Callback
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class MainActivity : AppCompatActivity() {

    private lateinit var apiService: CountryApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Find the views by their IDs
        val searchEditText = findViewById<EditText>(R.id.search)
        val button = findViewById<Button>(R.id.button)
        val returnTextView = findViewById<TextView>(R.id.returnText)

        // Clear the EditText when user clicks on it
        searchEditText.setOnFocusChangeListener { _, hasFocus ->
            if (hasFocus && searchEditText.text.toString() == "country") {
                searchEditText.text.clear()
            }
        }

        // Set up Retrofit
        val retrofit = Retrofit.Builder()
            .baseUrl("https://restcountries.com/v3.1/")
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        apiService = retrofit.create(CountryApiService::class.java)

        // Set up button click listener
        button.setOnClickListener {
            // Get the text from the EditText
            val userInput = searchEditText.text.toString().trim()

            // Check if input is empty
            if (userInput.isEmpty()) {
                returnTextView.text = "Please enter a country name"
            } else {
                // Fetch country data from API
                fetchCountryData(userInput, returnTextView)
            }
        }
    }

    private fun fetchCountryData(countryName: String, resultTextView: TextView) {
        // Show loading message
        resultTextView.text = "Loading..."

        // Make API call
        apiService.getCountryByName(countryName).enqueue(object : Callback<List<Country>> {
            override fun onResponse(call: Call<List<Country>>, response: Response<List<Country>>) {
                if (response.isSuccessful) {
                    val countries = response.body()
                    if (!countries.isNullOrEmpty()) {
                        val country = countries[0]

                        // Format and display the data
                        val displayText = """
                            Country: ${country.name.common}
                            Official Name: ${country.name.official}
                            Capital: ${country.capital?.joinToString(", ") ?: "N/A"}
                            Population: ${String.format("%,d", country.population)}
                            Region: ${country.region}
                            Subregion: ${country.subregion ?: "N/A"}
                        """.trimIndent()

                        resultTextView.text = displayText
                    } else {
                        resultTextView.text = "Country not found"
                    }
                } else {
                    resultTextView.text = "Error: Country not found"
                    Toast.makeText(this@MainActivity, "Failed to fetch data", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<List<Country>>, t: Throwable) {
                resultTextView.text = "Network error. Please check your connection."
                Toast.makeText(this@MainActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}