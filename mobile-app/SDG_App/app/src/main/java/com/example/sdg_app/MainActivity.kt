package com.example.sdg_app

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
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import java.util.Locale

class MainActivity : AppCompatActivity() {

    companion object {
        private const val PI_KEY = "ptBqdW6nzLavUqUPpEa5530vVQFWz8TKaoYFYthO"
    }

    private lateinit var apiService: CountryApiService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Find the views by their IDs
        val searchEditText = findViewById<EditText>(R.id.search)
        val button = findViewById<Button>(R.id.button)
        val returnTextView = findViewById<TextView>(R.id.returnText)

        // Make links in the TextView clickable
        returnTextView.movementMethod = android.text.method.LinkMovementMethod.getInstance()

        // Clear the EditText when user clicks on it
        searchEditText.setOnFocusChangeListener { _, hasFocus ->
            if (hasFocus && searchEditText.text.toString() == "country") {
                searchEditText.text.clear()
            }
        }

        // Set up Retrofit with the AWS API
        val interceptor = Interceptor { chain ->
            val newReq = chain.request().newBuilder()
                .addHeader("x-api-key", PI_KEY)
                .build()
            chain.proceed(newReq)
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(interceptor)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl("https://lvuxh1wgz6.execute-api.us-east-1.amazonaws.com/")
            .client(client)
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
                // Convert country name to ISO 3-letter code
                val countryCode = getCountryCode(userInput)

                if (countryCode != null) {
                    // Fetch country data from API
                    fetchCountryData(countryCode, returnTextView)
                } else {
                    returnTextView.text = "Country not recognized. Please try again with a valid country name."
                    Toast.makeText(this, "Invalid country name", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    // Convert country name to ISO 3-letter code
    private fun getCountryCode(countryName: String): String? {
        val locales = Locale.getAvailableLocales()

        for (locale in locales) {
            val displayCountry = locale.displayCountry

            // Check if the country name matches (case-insensitive)
            if (displayCountry.equals(countryName, ignoreCase = true)) {
                // Get ISO 3-letter country code
                return locale.isO3Country
            }
        }

        return null
    }

    private fun fetchCountryData(countryCode: String, resultTextView: TextView) {
        // Show loading message
        resultTextView.text = "Loading data for country code: $countryCode..."

        // Make API call
        apiService.getCountryData(countryCode).enqueue(object : Callback<ApiResponse> {
            override fun onResponse(call: Call<ApiResponse>, response: Response<ApiResponse>) {
                if (response.isSuccessful) {
                    val data = response.body()

                    if (data != null) {
                        // Build display text with all three sections
                        val displayText = android.text.SpannableStringBuilder().apply {
                            // ===== SECTION 1: COUNTRY INFO =====
                            append("━━━━━━━━━━━━━━━━━━━━━━━━\n")
                            append("     COUNTRY INFORMATION\n")
                            append("━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

                            if (data.country != null) {
                                append("Country: ${data.country.name ?: "N/A"}\n")
                                append("Code: ${data.country.code ?: "N/A"}\n")
                            } else {
                                append("No country information available\n")
                            }

                            // ===== SECTION 2: POVERTY DATA =====
                            append("\n━━━━━━━━━━━━━━━━━━━━━━━━\n")
                            append("     POVERTY DATA\n")
                            append("━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

                            if (!data.poverty_data.isNullOrEmpty()) {
                                // Show summary first
                                append("Total Years of Data: ${data.summary?.total_poverty_data_years ?: data.poverty_data.size}\n\n")

                                // Show latest data (last in the list)
                                val latestData = data.poverty_data.last()
                                append("📊 LATEST DATA (${latestData.reporting_year})\n")
                                append("─────────────────────────\n")
                                append("Survey: ${latestData.survey_acronym ?: "N/A"}\n")
                                append("Poverty Rate: ${latestData.headcount?.let { String.format("%.2f%%", it * 100) } ?: "N/A"}\n")
                                append("Population: ${latestData.reporting_pop?.let { String.format("%,.0f", it) } ?: "N/A"}\n")
                                append("Mean Income: ${latestData.mean?.let { String.format("%.2f", it) } ?: "N/A"}\n")
                                append("Median Income: ${latestData.median?.let { String.format("%.2f", it) } ?: "N/A"}\n")
                                append("Gini Index: ${latestData.gini?.let { String.format("%.4f", it) } ?: "N/A"}\n")
                                append("Poverty Line: ${latestData.poverty_line ?: "N/A"}\n\n")

                                // Show historical trend (oldest vs latest)
                                if (data.poverty_data.size > 1) {
                                    val oldestData = data.poverty_data.first()
                                    append("📈 HISTORICAL TREND\n")
                                    append("─────────────────────────\n")
                                    append("${oldestData.reporting_year}: ${oldestData.headcount?.let { String.format("%.2f%%", it * 100) } ?: "N/A"}\n")
                                    append("${latestData.reporting_year}: ${latestData.headcount?.let { String.format("%.2f%%", it * 100) } ?: "N/A"}\n")

                                    // Calculate change if both values exist
                                    if (oldestData.headcount != null && latestData.headcount != null) {
                                        val change = (oldestData.headcount - latestData.headcount) * 100
                                        val direction = if (change > 0) "↓ Decreased" else "↑ Increased"
                                        append("Change: $direction by ${String.format("%.2f", kotlin.math.abs(change))}%\n")
                                    }
                                }
                            } else {
                                append("No poverty data available\n")
                            }

                            // ===== SECTION 3: NON-PROFIT ORGANIZATIONS =====
                            append("\n━━━━━━━━━━━━━━━━━━━━━━━━\n")
                            append("     NON-PROFIT ORGANIZATIONS\n")
                            append("━━━━━━━━━━━━━━━━━━━━━━━━\n\n")

                            if (!data.nonprofits.isNullOrEmpty()) {
                                append("Total Organizations: ${data.summary?.total_nonprofits_found ?: data.nonprofits.size}\n\n")

                                // Show first 5 organizations (to avoid too much text)
                                val orgsToShow = data.nonprofits.take(5)
                                orgsToShow.forEachIndexed { index, org ->
                                    append("${index + 1}. ${org.name ?: "Unknown Organization"}\n")

                                    if (!org.description.isNullOrEmpty()) {
                                        append("   ${org.description}\n")
                                    }

                                    if (!org.location.isNullOrEmpty()) {
                                        append("   📍 ${org.location}\n")
                                    }

                                    if (!org.website.isNullOrEmpty()) {
                                        val startIndex = length
                                        append("   🌐 ${org.website}\n")

                                        // Make the URL clickable
                                        setSpan(
                                            android.text.style.URLSpan(org.website),
                                            startIndex + 5, // Skip "   🌐 "
                                            length - 1,     // Before the newline
                                            android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
                                        )
                                    }

                                    if (!org.tags.isNullOrEmpty()) {
                                        append("   🏷️  ${org.tags.take(3).joinToString(", ")}\n")
                                    }

                                    append("\n")
                                }

                                // Show message if there are more organizations
                                if (data.nonprofits.size > 5) {
                                    append("... and ${data.nonprofits.size - 5} more organizations\n")
                                }
                            } else {
                                append("No nonprofit organizations found\n")
                            }
                        }

                        resultTextView.text = displayText
                    } else {
                        resultTextView.text = "No data available for this country"
                    }
                } else {
                    resultTextView.text = "Error: ${response.code()}\nUnable to fetch data for country code: $countryCode"
                    Toast.makeText(this@MainActivity, "Failed to fetch data", Toast.LENGTH_SHORT).show()
                }
            }

            override fun onFailure(call: Call<ApiResponse>, t: Throwable) {
                resultTextView.text = "Network error. Please check your connection.\n\nError: ${t.message}"
                Toast.makeText(this@MainActivity, "Network error: ${t.message}", Toast.LENGTH_SHORT).show()
            }
        })
    }
}