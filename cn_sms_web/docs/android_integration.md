# Android Integration Guide

## Overview

This guide explains how to connect your Android app to the CNSMS backend.

## Connection Options

### Option 1: Local Network (Recommended for Development)

1. Connect Android device and PC to same Wi-Fi network
2. Find your PC's IP address:
   ```bash
   # Windows
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   ```
3. In Android app, set:
   ```kotlin
   const val BASE_URL = "http://192.168.1.100:5000/api/"
   ```

### Option 2: USB Debugging with ADB Port Forward

```bash
# Forward device port to PC
adb reverse tcp:5000 tcp:5000

# In Android app
const val BASE_URL = "http://localhost:5000/api/"
```

### Option 3: ngrok (HTTPS Tunnel)

```bash
# Install and run ngrok
ngrok http 5000

# Use the HTTPS URL in Android app
const val BASE_URL = "https://abc123.ngrok.io/api/"
```

## Android Network Configuration

Add to `AndroidManifest.xml`:

```xml
<!-- For HTTP connections (development) -->
<application
    android:usesCleartextTraffic="true"
    ... >
```

For Android 9+, create `res/xml/network_security_config.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">192.168.1.100</domain>
        <domain includeSubdomains="true">10.0.2.2</domain>
    </domain-config>
</network-security-config>
```

## Sample Code

### Login

```kotlin
// Retrofit interface
interface AuthApi {
    @POST("login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
}

// Data classes
data class LoginRequest(val email: String, val password: String)
data class LoginResponse(
    val message: String,
    val token: String,
    val user: User
)

// Usage
val response = authApi.login(LoginRequest(email, password))
if (response.isSuccessful) {
    val token = response.body()?.token
    // Save token for future requests
}
```

### Upload Incident

```kotlin
interface IncidentApi {
    @Multipart
    @POST("incidents")
    suspend fun createIncident(
        @Header("Authorization") token: String,
        @Part image: MultipartBody.Part,
        @Part("description") description: RequestBody,
        @Part("category") category: RequestBody,
        @Part("location") location: RequestBody
    ): Response<IncidentResponse>
}
```

## Testing with curl

```bash
# Register
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@test.com","password":"test123"}'

# Login
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123"}'

# Upload Incident (replace TOKEN)
curl -X POST http://localhost:5000/api/incidents \
  -H "Authorization: Bearer TOKEN" \
  -F "image=@photo.jpg" \
  -F "description=Suspicious activity" \
  -F "category=Suspicious" \
  -F "location=Building A"
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check firewall, verify IP address |
| 401 Unauthorized | Token expired, re-login |
| SSL error | Use HTTP for dev or valid HTTPS cert |
| Timeout | Check server is running, network connected |
