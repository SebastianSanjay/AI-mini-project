// Configuration file for API connections
const API_BASE = "http://localhost:8000";
const WS_BASE  = "ws://localhost:8000";

// Standard supported languages mapped to Indian regional + English
const SUPPORTED_LANGUAGES = [
    "English", "Hindi", "Kannada", "Tamil", "Telugu",
    "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi",
    "Odia", "Assamese", "Urdu", "Sanskrit", "Konkani",
    "Manipuri", "Nepali", "Kashmiri", "Sindhi", "Bodo",
    "Dogri", "Maithili", "Santali"
];

// Utility to populate dropdowns
function populateLanguageDropdown(selectElementId, includeEmpty = false) {
    const select = document.getElementById(selectElementId);
    if (!select) return;

    SUPPORTED_LANGUAGES.forEach(lang => {
        const option = document.createElement("option");
        option.value = lang;
        option.textContent = lang;
        select.appendChild(option);
    });
}
