const API_URL = "https://tx58keyabg.execute-api.us-east-1.amazonaws.com/prod?country=";
const COUNTRY_LIST_PATH = "./country-codes.json";

let countries = [];
let nonprofits = [];
let currentCountry = { name: "—", code: "—" };

const getEl = (id) => document.getElementById(id);

const inputField = getEl("countryInput");
const suggestionBox = getEl("suggestions");
const searchButton = getEl("fetchBtn");
const countryLabel = getEl("countryLabel");
const summaryText = getEl("summaryKpi");
const errorBox = getEl("error");
const emptyBox = getEl("empty");
const cardsContainer = getEl("cards");

async function loadCountryList() {
  try {
    const response = await fetch(COUNTRY_LIST_PATH);
    const data = await response.json();
    countries = data.map((c) => ({ ...c, _lower: c.country_name.toLowerCase() }));
  } catch {
    alert("country-codes.json not found");
  }
}

function findCountryByName(name) {
  if (!name) return null;
  const lower = name.toLowerCase();
  let found = countries.find((x) => x._lower === lower);
  if (found) return found;
  return countries.find((x) => x._lower.startsWith(lower)) || null;
}

function showCountrySuggestions(value) {
  const query = value.trim().toLowerCase();
  if (!query || !countries.length) {
    suggestionBox.classList.add("d-none");
    suggestionBox.innerHTML = "";
    return;
  }
  const matched = countries.filter((x) => x._lower.includes(query)).slice(0, 8);
  if (!matched.length) {
    suggestionBox.classList.add("d-none");
    suggestionBox.innerHTML = "";
    return;
  }

  suggestionBox.innerHTML = matched
    .map(
      (r) => `
    <div class="sugg-item" data-code="${r.country_code}" data-name="${r.country_name}">
      <div>${r.country_name}</div><div class="sugg-code">${r.country_code}</div>
    </div>`
    )
    .join("");

  suggestionBox.classList.remove("d-none");

  Array.from(suggestionBox.children).forEach((el) => {
    el.onclick = () => {
      inputField.value = el.getAttribute("data-name");
      suggestionBox.classList.add("d-none");
      fetchCountryData(el.getAttribute("data-code"), el.getAttribute("data-name"));
    };
  });
}

function setLoadingState(isLoading) {
  if (isLoading) {
    suggestionBox.classList.add("d-none");
    searchButton.dataset.label = searchButton.textContent;
    searchButton.innerHTML = `
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      Searching...`;
    searchButton.disabled = true;
    inputField.disabled = true;
  } else {
    searchButton.innerHTML = searchButton.dataset.label || "Search";
    searchButton.disabled = false;
    inputField.disabled = false;
  }
}

async function fetchCountryData(countryCode, fallbackName) {
  errorBox.classList.add("d-none");
  emptyBox.classList.add("d-none");
  cardsContainer.classList.add("d-none");
  cardsContainer.innerHTML = "";

  setLoadingState(true);

  try {
    const response = await fetch(API_URL + encodeURIComponent(countryCode));
    if (!response.ok) throw new Error("HTTP " + response.status);
    const data = await response.json();

    const resolvedCode = (data.country && data.country.code) || countryCode;
    const localMatch = countries.find((x) => x.country_code === resolvedCode);
    const resolvedName =
      (localMatch && localMatch.country_name) ||
      (data.country && data.country.name) ||
      fallbackName ||
      resolvedCode;

    nonprofits = Array.isArray(data.nonprofits) ? data.nonprofits : [];
    currentCountry = { name: resolvedName, code: resolvedCode };

    countryLabel.textContent = `Country: ${currentCountry.name} (${currentCountry.code})`;
    const updatedDate =
      data.summary && data.summary.generated_at
        ? new Date(data.summary.generated_at).toLocaleString()
        : "—";
    summaryText.textContent = `${nonprofits.length} organisations • Updated ${updatedDate}`;

    renderNonprofitCards();
  } catch (err) {
    errorBox.classList.remove("d-none");
    errorBox.textContent = "Failed to load. " + err.message;
  } finally {
    setLoadingState(false);
  }
}

function renderNonprofitCards() {
  if (!nonprofits.length) {
    emptyBox.classList.remove("d-none");
    return;
  }

  cardsContainer.innerHTML = nonprofits
    .map((org) => {
      const cover = org.coverImageUrl
        ? `<img class="org-cover" src="${org.coverImageUrl}" alt="">`
        : `<div class="org-cover"></div>`;
      const logo = org.logoUrl
        ? `<img class="org-logo" src="${org.logoUrl}" alt="">`
        : `<div class="org-logo bg-light"></div>`;
      const locationTag = org.location
        ? `<span class="badge rounded-pill text-bg-light">📍 ${org.location}</span>`
        : "";
      const donationLink = org.profileUrl || org.website;
      const donateButton = donationLink
        ? `<a class="btn btn-primary btn-sm" href="${donationLink}" target="_blank" rel="noopener">Donate</a>`
        : `<button class="btn btn-primary btn-sm" disabled>Donate</button>`;
      const profileButton = org.profileUrl
        ? `<a class="btn btn-outline-secondary btn-sm" href="${org.profileUrl}" target="_blank" rel="noopener">Profile</a>`
        : "";
      const websiteButton = org.website
        ? `<a class="btn btn-outline-secondary btn-sm" href="${org.website}" target="_blank" rel="noopener">Website</a>`
        : "";

      return `
        <div class="col-12 col-sm-6 col-md-4">
          <div class="card h-100">
            ${cover}
            <div class="card-body d-flex flex-column">
              <div class="d-flex align-items-center gap-2 mb-2">
                ${logo}
                <div>
                  <div class="fw-bold">${org.name || "—"}</div>
                  ${locationTag}
                </div>
              </div>
              <p class="card-text clamp-3">${org.description || ""}</p>
              <div class="mt-auto d-flex gap-2 pt-2">
                ${donateButton}${profileButton}${websiteButton}
              </div>
            </div>
          </div>
        </div>`;
    })
    .join("");

  cardsContainer.classList.remove("d-none");
}

// --- Event Listeners ---

inputField.addEventListener("input", (e) => showCountrySuggestions(e.target.value));

document.addEventListener("click", (e) => {
  if (e.target !== inputField && !suggestionBox.contains(e.target)) {
    suggestionBox.classList.add("d-none");
  }
});

searchButton.addEventListener("click", () => {
  const match = findCountryByName(inputField.value.trim());
  if (!match) {
    alert("Pick a country from the suggestions.");
    return;
  }
  fetchCountryData(match.country_code, match.country_name);
});

// --- Initialize on page load ---
(async () => {
  await loadCountryList();
})();
